"use client";
import { useEffect, useState } from 'react';
import { Suspense } from "react";
import { Arena, ArenaFallback } from "@/components/Arena";
import { BetDrawer } from "@/components/BetDrawer";
import { placeBet } from "@/lib/api";
import { GameState, BetRequest, GameRound } from "@/lib/types";

interface BettingInterfaceClientWrapperProps {
  initialGameState: GameState;
}

export default function BettingInterfaceClientWrapper({ initialGameState: serverInitialState }: BettingInterfaceClientWrapperProps) {
  const [gameState, setGameState] = useState<GameState>(serverInitialState);
  const [isBetting, setIsBetting] = useState(false); // For global feedback if needed

  // If serverInitialState changes (e.g. parent re-fetches), update client state
  useEffect(() => {
    setGameState(serverInitialState);
  }, [serverInitialState]);

  const handleActualPlaceBet = async (betData: BetRequest): Promise<void> => {
    setIsBetting(true);
    console.log("Placing bet with data (client-side):", betData);
    // Here you would show a toast: toast.loading("Placing your bet...");
    try {
      const response = await placeBet(betData);
      console.log("Bet API Response:", response);
      if (response.success && response.updated_round_state) {
        // toast.success("Bet placed successfully!");
        // Update game state with the new round state from the response
        setGameState(prevState => ({
          ...prevState, // Keep other parts of game state (like recent_bets if they weren't updated by this call)
          round: response.updated_round_state as GameRound, // Type assertion
          // Potentially re-fetch all bets or intelligently update recent_bets list if API provides new bet
        }));
        // A more robust solution would be to call fetchGameState() again or use SWR/TanStack Query's mutate/invalidateQueries
      } else {
        // toast.error(response.message || "Failed to place bet.");
        throw new Error(response.message || "Bet placement failed but API returned success=false or no round state.");
      }
    } catch (error) {
      console.error("Error placing bet:", error);
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
    return <ArenaFallback message="Game data is currently unavailable in BettingInterface." />;
  }

  const { round } = gameState;
  const walletAddress = "USER_WALLET_PLACEHOLDER"; // Replace with actual wallet state
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
          rightSideLabel={round.right_user.display_name || round.right_user.handle}
          minimumBet={minimumBet}
          onPlaceBet={handleActualPlaceBet} // Wire up the actual handler
        />
      </div>
    </>
  );
} 