# DragnCards Integration Documentation

This folder contains integration documentation and notes for compatibility with DragnCards, a web-based tabletop card game platform.

**Purpose**: Reference documentation for ensuring the Card Scraper outputs data in the correct format for DragnCards consumption.

## DragnCards CSV/TSV Format

DragnCards requires card data to be in CSV or TSV format with the following columns:

### Required Columns
- `databaseID` - Unique identifier for the card
- `name` - Card name
- `imageUrl` - URL to card image
- `cardBack` - URL to card back image
- `type` - Card type (e.g., "Unit", "Tactic", etc.)

### Data Columns
- `set` - Set this card belongs to
- `shardCost` - Cost in shards to play
- `barrier` - Barrier value (if applicable)
- `presence` - Presence value (if applicable)
- `actionLimit` - Action limit (if applicable)
- (Additional properties as needed)

## Resources

- **DragnCards Tutorial**: https://www.youtube.com/watch?v=mJ2kSApGxnI
- **Official DragnCards**: https://dragncards.com/

## Notes
These are taken while watching 
https://www.youtube.com/watch?v=mJ2kSApGxnI

The CSV or TSV needs to have specific column names:
databaseID
name
imageUrl
cardBack
type
below are just data
set
shardCost
barrier
presence
actionLimit
...


These notes help ensure that the Card Scraper (`card_scraper/` module) outputs data compatible with DragnCards' import format.