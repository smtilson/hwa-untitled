# Card Scraper

The purpose of this module is to scrape card data and images from DeckSmith (and potentially other sites) in order to produce files for use with apps like Card-Table or DragnCards.

## Layout

- `card_data_scraper.py` — pure HTML → dict extraction (no network). Entry point: `get_card_data(html_content)`.
- `main.py` — fetches HTML from DeckSmith, downloads images, generates CSV.
- `test_extraction.py` — runs the extractor against `sample_data/card_sample_*.html` and prints a per-field summary.
- `sample_data/` — saved DeckSmith card pages used for offline testing.

## Extracted fields

`get_card_data()` returns a dict with the following keys:

| Key | Description | Example |
|-----|-------------|---------|
| `name` | Card name (from `img[alt]`, falls back to `<title>`) | `"Baz Illisk"` |
| `type` | Card type | `"Agent"`, `"Obstacle"`, `"Moment"`, `"Source"` |
| `traits` | List of trait strings | `["Subterfuge", "Tactic"]` |
| `faction` | Faction derived from the `bg-<faction>` class | `"Remnants"`, `"Omniworks"`, `"Collective"` |
| `imageUrl` | URL of the front card image (`card.webp`) | `https://decksmith.app/.../card.webp` |
| `abilityText` | Card ability text (from `<meta name="description">`) | `"(Reaction) ..."` |
| `shardCost` | Shard cost (string) | `"2"` |
| `barrier` | Barrier value (string), `None` if not present | `"3"` |
| `scrapCost` | Scrap cost (string), `None` if not present | `"5"` |

`cardBack` is intentionally **not** extracted here — it is supplied downstream when the CSV is generated.

## Running the extraction tests

From the repo root, with the venv active:

```bash
source .venv/bin/activate
python -m card_scraper.test_extraction
```

This iterates over every `sample_data/card_sample_*.html` file and prints the extracted values plus a summary of how many fields were successfully populated.

## How the extraction works

DeckSmith renders each card stat as a "row":

```html
<div class="flex justify-between ...">
  <div class="uppercase ...">Type</div>
  <div class="text-black">
    <div class="inline-flex ...">
      <div class="rounded-md px-3 py-1 bg-neutral-50">Agent</div>
    </div>
  </div>
</div>
```

The helper `_find_by_text_and_get_sibling` locates the label text (anchored regex, e.g. `^\s*Type\s*$`), walks up to the row container, and returns the first `div.bg-neutral-50` inside that row. Traits use the same row pattern but collect every `div.bg-neutral-50` since a card can have multiple traits.

## `main.py` workflow

`main.py` is the orchestration layer that combines network fetching, the pure HTML extractor in `card_data_scraper.py`, image downloading, and CSV/JSON output.

### Entry point

When run as `python -m card_scraper.main`, the script currently executes:

1. `fetch_name_img_type()` — scrapes the DeckSmith card index, then visits every individual card page and collects a minimal `{name, imageUrl, type}` dict per card.
2. The resulting list is dumped to `data.json` (pretty-printed).

`create_csv_from_saved_images()` is also available but commented out; it builds a DragnCards-style CSV from images already on disk.

### Pipeline stages

**1. Discover card URLs — `fetch_hwa_card_urls()`**

Sends a GET to `https://decksmith.app/hubworldaidalon/cards`, parses the response with BeautifulSoup, and returns every `href` on `a.group` elements (the per-card links on the index page).

**2. Fetch each card page — `fetch_html_content(url)`**

Plain `requests.get` wrapper that returns the HTML text on 200, prints an error and returns `None` otherwise. Wrapped in `try/except` for connection-level failures.

**3. Extract per-card data — `fetch_card_data(html_content)`**

A trimmed-down extractor that:

- Selects every `<img alt="...">`, asserts there is exactly one, and pulls `name` from `alt` and `imageUrl` from `src`.
- Calls `get_card_type` from `card_data_scraper.py` for the type.

> **Note:** this is the *old* extractor and only returns `{name, imageUrl, type}`. The richer `get_card_data()` in `card_data_scraper.py` (which also extracts traits, faction, ability text, costs, barrier) is **not yet wired in** — replacing this call is a tracked TODO.

**4. Aggregate — `fetch_name_img_type()`**

Loops over the URLs from step 1, fetches HTML via step 2, runs step 3, and accumulates a list of card dicts. Prints progress per card.

**5. Persist**

The `__main__` block writes the list to `data.json`. CSV generation is currently disabled.

### Image downloading (separate flow)

`download_hwa_images()` is an alternate top-level flow:

1. `fetch_hwa_card_urls()` — same as above.
2. `fetch_card_data(url)` for each — gets `name` + `imageUrl`.
3. `download_all_images(...)` — iterates the list, calling `download_image(...)` per card.
4. `download_image(...)` — streams the `.webp` to disk under `hubworld-aidalon-card-images/`. Filenames are normalized via `convert_name()` (lowercase, spaces → `_`, curly apostrophe `’` → `__`).

`convert_back()` reverses the filename normalization to recover a display name from a saved file.

### CSV generation (DragnCards format)

Two CSV builders exist; both write the same fixed schema:

`databaseID, name, quantity, landscape, set, setType, imageUrl, cardBack, gameImageUrl, presence, actionLimit`

- The first row is a "game" header row (`databaseID = "Hubworld: Aidalon"`, with a `gameImageUrl` pointing at a BGG image).
- Each subsequent row is a card. `databaseID` is built from a fixed UUID prefix plus a 2-digit index. `cardBack` is hard-coded to a hosted ImageKit URL (this is the "injected downstream" cardBack referenced earlier).
- `set` / `setType` / `quantity` are decided by membership in hard-coded `SEEKERS` and `AGENTS` lists (currently undefined in this file — flagged as a TODO).

`create_from_decksmith_hwa_csv(filename, cards_data)` consumes scraped data; `create_csv_from_saved_images()` consumes filenames in `hubworld-aidalon-card-images/` (via `get_saved_cards_data` → `gen_my_card_data`, which rebuilds names with `convert_back` and points `imageUrl` at the author's ImageKit-hosted copies).

### Utilities

- `change_file_extension(extension, directory)` — appends an extension to any extension-less files in a directory (used to retroactively give downloaded images a `.webp` suffix).

### Known issues / TODOs

- `fetch_card_data` in `main.py` is the legacy minimal extractor; it should be replaced with `get_card_data` from `card_data_scraper.py` so traits/faction/ability/costs end up in `data.json` and the CSV.
- `SEEKERS` and `AGENTS` are referenced but not defined inside `main.py` — calling either CSV builder will raise `NameError` until these lists are imported or defined.
- `create_from_decksmith_hwa_csv` writes each card row *before* assigning `set` / `setType`, so those fields end up blank in the output.
- `convert_name`, `convert_back`, and `download_image` contain `print` statements that should be replaced with proper logging.