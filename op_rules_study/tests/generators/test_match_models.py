"""Unit tests for tournament.generators.MATCH_MODELS registry."""
from __future__ import annotations

import pytest

from tournament.generators import MATCH_MODELS


class TestMatchModels:
    def test_registry_contains_skilled_and_random(self):
        assert "skilled" in MATCH_MODELS
        assert "random" in MATCH_MODELS

    def test_registry_values_are_callable(self):
        for fn in MATCH_MODELS.values():
            assert callable(fn)
