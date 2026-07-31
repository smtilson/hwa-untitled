"""Unit tests for tournament.pairing.make_record_group_pairing."""

from __future__ import annotations

from random import Random

import pytest

from tournament.pairing import make_record_group_pairing
from tournament.standings import compute_records


class TestMakeRecordGroupPairing:
    def test_returns_callable(self):
        fn = make_record_group_pairing("adjacent")
        assert callable(fn)

    def test_unknown_strategy_raises(self):
        with pytest.raises(ValueError):
            make_record_group_pairing("nonexistent")

    def test_correct_number_of_pairs(self, small_tournament, pairing_context_factory):
        players, t = small_tournament()
        records = compute_records(t)
        ctx = pairing_context_factory([p.pid for p in players], round_number=2)
        fn = make_record_group_pairing("adjacent")
        pairs = fn(records, Random(0), ctx)
        assert len(pairs) == len(players) // 2

    def test_all_players_paired(self, small_tournament, pairing_context_factory):
        players, t = small_tournament()
        records = compute_records(t)
        ctx = pairing_context_factory([p.pid for p in players], round_number=2)
        fn = make_record_group_pairing("fold")
        pairs = fn(records, Random(0), ctx)
        pids_in_pairs = {pid for pair in pairs for pid in pair}
        assert pids_in_pairs == {p.pid for p in players}

    def test_no_player_paired_with_themselves(
        self, small_tournament, pairing_context_factory
    ):
        players, t = small_tournament()
        records = compute_records(t)
        ctx = pairing_context_factory([p.pid for p in players], round_number=2)
        fn = make_record_group_pairing("strong_weak")
        for a, b in fn(records, Random(0), ctx):
            assert a != b

    def test_fn_name_reflects_strategy(self):
        fn = make_record_group_pairing("fold")
        assert "fold" in fn.__name__

    def test_custom_rating_fn_accepted(self):
        fn = make_record_group_pairing(
            "adjacent", rating_fn=lambda seq: sum(f for f, _ in seq)
        )
        assert callable(fn)
