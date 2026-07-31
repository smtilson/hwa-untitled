"""Unit tests for tournament.pairing within-group ordering strategies."""
from __future__ import annotations

from random import Random

from tournament.pairing import _adjacent, _fold, _shuffle, _strong_weak


class TestAdjacent:
    def test_identity_order(self):
        assert _adjacent([0, 1, 2, 3], Random(0)) == [0, 1, 2, 3]

    def test_does_not_mutate(self):
        group = [3, 1, 2, 0]
        result = _adjacent(group, Random(0))
        assert result == group


class TestFold:
    def test_four_players(self):
        # [0, 1, 2, 3] → top=[0,1] bottom=[2,3] → [0,2,1,3]
        result = _fold([0, 1, 2, 3], Random(0))
        assert result == [0, 2, 1, 3]

    def test_six_players(self):
        result = _fold([0, 1, 2, 3, 4, 5], Random(0))
        assert result == [0, 3, 1, 4, 2, 5]

    def test_output_length_matches_input(self):
        group = list(range(8))
        assert len(_fold(group, Random(0))) == 8


class TestStrongWeak:
    def test_four_players_strongest_meets_weakest(self):
        # [0(best), 1, 2, 3(worst)] → pairs (0,3),(1,2) → order [0,3,1,2]
        result = _strong_weak([0, 1, 2, 3], Random(0))
        assert result == [0, 3, 1, 2]

    def test_six_players(self):
        result = _strong_weak([0, 1, 2, 3, 4, 5], Random(0))
        assert result == [0, 5, 1, 4, 2, 3]

    def test_output_length_matches_input(self):
        group = list(range(8))
        assert len(_strong_weak(group, Random(0))) == 8


class TestShuffle:
    def test_contains_same_elements(self):
        group = list(range(8))
        result = _shuffle(group, Random(42))
        assert sorted(result) == sorted(group)

    def test_does_not_mutate_input(self):
        group = list(range(6))
        original = group.copy()
        _shuffle(group, Random(0))
        assert group == original
