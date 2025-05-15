# AlgoFOMO Backend Development Plan

## Overview

The backend for AlgoFOMO will be built using FastAPI (managed with Pipenv), a modern, high-performance web framework for building APIs with Python. It will interact with Supabase for database operations, AlgoNode for Algorand blockchain integration, and OpenAI API for image generation.

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
│  Supabase DB &   │ │AlgoNode│ │  OpenAI        │
│     Storage      │ │  REST  │ │  Image API     │
└──────────────────┘ └───────┘ └─────────────────┘
```

## Environment Variables

```
ALGOD_NODE=https://mainnet-api.algonode.cloud
ALGOD_TOKEN=xxxxxxxx
HOT_WALLET_MNEMONIC="..."
OPENAI_API_KEY=...
SUPABASE_URL=...
SUPABASE_KEY=...
ADMIN_TOKEN=...  # For admin authentication
ROUND_INACTIVITY_TIMEOUT_SEC=1200 # 20 minutes for no bets
MAX_ROUND_DURATION_SEC=86400   # 24 hours absolute max from round start
BET_TIME_EXTENSION_SEC=60      # 1 minute extension per bet
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
    "current_deadline": "2023-05-15T12:20:00Z", // Deadline considering inactivity & bet extensions
    "absolute_deadline": "2023-05-16T12:00:00Z", // Max 24h deadline
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

Processes a new bet, verifies the transaction, updates the game state (including `current_deadline`, capped by `absolute_deadline`), and enqueues an image generation job.

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
  "new_momentum": 68,
  "new_current_deadline": "2023-05-15T12:21:00Z"
}
```

### 3. POST /admin/reset

Starts a new round. Initializes `started_at`, `absolute_deadline` (now + 24h), and `current_deadline` (now + inactivity_timeout). Requires admin token authentication.
Direct avatar image URLs and an optional initial momentum (0-100, default 50) are provided for the participants.

**Request:**
```json
{
  "left_avatar_url": "https://example.com/avatar1.png",
  "right_avatar_url": "https://example.com/avatar2.png",
  "initial_momentum": 50, // Optional, defaults to 50
  "admin_token": "your_secret_admin_token"
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
  "round_id": 124,
  "initial_current_deadline": "YYYY-MM-DDTHH:mm:ssZ",
  "absolute_deadline": "YYYY-MM-DDTHH:mm:ssZ"
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
      "current_deadline": "2023-05-15T12:30:00Z",
      "absolute_deadline": "2023-05-16T12:00:00Z",
      "img_url": "https://..."
    },
    // ... more rounds
  ]
}
```

## Background Jobs

### 1. render_image(job_id)

Generates a new image using OpenAI Image API based on the current game state and the latest bet's prompt.
The handles `left_handle` and `right_handle` (along with their constructed avatar URLs) are retrieved from the current round data.

1. Get the current round and latest bet data from Supabase.
2. Construct the prompt: `<left> vs <right>, cyber-arena, momentum=<x>% + user spell`.
3. Call OpenAI API (e.g., DALL-E 3) to generate the image.
4. Save the image URL to the round record in Supabase.
5. Optionally, store the image itself in Supabase Storage if direct URL is not permanent or desired.

### 2. cron_end_round()

Runs periodically (e.g., every 60 seconds) to check if the current active round should end.

1. Get the current active round from Supabase.
2. If no active round, do nothing.
3. Check end conditions in order:
    a. Momentum hit 0 or 100.
    b. Current time >= `round.current_deadline` (inactivity timeout).
    c. Current time >= `round.absolute_deadline` (max duration timeout).
4. If any condition is met:
    a. Mark the round as ended in Supabase.
    b. Calculate winners based on the final momentum (if timeout, side closer to edge wins).
    c. Update the round record with end time and winner information.

### 3. payout.py

Manual script to distribute ALGO to winners.

1. Get the ended rounds that haven't been paid out
2. For each round:
   - Calculate the distribution (90% to winners proportional to their bets, 10% to admin)
   - Create and sign transactions using the HOT_WALLET_MNEMONIC
   - Submit transactions to the Algorand network
   - Mark the round as paid out

## Data Models

(Using Pydantic for FastAPI request/response models and internal data structures where applicable)

### 1. Round (Pydantic model for API responses, mirrors Supabase table)

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Round(BaseModel):
    id: int
    left_handle: str
    right_handle: str
    momentum: int
    pot: int
    next_bet: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    current_deadline: datetime
    absolute_deadline: datetime
    img_url: Optional[str] = None

    class Config:
        orm_mode = True # if interacting with an ORM, else from_attributes = True for newer Pydantic
```

### 2. Bet (Pydantic model, mirrors Supabase table)

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
        orm_mode = True # or from_attributes = True
```

### 3. BetRequest (Pydantic model for POST /bet)

```python
from pydantic import BaseModel, field_validator

class BetRequest(BaseModel):
    txid: str
    side: str
    prompt: str

    @field_validator('side')
    def validate_side(cls, v):
        if v not in ['L', 'R']:
            raise ValueError('side must be either "L" or "R"')
        return v

    @field_validator('prompt')
    def validate_prompt(cls, v):
        if len(v) > 70: # As per PRD
            raise ValueError('prompt must be 70 characters or less')
        return v
```

### 4. AdminResetRequest (Pydantic model for POST /admin/reset)

```python
class AdminResetRequest(BaseModel):
    left_avatar_url: str
    right_avatar_url: str
    initial_momentum: int = Field(default=50, ge=0, le=100)
    admin_token: str
```

## Implementation Details

### Timer Management (New Section)
- **Round Start (`/admin/reset`):** 
    - `started_at` = now
    - `absolute_deadline` = `started_at` + `MAX_ROUND_DURATION_SEC`
    - `current_deadline` = `started_at` + `ROUND_INACTIVITY_TIMEOUT_SEC`
- **Bet Placement (`/bet`):**
    - New `current_deadline` = now + `ROUND_INACTIVITY_TIMEOUT_SEC`
    - This new `current_deadline` must be `min(new_current_deadline, round.absolute_deadline)`.
    - Update `rounds` table with the new `current_deadline`.

### Transaction Verification (remains the same)

### Impact Calculation (remains the same)

### Winner Calculation
(Logic for determining winning side based on momentum if edge hit, or closest to edge on timeout, remains valid. Timeout now covers inactivity, or max duration.)

### Impact Calculation (New Section based on PRD)
- Impact is calculated for each bet and stored in the `bets` table.
- Formula (from PRD): `impact = min( log10(bet_amount) * prompt_power * random_factor, 10.0 )`
  - `log10(bet_amount)`: `bet_amount` is clamped to be `>= 1.0` for this term to ensure a non-negative result from `log10`.
  - `prompt_power`: Calculated as `(number_of_words_in_spell / 10.0)`, then clamped between `0.5` and `1.5`.
  - `random_factor`: A random float between `0.8` and `1.2`.
  - The final result is also clamped to be non-negative, `max(0.0, calculated_value)`.
- This logic is implemented in `backend/utils/game_logic.py:calculate_bet_impact()`.

## File Structure (Managed with Pipenv)

```
backend/
├── Pipfile
├── Pipfile.lock
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models (as defined above)
├── routes/
│   ├── state.py         # GET /state endpoint
│   ├── bet.py           # POST /bet endpoint
│   ├── admin.py         # POST /admin/reset endpoint
│   └── history.py       # GET /history endpoint
├── services/
│   ├── algorand_service.py # Algorand integration
│   ├── supabase_service.py # Supabase integration
│   ├── openai_service.py   # OpenAI Image API integration
│   └── game_service.py     # Core game logic, timer management
├── jobs/
│   ├── render_image_job.py # Image generation job
│   ├── end_round_job.py    # Round end checking job
│   └── payout.py           # Payout script (manual)
├── utils/
│   ├── auth.py             # Authentication utilities (e.g., for admin token)
│   ├── validation.py       # General validation helpers (if any beyond Pydantic)
│   ├── helpers.py          # Misc helper functions
│   └── game_logic.py       # NEW: Bet impact calculation and other game-specific logic
├── config.py               # Configuration and environment variables loader
```

## Conclusion

This backend plan provides a comprehensive blueprint for implementing the AlgoFOMO game server using FastAPI with Pipenv. It covers updated API endpoints, background jobs including OpenAI integration, revised data models for new timer mechanics, and a refined file structure. The modular design aims for maintainability and extensibility.
