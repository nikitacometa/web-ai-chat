# AlgoFOMO - MVP Current State & Launch Checklist

**Document Version:** 1.1 (Reflects algosdk v3 usage)
**Last Updated:** (AI - Self-documenting timestamp, because I'm just that good)

## 1. Project Overview & MVP Goal

AlgoFOMO is a dynamic betting game centered around a shifting momentum bar influenced by user bets on one of two sides (represented by avatars). The core gameplay involves users placing bets (intended to be with ALGO cryptocurrency), casting "spells" (text prompts), and observing real-time updates to the game state, including a dynamically generated battle image.

The current MVP (Minimum Viable Product) aims to deliver a functional game loop including:
- Admin-initiated game rounds.
- User betting via Pera Wallet.
- Real-time game state updates (momentum, pot, timers, battle image).
- Automated round conclusion based on momentum or timeouts.
- (Mocked) Payouts to winners.
- (Mocked initially, now OpenAI-ready) Dynamic battle image generation.

## 2. Current Feature Implementation Status

### 2.1. Frontend (Next.js with TypeScript, React, Tailwind CSS)

- **Core UI Components:**
    - `App/Admin Panel (`app/admin/page.tsx`): Allows starting new rounds with specified avatar URLs, initial momentum, and an admin token. Includes `data-testid`s for E2E testing.
    - `Arena Component (`components/Arena.tsx`): Displays avatars, momentum bar, pot amount, round timer, and the battle image. Uses Shadcn UI `Avatar`. `data-testid`s added.
    - `BetDrawer Component (`components/BetDrawer.tsx`): Facilitates bet placement (side selection, amount, spell input). Uses Shadcn UI components (`Card`, `Button`, `Input`, `Textarea`, `RadioGroup`, `Label`). `data-testid`s added.
    - `WalletConnectButton Component (`components/WalletConnectButton.tsx`): Provides UI for Pera Wallet connection and disconnection. Uses Shadcn UI `Button`.
    - `BettingInterfaceClientWrapper Component (`components/BettingInterfaceClientWrapper.tsx`): Client-side wrapper orchestrating game state, Pera Wallet interactions for betting, and Supabase Realtime subscriptions.
- **State Management:**
    - Game state (`GameState`) primarily managed within `BettingInterfaceClientWrapper` using `useState`.
    - Pera Wallet connection state (`activeAddress`, `PeraWalletConnect` instance, etc.) managed globally via `PeraWalletContext` (`contexts/PeraWalletContext.tsx`).
- **API Interaction:**
    - `lib/api.ts`: Contains functions for all backend API calls (`fetchGameState`, `placeBet`, `startNewRound`, history calls).
    - `lib/types.ts`: Defines shared TypeScript interfaces for API requests/responses and game entities.
- **Wallet Integration (Pera Wallet Only):**
    - Direct integration with `@perawallet/connect`.
    - `PeraWalletProvider` wraps the root layout.
    - Connection/disconnection logic handled in `PeraWalletContext` and exposed via `usePeraWallet` hook.
    - `BettingInterfaceClientWrapper` uses the context to get `activeAddress` and the `peraWallet` instance for signing transactions.
    - Algorand payment transactions are constructed using `algosdk` (v3.2.0 patterns: `sender`, `receiver`), signed by Pera Wallet, and submitted to the network. The `tx_id` is then sent to the backend.
    - **CRITICAL BLOCKER (Algosdk Types):** While using `algosdk@^3.2.0` and v3 parameter names (`sender`, `receiver`) for `makePaymentTxnWithSuggestedParamsFromObject`, the TypeScript type for `PostTransactionsResponse` (from `sendRawTransaction().do()`) still appears to incorrectly omit the `txId` field. A workaround (casting response to `any`) is in place to access `txId`.
- **Real-time Updates:**
    - `BettingInterfaceClientWrapper` subscribes to Supabase Realtime channels for `rounds` (UPDATEs) and `bets` (INSERTs).
    - UI updates reactively based on these events (e.g., momentum, pot, new bets, battle image URL).
    - **USER ACTION REQUIRED:** Supabase dashboard configuration (enable Realtime for tables, set RLS). Current RLS policies are public-read.
- **Utility Functions:**
    - `lib/utils.ts`: Includes `truncateAddress` and other helpers.

### 2.2. Backend (FastAPI with Python)

- **API Endpoints:**
    - `POST /admin/reset`: Starts a new game round. Authenticated by a shared admin token. Triggers background task for initial image generation.
    - `POST /bet`: Processes user bets. Expects `tx_id`. Performs (mock) Algorand transaction verification. Creates bet record, updates round state (pot, momentum, deadline). Triggers background task for image generation.
    - `GET /state`: Returns current active game state including round details and recent bets.
    - `GET /history/rounds`: Returns paginated list of all game rounds.
    - `GET /history/bets/{round_id}`: Returns paginated list of bets for a specific round.
- **Game Logic & Services:**
    - `services/supabase_service.py`: Handles all database interactions with Supabase (creating/updating rounds, creating bets, fetching data). Includes helper `_map_db_round_to_pydantic`.
    - `services/algorand_service.py`: 
        - (Mock) `verify_bet_transaction`: Simulates Algorand transaction verification (always returns true currently).
        - `submit_payout_transaction`: Constructs and signs payout transactions using `HOT_WALLET_MNEMONIC`. **Actual network submission is commented out (mocked).**
    - `services/openai_service.py`: 
        - `generate_battle_image_url`: Integrates with OpenAI DALL-E 3 (if API key provided). **Includes fallback to mock Picsum images** if key is missing or API call fails.
    - `utils/game_logic.py`: Contains `calculate_bet_impact` function as per PRD (used in `create_bet_in_db`).
    - `models.py`: Pydantic models for API requests/responses and data structures.
- **Background Jobs:**
    - `jobs/end_round_job.py` (`check_and_end_active_round`): Checks for round end conditions (momentum, inactivity, max duration) and updates round status in DB. **USER ACTION REQUIRED:** Needs external scheduling (e.g., cron).
    - `jobs/render_image_job.py` (`trigger_render_battle_image`): Generates battle image via `openai_service` and updates DB. Triggered as FastAPI `BackgroundTasks` from `/admin/reset` and `/bet` routes.
    - `jobs/payout_job.py` (`process_payouts`): Fetches ended, unpaid rounds, calculates proportional winner payouts, (mock) submits payouts, and marks rounds as paid. **USER ACTION REQUIRED:** Needs external scheduling and implementation of real transaction submission.
- **Configuration:**
    - `config.py` and `backend/.env`: Manage settings like Supabase credentials, Admin Token, OpenAI key, Algorand node details, hot wallet mnemonic, game timeouts.

## 3. Technology Stack & Key Libraries

- **Frontend:**
    - Next.js (App Router)
    - React 18 (with Server and Client Components)
    - TypeScript
    - Tailwind CSS
    - Shadcn UI (for some UI components like Button, Card, Input, etc.)
    - Lucide React (icons)
    - `@perawallet/connect` (for Pera Algorand Wallet integration)
    - `algosdk`: `^3.2.0` (for Algorand transaction construction)
    - `supabase-js` (for Realtime subscriptions)
    - `sonner` (for toasts/notifications)
    - `framer-motion` (for minor animations)
- **Backend:**
    - FastAPI (Python web framework)
    - Pydantic (for data validation and settings management)
    - `supabase-py` (Python client for Supabase)
    - `openai` (Python client for OpenAI API)
    - `algosdk`: (Python SDK, version not explicitly changed, currently using v2 patterns)
    - Uvicorn (ASGI server)
    - Pipenv (for dependency management)
- **Database:**
    - Supabase (PostgreSQL + Realtime + Auth - though auth not used for users yet)
- **Testing:**
    - Playwright (for E2E tests - `tests/e2e/basic_game_flow.spec.ts` drafted)
    - `unittest` (Python built-in for backend unit tests - `tests/utils/test_game_logic.py` created)

## 4. Key Implementation Decisions & Rationale

- **Wallet Integration - PeraWallet Direct:** Shifted from `@txnlab/use-wallet` to direct `@perawallet/connect` integration to simplify the wallet layer for an MVP focused on a primary wallet and to bypass persistent typing issues with the former library in this specific environment.
- **External Service Mocking & Fallbacks:**
    - **OpenAI:** `openai_service.py` uses the real OpenAI API if a key is provided but gracefully falls back to placeholder images (Picsum) if the key is missing or API calls fail. This allows development and UI testing without requiring an active OpenAI subscription immediately.
    - **Algorand Transactions:** Bet verification (`algorand_service.verify_bet_transaction`) is currently a mock (always true). Payout submission (`algorand_service.submit_payout_transaction`) constructs and signs transactions but the final network send is commented out. This allows testing the surrounding logic without live transactions and incurring fees or requiring a configured hot wallet during early development.
- **Momentum Calculation:** The `bet.impact` (calculated in `utils/game_logic.py` based on bet amount and spell length as per PRD) is now used to directly modify the round's momentum in `update_round_after_bet_in_db`, replacing a simpler, less nuanced placeholder logic.
- **Background Tasks vs. Scheduled Jobs:**
    - Image generation (`render_image_job`) is triggered as a FastAPI `BackgroundTask` immediately after relevant events (new round, new bet) for responsiveness.
    - Round ending (`end_round_job`) and Payouts (`payout_job`) are designed as scripts to be run by an external scheduler (e.g., cron) due to their periodic, non-request-driven nature.
- **RLS Policies (Supabase):** Initial RLS policies grant public read access to `rounds` and `bets` tables to align with public API endpoints. Backend writes bypass RLS using the service role key. This prioritizes ease of access for an MVP; can be tightened later if specific data needs to be protected or require authentication.
- **`data-testid` for E2E Tests:** Key UI elements were proactively tagged with `data-testid` attributes to facilitate more robust and maintainable Playwright E2E tests.
- **Centralized Pera Wallet State:** A React Context (`PeraWalletContext`) was created to manage the Pera Wallet connection state globally on the frontend, allowing components like the header button and the betting interface to share this state seamlessly.
- **Algorand SDK v3 (JavaScript):** Upgraded frontend `algosdk` to `^3.2.0` and updated transaction construction parameters (`sender`, `receiver`) as per v3 migration guide. This aimed to resolve typing issues, though some persist with `PostTransactionsResponse`.

## 5. Critical Steps to Launch MVP

This section outlines the essential actions required to move from the current development state to a launchable MVP.

### 5.1. Resolve Frontend TypeScript & SDK Typing Issues

- **`algosdk` Typing for `PostTransactionsResponse` (`txId`):**
    - **Problem:** Despite using `algosdk@^3.2.0`, the `PostTransactionsResponse` type from `sendRawTransaction().do()` still seems to incorrectly omit the `txId` field. The code now uses `sender` and `receiver` for transaction creation as per v3 guidelines.
    - **Action:** The current workaround (casting response to `any` to access `txId`) remains. Further investigation into `algosdk@^3.2.0` type definitions or reporting this to the SDK maintainers might be needed for a clean fix. Verify the exact runtime response structure for `txId`.
- **(User-side) Linter Configuration for "Type-only Imports":**
    - **Problem:** The project's linter (likely ESLint with TypeScript parser) frequently flags valid component and context imports as "type-only imports."
    - **Action:** Review ESLint configuration (`.eslintrc.json`) and associated TypeScript parsing rules. This rule might be overly aggressive or misconfigured for React components / JSX. Adjusting the rule or providing overrides might be necessary for a cleaner linting experience.

### 5.2. Environment Variable Configuration

- **Backend (`backend/.env`):**
    - `SUPABASE_URL` & `SUPABASE_KEY`: Ensure these are correctly set (KEY should be the `service_role` key).
    - `OPENAI_API_KEY`: **Required for real image generation.**
    - `ADMIN_TOKEN`: **Must be a strong, unique random string.**
    - `HOT_WALLET_MNEMONIC`: **Required for real payouts.** Must be the mnemonic for a funded Algorand account (TestNet for testing, MainNet for production).
    - `GAME_TREASURY_ADDRESS`: **Required.** The Algorand address where user bets are sent.
    - `ALGOD_NODE_SERVER`, `ALGOD_NODE_TOKEN`, `ALGOD_NODE_PORT`: For backend Algorand interactions (e.g., payout job).
- **Frontend (`.env.local` or Vercel/hosting provider env vars):**
    - `NEXT_PUBLIC_SUPABASE_URL` & `NEXT_PUBLIC_SUPABASE_ANON_KEY`: For Supabase client and Realtime.
    - `NEXT_PUBLIC_API_URL`: Base URL for the backend API.
    - `NEXT_PUBLIC_ALGORAND_NETWORK`, `NEXT_PUBLIC_ALGORAND_NODE_SERVER`, `NEXT_PUBLIC_ALGORAND_NODE_TOKEN`, `NEXT_PUBLIC_ALGORAND_NODE_PORT`: For Pera Wallet connection and `algosdk` client on frontend.
    - `NEXT_PUBLIC_GAME_TREASURY_ADDRESS`: Required by frontend to construct bet transactions.

### 5.3. Supabase Setup (Manual)

- **Realtime:** In your Supabase project dashboard, navigate to `Database` -> `Replication`. Ensure your `public` schema is enabled as a source. Under `Publications`, select `supabase_realtime` and enable broadcasting for the `rounds` and `bets` tables.
- **Row Level Security (RLS):** Execute the following SQL in the Supabase SQL editor (or adapt as needed for stricter permissions):
    ```sql
    ALTER TABLE rounds ENABLE ROW LEVEL SECURITY;
    ALTER TABLE bets ENABLE ROW LEVEL SECURITY;
    CREATE POLICY "Public can read rounds" ON rounds FOR SELECT USING (true);
    CREATE POLICY "Public can read bets" ON bets FOR SELECT USING (true);
    -- Note: Backend writes use the service_role key, which bypasses RLS.
    ```

### 5.4. Backend Cron Job Scheduling (External)

- **`end_round_job.py`:** Schedule this script to run periodically (e.g., every minute) to automatically end rounds.
    - Example (Linux cron): `* * * * * /usr/bin/python3 /path/to/your/project/backend/jobs/end_round_job.py >> /var/log/algofomo_end_round.log 2>&1` (Adjust path and python interpreter).
    - Or use a cloud scheduler (AWS EventBridge, Google Cloud Scheduler) or a process manager like `systemd` if running on a dedicated server.
- **`payout_job.py`:** Schedule this script to run periodically (e.g., every 5-15 minutes, or as desired) to process payouts.
    - Similar scheduling methods apply.

### 5.5. Implement Real Transactions & Payouts

- **Bet Receiving Address:** Ensure `GAME_TREASURY_ADDRESS` (backend) and `NEXT_PUBLIC_GAME_TREASURY_ADDRESS` (frontend) are set to the correct Algorand account that will receive user bets.
- **Payout Hot Wallet:** Ensure `HOT_WALLET_MNEMONIC` in `backend/.env` corresponds to an Algorand account that is adequately funded (on TestNet for testing, MainNet for production) to cover payouts.
- **Uncomment Payout Code:** In `backend/services/algorand_service.py`, within the `submit_payout_transaction` function, uncomment the lines responsible for actual transaction submission (`algod_client.send_transaction(signed_txn)`) and error handling.

### 5.6. Test OpenAI Integration

- Provide a valid `OPENAI_API_KEY` in `backend/.env`.
- Test the image generation flow triggered by new rounds and new bets. Verify that DALL-E 3 images appear in the Arena. Test the fallback to Picsum images if the API key is invalid or calls fail.

### 5.7. Thorough End-to-End Testing

- Once all configurations are in place and type issues are resolved:
    - Test the full user flow: Admin creates round -> User connects Pera Wallet -> User places bet (transaction signed & submitted) -> Backend verifies bet -> Game state updates (UI & Realtime) -> Image updates -> Round ends (by momentum or timeout via cron job) -> Payout job runs (check logs for mock payouts, then test real payouts).
    - Test edge cases: Invalid inputs, wallet connection errors, transaction failures, API errors.
    - Verify E2E Playwright test (`basic_game_flow.spec.ts`) passes consistently.

### 5.8. Final MVP Checks

- **Admin Token Security:** Ensure `ADMIN_TOKEN` is a strong, unique secret and is not hardcoded anywhere other than the environment configuration.
- **Error Handling:** Review user-facing error messages for clarity and ensure no sensitive debug info is exposed.
- **Basic Responsiveness:** Check key UI views on common mobile screen sizes.

By addressing these critical steps, AlgoFOMO can move towards a functional and launchable MVP state. Good luck, you'll need it. (But mostly, you'll need to fix those types.) 