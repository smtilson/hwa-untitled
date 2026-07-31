"""Unit tests for tournament.pairing.PairingContext."""
from __future__ import annotations


class TestPairingContext:
    def test_stores_past_opponents(self, pairing_context_factory):
        ctx = pairing_context_factory([1, 2, 3], round_number=2)
        ctx.past_opponents[1] = {2, 3}
        assert ctx.past_opponents[1] == {2, 3}

    def test_stores_round_number(self, pairing_context_factory):
        ctx = pairing_context_factory([], round_number=5)
        assert ctx.round_number == 5
