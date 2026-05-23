
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

DECKSMITH_URL = "https://decksmith.app/hubworldaidalon/cards"


# MOVE -> fetcher.py, rename to `fetch_card_urls`
# CHANGES:
#  - Drop the `hwa` prefix; the module is already HWA-specific.
#  - Replace `print` with logging (logger.error on non-200).
#  - Consider raising on non-200 instead of returning [] so the orchestrator
#    can decide how to handle a failed index fetch.
def fetch_card_urls(headers=HEADERS, url=DECKSMITH_URL):
    # Send HTTP request
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the page: {response.status_code}")
        return []
    # Parse HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    card_link_elements = soup.select("a.group")
    return [target["href"] for target in card_link_elements]
