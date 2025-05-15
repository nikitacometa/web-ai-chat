# FOMO RUMBLE Development Plan

## Project Overview

FOMO RUMBLE is a game where two Twitter avatars fight over a momentum bar (0-100). Players can bet ALGO cryptocurrency and include a 10-word spell to influence the momentum bar. The game ends when the momentum bar hits an edge or after 20 minutes of inactivity, with winners splitting 90% of the pot and 10% going to the developer.

## Architecture

- **Frontend**: Next.js + Tailwind CSS
- **Backend**: FastAPI
- **Database**: Supabase (PostgreSQL + Storage)
- **Blockchain**: Algorand (via AlgoNode REST API)
- **Image Generation**: Replicate SDXL API

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

3. **Data fetching**:
   - Use SWR for polling or Supabase realtime for state updates
   - Implement proper error handling and loading states

4. **Styling**:
   - Use Tailwind CSS for styling
   - Use Magic UI for generating UI components

### 2. Backend Development

We'll create a new FastAPI backend in a separate directory:

1. **API Endpoints**:
   - GET /state - Get full round and last 10 bets
   - POST /bet - Process a bet with transaction ID, side, and prompt
   - POST /admin/reset - Start a new round (with token auth)
   - GET /history - Optional archive of past rounds

2. **Background Jobs**:
   - render_image - Generate images via Replicate SDXL API
   - cron_end_round - Check for round end conditions (edge hit or timeout)
   - payout.py - Manual script for distributing ALGO

3. **Integration**:
   - Algorand blockchain via py-algorand-sdk
   - Supabase for database access
   - Replicate for image generation

### 3. Database Setup

We'll use Supabase for database and storage:

1. **Tables**:
   ```sql
   create table rounds (
     id bigint primary key,
     left_handle text,
     right_handle text,
     momentum int,
     pot bigint,
     next_bet bigint,
     started_at timestamptz,
     ended_at timestamptz,
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
   - Set up realtime channel on rounds table for UI push

## Implementation Plan

### Phase 1: Setup and Basic Structure (1-2 days)

1. **Project Setup**:
   - Clean up the existing repository
   - Set up Supabase project
   - Create the database tables
   - Initialize the FastAPI backend

2. **Basic Frontend Structure**:
   - Update app layout and metadata
   - Create placeholder components
   - Set up routing

### Phase 2: Core Functionality (3-4 days)

1. **Wallet Integration**:
   - Implement Algorand wallet connection using use-wallet
   - Create the WalletConnect component

2. **Game UI**:
   - Implement the Arena component with momentum bar
   - Create the BetDrawer component
   - Implement basic game state management

3. **Backend Implementation**:
   - Create the state endpoint
   - Implement bet processing logic
   - Set up transaction verification

### Phase 3: Image Generation and Real-time Updates (2-3 days)

1. **Image Generation**:
   - Integrate with Replicate SDXL API
   - Implement the render_image job
   - Create image caching mechanism

2. **Real-time Updates**:
   - Set up Supabase realtime subscriptions
   - Implement the round end checking job
   - Create the AwaitSpinner component

### Phase 4: Admin and Payouts (1-2 days)

1. **Admin Interface**:
   - Create the AdminPanel component
   - Implement the reset endpoint
   - Add authentication for admin routes

2. **Payout System**:
   - Implement the payout script
   - Create winner calculation logic
   - Set up security measures for the custody wallet

### Phase 5: Testing and Refinement (2-3 days)

1. **Testing**:
   - Test all functionality
   - Verify security measures
   - Check performance under load

2. **Refinement**:
   - Fix bugs and issues
   - Optimize performance
   - Add final polish to the UI

## File Structure

### Frontend

```
app/
  layout.tsx                 # Main layout with metadata
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
  ui/                        # UI components
hooks/
  useGameState.ts            # Game state management
  useWallet.ts               # Wallet integration
lib/
  supabase.ts                # Supabase client
  utils.ts                   # Utility functions
```

### Backend

```
backend/
  server.py                  # Main FastAPI application
  models.py                  # Data models
  routes.py                  # API routes
  services.py                # Business logic
  jobs.py                    # Background jobs
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
- SWR (for data fetching)
- Magic UI (for UI generation)

### Backend

- FastAPI
- httpx
- python-dotenv
- supabase
- py-algorand-sdk

## Conclusion

This development plan outlines a structured approach to building the FOMO RUMBLE game. By leveraging the existing Next.js template and using recommended libraries for Algorand and Supabase integration, we can create a high-quality application efficiently. The plan breaks down the development into manageable phases and addresses potential challenges.

Total estimated development time: 9-14 days
