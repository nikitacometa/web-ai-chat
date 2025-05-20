# Background job for rendering images via OpenAI

import asyncio
import logging
import os
from typing import Optional
from fastapi import BackgroundTasks

from ..services.supabase_service import (
    get_active_round_from_db, 
    get_bets_for_round_db, 
    update_round_battle_image_url_in_db,
    # _map_db_round_to_pydantic # Not directly used by job, but by get_active_round
)
from ..services.openai_service import generate_battle_image_url # Corrected to relative import
from ..models import Round as RoundModel, Bet as BetModel # Assuming models is also in backend, changed to relative

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def trigger_render_battle_image(round_id: Optional[int] = None, custom_prompt: Optional[str] = None):
    """
    Generates a battle image for the specified round_id or the current active round 
    and updates the round record in the database.

    This function is intended to be called as an asynchronous background task.
    """
    logger.info(f"Render Battle Image job triggered for round_id: {round_id if round_id else 'current active'}")

    target_round: Optional[RoundModel] = None

    if round_id is not None:
        # Future enhancement: could implement get_round_by_id_from_db if needed for non-active rounds
        # For now, we still fetch the active round and check if it matches the provided round_id
        # This ensures we only operate on the *currently* active round that matches the ID.
        active_round_check = await get_active_round_from_db()
        if active_round_check and active_round_check.id == round_id:
            target_round = active_round_check
        else:
            logger.warning(f"Render job: Specified round_id {round_id} is not the active round or not found. Aborting image generation.")
            return
    else:
        target_round = await get_active_round_from_db()

    if not target_round:
        logger.info("Render job: No active round found. Nothing to render.")
        return
    
    if not target_round.active:
        logger.info(f"Render job: Round {target_round.id} is no longer active. Skipping image generation.")
        return

    logger.info(f"Render job: Processing round ID {target_round.id}")

    # Construct the prompt for image generation
    if custom_prompt:
        prompt = custom_prompt
        logger.info(f"Render job: Using provided custom prompt: '{prompt}'")
    else:
        # Fallback to existing prompt generation logic if no custom_prompt is given
        latest_bets: list[BetModel] = await get_bets_for_round_db(round_id=target_round.id, limit=1)
        latest_spell_prompt = "the arena is vibrant" # Default prompt
        if latest_bets:
            latest_spell_prompt = latest_bets[0].spell
            logger.info(f"Render job: Using spell from latest bet: '{latest_spell_prompt}'")
        else:
            logger.info("Render job: No bets found for spell prompt, using default.")

        prompt = (
            f"{target_round.left_user.display_name or 'Left Player'} vs "
            f"{target_round.right_user.display_name or 'Right Player'}, "
            f"epic battle in a mystical arena, momentum at {target_round.momentum}%, "
            f"last spell: {latest_spell_prompt}"
        )
    logger.info(f"Render job: Final DALL-E prompt: '{prompt}'")

    # Generate image URL (using mock service for now)
    image_url = await generate_battle_image_url(prompt=prompt, round_id=target_round.id)

    if image_url:
        logger.info(f"Render job: Successfully generated image URL: {image_url} for round {target_round.id}")
        success = await update_round_battle_image_url_in_db(round_id=target_round.id, image_url=image_url)
        if success:
            logger.info(f"Render job: Successfully updated battle_image_url for round {target_round.id} in DB.")
        else:
            logger.error(f"Render job: Failed to update battle_image_url for round {target_round.id} in DB.")
    else:
        logger.error(f"Render job: Failed to generate image URL for round {target_round.id}.")

if __name__ == "__main__":
    # Example of how to run this if it were a standalone script (for testing)
    # In FastAPI, you'd import trigger_render_battle_image and add it to BackgroundTasks
    
    # This example requires a round_id to be passed or for an active round to exist.
    # For direct execution testing, you might want to manually set up a round in your DB.
    test_round_id = 1 # Replace with an actual ID from your test DB if needed
    
    async def main_test(round_id_to_test=None):
        logger.info(f"Executing render_image_job.py directly for round_id: {round_id_to_test or 'current active'}...")
        # The 'settings' import was missing here for the direct execution part.
        # This will still fail if run directly unless settings are loaded,
        # but it's outside the FastAPI app context.
        # For now, I'm commenting out the settings check as it's not the primary execution path.
        # if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        #     logger.critical("Supabase URL or Key not configured. Cannot run job.")
        #     return
        await trigger_render_battle_image(round_id=round_id_to_test)
        logger.info("render_image_job.py direct execution finished.")

    # To run with a specific round ID:
    # asyncio.run(main_test(round_id_to_test=test_round_id))
    # To run for the current active round:
    asyncio.run(main_test()) 