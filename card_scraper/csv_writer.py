import csv


FIELDNAMES = [
    "databaseID",
    "name",
    "type",
    "traits",
    "faction",
    "abilityText",
    "shardCost",
    "barrier",
    "scrapCost",
    "quantity",
    "landscape",
    "set",
    "setType",
    "imageUrl",
    "cardBack",
    "gameImageUrl",
    "presence",
    "actionLimit",
]

BASE_ID = "A12DFAFA-84B5-4965-A8A7-35E2A30000"

# Header row identifying the game; written as the first data row in DragnCards CSVs.
GAME_HEADER_ROW = {
    "databaseID": "Hubworld: Aidalon",
    "name": "Hubworld: Aidalon",
    "gameImageUrl": "https://cf.geekdo-images.com/GSF1XABi4QyCvTXPZDgzjw__imagepage/img/x5b3FWRWXPLifWXoHcDaVkp73JI=/fit-in/900x600/filters:no_upscale():strip_icc()/pic8454145.jpg",
}

# Placeholder until the real card-back image source is wired in.
PLACEHOLDER_CARD_BACK = (
    "https://ik.imagekit.io/smtilson/Games/HubworldAidalon/"
    "HubworldAidalonCardBack.jpg?updatedAt=1743241452121"
)


# Default set classification for cards produced by get_card_data.
DEFAULT_SET = "Default Set"
DEFAULT_SET_TYPE = "Set Type Default"


def prepare_dragn_cards_rows(cards_data, card_back_url=PLACEHOLDER_CARD_BACK):
    """Build the list of row-dicts that will be written to the CSV.

    Maps the rich dicts returned by get_card_data to the DragnCards CSV
    column schema, adding required metadata fields without mutating the
    input cards.

    Returns a list of dicts including the leading game header row.
    """
    rows = [GAME_HEADER_ROW]

    for index, card in enumerate(cards_data, start=1):
        if card is None:
            continue

        id_number = f"{index:02d}"
        traits = card.get("traits")
        if isinstance(traits, list):
            traits = ", ".join(traits)

        row = {
            "databaseID": BASE_ID + id_number,
            "name": card.get("name"),
            "type": card.get("type"),
            "traits": traits,
            "faction": card.get("faction"),
            "abilityText": card.get("abilityText"),
            "shardCost": card.get("shardCost"),
            "barrier": card.get("barrier"),
            "scrapCost": card.get("scrapCost"),
            "quantity": 2,
            "landscape": "no",
            "set": DEFAULT_SET,
            "setType": DEFAULT_SET_TYPE,
            "imageUrl": card.get("imageUrl"),
            "cardBack": card_back_url,
        }
        rows.append(row)

    return rows


def write_dragn_cards_csv(filename, rows):
    """Write prepared row-dicts to `filename` in DragnCards CSV format.

    Pure file I/O: expects rows already enriched by `prepare_dragn_cards_rows`.
    """
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"CSV file '{filename}' created successfully with {len(rows)} rows.")
