# Background job for checking and ending rounds

import asyncio
from datetime import datetime, timezone
import logging
import os
import sys

# Add the parent directory (backend) to sys.path to allow sibling imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from services.supabase_service import get_active_round_from_db, end_round_in_db
from models import Round as RoundModel
from config import settings # To potentially use settings if needed, though not directly for now

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_and_end_active_round():
    """
    Checks the active game round for end conditions and processes round completion if necessary.
    """
    logger.info("Cron Job: Checking for active round to potentially end...")
    active_round: RoundModel = await get_active_round_from_db()

    if not active_round:
        logger.info("Cron Job: No active round found. Nothing to do.")
        return

    logger.info(f"Cron Job: Active round found: ID {active_round.id}, Momentum {active_round.momentum}, Current Deadline {active_round.current_deadline}")

    now = datetime.now(timezone.utc)
    winner_side: str | None = None
    end_reason: str | None = None

    # 1. Check for momentum win
    if active_round.momentum <= 0:
        winner_side = "left"
        end_reason = "Momentum reached 0 for left side."
    elif active_round.momentum >= 100:
        winner_side = "right"
        end_reason = "Momentum reached 100 for right side."
    
    # 2. Check for timeout (inactivity or max duration)
    # Ensure deadlines are timezone-aware for comparison if they aren't already
    # (Our RoundModel from supabase_service should provide timezone-aware datetimes)
    if not winner_side: # Only check timeouts if momentum hasn't decided a winner
        if now >= active_round.max_deadline:
            end_reason = f"Max round duration (at {active_round.max_deadline}) reached."
            # Determine winner by proximity if max duration timeout
            if active_round.momentum < 50:
                winner_side = "left"
            elif active_round.momentum > 50:
                winner_side = "right"
            else: # momentum == 50
                winner_side = "draw" # Or handle as per game rules, e.g. no winner, house wins
        elif now >= active_round.current_deadline:
            end_reason = f"Inactivity timeout (deadline {active_round.current_deadline}) reached."
            # Determine winner by proximity if inactivity timeout
            if active_round.momentum < 50:
                winner_side = "left"
            elif active_round.momentum > 50:
                winner_side = "right"
            else: # momentum == 50
                winner_side = "draw"

    if winner_side is not None and end_reason is not None:
        logger.info(f"Cron Job: Condition met to end round {active_round.id}. Winner: {winner_side}. Reason: {end_reason}")
        updated_round = await end_round_in_db(
            round_id=active_round.id, 
            winner_side=winner_side, 
            end_reason=end_reason
        )
        if updated_round:
            logger.info(f"Cron Job: Successfully ended round {active_round.id}. Confirmed winner: {updated_round.winner}")
        else:
            logger.error(f"Cron Job: Failed to end round {active_round.id} in DB despite conditions being met.")
    else:
        logger.info(f"Cron Job: No end conditions met for active round {active_round.id}.")

if __name__ == "__main__":
    logger.info("Executing end_round_job.py directly...")
    # Setup an asyncio event loop to run the async function
    try:
        asyncio.run(check_and_end_active_round())
        logger.info("end_round_job.py execution finished.")
    except Exception as e:
        logger.critical(f"Critical error running end_round_job: {e}", exc_info=True)

# async def run_end_round_check():
#     # fetches active round from supabase_service
#     # checks all end conditions (momentum, inactivity, max_duration)
#     # updates round status, calculates winners via game_service
#     pass 