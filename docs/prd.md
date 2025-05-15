AlgoFOMO – Tech Spec

⚡ Game in 10 seconds

Two Twitter avatars fight over a momentum bar (0-100).
Each bet ≥ last × 1.05 + 10-word spell → bar nudges, OpenAI DALL-E redraws arena.
Win conditions: Bar edge hit, 20 min inactivity, or 24-hour max round time. Each bet extends current timer by 1 min (up to 24h cap). Winners split 90% pot; 10% to dev.

⸻

1 Features & Mechanics

Thing	Spec
Teams	Hard-coded handles + avatar URLs.
Momentum	Starts 50, clamp 0-100.
Bet rule	nextBet = lastBet × 1.05, min 0.1 ALGO.
Impact	impact = min( log10(bet) × promptPw × rng(0.8-1.2), 10 ).promptPw = (#power-words)/10 (clamp 0.5-1.5).
Win	Bar edge, 20 min inactivity, or 24-hour max round time. Each bet extends current round timer by 1 minute (up to the 24-hour cap from round start).
Payout	90 % pot to winners ∝ spend, 10 % admin.
Image	OpenAI DALL-E prompt: <left> vs <right>, cyber-arena, momentum=<x>% + user spell.
Audit	Server tweets sha256(state) each update.


⸻

2 Architecture

Next.js  ⇆  FastAPI  ⇆  Supabase (Postgres + Storage)
            ↓
        AlgoNode REST
            ↓
      OpenAI Image API

Centralised custody wallet; no smart-contract.

⸻

3 Backend (FastAPI)

ENV

ALGOD_NODE=https://mainnet-api.algonode.cloud
ALGOD_TOKEN=xxxxxxxx
HOT_WALLET_MNEMONIC="..."
OPENAI_API_KEY=...
SUPABASE_URL=...
SUPABASE_KEY=...
ROUND_INACTIVITY_TIMEOUT_SEC=1200 # 20 minutes for no bets
MAX_ROUND_DURATION_SEC=86400   # 24 hours absolute max
BET_TIME_EXTENSION_SEC=60      # 1 minute extension per bet

Routes

Method	Path	Purpose
GET	/state	Full round + last 10 bets.
POST	/bet	Body {txid, side, prompt} → verify on AlgoNode, update state & timers, enqueue image.
POST	/admin/reset	Start new round (token-auth header).
GET	/history?round=n	Optional archive.

Jobs
	•	render_image(job_id) → OpenAI API → save URL.
	•	cron_end_round() (60 s) → check edge, inactivity timeout, or max duration timeout → mark ended, compute winners.
	•	payout.py manual script to distribute ALGO.

⸻

4 Supabase Schema

create table rounds (
  id bigint primary key,
  left_handle text,
  right_handle text,
  momentum int,
  pot bigint,
  next_bet bigint,
  started_at timestamptz,
  ended_at timestamptz,
  current_deadline timestamptz, -- Tracks the current dynamically extended deadline
  absolute_deadline timestamptz, -- Tracks the 24h absolute max deadline
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

Realtime channel on rounds row for UI push.

⸻

5 Frontend (Next.js + Tailwind)

Components / Views
	1.	Arena – AI generated image, momentum bar, avatars, pot, timer (showing time to current_deadline).
	2.	WalletConnect – Pera popup, save address.
	3.	BetDrawer – side selector + prompt (≤ 70 chars) + "WRECK THEM" button.
	4.	Await – spinner until /state.img_url flips.
	5.	EndModal – winner banner, claim note if in winners list, tweet brag.
	6.	Admin /admin – pick two handles, hit "Start".

SWR (3 s) or Supabase realtime to refresh /state.

⸻

6 Dev Quickstart

# backend
# Ensure pipenv is installed: pip install pipenv
# Initialize project: pipenv install fastapi[all] httpx python-dotenv supabase openai
# Activate env: pipenv shell
# Run: uvicorn server:app --reload

# frontend
# (Assuming project already cloned/created as algofomo)
# cd algofomo
npm i @perawallet/connect swr zustand tailwindcss @supabase/supabase-js
npm run dev
