"""Unit tests for tournament.models.Game."""
from __future__ import annotations

import pytest

from tournament.models import AGENTS_TO_WIN, Game


class TestGame:
    def test_valid_a_wins(self):
        g = Game(agents_a=3, agents_b=1)
        valid, msg = g.is_valid
        assert valid
        assert msg == ""

    def test_valid_b_wins(self):
        g = Game(agents_a=0, agents_b=3)
        valid, _ = g.is_valid
        assert valid

    def test_invalid_a_exceeds_max(self):
        g = Game(agents_a=4, agents_b=1)
        valid, msg = g.is_valid
        assert not valid
        assert "A" in msg

    def test_invalid_b_exceeds_max(self):
        g = Game(agents_a=1, agents_b=4)
        valid, msg = g.is_valid
        assert not valid
        assert "B" in msg

    def test_invalid_tie(self):
        g = Game(agents_a=2, agents_b=2)
        valid, _ = g.is_valid
        assert not valid

    def test_winner_is_a_true(self):
        assert Game(agents_a=3, agents_b=2).winner_is_a is True

    def test_winner_is_a_false(self):
        assert Game(agents_a=0, agents_b=3).winner_is_a is False

    def test_winner_is_a_raises_on_invalid(self):
        g = Game(agents_a=2, agents_b=2)
        with pytest.raises(Exception):
            _ = g.winner_is_a

    def test_agents_to_win_constant(self):
        assert AGENTS_TO_WIN == 3
