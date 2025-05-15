// Common types for the application
export type DataPart = { type: 'append-message'; message: string };

// AlgoFOMO Game Types
export interface TwitterUser {
  handle: string;
  avatar_url: string;
  display_name?: string;
}

export interface GameRound {
  id: number;
  left_user: TwitterUser;
  right_user: TwitterUser;
  momentum: number; // 0-100 scale
  pot_amount: number;
  start_time: string; // ISO datetime string
  current_deadline: string; // ISO datetime string
  max_deadline: string; // ISO datetime string
  active: boolean;
  winner?: "left" | "right" | null;
  battle_image_url?: string | null;
}

export interface Bet {
  id: number;
  round_id: number;
  side: "left" | "right";
  amount: number;
  spell: string;
  wallet_address: string;
  timestamp: string; // ISO datetime string
  processed: boolean;
  tx_id?: string | null;
}

export interface GameState {
  round: GameRound;
  recent_bets: Bet[];
  total_bets_count: number;
  left_side_bets_amount: number;
  right_side_bets_amount: number;
}

export interface BetRequest {
  round_id: number;
  side: "left" | "right";
  amount: number;
  spell: string;
  wallet_address: string;
}

export interface BetResponse {
  success: boolean;
  message: string;
  bet?: Bet;
  updated_round_state?: GameRound | null;
}
