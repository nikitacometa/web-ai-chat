import { GameState, BetRequest, BetResponse, GameRound, Bet } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Fetch the current game state
 */
export async function fetchGameState(): Promise<GameState> {
  try {
    const response = await fetch(`${API_BASE_URL}/state`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch game state: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching game state:', error);
    throw error;
  }
}

/**
 * Place a bet
 */
export async function placeBet(betRequest: BetRequest): Promise<BetResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/bet`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(betRequest),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to place bet: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error placing bet:', error);
    throw error;
  }
}

/**
 * Fetch past game rounds
 */
export async function fetchPastRounds(limit = 10, offset = 0): Promise<GameRound[]> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/history/rounds?limit=${limit}&offset=${offset}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (!response.ok) {
      throw new Error(`Failed to fetch past rounds: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching past rounds:', error);
    throw error;
  }
}

/**
 * Fetch bets for a specific round
 */
export async function fetchRoundBets(roundId: number, limit = 50, offset = 0): Promise<Bet[]> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/history/bets/${roundId}?limit=${limit}&offset=${offset}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    
    if (!response.ok) {
      throw new Error(`Failed to fetch round bets: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching round bets:', error);
    throw error;
  }
}

/**
 * Start a new game round (admin only)
 */
export async function startNewRound(
  leftHandle: string, 
  rightHandle: string, 
  adminToken: string
): Promise<{ success: boolean; round?: GameRound; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        left_handle: leftHandle,
        right_handle: rightHandle,
        initial_momentum: 50,
        admin_token: adminToken,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to start new round: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error starting new round:', error);
    throw error;
  }
} 