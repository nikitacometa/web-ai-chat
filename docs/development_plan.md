# AlgoFOMO Development Plan

## Project Overview

AlgoFOMO is a game where two Twitter avatars fight over a momentum bar (0-100). Players can bet ALGO cryptocurrency and include a 10-word spell to influence the momentum bar. The game ends when the momentum bar hits an edge, after 20 minutes of inactivity, or after a maximum of 24 hours. Each new bet extends the current round timer by 1 minute (up to the 24-hour cap). Winners split 90% of the pot and 10% going to the developer.

## Architecture

- **Frontend**: Next.js + Tailwind CSS
- **Backend**: FastAPI (managed with Pipenv)
- **Database**: Supabase (PostgreSQL + Storage)
- **Blockchain**: Algorand (via AlgoNode REST API)
- **Image Generation**: OpenAI Image API
- **Avatar Handling**: Direct avatar image URLs are provided manually via the admin interface.

## Development Approach

### 1. Frontend Development

We'll use the existing Next.js template as a starting point but simplify it significantly:

1. **Clean up the repository**:
   - Remove chat-related components and functionality
   - Simplify the structure to focus on game mechanics

2. **Create new components**:
   - Arena - Main game view with momentum bar, avatars, etc.
   - WalletConnect - Algorand wallet integration using use-wallet
   - BetDrawer - Betting interface
   - AwaitSpinner - Loading indicator
   - EndModal - Game end screen
   - AdminPanel - Admin interface
   - TimerDisplay - Component to show time until current_deadline

3. **Data fetching**:
   - Use SWR for polling or Supabase realtime for state updates
   - Implement proper error handling and loading states

4. **Styling**:
   - Use Tailwind CSS for styling.
   - Employ Magic UI for generating UI components, aiming for a **simple, minimalistic, yet stylish** aesthetic. Incorporate smooth animations and responsive "flexing" elements where appropriate, without overcomplicating the design.

### 2. Backend Development

We'll create a new FastAPI backend in a separate directory, using Pipenv for dependency management:

1. **API Endpoints**:
   - GET /state - Get full round and last 10 bets (including timer states)
   - POST /bet - Process a bet, update timers, and enqueue image generation
   - POST /admin/reset - Start a new round (with token auth)
   - GET /history - Optional archive of past rounds

2. **Background Jobs**:
   - render_image - Generate images via OpenAI Image API
   - cron_end_round - Check for round end conditions (edge hit, inactivity, or 24h max duration)
   - payout.py - Manual script for distributing ALGO

3. **Integration**:
   - Algorand blockchain via py-algorand-sdk
   - Supabase for database access
   - OpenAI API for image generation

### 3. Database Setup

We'll use Supabase for database and storage:

1. **Tables**:
   ```sql
   create table rounds (
     id bigint primary key,
     left_avatar_url text,
     right_avatar_url text,
     momentum int,
     pot bigint,
     next_bet bigint,
     started_at timestamptz,
     ended_at timestamptz,
     current_deadline timestamptz, -- Dynamically extended by bets
     absolute_deadline timestamptz, -- 24-hour cap from round start
     img_url text
   );

   create table bets (
     id bigint primary key,
     round_id bigint references rounds(id),
     sender text,
     side char(1),         -- 'L' or 'R'
     amount bigint,
     prompt text,
     impact real,
     created_at timestamptz
   );
   ```

2. **Realtime Subscriptions**:
   - Set up realtime channel on rounds table for UI push (especially for timer and image updates).

## Implementation Plan

### Phase 1: Setup and Basic Structure (1-2 days)

1. **Project Setup**:
   - Complete repository cleanup
   - Set up Supabase project
   - Create the database tables (as per updated schema)
   - Initialize the FastAPI backend using Pipenv

2. **Basic Frontend Structure**:
   - Update app layout and metadata for AlgoFOMO
   - Create placeholder components (including TimerDisplay)
   - Set up routing

### Phase 2: Core Functionality (3-4 days)

1. **Wallet Integration**:
   - Implement Algorand wallet connection using @txnlab/use-wallet
   - Create the WalletConnect component

2. **Game UI**:
   - Implement the Arena component (momentum bar, AI image placeholder, timer)
   - Create the BetDrawer component
   - Implement basic game state management (client-side)

3. **Backend Implementation (Core Game Logic)**:
   - Create the /state endpoint
   - Implement /bet processing logic (transaction verification, bet rules, momentum update, timer updates: current_deadline and ensuring it respects absolute_deadline)
   - Basic Supabase integration for reading/writing round and bet data.

### Phase 3: Image Generation and Real-time Updates (2-3 days)

1. **Image Generation**:
   - Integrate with OpenAI Image API
   - Implement the render_image background job
   - Update /state to reflect new img_url

2. **Real-time Updates & Round End Logic**:
   - Set up Supabase realtime subscriptions for frontend updates
   - Implement the cron_end_round job (checking all win/end conditions including inactivity and absolute_deadline)
   - Create the AwaitSpinner component for image loading

### Phase 4: Admin and Payouts (1-2 days)

1. **Admin Interface**:
   - Create the AdminPanel component
   - Implement the /admin/reset endpoint (setting initial current_deadline and absolute_deadline). Input for avatars will be direct image URLs and an optional initial momentum value.
   - Add authentication for admin routes

2. **Payout System**:
   - Implement the payout.py script
   - Create winner calculation logic
   - Set up security measures for the custody wallet

### Phase 5: Testing and Refinement (2-3 days)

1. **Testing**:
   - Test all functionality, especially timer logic and payouts
   - Verify security measures
   - Check performance under load

2. **Refinement**:
   - Fix bugs and issues
   - Optimize performance
   - Add final polish to the UI (animations, responsiveness)

## File Structure

### Frontend

```
app/
  layout.tsx                 # Main layout for AlgoFOMO
  page.tsx                   # Main game page
  admin/
    page.tsx                 # Admin interface
components/
  Arena.tsx                  # Main game view
  WalletConnect.tsx          # Wallet integration
  BetDrawer.tsx              # Betting interface
  AwaitSpinner.tsx           # Loading indicator
  EndModal.tsx               # Game end screen
  MomentumBar.tsx            # Momentum bar visualization
  TimerDisplay.tsx           # Shows time to deadline
  ui/                        # UI components (potentially from Magic UI)
hooks/
  useGameState.ts            # Game state management
  useWallet.ts               # Wallet integration hooks
lib/
  supabase.ts                # Supabase client
  utils.ts                   # Utility functions
  algorand.ts                # Algorand related utility functions (if any for frontend)
```

### Backend

```
backend/  # Managed with Pipenv
  Pipfile
  Pipfile.lock
  server.py                  # Main FastAPI application
  models.py                  # Data models
  routes.py                  # API routes
  services.py                # Business logic (game logic, timer logic)
  jobs.py                    # Background jobs (image_gen, end_round)
  utils.py                   # Utility functions
  config.py                  # Configuration
  payout.py                  # Payout script
```

## Dependencies

### Frontend

- Next.js
- Tailwind CSS
- @txnlab/use-wallet (for Algorand wallet integration)
- @supabase/supabase-js
- SWR (for data fetching, or react-query)
- Magic UI (for UI generation assistance)
- zustand (optional, for state management if needed beyond SWR/context)

### Backend (managed via Pipfile)

- fastapi[all]
- httpx
- python-dotenv
- supabase
- py-algorand-sdk
- openai
- uvicorn

## Conclusion

This development plan outlines a structured approach to building the AlgoFOMO game. By leveraging a clean Next.js setup, FastAPI with Pipenv, and Supabase, along with targeted UI generation, we can create a high-quality application efficiently. The plan breaks down the development into manageable phases, incorporating the new timer mechanics and image generation strategy.

Total estimated development time: 9-14 days (may need slight adjustment based on new complexities)
