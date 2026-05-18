# HWA Untitled

Hub for Hubworld: Aidalon-related projects and tools. This is a modular, multi-project repository designed to support simultaneous development of different components with the ability to spin off individual projects into separate repositories as they mature.

## Projects

This repository contains or will contain the following projects:

### 1. **Card Scraper** (`card_scraper/`)
Scrapes card data from online sources (DeckSmith, etc.) to generate standardized output files compatible with DragnCards, Card-Table, and other platforms.

- **Status**: In Progress
- **Outputs**: CSV/TSV files with card metadata and images
- **See**: [card_scraper/README.md](card_scraper/README.md)

### 2. **Card Data Query Service** (`card_query/`)
Processing layer that provides flexible querying and filtering of card data. Answers questions like "How many cards in this faction from these sets have property X?"

- **Status**: Planned
- **Depends On**: Internal data resource (independent of Card Scraper)

### 3. **Web App: Shard/Heat Tracker** (`web_app/`)
JavaScript-based interactive app for tracking in-game resources like shards and heat during gameplay.

- **Status**: Planned
- **Tech**: JavaScript/React
- **Depends On**: None (standalone)

### 4. **Event Backend** (`event_backend/`)
Backend service for collecting, storing, and aggregating event data from DragnCards-type applications.

- **Status**: Planned
- **Outputs**: APIs for event recording and statistics

### 5. **Discord Bot: Async Drafts** (`discord_bot/`)
Discord bot for managing asynchronous draft events with turn-based picking.

- **Status**: Planned
- **Depends On**: Card Scraper output

---

## Working with This Repository

### Project Structure
```
project-root/
├── README.md                    (this file)
├── Planning Doc.md              (comprehensive project status & roadmap)
├── card_scraper/                (main scraper module)
├── card_query/                  (query service - TBD)
├── web_app/                     (web frontend - TBD)
├── event_backend/               (backend service - TBD)
├── discord_bot/                 (discord bot - TBD)
└── dragn_cards/                 (DragnCards integration docs)
```

### Module Independence
Each module:
- Has its own folder with `README.md`, dependencies, and configuration
- Can be developed and tested independently
- Communicates with other modules via standardized data formats (JSON, CSV)
- Can eventually be extracted to a separate repository

### Getting Started

1. **Check the Planning Doc** for current status and what's being worked on:
   ```bash
   # Read the comprehensive project planning document
   cat "Planning Doc.md"
   ```

2. **Set up the environment**:
   ```bash
   # Create and activate virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
   ```

3. **Start working on a specific module**:
   ```bash
   cd card_scraper
   # Follow the module's README for specific setup
   cat README.md
   ```

### Running Different Modules

Each module has its own dependencies and setup. See the specific module's README for instructions.

---

## Development Guidelines

### Before Starting New Work
1. Update [Planning Doc.md](Planning%20Doc.md) with your plans
2. Mark the relevant section as "In Progress"
3. Note any blockers or dependencies

### Module Development Best Practices
- Keep modules loosely coupled
- Use standardized data formats for inter-module communication
- Write tests for your module
- Document API/interface changes
- Use consistent naming and structure across modules

### Data Standards
Card data uses a standardized format compatible with DragnCards:
```
databaseID, name, imageUrl, cardBack, type, set, shardCost, barrier, presence, actionLimit, ...
```

See [Planning Doc.md](Planning%20Doc.md) for complete specification.

### Spinning Off a Module
When a module is ready to become its own repository:
1. Extract to a new git repository
2. Update this repo to reference it as a submodule or external dependency
3. Maintain compatibility with shared data formats
4. Update this README and Planning Doc

---

## References

- **Hubworld: Aidalon**: Primary game/TCG being supported
- **DeckSmith**: https://decksmith.app/hubworldaidalon/cards (card source)
- **DragnCards**: https://www.youtube.com/watch?v=mJ2kSApGxnI (tutorial)

---

## Project Status

See [Planning Doc.md](Planning%20Doc.md) for detailed status, progress tracking, and roadmap.
