# Algorand blockchain interactions
# e.g., verifying transactions

# from algosdk.v2client import algod
# from ..config import settings

# algod_client = algod.AlgodClient(settings.ALGOD_TOKEN, settings.ALGOD_NODE)

# def verify_transaction(txid: str):
#     pass 

import logging
from typing import Optional, List
import random
import algosdk # Import algosdk
from algosdk import transaction
from algosdk.v2client import algod # For algod client
from ..models import Round as RoundModel, Bet as BetModel # Ensure these are imported
from ..config import settings # Ensure settings is imported for HOUSE_CUT_PERCENTAGE etc.
from ..services.supabase_service import get_bets_for_round_db, mark_round_as_paid_in_db # For db interactions
from decimal import Decimal, ROUND_HALF_UP # For calculations
from supabase import Client # Added import

# Assuming settings are available via an import path if this were a real module in an app
# For a standalone script context, config might need to be loaded differently.
# For now, this assumes it can access settings if part of the larger backend app.

logger = logging.getLogger(__name__)
logger_algoservice = logging.getLogger(__name__ + ".algorand_service") # More specific logger name

# Helper to get algod client, similar to frontend one
# This should ideally be a shared utility if used in multiple backend services.
def get_algod_client_for_backend():
    # Use node config from settings, assuming they are set for backend use too
    # These might not be prefixed with NEXT_PUBLIC_ if they are backend-only settings
    algod_address = getattr(settings, "ALGOD_NODE_SERVER", "https://testnet-api.algonode.cloud")
    algod_token = getattr(settings, "ALGOD_NODE_TOKEN", "") # Often empty for public nodes
    algod_port = getattr(settings, "ALGOD_NODE_PORT", "443")
    # PeraWalletConnect uses string for port, Algodv2 constructor can take string or number
    return algod.AlgodClient(algod_token, algod_address, headers={'User-Agent': 'AlgoFOMO-Backend-Payout'}) 
    # Note: Port is often part of algod_address or implied by https for default port 443.
    # The above initialization is common. If port is separate: new algosdk.Algodv2(token, server, port_as_string)

async def verify_bet_transaction(
    tx_id: str, 
    expected_sender: str, 
    expected_receiver: str, 
    expected_amount: float, 
    min_confirmations: int = 1 
) -> bool:
    """
    MOCK: Verifies an Algorand transaction against expected parameters.
    In a real implementation, this would query the Algorand network (e.g., AlgoNode).
    
    Args:
        tx_id: The Algorand transaction ID.
        expected_sender: The expected wallet address of the bettor.
        expected_receiver: The game's treasury wallet address.
        expected_amount: The expected bet amount (e.g., in ALGOs).
        min_confirmations: Minimum number of confirmations for the transaction.

    Returns:
        True if the transaction is verified (mock always returns True), False otherwise.
    """
    logger.info(
        f"[MOCK Algorand Service] Verifying transaction ID: {tx_id} for sender: {expected_sender}, "
        f"receiver: {expected_receiver}, amount: {expected_amount}"
    )
    
    # Simulate checking logic (in a real scenario, query AlgoNode or own node):
    # 1. Fetch transaction details by tx_id.
    # 2. Check if transaction is confirmed (block number exists, confirmations >= min_confirmations).
    # 3. Validate sender matches expected_sender.
    # 4. Validate receiver matches expected_receiver.
    # 5. Validate amount matches expected_amount (handle units carefully - ALGOs vs microAlgos).
    # 6. Check for any rekeying or other suspicious parameters.
    
    # For mock purposes, we'll assume it's always valid if it reaches here.
    if not tx_id or not expected_sender or not expected_receiver or expected_amount <= 0:
        logger.warning("[MOCK Algorand Service] Invalid parameters for verification.")
        return False # Basic sanity check for mock
        
    logger.info(f"[MOCK Algorand Service] Transaction {tx_id} VERIFIED (mock).")
    return True

# Payout configuration (can be moved to config.py if preferred)
HOUSE_CUT_PERCENTAGE = Decimal(settings.HOUSE_CUT_PERCENTAGE_STR) if hasattr(settings, 'HOUSE_CUT_PERCENTAGE_STR') else Decimal("0.10")
WINNERS_SHARE_PERCENTAGE = Decimal("1.00") - HOUSE_CUT_PERCENTAGE
MICRO_ALGO_CONVERSION = Decimal("1_000_000")

async def submit_payout_transaction(receiver_address: str, amount_microalgos: int, note: str) -> Optional[str]:
    """
    Constructs, signs (using HOT_WALLET_MNEMONIC), and (MOCK) submits a payout transaction.
    Returns a mock transaction ID on success, None on failure.
    """
    logger_algoservice.info(f"Mock Payout: To {receiver_address}, Amount: {amount_microalgos} microAlgos, Note: {note}")
    # Simulate a transaction ID for mock purposes
    mock_tx_id = f"mock_payout_tx_{receiver_address}_{amount_microalgos}_{note[:10].replace(' ', '_')}"
    return mock_tx_id

async def process_payouts_for_round(game_round: RoundModel, supabase_client) -> bool:
    """
    Processes payouts for a specific game_round.
    Returns True if all payouts were successful (or not needed), False otherwise.
    Uses the passed supabase_client for DB operations if necessary (though get_bets_for_round_db might use its own global).
    """
    logger_algoservice.info(f"Processing payouts for specific round ID: {game_round.id}, Winner: {game_round.winner}, Pot: {game_round.pot_amount}")
    
    if game_round.paid_at:
        logger_algoservice.info(f"Round {game_round.id} has already been paid out at {game_round.paid_at}. Skipping.")
        return True # Already paid, so successful in a sense

    if not game_round.winner or game_round.winner == "draw":
        logger_algoservice.warning(f"Round {game_round.id} has no clear winner ('{game_round.winner}') or is a draw. Skipping payout. Marking as paid.")
        await mark_round_as_paid_in_db(game_round.id, supabase_client) # Pass client
        return True # No payouts to make, considered successful

    # Use the supabase_client for fetching bets if get_bets_for_round_db is adapted, 
    # or ensure it uses the correct global one. For now, assuming it uses global or is passed.
    # Let's modify get_bets_for_round_db to accept an optional client later if needed.
    # For now, the global client in supabase_service will be used by get_bets_for_round_db.
    all_bets_for_round = await get_bets_for_round_db(round_id=game_round.id, limit=None) 
    if not all_bets_for_round:
        logger_algoservice.warning(f"No bets found for round {game_round.id}. Cannot process payouts. Marking as paid.")
        await mark_round_as_paid_in_db(game_round.id, supabase_client) # Pass client
        return True

    winning_bets = [bet for bet in all_bets_for_round if bet.side == game_round.winner]
    if not winning_bets:
        logger_algoservice.warning(f"No winning bets found for round {game_round.id} on side {game_round.winner}. Marking as paid.")
        await mark_round_as_paid_in_db(game_round.id, supabase_client) # Pass client
        return True
    
    total_winning_pool = sum(bet.amount for bet in winning_bets)
    if total_winning_pool <= 0:
        logger_algoservice.warning(f"Total winning pool for round {game_round.id} is zero or negative. Skipping payouts. Marking as paid.")
        await mark_round_as_paid_in_db(game_round.id, supabase_client) # Pass client
        return True

    total_pot_decimal = Decimal(str(game_round.pot_amount))
    winners_pot_total = total_pot_decimal * WINNERS_SHARE_PERCENTAGE
    logger_algoservice.info(f"Round {game_round.id} - Total Pot: {total_pot_decimal}, Winners' Share: {winners_pot_total}")

    payouts_successful_this_round = True
    for bet in winning_bets:
        proportion_of_winning_pool = Decimal(str(bet.amount)) / Decimal(str(total_winning_pool))
        payout_amount_algo = winners_pot_total * proportion_of_winning_pool
        payout_amount_microalgos = int((payout_amount_algo * MICRO_ALGO_CONVERSION).to_integral_value(rounding=ROUND_HALF_UP))

        if payout_amount_microalgos > 0:
            payout_tx_id = await submit_payout_transaction(
                receiver_address=bet.wallet_address,
                amount_microalgos=payout_amount_microalgos,
                note=f"AlgoFOMO Round {game_round.id} Payout - Bet {bet.id}"
            )
            if payout_tx_id:
                logger_algoservice.info(f"Mock payout for {bet.wallet_address} successful, TxID: {payout_tx_id}")
            else:
                logger_algoservice.error(f"Mock payout FAILED for {bet.wallet_address} for round {game_round.id}.")
                payouts_successful_this_round = False
                break 
        else:
            logger_algoservice.info(f"Calculated payout for bet {bet.id} is zero. Skipping.")

    if payouts_successful_this_round:
        logger_algoservice.info(f"All payouts for round {game_round.id} processed successfully. Marking round as paid.")
        await mark_round_as_paid_in_db(game_round.id, supabase_client) # Pass client
        return True
    else:
        logger_algoservice.error(f"Not all payouts were successful for round {game_round.id}. Round will NOT be marked as paid.")
        return False 