import requests
from bs4 import BeautifulSoup as BS
import csv
import os
import random

def fetch_hwa_card_urls():
    # Send HTTP request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    url = "https://decksmith.app/hubworldaidalon/cards"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve the page: {response.status_code}")
        return []
    # Parse HTML content
    soup = BS(response.content, "html.parser")
    card_link_elements = soup.select("a.group")
    return [target["href"] for target in card_link_elements]

def fetch_and_save_html(url, filename):
    """Fetch HTML content from URL and save to file"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            filepath = os.path.join("sample_data", filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Saved: {filename}")
            return True
        else:
            print(f"Failed to fetch {url}: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return False

def get_card_type(html_content):
    """Extract card type from HTML content"""
    import re
    soup = BS(html_content, "html.parser")
    
    # Find divs containing "Type" text (with whitespace tolerance)
    type_labels = soup.find_all("div", string=re.compile(r"Type"))
    
    if type_labels:
        # Get the parent flex container (the flex justify-between div)
        flex_container = type_labels[0].parent
        # The value is in a sibling div with class "bg-neutral-50"
        type_value = flex_container.find("div", class_="bg-neutral-50")
        
        if type_value:
            return type_value.get_text(strip=True)
    
    return None

if __name__ == "__main__":
    urls = fetch_hwa_card_urls()
    print(f"Total URLs found: {len(urls)}")
    
    # Sample 5 random URLs
    sample_urls = random.sample(urls, min(5, len(urls)))
    
    print(f"\nFetching HTML for {len(sample_urls)} random card pages...")
    for idx, url in enumerate(sample_urls, 1):
        filename = f"card_sample_{idx}.html"
        fetch_and_save_html(url, filename)