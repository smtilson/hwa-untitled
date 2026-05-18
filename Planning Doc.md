# HWA Untitled - Project Planning & Progress

Hub for all Hubworld: Aidalon-related projects. This repository is designed to be modular, allowing different components to be worked on simultaneously and potentially spun off into separate repositories as they mature.

## Project Modules

### 1. **Card Scraper** (`card_scraper/`)

**Status**: In Progress  
**Purpose**: Scrape card data from online sources (DeckSmith, etc.) to generate standardized output files  
**Outputs**: CSV/TSV files compatible with DragnCards, Card-Table, and other platforms  
**Key Features**:

- Fetches card images and metadata from DeckSmith
- Standardizes card data format
- Outputs in multiple formats for different consumers
- Extensible to support additional sources

**Current Progress**:

- [ ] Core scraping functionality from DeckSmith
- [ ] Card image downloading
- [ ] CSV/TSV generation for DragnCards format
- [ ] Data validation and error handling
- [ ] Support for additional data sources

---

### 2. **Card Data Query Service** (`card_query/`)

**Status**: Planned  
**Purpose**: Process and query card data with flexible filtering and aggregation  
**Use Cases**:

- "How many cards in Faction X from Sets A & B have property Y?"
- Aggregate statistics by faction, set, cost, etc.
- Card relationship mapping
- Advanced filtering and sorting

**Expected Outputs**:

- Query API (REST or GraphQL)
- JSON responses with structured card data
- Built on data from internal resource (not dependent on Card Scraper)

**Depends On**: Internal data resource only

---

### 3. **Web App: Shard/Heat Tracker** (`web_app/`)

**Status**: Planned  
**Tech Stack**: JavaScript/React  
**Purpose**: Small interactive app for tracking in-game resources  
**Features**:

- Shard pool tracking
- Heat tracking
- Network count tracking
- Quick reference card info pop up.
- Potentially multiplayer/session-based

**Depends On**: Nothing.

---

### 4. **Event Backend** (`event_backend/`)

**Status**: Planned  
**Purpose**: Backend for collecting event data from DragnCards-type applications  
**Features**:

- Event recording and storage
- Player statistics aggregation
- Deck tracking
- Tournament/league management

**API Consumers**: Web frontend, external tools

---

### 5. **Discord Bot: Async Drafts** (`discord_bot/`)

**Status**: Planned  
**Purpose**: Facilitate asynchronous draft events via Discord  
**Features**:

- Draft pool management
- Turn-based picking
- DM-based interactions
- Deck list generation

**Depends On**: Card Scraper

---

## Module Architecture & Dependencies

```
Largely Independent Modules:

Card Scraper (DeckSmith source)
  └─ Outputs → CSV/TSV for external platforms

Card Query Service (Internal data resource)
  └─ Outputs → REST/GraphQL API

Web App (Shard/Heat Tracker)
  └─ Standalone (no dependencies)

Event Backend
  └─ Collects event data from external sources

Discord Bot
  └─ Consumes Card Scraper output
```

**Key Principle**: Very few dependencies. Each module is largely independent:

- **Card Scraper**: Autonomous, scrapes from DeckSmith
- **Card Query Service**: Pulls from internal resource, provides query interface
- **Web App**: Standalone tracker UI
- **Event Backend**: Independent event collection
- **Discord Bot**: Uses Card Scraper output for card references

Modules have their own directories with independent configuration/dependencies.

---

## Development Guidelines

### Modularity Principles

1. Each module should be independently testable
2. Use standardized data formats (JSON, CSV) for inter-module communication
3. Minimal coupling between modules
4. Clear, documented APIs/interfaces
5. Self-contained configuration and dependencies

### Spinoff Strategy

When a module is ready to become its own repository:

1. Extract to separate git repo
2. Update this main repo to reference it as a submodule or external dependency
3. Maintain compatibility with shared data formats
4. Document the separation in this planning doc

### Folder Structure Convention

```
module_name/
├── README.md           # Module-specific documentation
├── requirements.txt    # (Python) or package.json (Node)
├── src/               # Main source code
├── tests/             # Module tests
├── data/              # Sample/test data (if applicable)
└── docs/              # Detailed documentation
```

---

## Progress Tracking

### Active Work

- [ ] Card Scraper: Complete DragnCards format output

### Next Up

- [ ] Card Query Service: Design and initial setup
- [ ] Web App: Project scaffolding

### Future

- [ ] Event Backend: Architecture and API design
- [ ] Discord Bot: Implementation

---

## Data Format Standards

### Card Data Format (CSV/TSV for DragnCards)

Required columns:

- `databaseID` - Unique identifier
- `name` - Card name
- `imageUrl` - URL to card image
- `cardBack` - URL to card back image
- `type` - Card type
- `set` - Card set
- `shardCost` - Shard cost to play
- `barrier` - Barrier value (if applicable)
- `presence` - Presence value (if applicable)
- `actionLimit` - Action limit (if applicable)

Additional columns as needed for specific platforms

---

## Resources & References

- [DragnCards Tutorial](https://www.youtube.com/watch?v=mJ2kSApGxnI)
- DeckSmith: <https://decksmith.app/hubworldaidalon/cards>
- Card sources: DeckSmith, [add others as discovered]

---

## Notes

- All projects centered on Hubworld: Aidalon TCG
- Maintain this document as the single source of truth for project status
- Update this document when starting new work or changing priorities
