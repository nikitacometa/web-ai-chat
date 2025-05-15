'use client';
import { useEffect, useState } from 'react';
import { Suspense } from 'react';
import { Arena, ArenaFallback } from '@/components/Arena';
import { BetDrawer } from '@/components/BetDrawer';
import { placeBet } from '@/lib/api';
import { GameState, BetRequest, GameRound, Bet } from '@/lib/types';
import { supabase } from '@/lib/supabase';

interface BettingInterfaceClientWrapperProps {
  initialGameState: GameState;
}

export default function BettingInterfaceClientWrapper({
  initialGameState: serverInitialState,
}: BettingInterfaceClientWrapperProps) {
  const [gameState, setGameState] = useState<GameState>(serverInitialState);
  const [isBetting, setIsBetting] = useState(false); // For global feedback if needed

  // If serverInitialState changes (e.g. parent re-fetches), update client state
  useEffect(() => {
    setGameState(serverInitialState);
  }, [serverInitialState]);

  // Supabase Realtime subscriptions
  useEffect(() => {
    if (!gameState.round || !gameState.round.id) {
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
  }, [gameState.round?.id]); // Depend on round.id

  const handleActualPlaceBet = async (betData: BetRequest): Promise<void> => {
    setIsBetting(true);
    console.log('Placing bet with data (client-side):', betData);
    // Here you would show a toast: toast.loading("Placing your bet...");
    try {
      const response = await placeBet(betData);
      console.log('Bet API Response:', response);
      if (response.success && response.updated_round_state) {
        // toast.success("Bet placed successfully!");
        // Update game state with the new round state from the response
        setGameState((prevState) => ({
          ...prevState, // Keep other parts of game state (like recent_bets if they weren't updated by this call)
          round: response.updated_round_state as GameRound, // Type assertion
          // Potentially re-fetch all bets or intelligently update recent_bets list if API provides new bet
        }));
        // A more robust solution would be to call fetchGameState() again or use SWR/TanStack Query's mutate/invalidateQueries
      } else {
        // toast.error(response.message || "Failed to place bet.");
        throw new Error(
          response.message ||
            'Bet placement failed but API returned success=false or no round state.',
        );
      }
    } catch (error) {
      console.error('Error placing bet:', error);
      // toast.error(error instanceof Error ? error.message : "An unexpected error occurred.");
      // Re-throw so BetDrawer can also catch it if it needs to
      throw error;
    } finally {
      setIsBetting(false);
      // toast.dismiss(); // Dismiss loading toast if any
    }
  };

  if (!gameState || !gameState.round) {
    // This can happen if initialGameState was bad, or if client state is somehow corrupted
    return (
      <ArenaFallback message="Game data is currently unavailable in BettingInterface." />
    );
  }

  const { round } = gameState;
  const walletAddress = 'USER_WALLET_PLACEHOLDER'; // Replace with actual wallet state
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
          walletAddress={walletAddress}
          leftSideLabel={round.left_user.display_name || round.left_user.handle}
          rightSideLabel={
            round.right_user.display_name || round.right_user.handle
          }
          minimumBet={minimumBet}
          onPlaceBet={handleActualPlaceBet} // Wire up the actual handler
        />
      </div>
    </>
  );
}
