import { Arena, ArenaFallback } from "@/components/Arena";
import { fetchGameState } from "@/lib/api";
import { GameState } from "@/lib/types";
import BettingInterfaceClientWrapper from "@/components/BettingInterfaceClientWrapper";
import { Suspense } from "react";

// This component remains a Server Component to fetch initial data
async function GameDataContainer({ initialGameState }: { initialGameState: GameState }) {
  const { round } = initialGameState;
  // This function is no longer needed, as betting logic is handled in the client wrapper
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
    </>
  );
}

// Main page will fetch initial data and pass to client components or GameDataContainer
export default async function AlgoFOMOPage() {
  let initialGameState: GameState;
  try {
    initialGameState = await fetchGameState();
  } catch (error) {
    console.error("Initial GameState fetch failed for AlgoFOMOPage:", error);
    return (
      <main className="flex flex-col items-center justify-center min-h-screen p-4 md:p-8">
        <h1 className="text-2xl text-red-500">Failed to load game data. Please try again later.</h1>
      </main>
    );
  }

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

      {/* BettingInterfaceClientWrapper will render Arena and BetDrawer and handle betting logic */}
      <BettingInterfaceClientWrapper initialGameState={initialGameState} />

      <div className="mt-6">
        <p className="text-center text-sm text-muted-foreground">Connect your Algorand wallet to join the battle</p>
      </div>
    </main>
  );
} 