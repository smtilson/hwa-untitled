from bs4 import BeautifulSoup
import re


# ============================================================================
# Generic Helper Functions (DRY extraction patterns)
# ============================================================================


def _get_soup(html_content):
    """Create a BeautifulSoup object from HTML content"""
    return BeautifulSoup(html_content, "html.parser")


def _get_element_text(soup, selector, index=0):
    """Get text content from an element by CSS selector
    
    Args:
        soup: BeautifulSoup object
        selector: CSS selector string
        index: Index of element if multiple matches (default: 0)
    
    Returns:
        Text content or None if not found
    """
    elements = soup.select(selector)
    if elements and len(elements) > index:
        return elements[index].get_text(strip=True)
    return None


def _get_element_attribute(soup, selector, attribute, index=0):
    """Get attribute value from an element by CSS selector
    
    Args:
        soup: BeautifulSoup object
        selector: CSS selector string
        attribute: Attribute name to retrieve
        index: Index of element if multiple matches (default: 0)
    
    Returns:
        Attribute value or None if not found
    """
    elements = soup.select(selector)
    if elements and len(elements) > index:
        return elements[index].get(attribute)
    return None


def _get_meta_content(soup, tag_type="name", tag_value=None):
    """Get content from a meta tag
    
    Args:
        soup: BeautifulSoup object
        tag_type: Either "name" or "property" (default: "name")
        tag_value: The value to match (e.g., "description" or "og:title")
    
    Returns:
        Content attribute value or None if not found
    """
    meta_tag = soup.find("meta", {tag_type: tag_value})
    if meta_tag:
        return meta_tag.get("content", "")
    return None


def _find_by_text_and_get_sibling(soup, text_pattern, sibling_selector, levels_up=1):
    """Find element by text content, go up N levels, then get value from sibling/child
    
    Args:
        soup: BeautifulSoup object
        text_pattern: Regex pattern to match text
        sibling_selector: CSS class/selector of the element with value
        levels_up: How many levels to traverse up before searching (default: 1)
    
    Returns:
        Text content from sibling element or None if not found
    """
    # Match exact text (stripped) to avoid partial matches
    elements = soup.find_all(string=re.compile(r"^\s*" + text_pattern + r"\s*$"))
    if elements:
        element = elements[0].parent
        # Traverse up the specified number of levels
        for _ in range(levels_up - 1):
            if element:
                element = element.parent

        if element:
            # Use select_one for CSS selector support
            value_element = element.select_one(sibling_selector)
            if value_element:
                return value_element.get_text(strip=True)
    return None


def _find_element_with_class(soup, element_type="div", classes=None):
    """Find first element containing any of the specified classes
    
    Args:
        soup: BeautifulSoup object
        element_type: HTML element type to search for
        classes: List of class names to match any of
    
    Returns:
        First matching element or None
    """
    if not classes:
        return None
    
    elements = soup.find_all(element_type, class_=re.compile("|".join(classes)))
    return elements[0] if elements else None


# ============================================================================
# Card Data Extraction Functions
# ============================================================================


def get_card_name(html_content):
    """Extract card name from HTML content"""
    soup = _get_soup(html_content)
    
    # Try img alt text first (most reliable)
    name = _get_element_attribute(soup, "img[alt]", "alt")
    if name:
        return name
    
    # Fallback to title tag, extract before first "|"
    title = _get_element_text(soup, "title")
    if title:
        return title.split(" | ")[0].strip()
    
    return None


def get_card_image_url(html_content):
    """Extract front card image URL from HTML content"""
    soup = _get_soup(html_content)
    # Find the card image in the main content area (not the logo in nav)
    # Look for img with alt that matches a card name pattern
    imgs = soup.find_all("img", alt=True)
    for img in imgs:
        src = img.get("src", "")
        # Card images contain "card.webp" in the URL
        if "card.webp" in src:
            return src
    # Fallback to first img with alt if no card image found
    return _get_element_attribute(soup, "img[alt]", "src")


def get_card_back_url(html_content):
    """Extract card back URL from HTML content (if available)"""
    front_url = get_card_image_url(html_content)
    if front_url and "card.webp" in front_url:
        return front_url.replace("card.webp", "cardback.webp")
    return None


def get_card_type(html_content):
    """Extract card type from HTML content"""
    soup = _get_soup(html_content)
    return _find_by_text_and_get_sibling(
        soup, 
        text_pattern=r"Type",
        sibling_selector="div.bg-neutral-50",
        levels_up=2
    )


def get_card_shard_cost(html_content):
    """Extract shard cost from HTML content"""
    soup = _get_soup(html_content)
    return _find_by_text_and_get_sibling(
        soup,
        text_pattern=r"Shard Cost",
        sibling_selector="div.bg-neutral-50",
        levels_up=2
    )


def get_card_barrier(html_content):
    """Extract barrier value from HTML content"""
    soup = _get_soup(html_content)
    return _find_by_text_and_get_sibling(
        soup,
        text_pattern=r"Barrier",
        sibling_selector="div.bg-neutral-50",
        levels_up=2
    )


def get_card_traits(html_content):
    """Extract list of traits from HTML content
    
    Returns a list of trait strings (e.g., ["Enforcer"], ["Location"]).
    Returns an empty list if no traits are found.
    """
    soup = _get_soup(html_content)
    elements = soup.find_all(string=re.compile(r"^\s*Traits\s*$"))
    if not elements:
        return []

    # Walk up to the row container (label div -> flex row)
    row = elements[0].parent
    if row is not None:
        row = row.parent
    if row is None:
        return []

    # All trait values are inside divs with class bg-neutral-50
    return [el.get_text(strip=True) for el in row.select("div.bg-neutral-50")]


def get_card_scrap_cost(html_content):
    """Extract scrap cost from HTML content"""
    soup = _get_soup(html_content)
    return _find_by_text_and_get_sibling(
        soup,
        text_pattern=r"Scrap Cost",
        sibling_selector="div.bg-neutral-50",
        levels_up=2
    )


def get_card_faction(html_content):
    """Extract card faction/set from HTML content"""
    soup = _get_soup(html_content)
    
    faction_classes = [
        "bg-collective",
        "bg-remnants",
        "bg-old-aidalon",
        "bg-omniworks",
    ]
    
    # Find first div with any faction class
    element = _find_element_with_class(soup, "div", faction_classes)
    if element:
        # Extract class name and convert to faction
        for cls in element.get("class", []):
            if cls.startswith("bg-"):
                return cls.replace("bg-", "").capitalize()
    
    return None


def get_card_ability_text(html_content):
    """Extract card ability/text description from HTML content"""
    soup = _get_soup(html_content)
    
    # Try meta description first
    ability = _get_meta_content(soup, tag_type="name", tag_value="description")
    if ability:
        return ability
    
    # Fallback to og:description
    return _get_meta_content(soup, tag_type="property", tag_value="og:description")


def get_card_data(html_content):
    """Extract all relevant card data from HTML content
    
    Returns a dictionary with the following keys:
    - name: Card name
    - type: Card type (Unit, Tactic, Reaction, etc.)
    - faction: Card faction/set
    - imageUrl: Front card image URL
    - cardBack: Card back image URL
    - abilityText: Card ability/description text
    - shardCost: Cost in shards to play
    - barrier: Barrier value
    - scrapCost: Scrap cost value
    """
    
    card_data = {
        "name": get_card_name(html_content),
        "type": get_card_type(html_content),
        "traits": get_card_traits(html_content),
        "faction": get_card_faction(html_content),
        "imageUrl": get_card_image_url(html_content),
        "abilityText": get_card_ability_text(html_content),
        "shardCost": get_card_shard_cost(html_content),
        "barrier": get_card_barrier(html_content),
        "scrapCost": get_card_scrap_cost(html_content),
    }
    
    return card_data
