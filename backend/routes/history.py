# GET /history endpoint
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..models import Round as RoundModel, Bet as BetModel
from ..services.supabase_service import get_all_rounds_from_db, get_bets_for_round_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/rounds", response_model=List[RoundModel])
async def get_rounds_history(
    offset: int = 0,
    limit: int = Query(default=20, ge=1, le=100), # Default 20, min 1, max 100
    active: Optional[bool] = None # Optional filter for active/inactive rounds
):
    """
    Retrieve a paginated history of game rounds.
    Can be filtered by active status.
    """
    logger.info(f"Fetching rounds history: offset={offset}, limit={limit}, active={active}")
    try:
        rounds = await get_all_rounds_from_db(limit=limit, offset=offset, active_only=active)
        if not rounds and offset == 0: # Only log "not found" if it's the first page and empty
            logger.info("No rounds found for the given criteria in history.")
            # Return empty list, not 404, as an empty history is valid
        return rounds
    except Exception as e:
        logger.error(f"Error fetching rounds history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve rounds history.")

@router.get("/bets/{round_id}", response_model=List[BetModel])
async def get_bets_for_round_history(
    round_id: int,
    offset: int = 0,
    limit: int = Query(default=50, ge=1, le=200) # Default 50, min 1, max 200 for bets
):
    """
    Retrieve a paginated list of all bets for a specific round.
    """
    logger.info(f"Fetching bets history for round_id: {round_id}, offset={offset}, limit={limit}")
    try:
        # First, check if round exists or is valid? For now, service will return empty if no bets.
        # For a more robust API, one might fetch the round itself first to ensure it's a valid ID.
        bets = await get_bets_for_round_db(round_id=round_id, limit=limit, offset=offset)
        
        if not bets and offset == 0:
            logger.info(f"No bets found for round_id {round_id}.")
            # Return empty list, not 404
        return bets
    except Exception as e:
        logger.error(f"Error fetching bets history for round {round_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to retrieve bets for round {round_id}.")

# Ensure this router is included in your main FastAPI app (e.g., in backend/main.py)
# from . import history
# app.include_router(history.router, prefix="/history", tags=["History"])

 