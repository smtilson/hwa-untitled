"""Unit tests for tournament.metrics.summary."""
from __future__ import annotations

import pytest

from tournament.metrics import mean_skill_gap, rematch_count, standings_skill_correlation, summary


class TestSummary:
    def test_returns_dict(self, tournament_factory):
        assert isinstance(summary(tournament_factory()), dict)

    def test_contains_expected_keys(self, tournament_factory):
        s = summary(tournament_factory())
        for key in (
            "mean_skill_gap",
            "standings_skill_correlation",
            "rematch_count",
            "rounds",
            "players",
        ):
            assert key in s, f"missing key: {key}"

    def test_rounds_matches_actual_rounds(self, tournament_factory):
        t = tournament_factory(8, 4)
        assert summary(t)["rounds"] == 4.0

    def test_players_matches_player_count(self, tournament_factory):
        t = tournament_factory(16, 3)
        assert summary(t)["players"] == 16.0

    def test_values_consistent_with_individual_functions(self, tournament_factory):
        t = tournament_factory(8, 3, "fold", 99)
        s = summary(t)
        assert s["mean_skill_gap"] == pytest.approx(mean_skill_gap(t))
        assert s["standings_skill_correlation"] == pytest.approx(
            standings_skill_correlation(t)
        )
        assert s["rematch_count"] == float(rematch_count(t))
