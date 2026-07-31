"""Unit tests for tournament.generators.make_players."""
from __future__ import annotations

from random import Random

import pytest

from tournament.generators import make_players


class TestMakePlayers:
    def test_correct_count(self):
        players = make_players(8, Random(0))
        assert len(players) == 8

    def test_pids_are_sequential_from_zero(self):
        players = make_players(4, Random(0))
        assert [p.pid for p in players] == [0, 1, 2, 3]

    def test_raises_for_odd_count(self):
        with pytest.raises(ValueError):
            make_players(3, Random(0))

    def test_skills_drawn_from_normal(self):
        players = make_players(100, Random(42))
        mean = sum(p.skill for p in players) / len(players)
        assert abs(mean) < 0.5   # should be close to 0
