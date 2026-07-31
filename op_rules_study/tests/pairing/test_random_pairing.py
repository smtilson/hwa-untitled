"""Unit tests for tournament.pairing.random_pairing."""
from __future__ import annotations

from random import Random

from tournament.pairing import random_pairing
from tournament.standings import compute_records


class TestRandomPairing:
    def test_correct_pair_count(self, small_tournament, pairing_context_factory):
        players, t = small_tournament()
        records = compute_records(t)
        ctx = pairing_context_factory([p.pid for p in players])
        pairs = random_pairing(records, Random(0), ctx)
        assert len(pairs) == 4

    def test_all_players_appear_once(self, small_tournament, pairing_context_factory):
        players, t = small_tournament()
        records = compute_records(t)
        ctx = pairing_context_factory([p.pid for p in players])
        pairs = random_pairing(records, Random(42), ctx)
        flat = [pid for pair in pairs for pid in pair]
        assert len(flat) == len(set(flat))

    def test_no_self_pairing(self, small_tournament, pairing_context_factory):
        players, t = small_tournament()
        records = compute_records(t)
        ctx = pairing_context_factory([p.pid for p in players])
        for a, b in random_pairing(records, Random(0), ctx):
            assert a != b
