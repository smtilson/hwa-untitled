"""Unit tests for tournament.standings.agent_differential."""
from __future__ import annotations

from tournament.standings import agent_differential


class TestAgentDifferential:
    def test_positive_diff(self):
        assert agent_differential([(6, 3), (5, 2)]) == 6

    def test_negative_diff(self):
        assert agent_differential([(2, 5)]) == -3

    def test_empty_sequence(self):
        assert agent_differential([]) == 0

    def test_symmetric(self):
        assert agent_differential([(3, 3)]) == 0
