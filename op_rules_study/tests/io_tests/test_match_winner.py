"""Unit tests for tournament.io._match_winner."""
from __future__ import annotations

from tournament.io import _match_winner
from tournament.models import Game, Match


class TestMatchWinner:
    def test_returns_player_id_for_win(self, match_factory):
        m = match_factory(1, 2, a_wins=True)
        assert _match_winner(m) == 1

    def test_returns_empty_string_for_draw(self):
        draw = Match(player_a=1, player_b=2, games=[Game(3, 2), Game(2, 3)])
        assert _match_winner(draw) == ""
