"""Unit tests for tournament.generators.skilled_match."""
from __future__ import annotations

from random import Random

import pytest

from tournament.generators import skilled_match
from tournament.models import Player


class TestSkilledMatch:
    def _players(self):
        return Player(pid=1, name="A", skill=2.0), Player(pid=2, name="B", skill=-2.0)

    def test_returns_match_with_two_games(self):
        a, b = self._players()
        m = skilled_match(a, b, Random(0))
        assert len(m.games) == 2

    def test_match_is_valid(self):
        a, b = self._players()
        valid, msg = skilled_match(a, b, Random(1)).is_valid
        assert valid, msg

    def test_agent_totals_never_tied(self):
        a, b = self._players()
        rng = Random(5)
        for _ in range(100):
            m = skilled_match(a, b, rng)
            assert m.total_agents_a != m.total_agents_b

    def test_strong_player_wins_more_often(self):
        a, b = self._players()
        wins = sum(1 for i in range(200) if skilled_match(a, b, Random(i)).winner == 1)
        assert wins > 140

    def test_player_ids_set_correctly(self):
        a, b = self._players()
        m = skilled_match(a, b, Random(0))
        assert m.player_a == 1 and m.player_b == 2

    def test_results_keys_are_player_pids(self):
        a, b = self._players()
        m = skilled_match(a, b, Random(0))
        assert set(m.results.keys()) - {"is_draw"} == {1, 2}
