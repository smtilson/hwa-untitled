from card_scraper.logging_utils import log_call
import csv
import logging

logger = logging.getLogger(__name__)


# CHANGES:
#  - Document the normalization rules in the docstring:
#      space -> _, curly apostrophe (U+2019) -> __, lowercase, reject ':'.
@log_call(logger=logger)
def convert_name(name):
    if ":" in name:
        raise ValueError("Name cannot contain ':'")
    apostrophe = chr(8217)
    new_name = name.replace(" ", "_").replace(apostrophe, "__").lower()
    return new_name


# CHANGES:
#  - Note: only needed if you still want to round-trip filenames back to
#    display names. If the new pipeline keeps `name` in the scraped dict
#    (which it will), this function becomes optional.
@log_call(logger=logger)
def convert_back(filename):
    apostrophe = chr(8217)
    name = filename.split(".")[0]
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
    return new_name


@log_call(logger=logger)
def csv_to_tsv(csv_path="hubworld_aidalon.csv", tsv_path="hubworld_aidalon.tsv"):
    """Convert a CSV file to a tab-separated TSV file.

    Defaults to the project's standard CSV output path.
    """
    with open(csv_path, "r", newline="", encoding="utf-8") as csvfile, open(
        tsv_path, "w", newline="", encoding="utf-8"
    ) as tsvfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(tsvfile, delimiter="\t")
        for row in reader:
            writer.writerow(row)

    print(f"Converted {csv_path} to {tsv_path}")
