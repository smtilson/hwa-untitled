"""Unit tests for tournament.pairing._ordered_ids."""
from __future__ import annotations

from tournament.pairing import _ordered_ids


class TestOrderedIds:
    def test_returns_all_pids(self, records_factory):
        records = records_factory(4)
        ids = _ordered_ids(records)
        assert set(ids) == {0, 1, 2, 3}

    def test_higher_agent_diff_first(self, records_factory):
        records = records_factory(2)
        records[0].agents_for = 10
        records[0].agents_against = 2
        records[0]._raw_results = [{"player_agents": 10, "opponent_agents": 2}]
        records[0]._agent_seq = []
        records[1].agents_for = 3
        records[1].agents_against = 8
        records[1]._raw_results = [{"player_agents": 3, "opponent_agents": 8}]
        records[1]._agent_seq = []
        ids = _ordered_ids(records)
        assert ids[0] == 0  # higher differential first
