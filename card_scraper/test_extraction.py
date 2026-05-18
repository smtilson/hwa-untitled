"""Test script to verify card data extraction methods"""

import os
from pathlib import Path
from .card_data_scraper import get_card_data
import json


def test_card_extraction():
    """Test extraction methods with sample HTML files"""

    sample_data_dir = Path(__file__).parent / "sample_data"

    # Find all HTML sample files
    html_files = list(sample_data_dir.glob("card_sample_*.html"))

    if not html_files:
        print("No sample HTML files found in sample_data/")
        return

    print(f"Found {len(html_files)} sample files\n")

    results = []

    for html_file in sorted(html_files):
        print(f"Processing: {html_file.name}")
        print("-" * 60)

        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        card_data = get_card_data(html_content)
        results.append(card_data)

        # Print extracted data
        for key, value in card_data.items():
            if value:
                # Truncate long values for display
                display_value = (
                    str(value)[:100] + "..." if len(str(value)) > 100 else value
                )
                print(f"  {key}: {display_value}")
            else:
                print(f"  {key}: [NOT FOUND]")

        print()

    # Summary
    print("=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)

    fields = ["name", "type", "faction", "imageUrl", "cardBack", "abilityText"]

    for field in fields:
        found = sum(1 for card in results if card.get(field))
        total = len(results)
        percentage = (found / total * 100) if total > 0 else 0
        status = "✓" if found == total else "⚠"
        print(f"{status} {field}: {found}/{total} ({percentage:.0f}%)")

    # Output as JSON
    print("\n" + "=" * 60)
    print("FULL OUTPUT (JSON)")
    print("=" * 60)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    test_card_extraction()
