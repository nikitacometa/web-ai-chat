# Supabase database interactions
# e.g., fetching rounds, creating bets

from supabase import create_client, Client
from ..config import settings
from ..models import Round as RoundModel, TwitterUser, Bet as BetModel, BetRequest # Modified import
from ..utils.game_logic import calculate_bet_impact # Import the new function
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Literal # Added Literal
import logging

logger = logging.getLogger(__name__)

# Ensure settings are loaded, especially SUPABASE_URL and SUPABASE_KEY
if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    logger.critical("Supabase URL or Key not configured in settings!")
    # Depending on desired behavior, could raise an exception or have a fallback
    # For now, this will likely cause create_client to fail if they are empty strings
    
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def _map_db_round_to_pydantic(db_round_data: dict) -> RoundModel:
    """Helper function to map a raw round dict from Supabase to a RoundModel."""
    left_user = TwitterUser(
        handle="Left Player", 
        avatar_url=db_round_data["left_avatar_url"], 
        display_name="Left Player"
    )
    right_user = TwitterUser(
        handle="Right Player", 
        avatar_url=db_round_data["right_avatar_url"], 
        display_name="Right Player"
    )
    return RoundModel(
        id=db_round_data["id"],
        left_user=left_user,
        right_user=right_user,
        momentum=db_round_data["momentum"],
        pot_amount=float(db_round_data["pot_amount"]),
        start_time=datetime.fromisoformat(db_round_data["start_time"].replace('Z', '+00:00')),
        current_deadline=datetime.fromisoformat(db_round_data["current_deadline"].replace('Z', '+00:00')),
        max_deadline=datetime.fromisoformat(db_round_data["max_deadline"].replace('Z', '+00:00')),
        active=db_round_data["active"],
        battle_image_url=db_round_data.get("battle_image_url"),
        winner=db_round_data.get("winner")
    )

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
            return _map_db_round_to_pydantic(created_db_round)
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
            return _map_db_round_to_pydantic(active_db_round)
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

async def create_bet_in_db(bet_input: BetRequest, round_id: int) -> Optional[BetModel]:
    """
    Creates a new bet in the Supabase 'bets' table.
    Calculates bet impact and includes it in the stored data.
    Returns the created bet data as a Pydantic model, or None on failure.
    """
    now = datetime.now(timezone.utc)
    
    # Calculate impact before creating the record
    impact_value = calculate_bet_impact(amount=bet_input.amount, spell=bet_input.spell)
    
    bet_data_to_insert = {
        "round_id": round_id,
        "wallet_address": bet_input.wallet_address,
        "side": bet_input.side,
        "amount": bet_input.amount,
        "spell": bet_input.spell,
        "timestamp": now.isoformat(),
        "processed": False, # Default, might be updated later if tx_id verification happens
        "impact": impact_value, # Add the calculated impact
        # tx_id is not included here, assuming it's added if/when Algorand tx is verified
    }

    try:
        logger.info(f"Inserting new bet for round {round_id}: {bet_data_to_insert}")
        response = supabase.table("bets").insert(bet_data_to_insert).execute()
        logger.debug(f"Supabase insert bet response: {response}")

        if response.data and len(response.data) > 0:
            created_db_bet = response.data[0]
            # Construct the BetModel from created_db_bet and bet_input
            # Ensure all fields required by BetModel are present
            return BetModel(
                id=created_db_bet["id"],
                round_id=created_db_bet["round_id"],
                wallet_address=created_db_bet["wallet_address"],
                side=created_db_bet["side"],
                amount=float(created_db_bet["amount"]),
                spell=created_db_bet["spell"],
                timestamp=datetime.fromisoformat(created_db_bet["timestamp"].replace('Z', '+00:00')),
                processed=created_db_bet["processed"],
                impact=created_db_bet.get("impact"), # Ensure impact is retrieved
                tx_id=created_db_bet.get("tx_id") # tx_id might not be there initially
            )
        else:
            actual_error = getattr(response, 'error', None)
            logger.error(f"Failed to insert bet or no data returned. Error: {actual_error}. Full response: {response}")
            return None
    except Exception as e:
        logger.error(f"Exception creating bet in Supabase: {e}", exc_info=True)
        return None

async def update_round_after_bet_in_db(round_id: int, bet_amount: float, bet_impact: float, bet_side: Literal["left", "right"]) -> Optional[RoundModel]:
    """
    Updates the round's pot_amount (using bet_amount), momentum (using bet_impact), 
    and current_deadline after a bet.
    Returns the updated round data as a Pydantic model, or None on failure.
    """
    try:
        # First, fetch the current state of the round
        round_response = supabase.table("rounds").select("*").eq("id", round_id).limit(1).execute()
        if not (round_response.data and len(round_response.data) > 0):
            logger.error(f"Round {round_id} not found for update.")
            return None
        
        current_round_data = round_response.data[0]
        logger.debug(f"Current round data for update: {current_round_data}")

        # 1. Update pot_amount
        new_pot_amount = float(current_round_data.get("pot_amount", 0.0)) + bet_amount

        # 2. Update momentum using bet_impact
        current_momentum = int(current_round_data.get("momentum", 50))
        # momentum_change = (bet_amount / 100.0) * 0.1 # OLD LOGIC - REMOVED
        
        if bet_side == "left":
            new_momentum = current_momentum - bet_impact
        else: # bet_side == "right"
            new_momentum = current_momentum + bet_impact
        
        # Clamp momentum between 0 and 100
        new_momentum_clamped = max(0.0, min(100.0, new_momentum))
        # Ensure momentum is stored as an integer if schema expects int
        new_momentum_int = int(round(new_momentum_clamped))


        # 3. Update current_deadline
        current_deadline_dt = datetime.fromisoformat(current_round_data["current_deadline"].replace('Z', '+00:00'))
        max_deadline_dt = datetime.fromisoformat(current_round_data["max_deadline"].replace('Z', '+00:00'))
        
        potential_new_deadline = current_deadline_dt + timedelta(seconds=settings.BET_TIME_EXTENSION_SEC)
        new_current_deadline_dt = min(potential_new_deadline, max_deadline_dt)

        update_payload = {
            "pot_amount": new_pot_amount,
            "momentum": new_momentum_int,
            "current_deadline": new_current_deadline_dt.isoformat(),
        }
        logger.info(f"Updating round {round_id} with payload: {update_payload}")

        response = supabase.table("rounds").update(update_payload).eq("id", round_id).execute()
        logger.debug(f"Supabase update round response: {response}")

        if response.data and len(response.data) > 0:
            updated_db_round = response.data[0]
            return _map_db_round_to_pydantic(updated_db_round)
        else:
            actual_error = getattr(response, 'error', None)
            logger.error(f"Failed to update round or no data returned. Error: {actual_error}. Full response: {response}")
            return None

    except Exception as e:
        logger.error(f"Exception updating round {round_id} after bet: {e}", exc_info=True)
        return None

async def get_bets_for_round_db(round_id: int, limit: Optional[int] = 10, offset: int = 0) -> List[BetModel]:
    """
    Fetches bets for a specific round from Supabase, with pagination.
    Orders bets by timestamp descending (most recent first).
    If limit is None, fetches all bets for the round.
    Returns a list of BetModel instances, or an empty list on failure or if no bets found.
    """
    try:
        query_message = f"Fetching bets for round {round_id}"
        if limit is not None:
            query_message += f" with limit {limit}, offset {offset}"
        else:
            query_message += " (all bets)"
        logger.info(query_message)

        query = (
            supabase.table("bets")
            .select("*")
            .eq("round_id", round_id)
            .order("timestamp", desc=True)
        )

        if limit is not None:
            query = query.range(offset, offset + limit - 1) # Supabase uses range for limit/offset
        
        response = await query.execute() # Changed to await query.execute() as it's an async call now

        logger.debug(f"Supabase get_bets_for_round response: {response}")

        if response.data:
            bets_data = response.data
            return [
                BetModel(
                    id=bet["id"],
                    round_id=bet["round_id"],
                    wallet_address=bet["wallet_address"],
                    side=bet["side"],
                    amount=float(bet["amount"]),
                    spell=bet["spell"],
                    timestamp=datetime.fromisoformat(bet["timestamp"].replace('Z', '+00:00')),
                    processed=bet["processed"],
                    impact=bet.get("impact"),
                    tx_id=bet.get("tx_id")
                )
                for bet in bets_data
            ]
        elif getattr(response, 'error', None):
            logger.error(f"Error fetching bets for round {round_id}: {response.error}")
            return []
        else:
            logger.info(f"No bets found for round {round_id}.")
            return []
    except Exception as e:
        logger.error(f"Exception fetching bets for round {round_id}: {e}", exc_info=True)
        return []

async def end_round_in_db(round_id: int, winner_side: Optional[Literal["left", "right", "draw"]] = None, end_reason: str = "unknown") -> Optional[RoundModel]:
    """
    Ends a round by setting active=False, ended_at=now, and recording the winner.
    Returns the updated round data, or None on failure.
    """
    now = datetime.now(timezone.utc)
    update_payload = {
        "active": False,
        "ended_at": now.isoformat(),
        "winner": winner_side, # Can be 'left', 'right', or 'draw' (or None if still undetermined)
        # We could add an 'end_reason' field to the table if desired
    }
    try:
        logger.info(f"Ending round {round_id}. Winner: {winner_side if winner_side else 'undetermined'}. Reason: {end_reason}. Payload: {update_payload}")
        response = supabase.table("rounds").update(update_payload).eq("id", round_id).execute()
        logger.debug(f"Supabase end_round response: {response}")

        if response.data and len(response.data) > 0:
            ended_db_round = response.data[0]
            return _map_db_round_to_pydantic(ended_db_round)
        else:
            actual_error = getattr(response, 'error', None)
            logger.error(f"Failed to end round {round_id} or no data returned. Error: {actual_error}")
            return None
    except Exception as e:
        logger.error(f"Exception ending round {round_id}: {e}", exc_info=True)
        return None

async def update_round_battle_image_url_in_db(round_id: int, image_url: str) -> bool:
    """
    Updates the battle_image_url for a specific round.
    Returns True on success, False on failure.
    """
    try:
        logger.info(f"Updating battle_image_url for round {round_id} to: {image_url}")
        response = (
            supabase.table("rounds")
            .update({"battle_image_url": image_url})
            .eq("id", round_id)
            .execute()
        )
        logger.debug(f"Supabase update_battle_image_url response: {response}")

        if getattr(response, 'error', None):
            logger.error(f"Error updating battle_image_url for round {round_id}: {response.error}")
            return False
        
        # Check if any row was actually updated (response.data might be empty for update)
        # For supabase-py v2, execute() on an update returns a ModelResponse with data (list of dicts) and count.
        # If response.data is not empty and count > 0, it means the update likely affected rows.
        if response.data and len(response.data) > 0:
             logger.info(f"Successfully updated battle_image_url for round {round_id}.")
             return True
        elif response.count is not None and response.count > 0: # Fallback for some client versions or scenarios
             logger.info(f"Successfully updated battle_image_url for round {round_id} (count based).")
             return True
        else:
            # This might happen if the round_id doesn't exist, or if the value was the same.
            # For our purposes, if no error and no data/count, it could mean no row matched or no change was needed.
            # Consider it a non-failure if no error, but log appropriately.
            logger.warning(f"Update battle_image_url for round {round_id} executed without error, but no data/count returned in response. This might mean the round was not found or value was unchanged. Response: {response}")
            # Depending on strictness, this could be False. For now, if no Supabase error, let's say True if round might not exist.
            # To be stricter, we'd want to confirm the round exists first or that count > 0.
            # For a simple update, if no error is thrown, we can assume the command reached Supabase.
            return True # Assuming no error means the operation was accepted by Supabase

    except Exception as e:
        logger.error(f"Exception updating battle_image_url for round {round_id}: {e}", exc_info=True)
        return False

# Placeholder for fetching bets for a round
# async def get_bets_for_round_from_db(round_id: int, limit: int = 10) -> List[BetModel]:
# pass 