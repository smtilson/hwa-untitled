# Card Query Service

**Status**: Planned  
**Purpose**: Process and query card data with flexible filtering and aggregation

## Overview

The Card Query Service is a processing and API layer for querying card data. It pulls from an internal data resource and provides a flexible query interface for other services.

## Features

- Flexible card filtering (by faction, set, cost, properties, etc.)
- Aggregation and statistics
- Advanced querying ("How many cards in Faction X from Sets A & B have property Y?")
- Card relationship mapping
- Quick lookups and searches

## Architecture

```
Internal Data Resource
    ↓
Card Query Service (processing & indexing)
    ↓
Query API (REST/GraphQL)
    ↓
End User for data analysis
```

## Data Input

Consumes card data from internal resource:
- Uses internal data source (not dependent on Card Scraper)
- Standardized data schema

## API Design (Planned)

```
GET /cards?faction=X&set=A,B&property=Y
GET /cards/:id
POST /query (complex queries)
GET /stats?faction=X
```

## Getting Started

This module is currently in the planning phase. See [Planning Doc](../Planning%20Doc.md) for status and next steps.

## Dependencies

- Internal data resource (primary)
- Python/Node.js (TBD)
- Database (TBD) or in-memory indexing

## See Also

- [Main README](../README.md) - Project overview
- [Planning Doc](../Planning%20Doc.md) - Comprehensive roadmap
