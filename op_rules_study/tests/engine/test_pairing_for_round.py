"""Unit tests for tournament.engine._pairing_for_round."""
from __future__ import annotations

from tournament.engine import _pairing_for_round


def _null_fn(records, rng, ctx):
    return []


def _null_fn2(records, rng, ctx):
    return []


def _null_fn3(records, rng, ctx):
    return []


class TestPairingForRound:
    def test_callable_returns_itself(self):
        assert _pairing_for_round(_null_fn, 1) is _null_fn
        assert _pairing_for_round(_null_fn, 5) is _null_fn

    def test_sequence_indexed_by_round(self):
        spec = [_null_fn, _null_fn2, _null_fn3]
        assert _pairing_for_round(spec, 1) is _null_fn
        assert _pairing_for_round(spec, 2) is _null_fn2
        assert _pairing_for_round(spec, 3) is _null_fn3

    def test_sequence_clamped_at_last(self):
        spec = [_null_fn, _null_fn2]
        assert _pairing_for_round(spec, 5) is _null_fn2

    def test_mapping_exact_match(self):
        spec = {1: _null_fn, 3: _null_fn2}
        assert _pairing_for_round(spec, 1) is _null_fn
        assert _pairing_for_round(spec, 3) is _null_fn2

    def test_mapping_fallback_to_latest(self):
        """Round 4 not in spec → fall back to round 3's function."""
        spec = {1: _null_fn, 3: _null_fn2}
        assert _pairing_for_round(spec, 4) is _null_fn2

    def test_mapping_fallback_to_earliest_when_round_before_any_key(self):
        """Round 0 before all keys → fall back to min key."""
        spec = {2: _null_fn, 4: _null_fn2}
        result = _pairing_for_round(spec, 1)
        assert result in (_null_fn, _null_fn2)
