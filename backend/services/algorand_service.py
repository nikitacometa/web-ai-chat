# Algorand blockchain interactions
# e.g., verifying transactions

# from algosdk.v2client import algod
# from ..config import settings

# algod_client = algod.AlgodClient(settings.ALGOD_TOKEN, settings.ALGOD_NODE)

# def verify_transaction(txid: str):
#     pass 

import logging
from typing import Optional
import random
import algosdk # Import algosdk
from algosdk import transaction
from algosdk.v2client import algod # For algod client

# Assuming settings are available via an import path if this were a real module in an app
# For a standalone script context, config might need to be loaded differently.
# For now, this assumes it can access settings if part of the larger backend app.
from ..config import settings

logger = logging.getLogger(__name__)

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

async def submit_payout_transaction(
    receiver_address: str, 
    amount_microalgos: int, 
    note: Optional[str] = None
) -> Optional[str]:
    """
    Constructs, signs (using HOT_WALLET_MNEMONIC), and (MOCK) submits a payout transaction.
    Returns a mock transaction ID on success, None on failure.
    """
    logger.info(
        f"[Algorand Service] Attempting payout of {amount_microalgos} microAlgos "
        f"to {receiver_address} with note: '{note}'"
    )

    if not settings.HOT_WALLET_MNEMONIC:
        logger.error("[Algorand Service] HOT_WALLET_MNEMONIC not configured. Cannot make payout.")
        return None
    
    try:
        hot_wallet_private_key = algosdk.mnemonic.to_private_key(settings.HOT_WALLET_MNEMONIC)
        hot_wallet_address = algosdk.account.address_from_private_key(hot_wallet_private_key)
        logger.info(f"[Algorand Service] Payout from hot wallet: {hot_wallet_address}")

        algod_client = get_algod_client_for_backend()
        suggested_params = await algod_client.suggested_params_as_object() # Fetch suggested params
        # Note: suggested_params_as_object() is a convenience if using a wrapper or newer SDK feature.
        # Standard is await algod_client.getTransactionParams().do()
        # Let's assume algod_client.suggested_params_as_object() works or adapt if needed.
        # Reverting to standard: 
        # params = await algod_client.getTransactionParams().do()

        # For robustness, explicitly get transaction parameters
        params = await algod_client.getTransactionParams().do()

        txn_note_encoded = note.encode('utf-8') if note else None

        unsigned_txn = algosdk.transaction.PaymentTxn(
            sender=hot_wallet_address,
            sp=params, # Use fetched params
            receiver=receiver_address,
            amt=amount_microalgos,
            note=txn_note_encoded
        )

        signed_txn = unsigned_txn.sign(hot_wallet_private_key)
        logger.info(f"[Algorand Service] Transaction signed for payout to {receiver_address}.")

        # MOCK SUBMISSION - In real implementation, uncomment and use:
        # try:
        #     tx_id = algod_client.send_transaction(signed_txn)
        #     logger.info(f"[Algorand Service] Payout transaction {tx_id} submitted to network.")
        #     # Optional: await algosdk.util.wait_for_confirmation(algod_client, tx_id, 4)
        #     return tx_id
        # except Exception as e:
        #     logger.error(f"[Algorand Service] Error submitting payout transaction: {e}", exc_info=True)
        #     return None
        
        # Mock response for now
        mock_tx_id = f"mock_payout_tx_{random.randint(100000, 999999)}"
        logger.info(f"[Algorand Service] MOCK Payout transaction {mock_tx_id} would have been submitted for {receiver_address}.")
        return mock_tx_id

    except Exception as e:
        logger.error(f"[Algorand Service] Error preparing payout transaction for {receiver_address}: {e}", exc_info=True)
        return None 