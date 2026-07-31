"""Unit tests for tournament.pairing._pair_sequence."""
from __future__ import annotations

import pytest

from tournament.pairing import _pair_sequence


class TestPairSequence:
    def test_basic_pairing(self):
        assert _pair_sequence([1, 2, 3, 4]) == [(1, 2), (3, 4)]

    def test_six_players(self):
        assert _pair_sequence([0, 1, 2, 3, 4, 5]) == [(0, 1), (2, 3), (4, 5)]

    def test_odd_length_raises(self):
        with pytest.raises(ValueError):
            _pair_sequence([1, 2, 3])

    def test_empty_returns_empty(self):
        assert _pair_sequence([]) == []
