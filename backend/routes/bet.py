# POST /bet endpoint
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from ..models import BetRequest, Bet as BetModel, Round as RoundModel, BetResponse
from ..services.supabase_service import (
    create_bet_in_db, 
    update_round_after_bet_in_db,
    get_active_round_from_db
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=BetResponse)
async def place_bet(bet_request: BetRequest) -> BetResponse:
    """
    Place a bet on the current game round.
    Validates the bet against the active round, creates the bet record,
    and updates the round state (pot, momentum, deadline).
    """
    try:
        active_round: Optional[RoundModel] = await get_active_round_from_db()

        if not active_round:
            logger.warning("Attempted to place bet with no active round.")
            raise HTTPException(status_code=400, detail="No active round to place a bet on.")

        if active_round.id != bet_request.round_id:
            logger.warning(
                f"Bet received for round {bet_request.round_id} but active round is {active_round.id}"
            )
            raise HTTPException(
                status_code=400, 
                detail=f"Bet intended for round {bet_request.round_id}, but active round is {active_round.id}."
            )

        # (HOOK for Future ALGO TX VERIFICATION - as per tasks.md, skip for now)
        # For now, assume bet is valid if API is called and passes Pydantic validation.
        
        logger.info(f"Placing bet for active round {active_round.id}: {bet_request}")

        created_bet: Optional[BetModel] = await create_bet_in_db(
            bet_input=bet_request, 
            round_id=active_round.id
        )

        if not created_bet:
            logger.error(f"Failed to create bet in DB for round {active_round.id}. Bet request: {bet_request}")
            raise HTTPException(status_code=500, detail="Failed to store bet details.")
        
        logger.info(f"Bet {created_bet.id} created successfully for round {active_round.id}.")

        # Now update the round state
        updated_round: Optional[RoundModel] = await update_round_after_bet_in_db(
            round_id=active_round.id,
            bet_amount=created_bet.amount, # Use amount from the confirmed created_bet
            bet_side=created_bet.side
        )

        if not updated_round:
            # If round update fails, it's a problem, but the bet IS placed.
            # Log this critical issue. The client will get the created bet, 
            # but the round state might be stale until next fetch or if realtime updates fix it.
            logger.error(
                f"Critical: Bet {created_bet.id} created, but failed to update round {active_round.id} state."
            )
            # Return success for bet creation, but acknowledge round update issue.
            # The 'updated_round_state' will be None or could be the old active_round state.
            # For simplicity, let's return None for updated_round_state in this specific error case.
            return BetResponse(
                success=True, # Bet was created
                message="Bet placed, but round state update failed. Please check round status.",
                bet=created_bet,
                updated_round_state=None # Or active_round to return the pre-update state
            )
        
        logger.info(f"Round {active_round.id} updated successfully after bet {created_bet.id}.")
        return BetResponse(
            success=True,
            message="Bet placed and round updated successfully!",
            bet=created_bet,
            updated_round_state=updated_round
        )

    except HTTPException as http_exc:
        # Re-raise HTTPException to let FastAPI handle it
        raise http_exc
    except ValueError as ve: # Catch Pydantic validation errors specifically if they bubble up
        logger.warning(f"Validation error placing bet: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error placing bet: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}") 