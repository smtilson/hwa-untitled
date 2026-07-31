"""Unit tests for tournament.pairing._avoid_rematches."""
from __future__ import annotations

from tournament.pairing import _avoid_rematches


class TestAvoidRematches:
    def test_no_rematches_unchanged(self, pairing_context_factory):
        order = [0, 1, 2, 3]
        ctx = pairing_context_factory(order, round_number=2)
        assert _avoid_rematches(order, ctx) == order

    def test_rematch_swapped(self, pairing_context_factory):
        # 0 and 1 have already played; 2 is available as a swap
        ctx = pairing_context_factory([0, 1, 2, 3], round_number=2)
        ctx.past_opponents[0] = {1}
        ctx.past_opponents[1] = {0}
        result = _avoid_rematches([0, 1, 2, 3], ctx)
        # After fix-up, 0 should NOT be paired with 1 at index 0,1
        assert result[1] != 1 or result[0] != 0

    def test_returns_same_length(self, pairing_context_factory):
        order = [0, 1, 2, 3, 4, 5]
        ctx = pairing_context_factory(order)
        assert len(_avoid_rematches(order, ctx)) == 6

    def test_does_not_mutate_input(self, pairing_context_factory):
        original = [0, 1, 2, 3]
        ctx = pairing_context_factory(original)
        _avoid_rematches(original, ctx)
        assert original == [0, 1, 2, 3]
