# Supabase database interactions
# e.g., fetching rounds, creating bets

from supabase import create_client, Client
from ..config import settings
from ..models import Round as RoundModel, TwitterUser # Import Pydantic model for type hinting
from datetime import datetime, timezone, timedelta
from typing import Optional, List # Added List for future bets
import logging

logger = logging.getLogger(__name__)

# Ensure settings are loaded, especially SUPABASE_URL and SUPABASE_KEY
if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    logger.critical("Supabase URL or Key not configured in settings!")
    # Depending on desired behavior, could raise an exception or have a fallback
    # For now, this will likely cause create_client to fail if they are empty strings
    
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

async def create_round_in_db(
    left_avatar_url: str, 
    right_avatar_url: str, 
    initial_momentum: int
) -> Optional[RoundModel]:
    """
    Creates a new round in the Supabase 'rounds' table.
    Returns the created round data as a Pydantic model, or None on failure.
    """
    now = datetime.now(timezone.utc)
    current_deadline = now + timedelta(seconds=settings.ROUND_INACTIVITY_TIMEOUT_SEC)
    max_deadline = now + timedelta(seconds=settings.MAX_ROUND_DURATION_SEC)

    # Ensure deadlines do not exceed max_deadline
    current_deadline = min(current_deadline, max_deadline)

    round_data_to_insert = {
        "left_avatar_url": left_avatar_url,
        "right_avatar_url": right_avatar_url,
        "momentum": initial_momentum,
        "pot_amount": 0.0,
        "start_time": now.isoformat(),
        "current_deadline": current_deadline.isoformat(),
        "max_deadline": max_deadline.isoformat(),
        "active": True,
        # ended_at, winner, battle_image_url will use db defaults (NULL)
    }

    try:
        logger.info(f"Inserting new round: {round_data_to_insert}")
        # Ensure table name matches exactly (e.g., 'rounds')
        response = supabase.table("rounds").insert(round_data_to_insert).execute()
        logger.debug(f"Supabase insert response: {response}")

        if response.data and len(response.data) > 0:
            created_db_round = response.data[0]
            left_user = TwitterUser(handle="Left Player", avatar_url=created_db_round["left_avatar_url"], display_name="Left Player")
            right_user = TwitterUser(handle="Right Player", avatar_url=created_db_round["right_avatar_url"], display_name="Right Player")
            
            return RoundModel(
                id=created_db_round["id"],
                left_user=left_user,
                right_user=right_user,
                momentum=created_db_round["momentum"],
                pot_amount=float(created_db_round["pot_amount"]),
                start_time=datetime.fromisoformat(created_db_round["start_time"].replace('Z', '+00:00')),
                current_deadline=datetime.fromisoformat(created_db_round["current_deadline"].replace('Z', '+00:00')),
                max_deadline=datetime.fromisoformat(created_db_round["max_deadline"].replace('Z', '+00:00')),
                active=created_db_round["active"],
                battle_image_url=created_db_round.get("battle_image_url"),
                winner=created_db_round.get("winner")
            )
        else:
            actual_error = getattr(response, 'error', None)
            logger.error(f"Failed to insert round or no data returned. Error: {actual_error}. Full response: {response}")
            return None
    except Exception as e:
        logger.error(f"Exception creating round in Supabase: {e}", exc_info=True)
        return None

async def get_active_round_from_db() -> Optional[RoundModel]:
    """
    Fetches the currently active round from Supabase.
    An active round is one where 'active' is True.
    If multiple are active (should not happen ideally), it fetches the one with the most recent start_time.
    Returns the round data as a Pydantic model, or None if no active round or on error.
    """
    try:
        # Ensure table name matches exactly
        response = (
            supabase.table("rounds")
            .select("*") # Select all columns explicitly if needed for mapping
            .eq("active", True)
            .order("start_time", desc=True)
            .limit(1)
            .execute()
        )
        logger.debug(f"Supabase get_active_round response: {response}")
        if response.data and len(response.data) > 0:
            active_db_round = response.data[0]
            left_user = TwitterUser(handle="Left Player", avatar_url=active_db_round["left_avatar_url"], display_name="Left Player")
            right_user = TwitterUser(handle="Right Player", avatar_url=active_db_round["right_avatar_url"], display_name="Right Player")

            return RoundModel(
                id=active_db_round["id"],
                left_user=left_user,
                right_user=right_user,
                momentum=active_db_round["momentum"],
                pot_amount=float(active_db_round["pot_amount"]),
                start_time=datetime.fromisoformat(active_db_round["start_time"].replace('Z', '+00:00')),
                current_deadline=datetime.fromisoformat(active_db_round["current_deadline"].replace('Z', '+00:00')),
                max_deadline=datetime.fromisoformat(active_db_round["max_deadline"].replace('Z', '+00:00')),
                active=active_db_round["active"],
                battle_image_url=active_db_round.get("battle_image_url"),
                winner=active_db_round.get("winner")
            )
        else:
            logger.info("No active round found.")
            return None
    except Exception as e:
        logger.error(f"Exception fetching active round: {e}", exc_info=True)
        return None

async def deactivate_all_active_rounds_in_db() -> bool:
    """
    Sets 'active' to False for all rounds currently marked as active.
    Returns True on success, False on failure or if an error occurs.
    """
    try:
        logger.info("Attempting to deactivate all currently active rounds.")
        response = (
            supabase.table("rounds")
            .update({"active": False, "ended_at": datetime.now(timezone.utc).isoformat()})
            .eq("active", True)
            .execute()
        )
        logger.debug(f"Supabase deactivate rounds response: {response}")
        
        # The update operation might not return data in the same way insert/select do.
        # We check if there was an error reported by Supabase.
        if getattr(response, 'error', None):
            logger.error(f"Error deactivating rounds: {response.error}")
            return False
        # If no error, assume success. response.count might indicate how many were updated.
        logger.info(f"Successfully sent deactivate request. Records affected (if supported by response): {getattr(response, 'count', 'N/A')}")
        return True
    except Exception as e:
        logger.error(f"Exception deactivating rounds: {e}", exc_info=True)
        return False

# Placeholder for fetching bets for a round
# async def get_bets_for_round_from_db(round_id: int, limit: int = 10) -> List[BetModel]:
#     pass 