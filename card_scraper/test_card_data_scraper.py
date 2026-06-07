"""Unit tests for card_data_scraper against sample_data/card_sample_*.html.

Run from the repo root with:
    pytest card_scraper/test_card_data_scraper.py -v
"""

from pathlib import Path

import pytest

from card_scraper.card_data_scraper import (
    get_card_ability_text,
    get_card_barrier,
    get_card_data,
    get_card_faction,
    get_card_image_url,
    get_card_name,
    get_card_scrap_cost,
    get_card_shard_cost,
    get_card_traits,
    get_card_type,
)


SAMPLE_DIR = Path(__file__).parent / "sample_data"


# Expected values per sample file. `None` means the field is expected to be
# absent (extractor should return None / [] for that card).
SAMPLES = {
    "card_sample_1.html": {
        "name": "Baz Illisk",
        "type": "Agent",
        "traits": ["Enforcer"],
        "faction": "Remnants",
        "image_slug": "baz-illisk",
        "shardCost": "2",
        "barrier": "2",
        "scrapCost": "3",
        "ability_prefix": "While this card is forged",
    },
    "card_sample_2.html": {
        "name": "Canal Network",
        "type": "Obstacle",
        "traits": ["Location"],
        "faction": "Omniworks",
        "image_slug": "canal-network",
        "shardCost": "3",
        "barrier": "2",
        "scrapCost": "5",
        "ability_prefix": "(Confront)",
    },
    "card_sample_3.html": {
        "name": "Cracking Down",
        "type": "Moment",
        "traits": ["Influence"],
        "faction": "Collective",
        "image_slug": "cracking-down",
        "shardCost": "2",
        "barrier": None,
        "scrapCost": None,
        "ability_prefix": "(Reaction) As you approach",
    },
    "card_sample_4.html": {
        "name": "Knot Today",
        "type": "Moment",
        "traits": ["Subterfuge", "Tactic"],
        "faction": "Remnants",
        "image_slug": "knot-today",
        "shardCost": "0",
        "barrier": None,
        "scrapCost": None,
        "ability_prefix": "(Reaction) As you discover a moment",
    },
    "card_sample_5.html": {
        "name": "Wall Wizard",
        "type": "Source",
        "traits": ["Persona"],
        "faction": "Remnants",
        "image_slug": "wall-wizard",
        "shardCost": "1",
        "barrier": None,
        "scrapCost": "4",
        "ability_prefix": "Refund 1.",
    },
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _load_sample(filename):
    path = SAMPLE_DIR / filename
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module", params=sorted(SAMPLES.keys()))
def sample(request):
    """Yields (filename, html_content, expected_dict) for each sample file."""
    filename = request.param
    html = _load_sample(filename)
    return filename, html, SAMPLES[filename]


# ---------------------------------------------------------------------------
# Sample-data sanity check
# ---------------------------------------------------------------------------


def test_all_sample_files_present():
    """Every filename listed in SAMPLES must exist on disk."""
    missing = [name for name in SAMPLES if not (SAMPLE_DIR / name).is_file()]
    assert not missing, f"Missing sample files: {missing}"


# ---------------------------------------------------------------------------
# Per-field extractor tests
# ---------------------------------------------------------------------------


def test_get_card_name(sample):
    _, html, expected = sample
    assert get_card_name(html) == expected["name"]


def test_get_card_type(sample):
    _, html, expected = sample
    assert get_card_type(html) == expected["type"]


def test_get_card_traits(sample):
    _, html, expected = sample
    assert get_card_traits(html) == expected["traits"]


def test_get_card_faction(sample):
    _, html, expected = sample
    assert get_card_faction(html) == expected["faction"]


def test_get_card_shard_cost(sample):
    _, html, expected = sample
    assert get_card_shard_cost(html) == expected["shardCost"]


def test_get_card_barrier(sample):
    _, html, expected = sample
    assert get_card_barrier(html) == expected["barrier"]


def test_get_card_scrap_cost(sample):
    _, html, expected = sample
    assert get_card_scrap_cost(html) == expected["scrapCost"]


def test_get_card_image_url_is_card_webp(sample):
    """imageUrl should be the actual card image, not the site logo."""
    _, html, expected = sample
    url = get_card_image_url(html)
    assert url is not None
    assert url.endswith("card.webp"), f"Expected card.webp URL, got: {url}"
    assert expected["image_slug"] in url, (
        f"Expected slug '{expected['image_slug']}' in {url}"
    )


def test_get_card_ability_text_prefix(sample):
    """abilityText should start with the expected prefix."""
    _, html, expected = sample
    ability = get_card_ability_text(html)
    assert ability is not None
    assert ability.startswith(expected["ability_prefix"]), (
        f"Expected prefix {expected['ability_prefix']!r}, got: {ability[:80]!r}"
    )


# ---------------------------------------------------------------------------
# Aggregated `get_card_data`
# ---------------------------------------------------------------------------


def test_get_card_data_returns_all_keys(sample):
    """get_card_data should always return the full set of keys."""
    _, html, _ = sample
    data = get_card_data(html)
    expected_keys = {
        "name",
        "type",
        "traits",
        "faction",
        "imageUrl",
        "abilityText",
        "shardCost",
        "barrier",
        "scrapCost",
    }
    assert set(data.keys()) == expected_keys


def test_get_card_data_matches_individual_extractors(sample):
    """Aggregated dict must agree with the individual extractor functions."""
    _, html, _ = sample
    data = get_card_data(html)
    assert data["name"] == get_card_name(html)
    assert data["type"] == get_card_type(html)
    assert data["traits"] == get_card_traits(html)
    assert data["faction"] == get_card_faction(html)
    assert data["imageUrl"] == get_card_image_url(html)
    assert data["abilityText"] == get_card_ability_text(html)
    assert data["shardCost"] == get_card_shard_cost(html)
    assert data["barrier"] == get_card_barrier(html)
    assert data["scrapCost"] == get_card_scrap_cost(html)


# ---------------------------------------------------------------------------
# Edge cases: empty/garbage input
# ---------------------------------------------------------------------------


def test_empty_html_returns_no_data():
    """Each extractor should gracefully handle empty input."""
    html = ""
    assert get_card_name(html) is None
    assert get_card_type(html) is None
    assert get_card_traits(html) == []
    assert get_card_faction(html) is None
    assert get_card_image_url(html) is None
    assert get_card_ability_text(html) is None
    assert get_card_shard_cost(html) is None
    assert get_card_barrier(html) is None
    assert get_card_scrap_cost(html) is None


def test_get_card_data_on_empty_html():
    """get_card_data should still return the full dict shape on empty input."""
    data = get_card_data("")
    assert data == {
        "name": None,
        "type": None,
        "traits": [],
        "faction": None,
        "imageUrl": None,
        "abilityText": None,
        "shardCost": None,
        "barrier": None,
        "scrapCost": None,
    }
