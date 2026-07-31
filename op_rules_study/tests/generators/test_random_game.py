"""Unit tests for tournament.generators.random_game."""
from __future__ import annotations

from random import Random

import pytest

from tournament.generators import random_game
from tournament.models import AGENTS_TO_WIN


class TestRandomGame:
    def test_always_produces_winner(self):
        rng = Random(10)
        for _ in range(200):
            g = random_game(rng)
            assert max(g.agents_a, g.agents_b) == AGENTS_TO_WIN

    def test_no_tied_agents(self):
        rng = Random(11)
        for _ in range(200):
            g = random_game(rng)
            assert g.agents_a != g.agents_b

    def test_game_is_valid(self):
        valid, msg = random_game(Random(0)).is_valid
        assert valid, msg
