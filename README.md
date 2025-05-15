# AlgoFOMO: The Ultimate Algorand Twitter Avatar Battle Game!

AlgoFOMO is a game where two Twitter avatars (represented by their handles) battle over a momentum bar (0-100). Players can bet ALGO cryptocurrency and include a 10-word spell to influence the momentum bar. The game ends when the momentum bar hits an edge (0 or 100), after 20 minutes of inactivity, or after a maximum of 24 hours. Each new bet extends the current round timer by 1 minute (up to the 24-hour cap).

## Tech Stack

- **Frontend**: Next.js (App Router), React, TypeScript, Tailwind CSS, Shadcn UI, Radix UI
- **Backend**: FastAPI (Python 3.11), Pydantic, Uvicorn
- **Database**: Supabase (PostgreSQL + Realtime + Storage for images eventually)
- **Image Generation**: OpenAI Image API (DALL-E)
- **Blockchain Interaction**: (Planned for Algorand - details TBD on exact SDK/library usage for transactions)
- **Development Environment**: Pipenv for backend Python dependencies, Docker & Docker Compose for backend service.

## Directory Structure

```
web-ai-chat/                  # Project Root
├── app/                      # Next.js App Directory (Frontend)
│   ├── (chat)/             # Chat related features (being phased out or repurposed)
│   ├── (auth)/             # Auth related features (being phased out or repurposed)
│   ├── admin/              # Admin panel for starting new rounds
│   └── page.tsx            # Main game page
├── backend/                  # FastAPI Backend
│   ├── Dockerfile            # Dockerfile for the backend service
│   ├── Pipfile               # Pipenv dependencies
│   ├── Pipfile.lock
│   ├── main.py               # FastAPI app entry point
│   ├── models.py             # Pydantic data models
│   ├── routes/               # API route handlers
│   ├── services/             # Business logic (placeholder)
│   ├── jobs/                 # Background jobs (placeholder)
│   ├── utils/                # Utility functions
│   └── config.py             # Configuration loader (placeholder)
├── components/               # React components (Shadcn UI, custom)
│   ├── Arena.tsx
│   ├── BetDrawer.tsx
│   ├── MomentumBar.tsx
│   ├── TimerDisplay.tsx
│   └── ui/                   # Shadcn UI components
├── docs/                     # Project documentation
│   ├── changelog.md
│   ├── development_plan.md
│   ├── backend_plan.md
│   └── prd.md
├── hooks/                    # Custom React hooks
├── lib/                      # Frontend libraries, utilities, API client
│   ├── api.ts                # Frontend API client for backend
│   └── types.ts              # TypeScript type definitions
├── public/                   # Static assets
├── .env.example              # Example environment variables for frontend
├── backend/.env.example      # Example environment variables for backend
├── docker-compose.yml        # Docker Compose configuration
├── next.config.ts
├── package.json
├── tsconfig.json
└── README.md                 # This file
```

## Installation

### Prerequisites

- Node.js (v18+ recommended)
- npm or pnpm (pnpm is used in this project)
- Python 3.11
- Pipenv
- Docker Desktop (or Docker Engine + Docker Compose CLI)

### Frontend Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd web-ai-chat
    ```
2.  **Install dependencies:**
    ```bash
    pnpm install
    ```
3.  **Set up environment variables:**
    Copy `.env.example` to `.env.local` and fill in the required values:
    ```
    NEXT_PUBLIC_API_URL=http://localhost:8000 # Or your deployed backend URL
    # Add other frontend specific env vars if any
    ```

### Backend Setup (with Docker)

1.  **Navigate to the backend directory** (if not already in project root):
    The `docker-compose.yml` is at the root, so commands should be run from there.

2.  **Set up environment variables for backend:**
    Create a `.env` file inside the `backend/` directory (`backend/.env`). You can copy `backend/.env.example` if it exists, or create it manually. It should contain:
    ```env
    # backend/.env
    ADMIN_API_TOKEN=your_secret_admin_token # Used to authenticate admin actions
    SUPABASE_URL=your_supabase_url # From your Supabase project settings
    SUPABASE_KEY=your_supabase_service_role_key # From your Supabase project settings
    OPENAI_API_KEY=your_openai_api_key # For image generation
    
    # Optional: For avatar URL construction, if made configurable
    # AVATAR_BASE_URL=https://unavatar.io/twitter/{handle}
    ```
    *Note: For Supabase, use the Service Role Key for backend operations if direct DB manipulation is planned, or the anon key if only using through Supabase client libraries with RLS.* Refer to Supabase docs for best practices.

## Running the Application

### 1. Backend (with Docker Compose)

From the project root directory (`web-ai-chat/`):

```bash
# Build and start the backend service in detached mode
docker-compose up --build -d
```

- The backend API will be available at `http://localhost:8000`.
- Logs can be viewed with `docker-compose logs -f backend`.
- To stop the service: `docker-compose down`.

### 2. Frontend

In a new terminal, from the project root directory (`web-ai-chat/`):

```bash
pnpm dev
```

- The frontend development server will be available at `http://localhost:3000` (or another port if 3000 is busy).

## How to Use

1.  **Admin Panel**: Navigate to `/admin` on the frontend.
    *   Enter the Twitter handles for the two participants.
    *   Enter the `ADMIN_API_TOKEN` (as configured in `backend/.env`).
    *   Click "Start New Round".
2.  **Main Game Page**: Navigate to the homepage (`/`).
    *   View the current battle arena: avatars, momentum bar, pot amount, and timer.
    *   Use the BetDrawer to select a side (Left/Right), enter a 10-word spell, and submit your bet (bet amount functionality is currently mocked).

## API Endpoints

The backend provides the following main API endpoints (running on `http://localhost:8000` by default):

-   `GET /state`: Fetches the current game state.
-   `POST /bet`: Submits a bet (currently mocked, no actual Algorand transaction).
-   `POST /admin/reset`: Starts a new game round (requires Admin Token).
-   `GET /history/rounds`: Fetches a list of past rounds.
-   `GET /history/bets/{round_id}`: Fetches bets for a specific round.

For detailed request/response schemas, refer to `docs/backend_plan.md` and the Pydantic models in `backend/models.py`.

## Configuration

-   **Frontend**: Environment variables are managed in `.env.local` (see `app/.env.example`).
    -   `NEXT_PUBLIC_API_URL`: URL of the backend API.
-   **Backend**: Environment variables are managed in `backend/.env` (used by Docker Compose).
    -   `ADMIN_API_TOKEN`: Secret token for admin operations.
    -   `SUPABASE_URL`, `SUPABASE_KEY`: Credentials for Supabase.
    -   `OPENAI_API_KEY`: For OpenAI image generation.

## What's Next / Future Enhancements

-   **Database Integration**: Fully implement Supabase for persistent storage of rounds, bets, and user data.
-   **Algorand Wallet Integration**: Connect frontend to Algorand wallets (e.g., using Pera Wallet, Defly, or @txnlab/use-wallet).
-   **Blockchain Transactions**: Process actual ALGO bets on the Algorand blockchain.
-   **Real-time Updates**: Utilize Supabase Realtime for live updates of game state on the frontend.
-   **OpenAI Image Generation**: Implement the `render_image` background job to dynamically create battle images.
-   **Background Jobs**: Implement `cron_end_round` to manage round lifecycle based on timers and game conditions.
-   **Payout System**: Develop and test the ALGO payout mechanism for winners.
-   **Error Handling & UX**: Robust error handling across frontend and backend, and refine user experience.
-   **Security**: Harden admin authentication, secure API keys, and implement best practices for wallet interactions.

## Deployment

-   **Frontend (Next.js)**: Recommended to deploy to **DigitalOcean App Platform** (connect Git repository) or a similar static/Node.js hosting service.
-   **Backend (FastAPI)**:
    -   **Option 1: DigitalOcean Droplet + Docker Compose**: Build the Docker image and run it using Docker Compose on a VPS. This gives full control.
    -   **Option 2: DigitalOcean App Platform**: Deploy the backend as a Docker container service on App Platform. Requires the `backend/Dockerfile`.
-   **Database**: Supabase (cloud-hosted).

Ensure environment variables are securely configured in your chosen deployment environment(s).
