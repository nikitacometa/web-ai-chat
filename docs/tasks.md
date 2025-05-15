# AlgoFOMO - Future Development Tasks

This document tracks planned tasks for the AlgoFOMO project.

## How to Use
- `[ ]` denotes a pending task.
- `[x]` denotes a completed task (though this document is for future tasks, so initially all will be `[ ]`).
- Tasks are grouped by feature. Within a feature group, tasks are generally ordered by dependency.

---

## Feature Group: Bet Integration & Core Game Logic

### Task 1.1: Backend - Bet Persistence & Logic
- `[ ]` Define/Confirm `bets` table schema in Supabase (as per `development_plan.md`).
  - Columns: `id` (PK), `round_id` (FK to `rounds`), `wallet_address` (bettor), `side` ('L' or 'R'), `amount` (numeric), `spell` (text), `timestamp` (timestamptz), `tx_id` (text, for Algorand tx, optional for now), `processed` (boolean).
- `[ ]` Implement `create_bet_in_db(bet_data)` in `backend/services/supabase_service.py`.
  - `[ ]` Store bet details as per schema.
- `[ ]` Implement `update_round_after_bet_in_db(round_id, bet_amount, bet_side)` in `supabase_service.py`.
  - `[ ]` Increment the round's `pot_amount`.
  - `[ ]` Calculate and apply momentum change based on `bet_amount` and `bet_side` (define this logic).
  - `[ ]` Calculate and update the round's `current_deadline` (extended by `BET_TIME_EXTENSION_SEC`, capped by `max_deadline`).
- `[ ]` Implement `get_bets_for_round_db(round_id, limit, offset)` in `supabase_service.py`.
- `[ ]` Refactor `POST /bet` endpoint (`backend/routes/bet.py`):
  - `[ ]` Validate request using `BetRequest` model.
  - `[ ]` (HOOK for Future ALGO TX VERIFICATION) For now, assume bet is valid if API is called.
  - `[ ]` Call `create_bet_in_db`.
  - `[ ]` Call `update_round_after_bet_in_db`.
  - `[ ]` Return success/failure and details of the created bet and updated round state.

### Task 1.2: Backend - Enhance `/state` Endpoint with Bets
- `[ ]` Modify `get_active_round_from_db` (or a wrapper in `supabase_service.py`) to also fetch recent bets (e.g., last 10) for the active round using `get_bets_for_round_db`.
- `[ ]` Update `GET /state` route (`backend/routes/state.py`):
  - `[ ]` Populate `recent_bets` in the `GameState` model.
  - `[ ]` Calculate and include `total_bets_count`, `left_side_bets_amount`, `right_side_bets_amount` in `GameState` based on all bets for the current round.

### Task 1.3: Frontend - Bet Submission & Display
- `[ ]` Add "Amount" input field to `BetDrawer.tsx` component (or confirm how bet amount is determined).
- `[ ]` Connect `BetDrawer.tsx` component's `onPlaceBet` (or equivalent) to `lib/api.ts`'s `placeBet` function, passing all required data from `BetRequest` model.
- `[ ]` Provide robust user feedback on bet submission (loading states, success/error messages).
- `[ ]` Display recent bets on the main game page using data from the updated `/state` endpoint.

---

## Feature Group: Real-time Updates (Supabase Realtime)

### Task 2.1: Backend - Supabase Realtime Configuration
- `[ ]` Verify Supabase project has Realtime enabled for `rounds` and `bets` tables.
- `[ ]` Review and configure Row Level Security (RLS) policies on `rounds` and `bets` tables to allow clients to subscribe to changes securely.

### Task 2.2: Frontend - Subscribe to Game State Changes
- `[ ]` In `app/page.tsx` (or a dedicated client component managing game state), use `@supabase/supabase-js` client to:
  - `[ ]` Subscribe to updates on the current active `rounds` table record (for fields like `momentum`, `pot_amount`, `current_deadline`, `battle_image_url`, `active`, `winner`).
  - `[ ]` Subscribe to new inserts on the `bets` table that match the current `active_round.id`.
- `[ ]` Update frontend state reactively based on these subscriptions. This should reduce or eliminate the need for polling `GET /state` after the initial load.

---

## Feature Group: Round Lifecycle & Automation

### Task 3.1: Backend - Automated Round Ending (`cron_end_round` Job)
- `[ ]` Implement `determine_winner(final_momentum)` utility function.
- `[ ]` Create/Update `end_round_in_db(round_id, winner_side, final_momentum, end_reason)` function in `supabase_service.py` to:
  - `[ ]` Set `active = false`.
  - `[ ]` Set `ended_at = now()`.
  - `[ ]` Set `winner = winner_side` (can be 'left', 'right', or 'draw/timeout').
- `[ ]` Implement the `cron_end_round` job (e.g., in `backend/jobs/end_round_job.py`):
  - `[ ]` Fetch the current active round using `get_active_round_from_db`.
  - `[ ]` If an active round exists, check end conditions:
    - Momentum at 0 or 100.
    - Current time >= `round.current_deadline` (inactivity).
    - Current time >= `round.max_deadline` (max duration).
  - `[ ]` If any end condition is met, determine winner and call `end_round_in_db`.
  - `[ ]` (HOOK for Future ALGO PAYOUT - to be triggered after round officially ends).
- `[ ]` Configure a scheduler (e.g., system cron, Celery Beat, cloud scheduler) to run `cron_end_round` job periodically (e.g., every minute).

---
## Feature Group: Battle Image Generation (OpenAI DALL-E)

### Task 4.1: Backend - Image Generation Service & Job
- `[ ]` Implement `openai_service.py` with a function to call DALL-E API (or chosen image gen API) with a given prompt and return the image URL. Ensure API key is handled securely via `settings`.
- `[ ]` Implement `update_round_battle_image_url_in_db(round_id, image_url)` in `supabase_service.py`.
- `[ ]` Design and implement the `render_battle_image_job` (e.g., in `backend/jobs/render_image_job.py`):
  - `[ ]` Define trigger conditions (e.g., on new round creation, after every N bets, or when a spell significantly changes momentum).
  - `[ ]` Job fetches necessary data: current round details (participant avatars for context, current momentum, last few spell prompts).
  - `[ ]` Constructs a descriptive prompt for the image generation API.
  - `[ ]` Calls `openai_service.py` to generate the image.
  - `[ ]` On success, calls `update_round_battle_image_url_in_db`.
- `[ ]` Integrate the triggering of `render_battle_image_job` (e.g., as an async task from `/admin/reset` and `/bet` endpoints).

### Task 4.2: Frontend - Display Dynamic Battle Image
- `[ ]` Ensure `Arena.tsx` component correctly displays the `battleImageUrl` from the game state.
- `[ ]` Image should update dynamically if a new one is generated (handled by Realtime updates to `rounds.battle_image_url`).

---

## Feature Group: Algorand Blockchain Integration

### Task 5.1: Frontend - Algorand Wallet Connection
- `[ ]` Integrate an Algorand wallet connection library (e.g., `@txnlab/use-wallet`, PeraConnect) into the Next.js frontend.
- `[ ]` Implement `WalletConnectButton.tsx` (or similar) for users to connect and disconnect their Algorand wallet.
- `[ ]` Store and manage connected wallet state (account address, network) globally or in relevant context.

### Task 5.2: Frontend - Initiating Algorand Bet Transaction
- `[ ]` Update the betting UI/flow (`BetDrawer.tsx`):
  - `[ ]` After user confirms bet details (side, spell, amount), construct an Algorand payment transaction (user's wallet to a designated game treasury wallet address).
  - `[ ]` Prompt user to sign the transaction using their connected wallet.
  - `[ ]` On successful signing, submit the signed transaction to the Algorand network (e.g., via AlgoNode API or wallet SDK).
  - `[ ]` Obtain the Algorand transaction ID (`tx_id`).
  - `[ ]` Call the backend `POST /bet` endpoint, including the `tx_id` along with other bet details.

### Task 5.3: Backend - Verifying Algorand Bet Transaction
- `[ ]` Implement `algorand_service.py`:
  - `[ ]` Function `verify_bet_transaction(tx_id, expected_sender, expected_receiver, expected_amount, algorand_node_client)` to query Algorand network (e.g., AlgoNode API).
    - Verify transaction confirmation, sender, receiver, and amount.
- `[ ]` Update `POST /bet` endpoint in `backend/routes/bet.py`:
  - `[ ]` Modify `BetRequest` model to include `tx_id: str`.
  - `[ ]` Before calling `create_bet_in_db`, call `algorand_service.verify_bet_transaction`.
  - `[ ]` Only if transaction is verified, proceed to store the bet (including `tx_id`) and update round state. If verification fails, return an appropriate error.

### Task 5.4: Backend - Algorand Payout System
- `[ ]` Design and implement a secure payout mechanism (e.g., as a script `payout_job.py` or an admin-triggered job).
  - `[ ]` Identify ended rounds that require payout (e.g., check a `payout_status` field in `rounds` table).
  - `[ ]` For each round, determine winners and calculate payout distribution (e.g., 90% of `pot_amount` to winning bettors, proportional to their bet amounts; 10% to house/treasury).
  - `[ ]` Securely manage a hot wallet (its mnemonic/key configured via environment variables) for sending payouts.
  - `[ ]` Construct and sign Algorand payment transactions from the hot wallet to winning bettors.
  - `[ ]` Submit transactions to the Algorand network.
  - `[ ]` Log payout transactions and update `rounds` table (e.g., set `payout_status = 'completed'`).

---

## Feature Group: History & Archives

### Task 6.1: Backend - Enhanced History Endpoints
- `[ ]` Fully implement `GET /history/rounds` in `backend/routes/history.py`:
  - `[ ]` Fetch paginated list of all rounds (not just active) from Supabase, ordered by `start_time` descending.
  - `[ ]` Include relevant summary data for each round (e.g., winner, final pot).
- `[ ]` Fully implement `GET /history/bets/{round_id}` in `backend/routes/history.py`:
  - `[ ]` Fetch all bets for a specific `round_id` from Supabase, paginated and ordered by `timestamp`.

### Task 6.2: Frontend - History Display UI
- `[ ]` (Lower priority) Design and implement frontend pages/components to:
  - `[ ]` Display a list of past game rounds with basic info and links to details.
  - `[ ]` Display detailed information for a selected past round, including its full list of bets.

---

## Feature Group: UI/UX Enhancements & Polish

- `[ ]` Conduct a thorough review of the overall UI for clarity, usability, and responsiveness across devices.
- `[ ]` Implement smooth animations and transitions for key game events (e.g., momentum bar updates, bet appearing, timer changes).
- `[ ]` Enhance loading states (e.g., skeleton loaders) and provide clear visual feedback for all user interactions.
- `[ ]` Standardize and improve the display of error messages and notifications.
- `[ ]` Refine the visual design for a more polished and engaging look and feel.

---

## Feature Group: Security & Error Handling Hardening

- `[ ]` Perform a security review of all backend endpoints, focusing on input validation, authentication, and authorization.
- `[ ]` Strengthen admin panel security if necessary (e.g., rate limiting, more complex token handling).
- `[ ]` Review and tighten Supabase Row Level Security (RLS) policies for all tables, ensuring least privilege access.
- `[ ]` Implement comprehensive server-side error logging and consider integrating an error monitoring service (e.g., Sentry).
- `[ ]` Sanitize any user-provided data that might be displayed to prevent XSS vulnerabilities (especially if spell text or user names from wallet are shown).
- `[ ]` Review dependencies for known vulnerabilities. 