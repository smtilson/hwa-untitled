"""Make the ``tournament`` package importable when running scripts directly.

Importing this module inserts the module root (``op_rules_study/``) onto
``sys.path`` so that ``import tournament`` works regardless of the current
working directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parent.parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

DATA_DIR = MODULE_ROOT / "data"
