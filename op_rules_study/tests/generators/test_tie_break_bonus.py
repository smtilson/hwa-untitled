"""Unit tests for tournament.generators._tie_break_bonus."""
from __future__ import annotations

from random import Random

import pytest

from tournament.generators import _tie_break_bonus, score_agent_probability
from tournament.models import Game


class TestTieBreakBonus:
    def _games_tied(self):
        return [Game(3, 2), Game(2, 3)]   # 5-5 total

    def _games_untied(self):
        return [Game(3, 1), Game(3, 2)]   # 6-3 total

    def test_no_tie_returns_zero_zero(self):
        assert _tie_break_bonus(self._games_untied(), Random(0)) == (0, 0)

    def test_tied_returns_one_bonus_total(self):
        result = _tie_break_bonus(self._games_tied(), Random(1))
        assert sum(result) == 1

    def test_prob_one_always_awards_a(self):
        for seed in range(20):
            assert _tie_break_bonus(self._games_tied(), Random(seed), score_agent_prob=1.0) == (1, 0)

    def test_prob_zero_always_awards_b(self):
        for seed in range(20):
            assert _tie_break_bonus(self._games_tied(), Random(seed), score_agent_prob=0.0) == (0, 1)
