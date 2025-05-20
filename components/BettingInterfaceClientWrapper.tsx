'use client';
import { useEffect, useState, useCallback } from 'react';
import { Suspense } from 'react';
import { Arena, ArenaFallback } from '@/components/Arena';
import { BetDrawer } from '@/components/BetDrawer';
import { placeBet } from '@/lib/api';
import { GameState, BetRequest, GameRound, Bet } from '@/lib/types';
import { supabase } from '@/lib/supabase';
import algosdk from 'algosdk';
import { usePeraWallet } from '@/contexts/PeraWalletContext';

// Helper to get algod client (should ideally be in a shared lib/algorand.ts or similar)
// For now, defining it here for simplicity in this step.
const getAlgodClient = () => {
  const algodToken = process.env.NEXT_PUBLIC_ALGORAND_NODE_TOKEN || '';
  const algodServer =
    process.env.NEXT_PUBLIC_ALGORAND_NODE_SERVER ||
    'https://testnet-api.algonode.cloud';
  const algodPort = process.env.NEXT_PUBLIC_ALGORAND_NODE_PORT || '443';
  return new algosdk.Algodv2(algodToken, algodServer, algodPort);
};

// TODO: Get this from settings/config
const GAME_TREASURY_ADDRESS =
  process.env.NEXT_PUBLIC_GAME_TREASURY_ADDRESS ||
  'PLACEHOLDER_TREASURY_ADDRESS_ALGONFOMO';

interface BettingInterfaceClientWrapperProps {
  initialGameState: GameState;
}

export default function BettingInterfaceClientWrapper({
  initialGameState: serverInitialState,
}: BettingInterfaceClientWrapperProps) {
  const [gameState, setGameState] = useState<GameState>(serverInitialState);
  const [isBetting, setIsBetting] = useState(false); // For global feedback if needed

  // Get Pera Wallet state and methods from context
  const {
    peraWallet, // The PeraWalletConnect instance from context
    activeAddress,
    // isPeraConnecting, // Not directly needed here, button handles its state
    // peraWalletAvailable, // Also handled by button
    // handlePeraConnect, // Not called directly here, button does it
    // handlePeraDisconnect // Not called directly here, button does it
  } = usePeraWallet();

  // If serverInitialState changes (e.g. parent re-fetches), update client state
  useEffect(() => {
    setGameState(serverInitialState);
  }, [serverInitialState]);

  // Supabase Realtime subscriptions
  useEffect(() => {
    if (!gameState.round || !gameState.round.id || !supabase) {
      return;
    }

    const currentRoundId = gameState.round.id;
    console.log(
      `Subscribing to Realtime updates for round ID: ${currentRoundId}`,
    );

    // Channel for round updates
    const roundChannel = supabase
      .channel(`round-${currentRoundId}-updates`)
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'rounds',
          filter: `id=eq.${currentRoundId}`,
        },
        (payload) => {
          console.log('Round UPDATE received:', payload);
          const updatedDbRound = payload.new as any; // Cast to any to access properties
          setGameState((prev) => {
            if (prev.round.id !== updatedDbRound.id) return prev; // Should not happen with filter

            // Construct the GameRound.left_user and GameRound.right_user
            // This assumes avatar URLs are directly on the round object in DB as per supabase_service.py
            const newLeftUser = {
              handle: 'Left Player', // Placeholder or fetch if available
              avatar_url: updatedDbRound.left_avatar_url,
              display_name: 'Left Player',
            };
            const newRightUser = {
              handle: 'Right Player', // Placeholder or fetch if available
              avatar_url: updatedDbRound.right_avatar_url,
              display_name: 'Right Player',
            };

            return {
              ...prev,
              round: {
                ...prev.round, // Keep existing fields not in payload if any
                id: updatedDbRound.id,
                left_user: newLeftUser,
                right_user: newRightUser,
                momentum: updatedDbRound.momentum,
                pot_amount: Number.parseFloat(updatedDbRound.pot_amount),
                start_time: updatedDbRound.start_time,
                current_deadline: updatedDbRound.current_deadline,
                max_deadline: updatedDbRound.max_deadline,
                active: updatedDbRound.active,
                winner: updatedDbRound.winner,
                battle_image_url: updatedDbRound.battle_image_url,
              },
            };
          });
        },
      )
      .subscribe((status, err) => {
        if (status === 'SUBSCRIBED') {
          console.log(
            `Successfully subscribed to round ${currentRoundId} updates!`,
          );
        } else if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT') {
          console.error(
            `Error subscribing to round ${currentRoundId} updates:`,
            err,
          );
        }
      });

    // Channel for new bets
    const RECENT_BETS_DISPLAY_LIMIT = 10; // Consistent with backend /state if needed
    const betsChannel = supabase
      .channel(`round-${currentRoundId}-new-bets`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'bets',
          filter: `round_id=eq.${currentRoundId}`,
        },
        (payload) => {
          console.log('New BET received:', payload);
          const newBet = payload.new as Bet;
          setGameState((prev) => {
            const updatedRecentBets = [newBet, ...prev.recent_bets].slice(
              0,
              RECENT_BETS_DISPLAY_LIMIT,
            );
            let newLeftSideAmount = prev.left_side_bets_amount;
            let newRightSideAmount = prev.right_side_bets_amount;

            if (newBet.side === 'left') {
              newLeftSideAmount += newBet.amount;
            } else if (newBet.side === 'right') {
              newRightSideAmount += newBet.amount;
            }

            return {
              ...prev,
              recent_bets: updatedRecentBets,
              total_bets_count: prev.total_bets_count + 1,
              left_side_bets_amount: newLeftSideAmount,
              right_side_bets_amount: newRightSideAmount,
            };
          });
        },
      )
      .subscribe((status, err) => {
        if (status === 'SUBSCRIBED') {
          console.log(
            `Successfully subscribed to new bets for round ${currentRoundId}!`,
          );
        } else if (status === 'CHANNEL_ERROR' || status === 'TIMED_OUT') {
          console.error(
            `Error subscribing to new bets for round ${currentRoundId}:`,
            err,
          );
        }
      });

    // Cleanup
    return () => {
      console.log(
        `Unsubscribing from Realtime updates for round ID: ${currentRoundId}`,
      );
      supabase.removeChannel(roundChannel);
      supabase.removeChannel(betsChannel);
      // supabase.removeAllChannels(); // Use if you want to remove all, regardless of specific round
    };
  }, [gameState.round?.id, supabase]); // Added supabase to dependency array

  const handleActualPlaceBet = async (
    betDataFromDrawer: Omit<BetRequest, 'tx_id' | 'wallet_address'> & {
      amount: number;
      side: 'left' | 'right';
      spell: string;
    },
  ) => {
    if (!activeAddress || !peraWallet) {
      console.error(
        'Pera Wallet not connected or PeraWallet instance not available.',
      );
      throw new Error(
        'Wallet not connected. Please connect your Pera Wallet to place a bet.',
      );
    }
    if (
      !GAME_TREASURY_ADDRESS ||
      GAME_TREASURY_ADDRESS === 'PLACEHOLDER_TREASURY_ADDRESS_ALGONFOMO'
    ) {
      console.error('Game treasury address is not configured.');
      throw new Error(
        'Game treasury address is not configured. Bet cannot be placed.',
      );
    }

    setIsBetting(true);
    console.log('Placing bet, data from drawer:', betDataFromDrawer);

    try {
      const algodClient = getAlgodClient();
      const suggestedParams = await algodClient.getTransactionParams().do();
      const amountInMicroAlgos = Math.round(
        betDataFromDrawer.amount * 1_000_000,
      );

      const paymentTxnObject = {
        sender: activeAddress,
        receiver: GAME_TREASURY_ADDRESS,
        amount: amountInMicroAlgos,
        suggestedParams,
        note: new Uint8Array(
          Buffer.from(
            `AlgoFOMO Bet: Round ${gameState.round.id}, Spell: ${betDataFromDrawer.spell}`,
          ),
        ),
      };
      const txnToSign =
        algosdk.makePaymentTxnWithSuggestedParamsFromObject(paymentTxnObject);

      const signedTxns = await peraWallet.signTransaction([
        [{ txn: txnToSign, signers: [activeAddress] }],
      ]);

      // Submit transaction - casting to any due to incorrect PostTransactionsResponse type in algosdk v3.2.0
      const submissionResponse: any = await algodClient
        .sendRawTransaction(signedTxns[0])
        .do();
      // Correctly assign txId by accessing the .txid (lowercase) property from the submissionResponse object
      const txId: string = submissionResponse.txid;
      console.log('Transaction submitted with Pera, ID:', txId);

      if (!txId) {
        console.error(
          'Failed to retrieve transaction ID from Pera submission response object property .txid.',
        );
        throw new Error(
          'Transaction ID was not returned after submission (from .txid).',
        );
      }

      const finalBetRequest: BetRequest = {
        round_id: gameState.round.id,
        side: betDataFromDrawer.side,
        amount: betDataFromDrawer.amount,
        spell: betDataFromDrawer.spell,
        wallet_address: activeAddress,
        tx_id: txId,
      };

      const response = await placeBet(finalBetRequest);
      console.log('Bet API Response:', response);

      if (response.success && response.updated_round_state) {
        setGameState((prevState) => ({
          ...prevState,
          round: response.updated_round_state as GameRound,
        }));
      } else {
        throw new Error(
          response.message ||
            'Bet processing failed after transaction submission.',
        );
      }
    } catch (error) {
      console.error('Error during Pera bet placement process:', error);
      throw error;
    } finally {
      setIsBetting(false);
    }
  };

  if (!gameState || !gameState.round) {
    // This can happen if initialGameState was bad, or if client state is somehow corrupted
    return (
      <ArenaFallback message="Game data is currently unavailable in BettingInterface." />
    );
  }

  const { round } = gameState;
  // const walletAddress = "USER_WALLET_PLACEHOLDER"; // Replaced by activeAddress from useWallet
  const minimumBet = 0.1; // Could come from config or game state

  return (
    <>
      <Suspense fallback={<ArenaFallback />}>
        <Arena
          leftAvatar={{
            src: round.left_user.avatar_url,
            alt: round.left_user.display_name || round.left_user.handle,
            fallback: round.left_user.handle.substring(0, 2).toUpperCase(),
          }}
          rightAvatar={{
            src: round.right_user.avatar_url,
            alt: round.right_user.display_name || round.right_user.handle,
            fallback: round.right_user.handle.substring(0, 2).toUpperCase(),
          }}
          momentum={round.momentum}
          potAmount={`${round.pot_amount.toLocaleString()} ALGO`}
          endTime={new Date(round.current_deadline)}
          battleImageUrl={round.battle_image_url || undefined}
        />
      </Suspense>

      <div className="mt-6 w-full max-w-md">
        <BetDrawer
          roundId={round.id}
          walletAddress={activeAddress || ''} // Use activeAddress from context
          leftSideLabel={round.left_user.display_name || round.left_user.handle}
          rightSideLabel={
            round.right_user.display_name || round.right_user.handle
          }
          minimumBet={minimumBet}
          onPlaceBet={handleActualPlaceBet as any} // Cast as any due to BetRequest modification for internal handling
        />
      </div>
    </>
  );
}
