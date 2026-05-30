from logging_utils import log_call
import logging
import requests
from bs4 import BeautifulSoup
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
DECKSMITH_URL = "https://decksmith.app/hubworldaidalon/cards"
logger = logging.getLogger(__name__)


@log_call(logger=logger)
def fetch_card_urls(headers=HEADERS, url=DECKSMITH_URL):
    # Send HTTP request    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.warning("Unexpected status code. \n URL: %s\nStatus Code= %s\n\nResponse: %s\n", url, response.status_code, response.text)
    # Parse HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    card_link_elements = soup.select("a.group")
    return [target["href"] for target in card_link_elements]


@log_call(logger=logger)
def fetch_html(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.text
    else:
        logger.error("Failed to fetch. \n URL: %s\nStatus Code= %s\n\nRespons: %s\n", url, response.status_code, response.text)
        response.raise_for_status()

