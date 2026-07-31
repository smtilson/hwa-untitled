"""Unit tests for tournament.metrics.mean_skill_gap."""
from __future__ import annotations

import pytest

from tournament.metrics import mean_skill_gap
from tournament.models import Player, Round, Tournament


class TestMeanSkillGap:
    def test_returns_float(self, tournament_factory):
        assert isinstance(mean_skill_gap(tournament_factory()), float)

    def test_empty_tournament_returns_zero(self):
        t = Tournament(players=[Player(pid=1, name="A", skill=1.0)])
        assert mean_skill_gap(t) == 0.0

    def test_non_negative(self, tournament_factory):
        assert mean_skill_gap(tournament_factory()) >= 0.0

    def test_equal_skill_gap_is_zero(self, match_factory):
        p1 = Player(pid=1, name="A", skill=1.0)
        p2 = Player(pid=2, name="B", skill=1.0)
        t = Tournament(players=[p1, p2])
        t.rounds.append(Round(number=1, matches=[match_factory(1, 2)]))
        assert mean_skill_gap(t) == pytest.approx(0.0)

    def test_random_pairing_higher_gap_than_skill_pairing(self, tournament_factory):
        """Over many trials, random pairing should average a higher skill gap."""
        adj_gaps = [
            mean_skill_gap(tournament_factory(16, 5, "adjacent", s)) for s in range(30)
        ]
        rnd_gaps = [
            mean_skill_gap(tournament_factory(16, 5, "random", s)) for s in range(30)
        ]
        assert sum(adj_gaps) < sum(rnd_gaps)
