import { Arena } from "@/components/Arena";
import BetDrawerExample from "@/components/BetDrawer";
import { fetchGameState } from "@/lib/api";
import { Suspense } from "react";
import { GameState } from "@/lib/types";

// Game state loader component
async function GameArena() {
  // In a real implementation, fetch from the API
  // For now, using the static example since the API isn't available in production
  let gameState: GameState;
  
  try {
    gameState = await fetchGameState();
  } catch (error) {
    console.error("Error loading game state:", error);
    // Fallback to example data
    return <ArenaFallback />;
  }
  
  const { round } = gameState;
  
  return (
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
  );
}

// Fallback component with example data
function ArenaFallback() {
  return (
    <Arena
      leftAvatar={{
        src: "https://pbs.twimg.com/profile_images/1683325380441128960/yRsRRjGO_400x400.jpg",
        alt: "Elon Musk",
        fallback: "EM",
      }}
      rightAvatar={{
        src: "https://pbs.twimg.com/profile_images/1590968738358079488/IY9Gx6Ok_400x400.jpg",
        alt: "SBF",
        fallback: "SBF",
      }}
      momentum={65}
      potAmount="12,345.67 ALGO"
      endTime={new Date(Date.now() + 3600000)} // 1 hour from now
    />
  );
}

export default function AlgoFOMOPage() {
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

      {/* Arena Component with Suspense */}
      <Suspense fallback={<ArenaFallback />}>
        <GameArena />
      </Suspense>

      {/* Bet Drawer Component */}
      <div className="mt-6 w-full max-w-md">
        <BetDrawerExample />
      </div>

      {/* Placeholder for Wallet Connect Component - Will be implemented in Phase 2 */}
      <div className="mt-6">
        <p className="text-center text-sm text-muted-foreground">Connect your Algorand wallet to join the battle</p>
      </div>
    </main>
  );
} 