# Discord Bot: Async Drafts

**Status**: Planned  
**Purpose**: Facilitate asynchronous draft events via Discord

## Overview

A Discord bot for managing turn-based, asynchronous draft events. Players can participate in drafts through Discord DMs with turn-based picking, allowing drafts to progress naturally without requiring all participants to be online simultaneously.

## Features (Planned)

- Draft pool management and setup
- Turn-based picking via DM
- Draft state persistence
- Automatic notifications to next drafter
- Deck list generation from picks
- Statistics tracking (if linked to Event Backend)
- Multiple draft formats support
- Spectator mode for active drafts

## Architecture

```
Discord API
    ↓
Discord Bot
    ↓
Event Backend (optional)
Card Query Service (card lookups)
```

## Getting Started

This module is currently in the planning phase. See [Planning Doc](../Planning%20Doc.md) for status and next steps.

## Commands (Planned)

```
!draft create <format> - Create new draft
!draft join <draft_id> - Join draft
!draft list - See available drafts
!draft info <draft_id> - Draft info and status
!pick <card_id> - Pick card in draft
```

## Dependencies

- discord.py or discord.js
- Card data from Card Scraper
- Event Backend (optional, for tracking stats)
- Card Query Service (for card lookups)

## Directory Structure (Template)

```
discord_bot/
├── README.md
├── requirements.txt
├── src/
│   ├── bot.py
│   ├── commands/
│   ├── services/
│   └── models/
├── tests/
└── .env.example
```

## Configuration

Create `.env` file with:
```
DISCORD_TOKEN=your_token_here
EVENT_BACKEND_URL=http://localhost:5000
CARD_QUERY_URL=http://localhost:8000
```

## See Also

- [Main README](../README.md) - Project overview
- [Planning Doc](../Planning%20Doc.md) - Comprehensive roadmap
