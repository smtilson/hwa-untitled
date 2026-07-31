"""Unit tests for tournament.standings.make_rank_key."""
from __future__ import annotations

import pytest

from tournament.standings import agent_differential, make_rank_key


class TestMakeRankKey:
    def test_returns_callable(self):
        assert callable(make_rank_key())

    def test_default_uses_agent_differential(self, record_factory):
        r = record_factory([(2, 0, 6, 3)])  # diff = 3
        assert make_rank_key()(r) == pytest.approx(3.0)

    def test_custom_metric_used(self, record_factory):
        r = record_factory([(2, 0, 6, 3)])
        key = make_rank_key(rating_fn=lambda seq: sum(f for f, _ in seq))
        assert key(r) == pytest.approx(6.0)

    def test_none_falls_back_to_default(self, record_factory):
        key_default = make_rank_key(None)
        key_explicit = make_rank_key(agent_differential)
        r = record_factory([(2, 0, 10, 4), (0, 2, 2, 8)])
        assert key_default(r) == key_explicit(r)

    def test_sorting_order_best_first(self, record_factory):
        r_high = record_factory([(2, 0, 10, 2)], pid=1)
        r_low = record_factory([(2, 0, 3, 8)], pid=2)
        key = make_rank_key()
        assert key(r_high) > key(r_low)
