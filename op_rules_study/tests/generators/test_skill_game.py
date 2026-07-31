"""Unit tests for tournament.generators.skill_game."""
from __future__ import annotations

from random import Random

import pytest

from tournament.generators import skill_game
from tournament.models import AGENTS_TO_WIN


class TestSkillGame:
    def test_always_produces_a_winner(self):
        rng = Random(1)
        for _ in range(200):
            g = skill_game(0.5, -0.5, rng)
            assert max(g.agents_a, g.agents_b) == AGENTS_TO_WIN

    def test_no_tied_agents(self):
        rng = Random(2)
        for _ in range(200):
            g = skill_game(0.0, 0.0, rng)
            assert g.agents_a != g.agents_b

    def test_game_is_valid(self):
        g = skill_game(1.0, -1.0, Random(3))
        valid, msg = g.is_valid
        assert valid, msg

    def test_strong_player_wins_more_often(self):
        rng = Random(42)
        a_wins = sum(1 for _ in range(500) if skill_game(2.0, -2.0, rng).winner_is_a)
        assert a_wins > 350   # heavily favoured
