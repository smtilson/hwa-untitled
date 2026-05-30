from log_utils import log_call
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
