"""Unit tests for tournament.standings.group_by_record."""
from __future__ import annotations

from tournament.standings import compute_records, group_by_record


class TestGroupByRecord:
    def test_groups_by_game_wins_losses(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        groups = group_by_record(recs)
        # All keys should be in "wins-losses" format
        for key in groups:
            parts = key.split("-")
            assert len(parts) == 2
            assert parts[0].isdigit() and parts[1].isdigit()

    def test_best_group_first(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        groups = group_by_record(recs)
        keys = list(groups.keys())
        # First key should have highest wins
        first_wins = int(keys[0].split("-")[0])
        last_wins = int(keys[-1].split("-")[0])
        assert first_wins >= last_wins

    def test_all_players_present(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        groups = group_by_record(recs)
        pids = {r.pid for recs_in_group in groups.values() for r in recs_in_group}
        assert pids == {1, 2, 3, 4}
