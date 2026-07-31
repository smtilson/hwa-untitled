# =============================================================================
# REFACTOR PLAN
# =============================================================================
# Target layout (one concern per file):
#
#   card_scraper/
#   ├── card_data_scraper.py   # HTML -> dict (already clean, no changes)
#   ├── fetcher.py             # network only
#   ├── downloader.py          # image download + filename helpers
#   ├── csv_writer.py          # DragnCards CSV serialization
#   ├── utils.py               # convert_name / convert_back
#   └── main.py                # orchestration entry point ONLY
#
# Why: main.py currently mixes network, file I/O, CSV serialization, and
# filename munging, plus legacy code. Splitting by concern makes each piece
# independently testable and lets card_data_scraper.py stay the canonical
# extractor.
#
# -----------------------------------------------------------------------------


# =============================================================================
# NEW __main__ BLOCK (to replace everything below after refactor)
# =============================================================================
from card_scraper.fetcher import fetch_card_urls, fetch_html
from card_scraper.card_data_scraper import get_card_data
from card_scraper.downloader import download_all_images
from card_scraper.csv_writer import write_dragn_cards_csv, PLACEHOLDER_CARD_BACK, prepare_dragn_cards_rows
import json

def run_pipeline(
    output_dir="hubworld-aidalon-card-images",
    csv_path="hubworld_aidalon.csv",
    json_path="data.json",
    card_back_url=PLACEHOLDER_CARD_BACK,
):
    # 1. Discover
    urls = fetch_card_urls()

    # 2. Scrape full card data (name, type, traits, faction, imageUrl,
    #    abilityText, shardCost, barrier, scrapCost)
    cards = []
    for url in urls:
        html = fetch_html(url)
        if html is None:
            continue
        cards.append(get_card_data(html))

    # 3. Snapshot the structured data (handy for debugging / re-runs without
    #    re-scraping)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=4)

    # 4. Download images
    download_all_images(cards, output_dir)

    # 5. Build CSV (cardBack is a placeholder until the real source is wired)
    rows = prepare_dragn_cards_rows(cards, PLACEHOLDER_CARD_BACK)
    write_dragn_cards_csv(csv_path, rows)


if __name__ == "__main__":
    run_pipeline()
