"""Unit tests for tournament.pairing.REGISTRY and get."""
from __future__ import annotations

from random import Random

import pytest

from tournament.pairing import REGISTRY, get
from tournament.standings import compute_records


class TestRegistry:
    def test_contains_expected_keys(self):
        for name in (
            "adjacent",
            "fold",
            "strong_weak",
            "random_within_record",
            "random",
        ):
            assert name in REGISTRY

    def test_all_values_callable(self):
        for fn in REGISTRY.values():
            assert callable(fn)

    def test_get_returns_correct_function(self):
        fn = get("adjacent")
        assert fn is REGISTRY["adjacent"]

    def test_get_raises_key_error_for_unknown(self):
        with pytest.raises(KeyError):
            get("not_a_strategy")

    def test_all_registered_strategies_produce_valid_pairings(
        self, small_tournament, pairing_context_factory
    ):
        players, t = small_tournament()
        records = compute_records(t)
        ctx = pairing_context_factory([p.pid for p in players], round_number=2)
        for name, fn in REGISTRY.items():
            pairs = fn(records, Random(0), ctx)
            assert len(pairs) == 4, f"{name} produced wrong pair count"
            flat = [pid for pair in pairs for pid in pair]
            assert len(flat) == len(set(flat)), f"{name} duplicated a player"
