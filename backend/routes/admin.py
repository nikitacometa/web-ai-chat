# POST /admin/reset endpoint
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, Any, Optional
from supabase import Client
from ..models import AdminResetRequest, Round as RoundResponseModel, GameState, StartGameRequest
from ..services.supabase_service import (
    create_round_in_db,
    deactivate_all_active_rounds_in_db,
    get_active_round_from_db,
    create_mock_game_state_in_db,
    get_full_game_state_by_round,
    get_supabase_client,
    manually_end_active_game
)
from ..jobs.render_image_job import trigger_render_battle_image # Import the job
from ..config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# This should be properly secured in production
# Modified to raise HTTPException on failure and return token on success
async def verify_admin_token(token: Optional[str] = Query(None)) -> str:
    if not settings.ADMIN_TOKEN:
        logger.error("CRITICAL: ADMIN_TOKEN is not configured in server settings.")
        raise HTTPException(status_code=500, detail="Admin token not configured")
    if not token:
        logger.warning("Admin token missing from request.")
        raise HTTPException(status_code=401, detail="Not authenticated: Admin token required")
    if token == settings.ADMIN_TOKEN:
        return token # Return the token if valid
    else:
        logger.warning("Invalid admin token received.")
        raise HTTPException(status_code=401, detail="Invalid admin token")

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
    # Token verification is now part of the reset_request Pydantic model or needs to be passed explicitly
    # For now, let's assume AdminResetRequest contains admin_token and we verify it here
    # OR, we add it as a dependency similar to the other endpoint.
    # For consistency with seed_mock_game, let's adapt it to use the dependency.
    # This means AdminResetRequest might not need the admin_token field if passed via Query/Header.

    # The original reset_game was checking reset_request.admin_token directly.
    # Let's keep that logic for now to minimize changes to this specific endpoint's structure,
    # unless you want to standardize token handling to use Depends for this route too.
    # For now, the original direct check within reset_game for reset_request.admin_token is kept.
    # This verify_admin_token dependency function is primarily for the new seed_mock_game endpoint.
    
    logger.info(f"Admin reset request received for L: {reset_request.left_avatar_url}, R: {reset_request.right_avatar_url}")
    # Manually verify the token from the request body for this specific endpoint
    if not settings.ADMIN_TOKEN:
        logger.error("CRITICAL: ADMIN_TOKEN is not configured in server settings for /reset.")
        raise HTTPException(status_code=500, detail="Admin token not configured on server.")
    if reset_request.admin_token != settings.ADMIN_TOKEN:
        logger.warning("Invalid admin token for /reset endpoint.")
        raise HTTPException(status_code=401, detail="Invalid admin token for reset")
    
    try:
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

@router.post("/seed_mock_game", response_model=GameState, tags=["Admin"])
async def seed_mock_game_state(
    supabase: Client = Depends(get_supabase_client),
    # admin_token will now be the string token if verification passed
    verified_token_string: str = Depends(verify_admin_token) 
):
    """
    Sets up a predefined mock game state. Deactivates any current active round.
    Protected by admin token dependency.
    """
    # Now verified_token_string is the actual token string, safe to slice
    logger.info(f"Admin request to seed mock game state received with token: {verified_token_string[:5]}...") 
    
    created_round = await create_mock_game_state_in_db(supabase)
    if not created_round:
        logger.error("Failed to create mock game state in DB.")
        raise HTTPException(status_code=500, detail="Failed to create mock game state")
    
    # Construct the full game state to return
    # This is similar to what the /state endpoint does
    full_game_state = await get_full_game_state_by_round(created_round, supabase)
    if not full_game_state:
        logger.error("Successfully created mock round but failed to fetch full game state.")
        # Still return a success, but with potentially incomplete recent_bets if that part failed
        # Or, decide if this scenario should also be a 500 error.
        # For now, let's assume if the round was created, it's mostly a success for seeding.
        # However, to match the response_model=GameState, we need to return a valid GameState.
        # If get_full_game_state_by_round can fail to return a GameState, this needs robust handling.
        # A simpler approach for now if get_full_game_state_by_round is robust:
        return full_game_state
        
    logger.info(f"Successfully seeded mock game state with round ID: {created_round.id}")
    return full_game_state

@router.post("/start_game", response_model=RoundResponseModel, tags=["Admin"])
async def start_custom_game(
    request_data: StartGameRequest,
    background_tasks: BackgroundTasks,
    supabase: Client = Depends(get_supabase_client) # Reusing the supabase client dependency
) -> RoundResponseModel:
    """
    Starts a new game with custom player details and initial settings.
    Deactivates any current active round.
    Triggers a background task for initial image generation.
    """
    logger.info(f"Admin /start_game request received for L: {request_data.left_player_handle}, R: {request_data.right_player_handle}")

    # Verify admin token from request body (similar to /reset endpoint)
    if not settings.ADMIN_TOKEN:
        logger.error("CRITICAL: ADMIN_TOKEN is not configured in server settings for /start_game.")
        raise HTTPException(status_code=500, detail="Admin token not configured on server.")
    if request_data.admin_token != settings.ADMIN_TOKEN:
        logger.warning("Invalid admin token for /start_game endpoint.")
        raise HTTPException(status_code=401, detail="Invalid admin token for /start_game")

    logger.info("Admin token verified for /start_game. Proceeding to deactivate existing rounds.")
    deactivated_ok = await deactivate_all_active_rounds_in_db() # Uses global supabase client
    if not deactivated_ok:
        logger.error("Failed to deactivate existing active rounds for /start_game. This might lead to multiple active rounds.")
        # Consider if this should be a hard failure
    else:
        logger.info("Successfully deactivated existing active rounds (or no active rounds found) for /start_game.")

    logger.info(f"Attempting to create new round via /start_game with L_avatar: {request_data.left_player_avatar_url}, R_avatar: {request_data.right_player_avatar_url}, Momentum: {request_data.initial_momentum}")
    new_round = await create_round_in_db(
        left_avatar_url=request_data.left_player_avatar_url,
        right_avatar_url=request_data.right_player_avatar_url,
        initial_momentum=request_data.initial_momentum
        # create_round_in_db uses the global supabase client
    )

    if not new_round:
        logger.error("Failed to create new round in DB for /start_game.")
        raise HTTPException(status_code=500, detail="Failed to create new round for /start_game.")

    logger.info(f"New round {new_round.id} created successfully via /start_game.")

    # Construct a detailed prompt for the initial image generation
    # Using provided player details and initial spell prompt
    image_prompt = (
        f"{request_data.left_player_display_name or request_data.left_player_handle} vs "
        f"{request_data.right_player_display_name or request_data.right_player_handle}, "
        f"battle in a vibrant arena, momentum at {new_round.momentum}%. "
        f"Initial scene: {request_data.initial_spell_prompt}"
    )
    
    # Add task to generate image with the constructed prompt
    # trigger_render_battle_image itself will use its own logic to call openai_service
    # and update_round_battle_image_url_in_db
    background_tasks.add_task(trigger_render_battle_image, round_id=new_round.id, custom_prompt=image_prompt)
    logger.info(f"Background task added for initial image (round {new_round.id}) with custom prompt: {image_prompt[:100]}...")

    return new_round

@router.post("/end_game", tags=["Admin"], response_model=Dict[str, Any])
async def end_current_game_admin(
    supabase: Client = Depends(get_supabase_client),
    admin_token: str = Depends(verify_admin_token) # Protected by admin token
):
    """
    Manually ends the current active game, determines winner, and processes payouts.
    """
    logger.info(f"Admin /end_game request received with token: {admin_token[:5]}...")
    
    ended_round, message = await manually_end_active_game(supabase)
    
    if not ended_round:
        # This case implies no active round was found, or it was already inactive.
        # The message from manually_end_active_game will be more specific.
        logger.info(f"Admin /end_game: {message}")
        # Return 200 OK with a message if no active game, or if it failed to end (error already logged)
        # Or choose a different status code like 404 if no active game.
        # For now, let's be consistent and if message implies no active game, it's not an error.
        if "No active game found" in message or "already inactive" in message:
            return {"message": message, "round_id": ended_round.id if ended_round else None}
        else: # Actual failure to end or process
            raise HTTPException(status_code=500, detail=message)
            
    logger.info(f"Admin /end_game: Successfully processed. Round ID: {ended_round.id}. Message: {message}")
    return {"message": message, "round_id": ended_round.id, "winner": ended_round.winner, "paid_at": ended_round.paid_at}

