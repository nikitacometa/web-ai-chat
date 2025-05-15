
FOMO RUMBLE – Tech Spec

⚡ Game in 10 seconds

Two Twitter avatars fight over a momentum bar (0-100).
Each bet ≥ last × 1.05 + 10-word spell → bar nudges, SDXL redraws arena.
Edge hit or 20 min idle → winners split 90 % pot; 10 % to dev.

⸻

1 Features & Mechanics

Thing	Spec
Teams	Hard-coded handles + avatar URLs.
Momentum	Starts 50, clamp 0-100.
Bet rule	nextBet = lastBet × 1.05, min 0.1 ALGO.
Impact	impact = min( log10(bet) × promptPw × rng(0.8-1.2), 10 ).promptPw = (#power-words)/10 (clamp 0.5-1.5).
Win	Bar edge or 20 min silence.
Payout	90 % pot to winners ∝ spend, 10 % admin.
Image	SDXL prompt: <left> vs <right>, cyber-arena, momentum=<x>% + user spell.
Audit	Server tweets sha256(state) each update.


⸻

2 Architecture

Next.js  ⇆  FastAPI  ⇆  Supabase (Postgres + Storage)
            ↓
        AlgoNode REST
            ↓
      Replicate SDXL API

Centralised custody wallet; no smart-contract.

⸻

3 Backend (FastAPI)

ENV

ALGOD_NODE=https://mainnet-api.algonode.cloud
ALGOD_TOKEN=xxxxxxxx
HOT_WALLET_MNEMONIC="..."
REPLICATE_API_TOKEN=...
SUPABASE_URL=...
SUPABASE_KEY=...
ROUND_TIMEOUT_SEC=1200

Routes

Method	Path	Purpose
GET	/state	Full round + last 10 bets.
POST	/bet	Body {txid, side, prompt} → verify on AlgoNode, update state, enqueue image.
POST	/admin/reset	Start new round (token-auth header).
GET	/history?round=n	Optional archive.

Jobs
	•	render_image(job_id) → Replicate → save URL.
	•	cron_end_round() (60 s) → edge or idle timeout → mark ended, compute winners.
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
	1.	Arena – SD image, momentum bar, avatars, pot, timer.
	2.	WalletConnect – Pera popup, save address.
	3.	BetDrawer – side selector + prompt (≤ 70 chars) + “WRECK THEM” button.
	4.	Await – spinner until /state.img_url flips.
	5.	EndModal – winner banner, claim note if in winners list, tweet brag.
	6.	Admin /admin – pick two handles, hit “Start”.

SWR (3 s) or Supabase realtime to refresh /state.

⸻

6 Dev Quickstart

# backend
pip install fastapi[all] httpx python-dotenv supabase
uvicorn server:app --reload

# frontend
npx create-next-app fomo-rumble
cd fomo-rumble
npm i @perawallet/connect swr zustand tailwindcss
npm run dev
