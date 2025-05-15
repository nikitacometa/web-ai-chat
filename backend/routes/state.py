# GET /state endpoint
from fastapi import APIRouter, HTTPException
from typing import List 

from ..models import GameState, Bet as BetModel, Round as RoundModel # Updated BetModel import
from ..services.supabase_service import get_active_round_from_db, get_bets_for_round_db # Added get_bets_for_round_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Configuration for recent bets display
RECENT_BETS_LIMIT = 10

@router.get("/", response_model=GameState)
async def get_current_state():
    """
    Get the current game state including the active round, recent bets,
    total bet count, and total amounts wagered on each side.
    """
    logger.info("Fetching current game state.")
    try:
        active_round: RoundModel = await get_active_round_from_db()
        
        if not active_round:
            logger.info("No active game round found for /state endpoint.")
            raise HTTPException(status_code=404, detail="No active game round found.")
        
        logger.info(f"Active round ID {active_round.id} found. Fetching all bets for this round.")
        all_bets_for_round: List[BetModel] = await get_bets_for_round_db(
            round_id=active_round.id, 
            limit=None # Fetch all bets
        )
        logger.info(f"Fetched {len(all_bets_for_round)} total bets for round {active_round.id}.")

        # Prepare data for GameState
        recent_bets_list: List[BetModel] = all_bets_for_round[:RECENT_BETS_LIMIT]
        
        total_bets_count = len(all_bets_for_round)
        left_side_bets_amount = 0.0
        right_side_bets_amount = 0.0

        for bet in all_bets_for_round:
            if bet.side == "left":
                left_side_bets_amount += bet.amount
            elif bet.side == "right":
                right_side_bets_amount += bet.amount
            # Else: side is something unexpected, or amount is weird. Pydantic models should catch this.

        game_state = GameState(
            round=active_round,
            recent_bets=recent_bets_list,
            total_bets_count=total_bets_count,
            left_side_bets_amount=left_side_bets_amount,
            right_side_bets_amount=right_side_bets_amount
        )
        
        logger.info(f"Returning game state for round {active_round.id} with {total_bets_count} bets.")
        return game_state
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error retrieving game state: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve game state: {str(e)}") 