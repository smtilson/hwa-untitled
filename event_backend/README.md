# Event Backend Service

**Status**: Planned  
**Purpose**: Collect, store, and aggregate event data from DragnCards-type applications

## Overview

Backend service that records and stores event data from gameplay sessions, tournaments, and leagues. Provides APIs for querying statistics, player ratings, and tournament results.

## Features (Planned)

- Event recording and storage
- Player statistics aggregation (win rates, card usage, etc.)
- Deck tracking and analysis
- Tournament and league management
- Leaderboards and ratings
- Event replay/log storage

## API Endpoints (Planned)

```
POST /events - Record a game event
GET /events/:id - Get event details
GET /players/:id/stats - Player statistics
GET /tournaments - List tournaments
POST /tournaments - Create tournament
GET /decks - Deck listings
POST /decks - Record deck
```

## Architecture

```
Discord Bot / Web App
    ↓
Event Backend API
    ↓
Database (PostgreSQL/MongoDB/etc.)
```

## Getting Started

This module is currently in the planning phase. See [Planning Doc](../Planning%20Doc.md) for status and next steps.

## Technology Stack (Planned)

- Backend: Python (Flask/FastAPI) or Node.js (Express)
- Database: PostgreSQL or MongoDB
- Deployment: Docker containers

## Data Models (Planned)

- Events (games played, outcomes)
- Players (accounts, ratings)
- Decks (deck lists with card combinations)
- Tournaments (structure, participants, results)

## See Also

- [Main README](../README.md) - Project overview
- [Planning Doc](../Planning%20Doc.md) - Comprehensive roadmap
