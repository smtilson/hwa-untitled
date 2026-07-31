from card_scraper.logging_utils import log_call
from card_scraper.utils import convert_name
import requests
import logging
import os

logger = logging.getLogger(__name__)

@log_call(logger=logger)
def download_all_images(cards:list[dict], output_dir:str):
    os.makedirs(output_dir, exist_ok=True)
    successful = 0
    failed = 0

    for card in cards:
        if card.get("imageUrl") is None:
            continue
        image_url = card["imageUrl"]
        image_name = card["name"]
        if download_image(image_url, image_name, output_dir):
            successful += 1
        else:
            failed += 1
    logger.info("Download complete. Successful: %s, Failed: %s", successful, failed)


# CHANGES:
#  - Replace `print` with logging.
#  - Consider returning the file path on success (None on failure) so callers
#    can record where each image landed.
#  - `convert_name` import comes from utils.py after the split.
@log_call(logger=logger)
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
