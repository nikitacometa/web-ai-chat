import { Arena, ArenaFallback } from "@/components/Arena";
import { BetDrawer } from "@/components/BetDrawer";
import { fetchGameState, placeBet } from "@/lib/api";
import { Suspense } from "react";
import { GameState, BetRequest, BetResponse, GameRound } from "@/lib/types";

// This component remains a Server Component to fetch initial data
async function GameDataContainer({ initialGameState }: { initialGameState: GameState }) {
  // This component would re-render if initialGameState changes via server action/revalidation
  // Or, for more client-side dynamic updates, we'd need SWR/React Query here
  // and turn this into a Client Component.
  // For now, it displays the passed state and wires up BetDrawer.

  const { round } = initialGameState;

  // This function will be passed to BetDrawer. 
  // It needs to be a Server Action or called from a client component that then calls an API route.
  // For now, we'll make it a prop and assume the page calling it will handle the API call.
  // This is a simplification for this step. A more robust solution involves client-side data fetching hooks.

  // Placeholder for wallet address - replace with actual wallet integration later
  const walletAddress = "USER_WALLET_PLACEHOLDER"; 
  const minimumBet = 0.1; // This could also come from config or game state

  async function handlePlaceBet(betData: BetRequest): Promise<void> {
    // THIS IS A SERVER ACTION PLACEHOLDER / CONCEPT
    // In a real app, this would likely be a client-side function calling `placeBet` from `lib/api.ts`
    // and handling state updates (e.g. via SWR mutate, react-query, or useState + manual refetch)
    // For now, to keep `AlgoFOMOPage` as a Server Component and `BetDrawer` a Client Component,
    // this interaction is tricky without a client-side handler for the API call.
    
    // console.log("Server Action: handlePlaceBet called with:", betData);
    // const response = await placeBet(betData); // This would be the actual API call
    // console.log("Server Action: BetResponse:", response);
    // Here you would revalidate data or redirect
    // For the current structure, the BetDrawer client component will do the actual API call.
    // So this function in GameDataContainer might not be used directly by BetDrawer if BetDrawer calls API itself.
    // Let's adjust so that AlgoFOMOPage (client component) defines this handler.
    throw new Error("handlePlaceBet should be implemented in a Client Component or as a Server Action called from client.");
  }

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
          walletAddress={walletAddress} // This needs to come from actual wallet state eventually
          leftSideLabel={round.left_user.display_name || round.left_user.handle}
          rightSideLabel={round.right_user.display_name || round.right_user.handle}
          minimumBet={minimumBet} 
          // onPlaceBet will be provided by a client component wrapper
        />
      </div>
    </>
  );
}

// Main page will fetch initial data and pass to client components or GameDataContainer
export default async function AlgoFOMOPage() {
  // This page becomes a client component to handle API calls and state updates for betting.
  // Or, we introduce a new client component wrapper around BetDrawer.
  // Let's create a client component `BettingInterface` that fetches initial state and handles betting.

  let initialGameState: GameState;
  try {
    initialGameState = await fetchGameState();
  } catch (error) {
    console.error("Initial GameState fetch failed for AlgoFOMOPage:", error);
    // Render a more prominent error display or fallback for the whole page
    return (
      <main className="flex flex-col items-center justify-center min-h-screen p-4 md:p-8">
        <h1 className="text-2xl text-red-500">Failed to load game data. Please try again later.</h1>
      </main>
    );
  }

  // This is moving towards making AlgoFOMOPage a client component if it directly handles betting.
  // To keep server components for initial render, we need a dedicated client component for betting interaction.

  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4 md:p-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-500 to-red-500">
          AlgoFOMO
        </h1>
        <p className="mt-3 text-lg md:text-xl text-muted-foreground">
          The Ultimate Algorand Twitter Avatar Battle Game!
        </p>
        <p className="mt-2 text-sm text-muted-foreground">
          Watch Twitter avatars battle for dominance and bet on your champion
        </p>
      </div>

      {/* GameDataContainer will render Arena and BetDrawer. It needs the actual onPlaceBet handler */}
      {/* We need a client component to provide this handler. */}
      <BettingInterfaceClientWrapper initialGameState={initialGameState} />

      <div className="mt-6">
        <p className="text-center text-sm text-muted-foreground">Connect your Algorand wallet to join the battle</p>
      </div>
    </main>
  );
}

// NEW CLIENT COMPONENT to handle betting logic
"use client"; // This makes the component a Client Component
import { useEffect, useState } from 'react'; // For client-side state
// We would also import a toast library here, e.g., import { toast } from 'react-hot-toast';

function BettingInterfaceClientWrapper({ initialGameState: serverInitialState }: { initialGameState: GameState }) {
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