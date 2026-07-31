"""Unit tests for tournament.generators.score_agent_probability."""
from __future__ import annotations

import pytest

from tournament.generators import score_agent_probability


class TestScoreAgentProbability:
    def test_equal_skills_returns_half(self):
        assert score_agent_probability(0.0, 0.0) == pytest.approx(0.5)

    def test_a_stronger_returns_above_half(self):
        assert score_agent_probability(1.0, 0.0) > 0.5

    def test_b_stronger_returns_below_half(self):
        assert score_agent_probability(0.0, 1.0) < 0.5

    def test_return_value_in_unit_interval(self):
        for sa, sb in [(2.0, -2.0), (-2.0, 2.0), (0.0, 0.0), (5.0, 5.0)]:
            p = score_agent_probability(sa, sb)
            assert 0.0 < p < 1.0

    def test_symmetric(self):
        p = score_agent_probability(1.0, 0.0)
        q = score_agent_probability(0.0, 1.0)
        assert p + q == pytest.approx(1.0)
