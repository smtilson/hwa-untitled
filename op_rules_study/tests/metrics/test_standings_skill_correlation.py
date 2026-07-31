"""Unit tests for tournament.metrics.standings_skill_correlation."""
from __future__ import annotations

import pytest

from tournament.metrics import standings_skill_correlation
from tournament.models import Player, Round, Tournament


class TestStandingsSkillCorrelation:
    def test_returns_float(self, tournament_factory):
        assert isinstance(standings_skill_correlation(tournament_factory()), float)

    def test_value_in_valid_range(self, tournament_factory):
        corr = standings_skill_correlation(tournament_factory(16, 5))
        assert -1.0 <= corr <= 1.0

    def test_single_player_returns_zero(self):
        t = Tournament(players=[Player(pid=1, name="A", skill=1.0)])
        assert standings_skill_correlation(t) == 0.0

    def test_positive_for_skill_based_simulation(self, tournament_factory):
        """Skill-based matches should produce positive standings-skill correlation."""
        corr = standings_skill_correlation(tournament_factory(16, 5, "adjacent", 7))
        assert corr > 0.0

    def test_perfect_correlation_known_case(self, match_factory):
        """When player 1 (skill=2) always beats player 2 (skill=-2),
        the single-match standings perfectly reflect skill order."""
        p1 = Player(pid=1, name="Strong", skill=2.0)
        p2 = Player(pid=2, name="Weak", skill=-2.0)
        t = Tournament(players=[p1, p2])
        t.rounds.append(Round(number=1, matches=[match_factory(1, 2, a_wins=True)]))
        corr = standings_skill_correlation(t)
        assert corr == pytest.approx(1.0)
