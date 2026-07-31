"""Unit tests for tournament.models.Tournament."""
from __future__ import annotations

import pytest

from tournament.models import Player, Round, Tournament


class TestTournament:
    def _make_tournament(self, a_wins_match_factory, b_wins_match_factory, draw_match_factory) -> Tournament:
        players = [Player(pid=i, name=f"P{i}") for i in range(1, 5)]
        t = Tournament(players=players)
        t.rounds.append(
            Round(number=1, matches=[a_wins_match_factory(1, 2), b_wins_match_factory(3, 4)])
        )
        t.rounds.append(
            Round(number=2, matches=[draw_match_factory(1, 3), a_wins_match_factory(2, 4)])
        )
        return t

    def test_player_ids(self, a_wins_match_factory, b_wins_match_factory, draw_match_factory):
        t = self._make_tournament(a_wins_match_factory, b_wins_match_factory, draw_match_factory)
        assert set(t.player_ids) == {1, 2, 3, 4}

    def test_player_by_id_found(self, a_wins_match_factory, b_wins_match_factory, draw_match_factory):
        t = self._make_tournament(a_wins_match_factory, b_wins_match_factory, draw_match_factory)
        p = t.player_by_id(3)
        assert p is not None and p.pid == 3

    def test_player_by_id_missing(self, a_wins_match_factory, b_wins_match_factory, draw_match_factory):
        assert self._make_tournament(a_wins_match_factory, b_wins_match_factory, draw_match_factory).player_by_id(99) is None

    def test_past_opponents_after_two_rounds(self, a_wins_match_factory, b_wins_match_factory, draw_match_factory):
        t = self._make_tournament(a_wins_match_factory, b_wins_match_factory, draw_match_factory)
        assert t.past_opponents(1) == {2, 3}

    def test_past_opponents_empty_before_rounds(self):
        t = Tournament(players=[Player(pid=1, name="A")])
        assert t.past_opponents(1) == set()

    def test_assign_algorithm(self):
        t = Tournament(players=[])

        def fn(r, rng, ctx):
            return []

        t.assign_algorithm(fn)
        assert t._algorithm is fn
