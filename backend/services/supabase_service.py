# Supabase database interactions
# e.g., fetching rounds, creating bets

from supabase import create_client, Client
from ..config import settings
from ..models import Round as RoundModel, TwitterUser, Bet as BetModel, BetRequest, GameState # Modified import
from ..utils.game_logic import calculate_bet_impact # Import the new function
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Literal, Tuple # Added Literal and Tuple
import logging

logger = logging.getLogger(__name__)

# Ensure settings are loaded, especially SUPABASE_URL and SUPABASE_KEY
if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
    logger.critical("Supabase URL or Key not configured in settings!")
    # Depending on desired behavior, could raise an exception or have a fallback
    # For now, this will likely cause create_client to fail if they are empty strings
    
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_supabase_client() -> Client:
    """FastAPI dependency to get the global Supabase client."""
    return supabase

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
        
        response = query.execute() # Changed to query.execute() as it's an async call now

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

async def get_ended_unpaid_rounds_from_db(limit: int = 10) -> List[RoundModel]:
    """
    Fetches ended rounds (active=False, winner IS NOT NULL) that have not been paid (paid_at IS NULL).
    Orders by ended_at ascending to process older rounds first.
    """
    try:
        logger.info(f"Fetching up to {limit} ended and unpaid rounds.")
        response = (
            supabase.table("rounds")
            .select("*")
            .eq("active", False)
            .not_("winner", "is", "null") # Winner must be set
            .is_("paid_at", "null")       # paid_at must be null
            .order("ended_at", desc=False) # Process oldest first
            .limit(limit)
            .execute()
        )
        logger.debug(f"Supabase get_ended_unpaid_rounds response: {response}")

        if response.data:
            return [_map_db_round_to_pydantic(db_round) for db_round in response.data]
        elif getattr(response, 'error', None):
            logger.error(f"Error fetching ended unpaid rounds: {response.error}")
            return []
        else:
            logger.info("No ended unpaid rounds found.")
            return []
    except Exception as e:
        logger.error(f"Exception fetching ended unpaid rounds: {e}", exc_info=True)
        return []

async def get_all_rounds_from_db(limit: int = 20, offset: int = 0, active_only: Optional[bool] = None) -> List[RoundModel]:
    """
    Fetches rounds from Supabase with pagination.
    Orders by start_time descending (most recent first).
    Can optionally filter by 'active' status.
    """
    try:
        query_message = f"Fetching rounds with limit {limit}, offset {offset}"
        if active_only is not None:
            query_message += f", active_only={active_only}"
        logger.info(query_message)

        query = supabase.table("rounds").select("*").order("start_time", desc=True).range(offset, offset + limit - 1)
        
        if active_only is not None:
            query = query.eq("active", active_only)
            
        response = query.execute() # Assuming supabase-py v2+ might make execute() awaitable on query itself
                                      # or specific client (like postgrest-py) is async.
                                      # If strictly sync, remove await and ensure client setup is sync for routes.

        logger.debug(f"Supabase get_all_rounds response: {response}")

        if response.data:
            return [_map_db_round_to_pydantic(db_round) for db_round in response.data]
        elif getattr(response, 'error', None):
            logger.error(f"Error fetching rounds: {response.error}")
            return []
        else:
            logger.info("No rounds found for the given criteria.")
            return []
    except Exception as e:
        logger.error(f"Exception fetching rounds: {e}", exc_info=True)
        return []

async def create_mock_game_state_in_db(supabase: Client) -> Optional[RoundModel]:
    """
    Deactivates any current round and sets up a new mock game round with mock bets.
    """
    logger.info("Attempting to set up mock game state.")
    
    # 1. Deactivate any existing active rounds
    await deactivate_all_active_rounds_in_db()
    logger.info("Deactivated any existing active rounds.")

    # 2. Define Mock Data
    now = datetime.now(timezone.utc)
    # We are creating mock users just to get their avatar_url for the round table
    # The current _map_db_round_to_pydantic creates TwitterUser objects on the fly
    # using only avatar_url from the DB and hardcoded handles/display_names.
    # So, for mock round insertion, we only need to provide the avatar URLs.
    mock_left_avatar_url = "https://picsum.photos/seed/mockleft/200"
    mock_right_avatar_url = "https://picsum.photos/seed/mockright/200"

    mock_round_data = {
        "left_avatar_url": mock_left_avatar_url,
        "right_avatar_url": mock_right_avatar_url,
        "momentum": 65,
        "pot_amount": 125.0,
        "start_time": now.isoformat(),
        "current_deadline": (now + timedelta(minutes=15)).isoformat(),
        "max_deadline": (now + timedelta(hours=23, minutes=55)).isoformat(),
        "active": True,
        "battle_image_url": "https://picsum.photos/seed/battle/1024/768" # Initial mock image
    }

    try:
        logger.info(f"Inserting mock round data: {mock_round_data}")
        round_insert_response = supabase.table("rounds").insert(mock_round_data).execute()
        logger.info(f"Mock round insert response: {round_insert_response}")
        
        if not round_insert_response.data:
            logger.error("Failed to insert mock round or no data returned.")
            return None
        
        inserted_round_raw = round_insert_response.data[0]
        # Map raw DB round to Pydantic model
        created_round = _map_db_round_to_pydantic(inserted_round_raw)
        if not created_round:
            logger.error("Failed to map inserted mock round to Pydantic model.")
            return None
        logger.info(f"Successfully inserted mock round with ID: {created_round.id}")

        # 3. Define Mock Bets for this round
        mock_bets_data = [
            {
                "round_id": created_round.id,
                "side": "left",
                "amount": 50.0,
                "spell": "Fortuna Major!",
                "wallet_address": "MOCKWALLETLEFT001",
                "tx_id": "mocktx_left_001",
                "timestamp": (now - timedelta(seconds=30)).isoformat(), # Bet placed 30s ago
                "processed": True, # Assume processed for mock
                "impact": 10.0 # Example impact
            },
            {
                "round_id": created_round.id,
                "side": "right",
                "amount": 75.0,
                "spell": "Imperium Maxima!",
                "wallet_address": "MOCKWALLETRIGHT002",
                "tx_id": "mocktx_right_002",
                "timestamp": (now - timedelta(seconds=15)).isoformat(), # Bet placed 15s ago
                "processed": True,
                "impact": -15.0 # Example impact
            }
        ]
        logger.info(f"Inserting mock bets data: {mock_bets_data}")
        bets_insert_response = supabase.table("bets").insert(mock_bets_data).execute()
        logger.info(f"Mock bets insert response: {bets_insert_response}")

        if not bets_insert_response.data:
            logger.warning("No data returned from mock bets insertion, but proceeding with round.")
        else:
            logger.info(f"Successfully inserted {len(bets_insert_response.data)} mock bets.")

        return created_round # Return the created round model
    
    except Exception as e:
        logger.error(f"Error creating mock game state: {e}", exc_info=True)
        return None

# Ensure _map_db_round_to_pydantic is available and correctly maps user info
# If _map_db_round_to_pydantic expects left_user_info and right_user_info as dicts,
# make sure it loads them from JSON string if that's how they are stored from insert.

async def get_full_game_state_by_round(round_obj: RoundModel, supabase: Client) -> GameState:
    """Helper to construct the full GameState object from a round."""
    recent_bets_raw = await get_bets_for_round_db(round_id=round_obj.id, supabase_client=supabase, limit=10) # Use existing
    
    recent_bets_models = []
    total_bets_count = 0
    left_side_bets_amount = 0.0
    right_side_bets_amount = 0.0

    # Re-fetch all bets for the round to calculate aggregates accurately
    all_bets_for_round_response = await supabase.table("bets").select("*", count="exact").eq("round_id", round_obj.id).execute()
    
    if all_bets_for_round_response.data:
        total_bets_count = all_bets_for_round_response.count or len(all_bets_for_round_response.data)
        for bet_data in all_bets_for_round_response.data:
            # Map raw bet data to BetModel. Assuming a helper or direct Pydantic conversion.
            # For simplicity, let's assume BetModel can be directly instantiated if fields match.
            # This might need a _map_db_bet_to_pydantic if structure differs significantly.
            try:
                bet_model = BetModel(**bet_data) # Direct instantiation
                if bet_model.side == "left":
                    left_side_bets_amount += bet_model.amount
                elif bet_model.side == "right":
                    right_side_bets_amount += bet_model.amount
                
                # For recent_bets, use the already mapped ones from get_bets_for_round_db
                # This part is a bit tricky: get_bets_for_round_db likely returns Pydantic models.
                # We need to ensure `recent_bets_models` is populated correctly.
                # Let's assume get_bets_for_round_db returns a list of BetModel.
            except Exception as e:
                logger.error(f"Error mapping bet data to BetModel: {bet_data}, error: {e}")


    # Populate recent_bets_models from recent_bets_raw (which should be list[BetModel])
    if isinstance(recent_bets_raw, list): # Ensure it's a list (of BetModels)
        recent_bets_models = recent_bets_raw
    else: # If it returns raw data or something else, this needs adjustment
        logger.warning(f"get_bets_for_round_db returned unexpected type: {type(recent_bets_raw)}")


    return GameState(
        round=round_obj,
        recent_bets=recent_bets_models,
        total_bets_count=total_bets_count,
        left_side_bets_amount=left_side_bets_amount,
        right_side_bets_amount=right_side_bets_amount
    )

# Placeholder for fetching bets for a round
# async def get_bets_for_round_from_db(round_id: int, limit: int = 10) -> List[BetModel]:
# pass 

async def manually_end_active_game(supabase: Client) -> Tuple[Optional[RoundModel], str]:
    """
    Manually ends the current active game, determines winner based on momentum,
    and processes (mock) payouts.
    Returns the ended round and a status message.
    """
    # Local import to break circular dependency
    from ..services.algorand_service import process_payouts_for_round

    logger.info("Attempting to manually end the active game.")
    active_round = await get_active_round_from_db() # Uses global supabase client

    if not active_round:
        logger.info("No active game found to manually end.")
        return None, "No active game found to end."
    
    if not active_round.active:
        logger.info(f"Round {active_round.id} is already inactive. Cannot end again.")
        return active_round, f"Round {active_round.id} is already inactive."

    logger.info(f"Manually ending round ID: {active_round.id}")

    # Determine winner based on momentum
    winner_side: Optional[Literal["left", "right", "draw"]] = None
    if active_round.momentum < 50:
        winner_side = "left"
    elif active_round.momentum > 50:
        winner_side = "right"
    else: # Momentum is 50
        winner_side = "draw"
    
    logger.info(f"Determined winner for round {active_round.id} is: {winner_side} (momentum: {active_round.momentum})")

    ended_round = await end_round_in_db(active_round.id, winner_side, end_reason="manual_admin_end")
    if not ended_round:
        logger.error(f"Failed to mark round {active_round.id} as ended in DB.")
        return active_round, f"Failed to end round {active_round.id} in database."
    
    logger.info(f"Round {ended_round.id} successfully marked as ended. Winner: {ended_round.winner}. Proceeding to payouts.")

    # Process payouts for the ended round
    # Pass the supabase client dependency obtained by the route
    payouts_processed_successfully = await process_payouts_for_round(ended_round, supabase)
    
    payout_message = "Payouts processed (mocked)." if payouts_processed_successfully else "Payout processing failed or some payouts were unsuccessful."
    if ended_round.paid_at: # Check if process_payouts_for_round marked it as paid
        payout_message += f" Round marked as paid at {ended_round.paid_at}."
    else:
        payout_message += " Round not marked as paid."

    logger.info(f"Manual end game process for round {ended_round.id} complete. {payout_message}")
    return ended_round, f"Game ended. Winner: {ended_round.winner}. {payout_message}"

async def mark_round_as_paid_in_db(round_id: int, client: Optional[Client] = None) -> bool:
    """
    Marks a round as paid by setting the paid_at timestamp.
    Uses the provided client or the global supabase client.
    """
    db_client = client if client else supabase # Use provided client or fallback to global
    now = datetime.now(timezone.utc)
    try:
        logger.info(f"Marking round {round_id} as paid at {now.isoformat()}.")
        response = (
            db_client.table("rounds")
            .update({"paid_at": now.isoformat()})
            .eq("id", round_id)
            .execute()
        )
        if getattr(response, 'error', None):
            logger.error(f"Error marking round {round_id} as paid: {response.error}")
            return False
        # Check if any row was actually updated
        if response.data and len(response.data) > 0:
            logger.info(f"Successfully marked round {round_id} as paid.")
            return True
        elif response.count is not None and response.count > 0: 
            logger.info(f"Successfully marked round {round_id} as paid (count based).")
            return True
        else:
            logger.warning(f"Mark round {round_id} as paid executed without error, but no data/count returned. Round might not have been found or value was unchanged.")
            return True # Or False if stricter check needed
    except Exception as e:
        logger.error(f"Exception marking round {round_id} as paid: {e}", exc_info=True)
        return False 