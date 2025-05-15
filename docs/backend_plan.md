# FOMO RUMBLE Backend Development Plan

## Overview

The backend for FOMO RUMBLE will be built using FastAPI, a modern, high-performance web framework for building APIs with Python. It will interact with Supabase for database operations, AlgoNode for Algorand blockchain integration, and Replicate for SDXL image generation.

## Architecture

```
                  ┌─────────────┐
                  │   FastAPI   │
                  │   Backend   │
                  └─────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
┌─────────▼────────┐ ┌───▼───┐ ┌────────▼────────┐
│  Supabase DB &   │ │AlgoNode│ │  Replicate     │
│     Storage      │ │  REST  │ │  SDXL API      │
└──────────────────┘ └───────┘ └─────────────────┘
```

## Environment Variables

```
ALGOD_NODE=https://mainnet-api.algonode.cloud
ALGOD_TOKEN=xxxxxxxx
HOT_WALLET_MNEMONIC="..."
REPLICATE_API_TOKEN=...
SUPABASE_URL=...
SUPABASE_KEY=...
ROUND_TIMEOUT_SEC=1200
ADMIN_TOKEN=...  # For admin authentication
```

## API Endpoints

### 1. GET /state

Returns the current round state and the last 10 bets.

**Response:**
```json
{
  "round": {
    "id": 123,
    "left_handle": "user1",
    "right_handle": "user2",
    "momentum": 65,
    "pot": 1000000,
    "next_bet": 105000,
    "started_at": "2023-05-15T12:00:00Z",
    "ended_at": null,
    "img_url": "https://..."
  },
  "bets": [
    {
      "id": 456,
      "round_id": 123,
      "sender": "ALGO123...",
      "side": "L",
      "amount": 100000,
      "prompt": "fire dragon attack",
      "impact": 2.5,
      "created_at": "2023-05-15T12:05:00Z"
    },
    // ... more bets
  ]
}
```

### 2. POST /bet

Processes a new bet, verifies the transaction, updates the game state, and enqueues an image generation job.

**Request:**
```json
{
  "txid": "ALGO_TRANSACTION_ID",
  "side": "L",  // "L" or "R"
  "prompt": "fire dragon attack"  // Max 70 chars
}
```

**Response:**
```json
{
  "success": true,
  "bet_id": 457,
  "impact": 3.2,
  "new_momentum": 68
}
```

### 3. POST /admin/reset

Starts a new round with specified Twitter handles. Requires admin token authentication.

**Request:**
```json
{
  "left_handle": "user1",
  "right_handle": "user2"
}
```

**Headers:**
```
Authorization: Bearer ADMIN_TOKEN
```

**Response:**
```json
{
  "success": true,
  "round_id": 124
}
```

### 4. GET /history

Returns historical rounds data.

**Query Parameters:**
- `round` (optional): Specific round ID to retrieve

**Response:**
```json
{
  "rounds": [
    {
      "id": 123,
      "left_handle": "user1",
      "right_handle": "user2",
      "momentum": 100,  // Final momentum
      "pot": 1500000,
      "winner_side": "R",
      "started_at": "2023-05-15T12:00:00Z",
      "ended_at": "2023-05-15T12:30:00Z",
      "img_url": "https://..."
    },
    // ... more rounds
  ]
}
```

## Background Jobs

### 1. render_image(job_id)

Generates a new image using Replicate SDXL API based on the current game state and the latest bet's prompt.

1. Get the current round and latest bet
2. Construct the prompt: `<left> vs <right>, cyber-arena, momentum=<x>% + user spell`
3. Call Replicate API to generate the image
4. Save the image URL to the round record
5. Update the Supabase storage with the image

### 2. cron_end_round()

Runs every 60 seconds to check if the current round should end.

1. Get the current active round
2. Check if the momentum has hit 0 or 100
3. Check if the round has been idle for more than ROUND_TIMEOUT_SEC seconds
4. If either condition is met, mark the round as ended
5. Calculate winners based on the final momentum
6. Update the round record with the end time and winner information

### 3. payout.py

Manual script to distribute ALGO to winners.

1. Get the ended rounds that haven't been paid out
2. For each round:
   - Calculate the distribution (90% to winners proportional to their bets, 10% to admin)
   - Create and sign transactions using the HOT_WALLET_MNEMONIC
   - Submit transactions to the Algorand network
   - Mark the round as paid out

## Data Models

### 1. Round

```python
class Round(BaseModel):
    id: int
    left_handle: str
    right_handle: str
    momentum: int
    pot: int
    next_bet: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    img_url: Optional[str] = None
    
    class Config:
        orm_mode = True
```

### 2. Bet

```python
class Bet(BaseModel):
    id: int
    round_id: int
    sender: str
    side: str  # "L" or "R"
    amount: int
    prompt: str
    impact: float
    created_at: datetime
    
    class Config:
        orm_mode = True
```

### 3. BetRequest

```python
class BetRequest(BaseModel):
    txid: str
    side: str
    prompt: str
    
    @validator('side')
    def validate_side(cls, v):
        if v not in ['L', 'R']:
            raise ValueError('side must be either "L" or "R"')
        return v
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if len(v) > 70:
            raise ValueError('prompt must be 70 characters or less')
        return v
```

### 4. AdminResetRequest

```python
class AdminResetRequest(BaseModel):
    left_handle: str
    right_handle: str
```

## Implementation Details

### 1. Transaction Verification

1. Get the transaction details from AlgoNode using the txid
2. Verify that the transaction is valid and confirmed
3. Check that the amount meets the minimum bet requirement
4. Verify that the receiver is the game's wallet address

### 2. Impact Calculation

```python
def calculate_impact(bet_amount, prompt):
    # Count power words in the prompt
    power_words = count_power_words(prompt)
    prompt_power = min(max(power_words / 10, 0.5), 1.5)
    
    # Calculate impact based on bet amount and prompt power
    impact = min(math.log10(bet_amount) * prompt_power * random.uniform(0.8, 1.2), 10)
    
    return impact
```

### 3. Momentum Update

```python
def update_momentum(current_momentum, impact, side):
    if side == 'L':
        new_momentum = current_momentum - impact
    else:  # side == 'R'
        new_momentum = current_momentum + impact
    
    # Clamp momentum between 0 and 100
    return max(0, min(100, new_momentum))
```

### 4. Winner Calculation

```python
def calculate_winners(round_id):
    # Get the round
    round = get_round(round_id)
    
    # Determine winning side
    if round.momentum <= 0:
        winning_side = 'L'
    elif round.momentum >= 100:
        winning_side = 'R'
    else:
        # If timeout, side closer to edge wins
        winning_side = 'L' if round.momentum < 50 else 'R'
    
    # Get all bets for the winning side
    winning_bets = get_bets_by_side(round_id, winning_side)
    
    # Calculate payouts (90% to winners proportional to their bets)
    total_winning_amount = sum(bet.amount for bet in winning_bets)
    winner_pot = round.pot * 0.9
    
    payouts = []
    for bet in winning_bets:
        payout = (bet.amount / total_winning_amount) * winner_pot
        payouts.append({
            "address": bet.sender,
            "amount": int(payout)
        })
    
    # 10% to admin
    admin_payout = round.pot * 0.1
    payouts.append({
        "address": ADMIN_ADDRESS,
        "amount": int(admin_payout)
    })
    
    return payouts
```

## File Structure

```
backend/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models
├── routes/
│   ├── state.py         # GET /state endpoint
│   ├── bet.py           # POST /bet endpoint
│   ├── admin.py         # POST /admin/reset endpoint
│   └── history.py       # GET /history endpoint
├── services/
│   ├── algorand.py      # Algorand integration
│   ├── supabase.py      # Supabase integration
│   ├── replicate.py     # Replicate SDXL integration
│   └── game.py          # Game logic
├── jobs/
│   ├── render_image.py  # Image generation job
│   ├── end_round.py     # Round end checking job
│   └── payout.py        # Payout script
├── utils/
│   ├── auth.py          # Authentication utilities
│   ├── validation.py    # Input validation
│   └── helpers.py       # Misc helper functions
├── config.py            # Configuration and environment variables
└── requirements.txt     # Dependencies
```

## Conclusion

This backend plan provides a comprehensive blueprint for implementing the FOMO RUMBLE game server. It covers all the required functionality, including API endpoints, background jobs, data models, and implementation details. The modular structure allows for easy maintenance and extension.
