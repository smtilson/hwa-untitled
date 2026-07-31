"""Unit tests for tournament.models.Round."""
from __future__ import annotations

import pytest

from tournament.models import Game, Match, Round


class TestRound:
    def _make_round(self, a_wins_match_factory, b_wins_match_factory) -> Round:
        return Round(number=1, matches=[a_wins_match_factory(1, 2), b_wins_match_factory(3, 4)])

    def test_is_valid_true(self, a_wins_match_factory, b_wins_match_factory):
        valid, msg = self._make_round(a_wins_match_factory, b_wins_match_factory).is_valid
        assert valid, msg

    def test_is_valid_propagates_bad_match(self):
        bad = Match(player_a=1, player_b=1, games=[Game(3, 1), Game(3, 2)])
        rnd = Round(number=1, matches=[bad])
        valid, _ = rnd.is_valid
        assert not valid

    def test_opponents_returns_full_map(self, a_wins_match_factory, b_wins_match_factory):
        opp = self._make_round(a_wins_match_factory, b_wins_match_factory).opponents()
        assert opp[1] == 2 and opp[3] == 4

    def test_player_results_winner(self, a_wins_match_factory, b_wins_match_factory):
        res = self._make_round(a_wins_match_factory, b_wins_match_factory).player_results(1)
        assert res["wins"] == 2
        assert res["opponent"] == 2

    def test_overall_results_round_number(self, a_wins_match_factory, b_wins_match_factory):
        assert self._make_round(a_wins_match_factory, b_wins_match_factory).overall_results["round"] == 1

    def test_overall_results_all_pids_present(self, a_wins_match_factory, b_wins_match_factory):
        ov = self._make_round(a_wins_match_factory, b_wins_match_factory).overall_results["matches"]
        assert set(ov.keys()) == {1, 2, 3, 4}
