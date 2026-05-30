import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import re
from card_scraper.card_data_scraper import get_card_type

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
# Dead code to remove (or archive under card_scraper/old/):
#   - fetch_card_data           (legacy minimal extractor; superseded by
#                                 get_card_data in card_data_scraper.py)
#   - fetch_name_img_type       (only consumer of fetch_card_data)
#   - gen_my_card_data_old      (renamed/dead)
#   - get_saved_cards_data      (only used by create_csv_from_saved_images)
#   - create_csv_from_saved_images
#                               (builds CSV from disk filenames; superseded by
#                                 the new orchestration that builds CSV from
#                                 freshly-scraped data)
#   - change_file_extension     (one-off migration helper, not part of the
#                                 pipeline; archive if you might need it again)
#
# -----------------------------------------------------------------------------
# New orchestration (see __main__ block at the bottom of this file):
#
#   def run_pipeline(output_dir, csv_path, card_back_url=PLACEHOLDER_CARD_BACK):
#       urls    = fetch_card_urls()                # fetcher.py
#       cards   = [get_card_data(fetch_html(u))    # card_data_scraper.py
#                  for u in urls]
#       download_all_images(cards, output_dir)     # downloader.py
#       write_dragncards_csv(cards, csv_path,      # csv_writer.py
#                            card_back_url=card_back_url)
#
# PLACEHOLDER_CARD_BACK lives in csv_writer.py (or a constants module) so the
# real URL can be swapped in one place once it's available.
# =============================================================================


# =============================================================================
# NEW __main__ BLOCK (to replace everything below after refactor)
# =============================================================================
# from card_scraper.fetcher       import fetch_card_urls, fetch_html
# from card_scraper.card_data_scraper import get_card_data
# from card_scraper.downloader    import download_all_images
# from card_scraper.csv_writer    import write_dragncards_csv, PLACEHOLDER_CARD_BACK
#
# def run_pipeline(
#     output_dir="hubworld-aidalon-card-images",
#     csv_path="hubworld_aidalon.csv",
#     json_path="data.json",
#     card_back_url=PLACEHOLDER_CARD_BACK,
# ):
#     # 1. Discover
#     urls = fetch_card_urls()
#
#     # 2. Scrape full card data (name, type, traits, faction, imageUrl,
#     #    abilityText, shardCost, barrier, scrapCost)
#     cards = []
#     for url in urls:
#         html = fetch_html(url)
#         if html is None:
#             continue
#         cards.append(get_card_data(html))
#
#     # 3. Snapshot the structured data (handy for debugging / re-runs without
#     #    re-scraping)
#     with open(json_path, "w", encoding="utf-8") as f:
#         json.dump(cards, f, indent=4)
#
#     # 4. Download images
#     download_all_images(cards, output_dir)
#
#     # 5. Build CSV (cardBack is a placeholder until the real source is wired)
#     write_dragncards_csv(cards, csv_path, card_back_url=card_back_url)
#
# if __name__ == "__main__":
#     run_pipeline()
# =============================================================================

if __name__ == "__main__":
    #create_csv_from_saved_images()
    my_list = fetch_name_img_type()
    with open("data.json", "w") as json_file:
        # 'indent=4' makes the JSON file human-readable
        json.dump(my_list, json_file, indent=4)    
