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


# MOVE -> fetcher.py, rename to `fetch_html`
# CHANGES:
#  - Use the module-level HEADERS constant; don't redefine the dict inline.
#  - Replace `print` with logging.
#  - Consider response.raise_for_status() + a single except block.
def fetch_html_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


# DELETE (legacy)
# Superseded by `get_card_data` in card_data_scraper.py, which returns the
# full dict including traits, faction, ability text, shardCost, barrier,
# scrapCost. The new orchestrator calls get_card_data directly.
def fetch_card_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    imgs = soup.select("img")
    imgs = [img for img in imgs if img.get("alt")]
    if len(imgs) != 1:
        print("Something is wrong with the imgs that were found")
        return imgs
    img_src = imgs[0]["src"]
    name = imgs[0]["alt"]
    card_type = get_card_type(html_content)
    return {"name": name, "imageUrl": img_src, "type": card_type}
    
    # more card data can be gleaned but it is dependent on the card type
    # and I don't want to figure that out yet.


# MOVE -> downloader.py
# CHANGES:
#  - Signature: `download_all_images(cards, output_dir)` where each `card` is
#    the dict returned by get_card_data (has `name` and `imageUrl`).
#  - Replace `print` with logging; return a (successful, failed) tuple so the
#    orchestrator can report results.
#  - Skip cards whose imageUrl is None (some cards may not have one).
def download_all_images(data_list, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    successful = 0
    failed = 0

    for datum in data_list:
        if datum is None:
            continue
        image_url = datum["imageUrl"]
        image_name = datum["name"]
        if download_image(image_url, image_name, output_folder):
            successful += 1
        else:
            failed += 1
    print(f"Download complete. Successful: {successful}, Failed: {failed}")


# MOVE -> utils.py
# CHANGES:
#  - Remove the debug `print` statements.
#  - Document the normalization rules in the docstring:
#      space -> _, curly apostrophe (U+2019) -> __, lowercase, reject ':'.
def convert_name(name):
    if ":" in name:
        raise ValueError("Name cannot contain ':'")
    apostrophe = chr(8217)
    print(name)

    new_name = name.replace(" ", "_").replace(apostrophe, "__").lower()
    print(new_name)
    return new_name


# MOVE -> utils.py
# CHANGES:
#  - Remove debug `print` statements.
#  - Note: only needed if you still want to round-trip filenames back to
#    display names. If the new pipeline keeps `name` in the scraped dict
#    (which it will), this function becomes optional.
def convert_back(filename):
    apostrophe = chr(8217)
    name = filename.split(".")[0]
    print(name)
    name = name.replace("__", apostrophe).replace("_", " ")
    words = name.split(" ")
    new_name = ""
    for i, word in enumerate(words):
        if i == 0:
            new_name += words[0].capitalize()
        elif word in {"a", "the", "&"}:
            new_name += " " + word
        else:
            new_name += " " + word.capitalize()
    print(new_name)
    return new_name


# MOVE -> downloader.py
# CHANGES:
#  - Replace `print` with logging.
#  - Consider returning the file path on success (None on failure) so callers
#    can record where each image landed.
#  - `convert_name` import comes from utils.py after the split.
def download_image(image_url, image_name, save_path):
    file_name = convert_name(image_name) + ".webp"
    file_path = os.path.join(save_path, file_name)
    try:
        response = requests.get(image_url, stream=True, timeout=20)
        response.raise_for_status()  # Raise an error for bad responses
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Successfully downloaded {image_name}.")
        return True
    except Exception as e:
        print(f"Failed to download {image_name}: {e}")
        return False


# DELETE
# Replaced by `run_pipeline()` in main.py. This function also has a bug:
# it passes a URL string to `fetch_card_data`, which expects HTML content.
def download_hwa_images():
    urls = fetch_hwa_card_urls()
    data = [fetch_card_data(url) for url in urls]
    output_folder = "hubworld-aidalon-card-images"
    download_all_images(data, output_folder)


# DELETE or archive (one-off migration helper, not part of the pipeline)
def change_file_extension(extension, directory):
    if not os.path.isdir(directory):
        print(f"{directory} does not exist..")
        return
    files_renamed = 0
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isdir(file_path):
            continue
        name, ext = os.path.splitext(filename)
        if ext:
            continue
        new_filename = f"{filename}.{extension}"
        new_file_path = os.path.join(directory, new_filename)
        try:
            os.rename(file_path, new_file_path)
            files_renamed += 1
            print(f"Renamed {filename} to {new_filename}")
        except Exception as e:
            print(f"Failed to rename {filename}: {e}")
    print(f"\nCompleted: {files_renamed} files renamed with .webp extension.")


# MOVE -> csv_writer.py, rename to `write_dragncards_csv`
# CHANGES (important — current code has bugs):
#  1. BUG: `writer.writerow(card)` is called BEFORE `card["set"]` and
#     card["setType"]` are assigned, so those columns are blank in output.
#     Move the writerow call to the END of the loop body.
#  2. SEEKERS is referenced but not defined — will raise NameError. Either
#     import it from a constants module, accept it as a parameter, or load
#     from a config file (preferred).
#  3. Hard-coded cardBack URL: take `card_back_url` as a parameter with a
#     PLACEHOLDER_CARD_BACK default so it can be swapped later.
#  4. Signature: `write_dragncards_csv(cards, path, card_back_url=...)`.
#  5. Use `enumerate(cards, start=1)` and f"{i:02d}" for id_number instead
#     of the string-length check.
#  6. The gameImageUrl/presence/actionLimit assignments to None are
#     unnecessary — DictWriter fills missing keys with empty strings.
#  7. Consider accepting `cards` as the rich dicts from get_card_data and
#     mapping the scraper fields -> CSV columns explicitly (don't mutate the
#     input dicts in place).
def create_from_decksmith_hwa_csv(filename, cards_data):
    fieldnames = [
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
    base_id = "A12DFAFA-84B5-4965-A8A7-35E2A30000"
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        first_line = {
            "databaseID": "Hubworld: Aidalon",
            "name": "Hubworld: Aidalon",
            "gameImageUrl": "https://cf.geekdo-images.com/GSF1XABi4QyCvTXPZDgzjw__imagepage/img/x5b3FWRWXPLifWXoHcDaVkp73JI=/fit-in/900x600/filters:no_upscale():strip_icc()/pic8454145.jpg",
        }
        writer.writerow(first_line)
        for index, card in enumerate(cards_data):
            if card is not None:
                # add the databaseID and quantity fields
                index = str(index + 1)
                id_number = index if len(index) == 2 else "0" + index
                card["databaseID"] = base_id + id_number
                card["quantity"] = 2
                # add the landscape field
                card["landscape"] = "no"
                card["cardBack"] = (
                    "https://ik.imagekit.io/smtilson/Games/HubworldAidalon/HubworldAidalonCardBack.jpg?updatedAt=1743241452121"
                )
                card["gameImageUrl"] = None
                card["presence"] = None
                card["actionLimit"] = None
                writer.writerow(card)
                # TODO: SEEKERS is a hardcoded list - should be defined or loaded from config
                if card["name"] in SEEKERS:
                    card["set"] = "Demo Seekers"
                    card["setType"] = "Seekers"
                else:
                    card["set"] = "Preview Deck"
                    card["setType"] = "Premade Decks"

    print(f"CSV file '{filename}' created successfully with {len(cards_data)} cards.")


# DELETE (legacy, disk-based path)
def get_saved_cards_data():
    directory = "hubworld-aidalon-card-images"
    cards_data = []
    for card_name in os.listdir(directory):
        file_path = os.path.join(directory, card_name)
        if os.path.isdir(file_path):
            continue
        cards_data.append(gen_my_card_data(card_name))
    return cards_data


# DELETE (legacy)
def gen_my_card_data_old(card_name):
    name = convert_back(card_name)
    base_image_url = (
        "https://ik.imagekit.io/smtilson/Games/HubworldAidalon/PreviewDeck/"
    )
    return {"name": name, "imageUrl": base_image_url + card_name}


# DELETE (legacy, superseded by write_dragncards_csv consuming fresh scrape)
def create_csv_from_saved_images():
    # this is sort of broken now because I changed the names of the saved images to be more consistent and easier to work with, but it should be easy enough to fix by converting the names back to their original format. I will do that in a bit, but for now I want to move on to other things.
    fieldnames = [
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
    base_id = "A12DFAFA-84B5-4965-A8A7-35E2A30000"
    cards_data = get_saved_cards_data()
    filename = "hubworld_aidalon.csv"
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        first_line = {
            "databaseID": "Hubworld: Aidalon",
            "name": "Hubworld: Aidalon",
            "gameImageUrl": "https://cf.geekdo-images.com/GSF1XABi4QyCvTXPZDgzjw__imagepage/img/x5b3FWRWXPLifWXoHcDaVkp73JI=/fit-in/900x600/filters:no_upscale():strip_icc()/pic8454145.jpg",
        }
        writer.writerow(first_line)
        for index, card in enumerate(cards_data):
            if card is not None:
                # add the databaseID and quantity fields
                index = str(index + 1)
                id_number = index if len(index) == 2 else "0" + index
                card["databaseID"] = base_id + id_number

                # add the landscape field
                card["landscape"] = "no"
                card["cardBack"] = (
                    "https://ik.imagekit.io/smtilson/Games/HubworldAidalon/HubworldAidalonCardBack.jpg?updatedAt=1743241452121"
                )
                card["gameImageUrl"] = None
                card["presence"] = None
                card["actionLimit"] = None
                # TODO: SEEKERS is a hardcoded list - should be defined or loaded from config
                if card["name"] in SEEKERS:
                    card["set"] = "Demo Seekers"
                    card["setType"] = "Seekers"
                    card["quantity"] = 1
                # TODO: AGENTS is a hardcoded list - should be defined or loaded from config
                elif card["name"] in AGENTS:
                    card["quantity"] = 1
                    card["set"] = "Preview Deck"
                    card["setType"] = "Premade Decks"
                else:
                    card["quantity"] = 2
                    card["set"] = "Preview Deck"
                    card["setType"] = "Premade Decks"
                writer.writerow(card)

    print(f"CSV file '{filename}' created successfully with {len(cards_data)} cards.")

# DELETE (legacy, only consumer of the legacy fetch_card_data)
# outdated
def fetch_name_img_type():
    urls = fetch_hwa_card_urls()
    data = []
    for url in urls:
        card = url.split("cards/")[-1]
        print(f"Fetching data for {card}...")
        html_content = fetch_html_content(url)
        if html_content:
            card_data = fetch_card_data(html_content)
            data.append(card_data)
            print(f"Fetched data for {card_data['name']} - Type: {card_data['type']}")
    return data



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
