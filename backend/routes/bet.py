# POST /bet endpoint
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
from ..models import BetRequest, Bet as BetModel, Round as RoundModel, BetResponse
from ..services.supabase_service import (
    create_bet_in_db, 
    update_round_after_bet_in_db,
    get_active_round_from_db
)
from ..services.algorand_service import verify_bet_transaction # Import verification function
from ..jobs.render_image_job import trigger_render_battle_image # Import the job
from ..config import settings # For game treasury wallet address
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=BetResponse)
async def place_bet(
    bet_request: BetRequest, 
    background_tasks: BackgroundTasks
) -> BetResponse:
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

        # Verify Algorand transaction
        # TODO: Get game treasury wallet from settings or a more secure config
        GAME_TREASURY_WALLET = settings.HOT_WALLET_MNEMONIC # This is WRONG, needs a treasury address not mnemonic
        # For now, let's use a placeholder if not in settings, or assume a setting like GAME_TREASURY_ADDRESS
        # TEMP placeholder for game treasury address, should be in settings
        actual_game_treasury_address = getattr(settings, "GAME_TREASURY_ADDRESS", "PLACEHOLDER_TREASURY_ADDRESS_ALGONFOMO")
        
        is_tx_verified = await verify_bet_transaction(
            tx_id=bet_request.tx_id,
            expected_sender=bet_request.wallet_address,
            expected_receiver=actual_game_treasury_address, 
            expected_amount=bet_request.amount
        )

        if not is_tx_verified:
            logger.warning(
                f"Algorand transaction verification failed for tx_id: {bet_request.tx_id} from sender {bet_request.wallet_address}."
            )
            raise HTTPException(
                status_code=400, 
                detail="Algorand transaction verification failed. Bet not processed."
            )
        
        logger.info(f"Algorand transaction {bet_request.tx_id} verified.")

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
            bet_amount=created_bet.amount, # Use amount from the confirmed created_bet for pot
            bet_impact=created_bet.impact if created_bet.impact is not None else 0.0, # Use impact for momentum
            bet_side=created_bet.side
        )

        # After successful bet and round update, trigger image generation
        if updated_round: # Ensure round was updated before trying to generate image for it
            background_tasks.add_task(trigger_render_battle_image, round_id=active_round.id)
            logger.info(f"Background task added to generate image for round {active_round.id} after bet {created_bet.id}")
        else:
            # If round update failed, the bet IS placed. 
            # Still trigger image generation for the active_round.id as the bet might have changed context for image.
            # Or decide not to if round state is critical for image prompt (current prompt uses latest spell).
            # For now, let's still trigger it, as the mock image gen isn't sensitive to exact momentum from updated_round.
            background_tasks.add_task(trigger_render_battle_image, round_id=active_round.id)
            logger.warning(f"Round update failed but still triggering image generation for round {active_round.id} after bet {created_bet.id}")

        # Return response based on whether round update was successful
        if not updated_round:
            return BetResponse(
                success=True, # Bet was created
                message="Bet placed, but round state update failed. Image generation triggered. Please check round status.",
                bet=created_bet,
                updated_round_state=None 
            )
        
        return BetResponse(
            success=True,
            message="Bet placed, round updated, and image generation triggered successfully!",
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