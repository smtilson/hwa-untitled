"""Unit tests for tournament.standings.sort_groups."""
from __future__ import annotations

from tournament.standings import compute_records, group_by_record, sort_groups


class TestSortGroups:
    def test_within_group_sorted_best_first(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        groups = group_by_record(recs)
        sorted_g = sort_groups(groups)
        for recs_in_group in sorted_g.values():
            diffs = [r.agent_diff for r in recs_in_group]
            assert diffs == sorted(diffs, reverse=True)

    def test_custom_metric_applied(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        groups = group_by_record(recs)
        sorted_g = sort_groups(groups, rating_fn=lambda seq: sum(f for f, _ in seq))
        for recs_in_group in sorted_g.values():
            scores = [r.agents_for for r in recs_in_group]
            assert scores == sorted(scores, reverse=True)

    def test_keys_unchanged(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        groups = group_by_record(recs)
        assert list(sort_groups(groups).keys()) == list(groups.keys())
