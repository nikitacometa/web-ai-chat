# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI chat application built with a modern stack consisting of:
- **Frontend**: Next.js 14 with App Router, React Server Components, TypeScript
- **Backend**: FastAPI (Python) with MongoDB for user app management
- **Infrastructure**: Docker Compose for local development, PostgreSQL for chat data, Redis for caching
- **AI Integration**: AI SDK for LLM interactions, supporting xAI (default), OpenAI, and other providers

## Key Commands

### Development
```bash
# Install dependencies (using pnpm)
pnpm install

# Run development server
pnpm dev

# Run the entire stack with Docker Compose
docker compose up -d

# Stop all services
docker compose down
```

### Testing
```bash
# Run Playwright E2E tests
pnpm test:e2e

# Run route tests
pnpm test:routes

# Run specific test file
pnpm playwright test tests/e2e/chat.test.ts
```

### Build & Production
```bash
# Build Next.js app
pnpm build

# Start production server
pnpm start

# Lint code
pnpm lint
```

### Backend (Python/FastAPI)
```bash
cd backend

# Install dependencies
pipenv install --dev

# Run development server
pipenv run uvicorn app.main:app --reload

# Run tests
pipenv run pytest

# Format code
pipenv run black .

# Type checking
pipenv run mypy .
```

## Architecture Overview

### Frontend Structure
- `/app` - Next.js 14 App Router pages and API routes
  - `/(auth)` - Authentication flow (login, register)
  - `/(chat)` - Main chat interface and API routes
  - `/with-app` - App integration pages
- `/components` - Reusable React components
- `/lib` - Core utilities and integrations
  - `/ai` - AI SDK integration, models, tools, prompts
  - `/db` - Database schema and queries (PostgreSQL via Drizzle ORM)
- `/artifacts` - Artifact generation system (code, images, text, sheets)

### Backend Structure
- `/backend/app` - FastAPI application
  - `/core` - Core configuration
  - `/database` - MongoDB connection setup
  - `/models` - Database models
  - `/routes` - API endpoints
  - `/schemas` - Pydantic schemas

### Key Technologies
- **Database**: PostgreSQL (chat data), MongoDB (user apps), Redis (caching)
- **Authentication**: Auth.js with database sessions
- **File Storage**: Vercel Blob
- **AI Tools**: Document creation/update, weather data, suggestions
- **Testing**: Playwright for E2E tests

## Environment Setup

Required environment variables:
- `AUTH_SECRET` - Authentication secret (generate with `openssl rand -base64 32`)
- `XAI_API_KEY` - xAI API key for chat models
- `BLOB_READ_WRITE_TOKEN` - Vercel Blob storage token
- `POSTGRES_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- MongoDB credentials (when using Docker Compose)

## Docker Services

The application runs multiple services via Docker Compose:
- **mongodb**: MongoDB 8.0 on port 27017
- **redis**: Redis 7.2 on port 6379
- **backend**: FastAPI backend on port 8000
- **web**: Next.js frontend on port 3000
- **landing**: Landing page on port 3001

## Important Patterns

### AI Integration
- Uses AI SDK with streaming support
- Implements resumable streams for better reliability
- Custom tools for document manipulation and suggestions
- Model switching between standard and reasoning models

### Database Operations
- Uses Drizzle ORM for PostgreSQL
- Beanie ODM for MongoDB in the backend
- Migration system for schema changes

### Testing Strategy
- E2E tests cover critical user flows (chat, artifacts, reasoning)
- Route tests validate API endpoints
- Tests use fixtures for consistent setup