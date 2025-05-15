# AlgoFOMO Changelog

All notable changes to the AlgoFOMO project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
but adapted for our needs. Each entry contains:
- Date (YYYY-MM-DD)
- Type (Feature, Fix, Change, Refactor)
- Component (Backend, Frontend, etc.)
- Description (brief, focused on impact)

## Unreleased

### 2024-07-26

#### Feature - Basic Supabase Round Integration (Backend)
- **Backend**: Initialized Supabase client in `backend/services/supabase_service.py`.
- **Backend**: Implemented `create_round_in_db` function in `supabase_service.py` to insert new rounds into the 'rounds' table, calculating start time and deadlines.
- **Backend**: Implemented `deactivate_all_active_rounds_in_db` function in `supabase_service.py` to mark existing active rounds as inactive before creating a new one.
- **Backend**: Implemented `get_active_round_from_db` function in `supabase_service.py` to fetch the current active round.
- **Backend**: Updated `/admin/reset` route in `backend/routes/admin.py` to use `deactivate_all_active_rounds_in_db` and `create_round_in_db`. Unused `os` import removed.
- **Backend**: Updated `GET /state` route in `backend/routes/state.py` to use `get_active_round_from_db`. Returns 404 if no active round is found. `GameState` model populated with the active round and placeholder/empty bet information.
- **Database Schema Note**: Assumes `rounds` table in Supabase with fields like `id`, `left_avatar_url`, `right_avatar_url`, `momentum`, `pot_amount`, `start_time`, `current_deadline`, `max_deadline`, `active`, `ended_at`, `winner`, `battle_image_url`.

#### Change - Admin & Avatar Handling
- **Backend**: Modified `/admin/reset` endpoint and `AdminResetRequest` model to accept direct avatar image URLs (`left_avatar_url`, `right_avatar_url`) and an optional `initial_momentum` instead of Twitter handles. Placeholder names ("Left Player", "Right Player") are now used for `handle` and `display_name` in the `TwitterUser` model for participants.
- **Backend**: Timeout durations for rounds (inactivity, max duration) in the `/admin/reset` mock implementation are now configurable via environment variables (`ROUND_INACTIVITY_TIMEOUT_MINUTES`, `MAX_ROUND_DURATION_HOURS`) with defaults.
- **Frontend**: Updated Admin Panel (`app/admin/page.tsx`) to include input fields for two avatar URLs and initial momentum, replacing Twitter handle inputs. UI updated to reflect these changes.
- **Frontend**: Modified `lib/api.ts` (`startNewRound` function) to send avatar URLs and initial momentum to the backend.
- **Documentation**: Updated `README.md`, `docs/development_plan.md`, and `docs/backend_plan.md` to reflect the new avatar handling mechanism and API changes.
- **Database Schema Note**: The `rounds` table in Supabase needs to be updated. The columns `left_handle` (text) and `right_handle` (text) should be changed to `left_avatar_url` (text) and `right_avatar_url` (text) respectively to align with these changes. (This is a manual database migration or requires a separate script).

### Added
- Implemented `create_bet_in_db` function in `backend/services/supabase_service.py` to persist new bets to the Supabase `bets` table.
- Implemented `update_round_after_bet_in_db` function in `backend/services/supabase_service.py` to:
  - Increment round's `pot_amount`.
  - Update round's `momentum` based on bet side and amount (initial simple logic: `(bet_amount / 100.0) * 0.1` shift, clamped 0-100).
  - Extend round's `current_deadline` by `BET_TIME_EXTENSION_SEC` (60s), respecting `max_deadline`.
- Modified `get_bets_for_round_db` in `backend/services/supabase_service.py` to support fetching all bets for a round (when `limit=None`) and corrected its `execute()` call to be awaited.
- Enhanced `GET /state` endpoint in `backend/routes/state.py` to:
  - Fetch all bets for the active round using `get_bets_for_round_db`.
  - Populate `GameState.recent_bets` with the latest (e.g., 10) bets.
  - Calculate and populate `GameState.total_bets_count`, `GameState.left_side_bets_amount`, and `GameState.right_side_bets_amount` based on all bets for the round.
- Added `BetResponse` Pydantic model to `backend/models.py`.
- Updated the `BetResponse` interface in `lib/types.ts` to align with the backend, replacing `new_momentum` and `new_deadline` with `updated_round_state: GameRound | null`.
- Refactored `components/BetDrawer.tsx`:
  - Added `roundId` and `walletAddress` to props.
  - Changed `onPlaceBet` prop to accept a `BetRequest` object and return a `Promise`.
  - Added an `Input` field for the bet `amount` with validation.
  - Updated `handleSubmit` to construct `BetRequest` and call `onPlaceBet`.
  - Implemented basic success/error feedback messages within the component.
- Removed `BetDrawerExample` default export from `components/BetDrawer.tsx`.
- Refactored `app/page.tsx` for bet submission functionality:
  - Introduced `BettingInterfaceClientWrapper`, a new client component, to handle bet interactions.
  - The main `AlgoFOMOPage` server component fetches initial game state and passes it to `BettingInterfaceClientWrapper`.
  - `BettingInterfaceClientWrapper` manages its local `gameState` and provides the `onPlaceBet` handler to `BetDrawer`.
  - The `onPlaceBet` handler now calls the `placeBet` API and updates the local `gameState.round` with the API response for UI reactivity.
  - Uses a placeholder for `walletAddress` pending wallet integration.
- Added and exported an `ArenaFallback` component within `components/Arena.tsx` (and removed `ArenaExample`) to be used by `app/page.tsx`.

## 2023-09-22

### Backend
- **Feature**: Defined data models with Pydantic (TwitterUser, Round, Bet, GameState)
- **Feature**: Implemented FastAPI routes (state, bet, admin, history)
- **Feature**: Added mock data services for development
- **Feature**: Added CORS middleware for frontend integration

### Frontend
- **Feature**: Created type definitions for game data
- **Feature**: Added API client service with functions for all endpoints
- **Feature**: Updated main page to fetch game state with proper fallbacks
- **Feature**: Added admin panel for starting new game rounds
- **Change**: Connected BetDrawer component to main layout

### Integration
- **Feature**: Connected frontend components to backend API
- **Feature**: Implemented game state loading with Suspense

## 2023-09-15

### Project Setup
- **Feature**: Initial project cleaned up from chat application to game structure 
- **Feature**: Designed core UI components (Arena, MomentumBar, TimerDisplay)
- **Feature**: Created betting interface with BetDrawer component
- **Feature**: Set up basic admin panel structure 