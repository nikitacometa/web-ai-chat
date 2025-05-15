# POST /admin/reset endpoint
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from ..models import AdminResetRequest, Round as RoundResponseModel
from ..services.supabase_service import create_round_in_db, deactivate_all_active_rounds_in_db
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

@router.post("/reset", response_model=Dict[str, Any])
async def reset_game(request: AdminResetRequest):
    """
    Deactivates any existing active round and starts a new game round,
    storing it in the database.
    """
    logger.info(f"Admin reset request received: {request.model_dump(exclude={'admin_token'})}")
    try:
        # Verify admin token
        if not verify_admin_token(request.admin_token):
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
        logger.info(f"Attempting to create new round with L: {request.left_avatar_url}, R: {request.right_avatar_url}, M: {request.initial_momentum}")
        created_round: Optional[RoundResponseModel] = await create_round_in_db(
            left_avatar_url=request.left_avatar_url,
            right_avatar_url=request.right_avatar_url,
            initial_momentum=request.initial_momentum
        )
        
        if not created_round:
            logger.error("Database service failed to create new round.")
            raise HTTPException(status_code=500, detail="Failed to create new round in database.")
        
        logger.info(f"New round created successfully: ID {created_round.id}")
        return {
            "success": True,
            "round": created_round.model_dump(), # Use Pydantic model's dict representation
            "message": "New round started successfully!"
        }
    except HTTPException as http_exc: # Re-raise HTTPExceptions directly
        logger.debug(f"HTTPException in reset_game: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error in reset_game: {str(e)}", exc_info=True)
        # Ensure a generic message for unexpected errors
        raise HTTPException(status_code=500, detail="An unexpected error occurred while starting the new round.")

