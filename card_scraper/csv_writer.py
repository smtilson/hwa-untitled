import csv


FIELDNAMES = [
    "databaseID",
    "name",
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


# CHANGES (still apply):
#  2. SEEKERS is referenced but not defined — will raise NameError. Either
#     import it from a constants module, accept it as a parameter, or load
#     from a config file (preferred).
#  5. Use `enumerate(cards, start=1)` and f"{i:02d}" for id_number instead
#     of the string-length check.
#  6. The gameImageUrl/presence/actionLimit assignments to None are
#     unnecessary — DictWriter fills missing keys with empty strings.
#  7. Consider accepting `cards` as the rich dicts from get_card_data and
#     mapping the scraper fields -> CSV columns explicitly (don't mutate the
#     input dicts in place).
def prepare_dragn_cards_rows(cards_data, card_back_url=PLACEHOLDER_CARD_BACK):
    """Build the list of row-dicts that will be written to the CSV.

    Performs all per-card enrichment / validation:
      - skips falsy cards
      - assigns databaseID, quantity, landscape, cardBack
      - assigns set / setType based on SEEKERS membership

    Returns a list of dicts including the leading game header row.
    """
    rows = [GAME_HEADER_ROW]

    for index, card in enumerate(cards_data):
        if card is None:
            continue

        # databaseID = base + 2-digit index
        index = str(index + 1)
        id_number = index if len(index) == 2 else "0" + index
        card["databaseID"] = BASE_ID + id_number
        card["quantity"] = 2
        card["landscape"] = "no"
        card["cardBack"] = card_back_url
        card["gameImageUrl"] = None
        card["presence"] = None
        card["actionLimit"] = None

        # TODO: SEEKERS is a hardcoded list - should be defined or loaded from config
        if card["name"] in SEEKERS:
            card["set"] = "Demo Seekers"
            card["setType"] = "Seekers"
        else:
            card["set"] = "Preview Deck"
            card["setType"] = "Premade Decks"

        rows.append(card)

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
