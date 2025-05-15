# AlgoFOMO Changelog

All notable changes to the AlgoFOMO project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
but adapted for our needs. Each entry contains:
- Date (YYYY-MM-DD)
- Type (Feature, Fix, Change, Refactor)
- Component (Backend, Frontend, etc.)
- Description (brief, focused on impact)

## Unreleased

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