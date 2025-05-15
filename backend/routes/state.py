# GET /state endpoint
from fastapi import APIRouter, HTTPException
from typing import List # For recent_bets, though it will be empty for now

from ..models import GameState, Bet # Bet for future recent_bets type hint
from ..services.supabase_service import get_active_round_from_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=GameState)
async def get_current_state():
    """
    Get the current game state including the active round.
    Recent bets are not yet implemented and will be an empty list.
    """
    logger.info("Fetching current game state.")
    try:
        active_round = await get_active_round_from_db()
        
        if not active_round:
            logger.info("No active game round found.")
            raise HTTPException(status_code=404, detail="No active game round found.")
        
        # For now, recent_bets is an empty list.
        # This will be populated in a future task.
        recent_bets_list: List[Bet] = [] 
        
        game_state = GameState(
            round=active_round,
            recent_bets=recent_bets_list,
            total_bets_count=0, # Placeholder, to be calculated later
            left_side_bets_amount=0.0, # Placeholder
            right_side_bets_amount=0.0 # Placeholder
        )
        logger.info(f"Active round ID {active_round.id} found. Returning game state.")
        return game_state
    except HTTPException as http_exc: # Re-raise HTTPExceptions from services or self-raised
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error retrieving game state: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve game state: {str(e)}") 