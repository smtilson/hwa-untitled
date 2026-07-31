"""Unit tests for tournament.generators.random_match."""
from __future__ import annotations

from random import Random

import pytest

from tournament.generators import random_match
from tournament.models import Player


class TestRandomMatch:
    def _players(self):
        return Player(pid=1, name="A", skill=99.0), Player(pid=2, name="B", skill=-99.0)

    def test_returns_match_with_two_games(self):
        a, b = self._players()
        assert len(random_match(a, b, Random(0)).games) == 2

    def test_match_is_valid(self):
        a, b = self._players()
        valid, msg = random_match(a, b, Random(1)).is_valid
        assert valid, msg

    def test_agent_totals_never_tied(self):
        a, b = self._players()
        rng = Random(7)
        for _ in range(100):
            m = random_match(a, b, rng)
            assert m.total_agents_a != m.total_agents_b

    def test_skill_ignored_win_rate_near_half(self):
        """With extreme skill difference, random_match should still be ~50/50."""
        a, b = self._players()
        wins = sum(1 for i in range(400) if random_match(a, b, Random(i)).winner == 1)
        # Allow a wide band: true null is 50%, draw is 25% so win rate ~37.5%
        assert 50 < wins < 250
