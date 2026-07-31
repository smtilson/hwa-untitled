"""Unit tests for tournament.models.Player."""
from __future__ import annotations

import pytest

from tournament.models import Player


class TestPlayer:
    def test_fields_stored(self):
        p = Player(pid=7, name="Alice", skill=1.5)
        assert p.pid == 7
        assert p.name == "Alice"
        assert p.skill == 1.5

    def test_default_skill_is_zero(self):
        p = Player(pid=0, name="Bob")
        assert p.skill == 0.0

    def test_frozen_raises_on_mutation(self):
        p = Player(pid=1, name="Alice")
        with pytest.raises((AttributeError, TypeError)):
            p.skill = 9.9  # type: ignore[misc]

    def test_different_pids_are_not_equal(self):
        assert Player(pid=1, name="A") != Player(pid=2, name="A")
