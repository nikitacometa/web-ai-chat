# POST /admin/reset endpoint
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, Optional
from ..models import AdminResetRequest, Round as RoundResponseModel
from ..services.supabase_service import create_round_in_db, deactivate_all_active_rounds_in_db
from ..jobs.render_image_job import trigger_render_battle_image # Import the job
from ..config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# This should be properly secured in production
def verify_admin_token(token: str) -> bool:
    if not settings.ADMIN_TOKEN:
        logger.error("ADMIN_TOKEN is not configured in settings.")
        return False
    return token == settings.ADMIN_TOKEN

@router.post("/reset", response_model=RoundResponseModel) # Return the new round model
async def reset_game(
    reset_request: AdminResetRequest, 
    background_tasks: BackgroundTasks
) -> RoundResponseModel:
    """
    Resets the game: deactivates any current active round, creates a new one 
    with provided avatar URLs and initial momentum. 
    Triggers a background task to generate the initial battle image.
    """
    logger.info(f"Admin reset request received with token: {reset_request.admin_token[:5]}...")
    try:
        # Verify admin token
        if not verify_admin_token(reset_request.admin_token):
            logger.warning("Invalid admin token attempt.")
            raise HTTPException(status_code=401, detail="Invalid admin token")
        
        # Deactivate all other active rounds first
        logger.info("Attempting to deactivate existing active rounds.")
        deactivated_ok = await deactivate_all_active_rounds_in_db()
        if not deactivated_ok:
            logger.error("Failed to deactivate existing active rounds. This might lead to multiple active rounds.")
            # Depending on policy, we could raise an error here:
            # raise HTTPException(status_code=500, detail="Failed to deactivate existing rounds before creating new one.")
        else:
            logger.info("Successfully deactivated existing active rounds (or no active rounds found).")

        # Create the new round in the database
        logger.info(f"Attempting to create new round with L: {reset_request.left_avatar_url}, R: {reset_request.right_avatar_url}, M: {reset_request.initial_momentum}")
        new_round: Optional[RoundResponseModel] = await create_round_in_db(
            left_avatar_url=reset_request.left_avatar_url,
            right_avatar_url=reset_request.right_avatar_url,
            initial_momentum=reset_request.initial_momentum
        )
        
        if not new_round:
            logger.error("Failed to create new round in DB during admin reset.")
            raise HTTPException(status_code=500, detail="Failed to create new round after deactivation.")
        
        logger.info(f"New round {new_round.id} created successfully via admin reset.")
        
        # Trigger initial battle image generation in the background
        background_tasks.add_task(trigger_render_battle_image, round_id=new_round.id)
        logger.info(f"Background task added to generate initial image for round {new_round.id}")

        return new_round
    except HTTPException as http_exc: # Re-raise HTTPExceptions directly
        logger.debug(f"HTTPException in reset_game: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in reset_game: {str(e)}", exc_info=True)
        # Ensure a generic message for unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred while starting the new round.")

