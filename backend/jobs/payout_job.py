import asyncio
import logging
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

# Add the parent directory (backend) to sys.path to allow sibling imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from services.supabase_service import (
    get_ended_unpaid_rounds_from_db,
    get_bets_for_round_db,
    mark_round_as_paid_in_db
)
from services.algorand_service import submit_payout_transaction # Mock for now
from models import Round as RoundModel, Bet as BetModel
from config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Payout configuration
HOUSE_CUT_PERCENTAGE = Decimal("0.10") # 10% for the house/developer
WINNERS_SHARE_PERCENTAGE = Decimal("1.00") - HOUSE_CUT_PERCENTAGE # 90% for winners

# Algorand minimum unit (microAlgos)
MICRO_ALGO_CONVERSION = Decimal("1_000_000")

async def process_payouts():
    """
    Fetches ended, unpaid rounds and processes payouts for them.
    """
    logger.info("Payout Job: Starting to process payouts for ended rounds...")
    
    unpaid_rounds = await get_ended_unpaid_rounds_from_db(limit=5) # Process a few at a time
    if not unpaid_rounds:
        logger.info("Payout Job: No ended unpaid rounds found. Nothing to do.")
        return

    logger.info(f"Payout Job: Found {len(unpaid_rounds)} unpaid rounds to process.")

    for game_round in unpaid_rounds:
        logger.info(f"Payout Job: Processing round ID: {game_round.id}, Winner: {game_round.winner}, Pot: {game_round.pot_amount}")
        if not game_round.winner or game_round.winner == "draw":
            logger.warning(f"Payout Job: Round {game_round.id} has no clear winner ('{game_round.winner}') or is a draw. Skipping payout. Marking as paid to avoid re-processing.")
            # Optionally, handle draw payout differently (e.g., return bets, or all to house)
            # For now, just marking as paid to prevent loop if it's a draw with no specific payout logic.
            await mark_round_as_paid_in_db(game_round.id)
            continue

        all_bets_for_round = await get_bets_for_round_db(round_id=game_round.id, limit=None) # Fetch all bets
        if not all_bets_for_round:
            logger.warning(f"Payout Job: No bets found for round {game_round.id}. Cannot process payouts. Marking as paid.")
            await mark_round_as_paid_in_db(game_round.id)
            continue

        winning_bets = [bet for bet in all_bets_for_round if bet.side == game_round.winner]
        if not winning_bets:
            logger.warning(f"Payout Job: No winning bets found for round {game_round.id} on side {game_round.winner}. Pot might go to house or be handled differently. Marking as paid.")
            # All to house? For now, just mark paid.
            await mark_round_as_paid_in_db(game_round.id)
            continue
        
        total_winning_pool = sum(bet.amount for bet in winning_bets)
        if total_winning_pool <= 0:
            logger.warning(f"Payout Job: Total winning pool for round {game_round.id} is zero or negative. Skipping payouts. Marking as paid.")
            await mark_round_as_paid_in_db(game_round.id)
            continue

        # Calculate amounts
        total_pot_decimal = Decimal(str(game_round.pot_amount)) # Ensure pot_amount is float or str
        winners_pot_total = total_pot_decimal * WINNERS_SHARE_PERCENTAGE
        # house_take = total_pot_decimal * HOUSE_CUT_PERCENTAGE # For logging or separate tx if needed

        logger.info(f"Payout Job: Round {game_round.id} - Total Pot: {total_pot_decimal}, Winners' Share: {winners_pot_total}")

        payouts_successful_for_round = True
        for bet in winning_bets:
            proportion_of_winning_pool = Decimal(str(bet.amount)) / Decimal(str(total_winning_pool))
            payout_amount_algo = winners_pot_total * proportion_of_winning_pool
            payout_amount_microalgos = int((payout_amount_algo * MICRO_ALGO_CONVERSION).to_integral_value(rounding=ROUND_HALF_UP))

            if payout_amount_microalgos > 0:
                logger.info(f"Payout Job: Paying out {payout_amount_microalgos} microAlgos to {bet.wallet_address} for bet ID {bet.id} in round {game_round.id}")
                
                # Mock payout submission
                payout_tx_id = await submit_payout_transaction(
                    receiver_address=bet.wallet_address,
                    amount_microalgos=payout_amount_microalgos,
                    note=f"AlgoFOMO Round {game_round.id} Payout - Bet {bet.id}"
                )
                if payout_tx_id:
                    logger.info(f"Payout Job: Mock payout for {bet.wallet_address} successful, TxID: {payout_tx_id}")
                else:
                    logger.error(f"Payout Job: Mock payout FAILED for {bet.wallet_address} for round {game_round.id}.")
                    payouts_successful_for_round = False
                    # Potentially break or collect all failures before deciding not to mark as paid
                    break # Stop processing payouts for this round if one fails
            else:
                logger.info(f"Payout Job: Calculated payout for bet {bet.id} is zero. Skipping.")

        if payouts_successful_for_round:
            logger.info(f"Payout Job: All payouts for round {game_round.id} processed (or skipped if zero). Marking round as paid.")
            await mark_round_as_paid_in_db(game_round.id)
        else:
            logger.error(f"Payout Job: Not all payouts were successful for round {game_round.id}. Round will NOT be marked as paid. Will retry later.")
    
    logger.info("Payout Job: Finished processing payouts.")

if __name__ == "__main__":
    logger.info("Executing payout_job.py directly...")
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY or not settings.HOT_WALLET_MNEMONIC:
        logger.critical("Supabase or Hot Wallet Mnemonic not configured. Cannot run payout job.")
        # HOT_WALLET_MNEMONIC check is more for the real algorand_service
        # but good to keep in mind for configuration completeness.
        sys.exit(1)
    
    asyncio.run(process_payouts())
    logger.info("payout_job.py direct execution finished.")
