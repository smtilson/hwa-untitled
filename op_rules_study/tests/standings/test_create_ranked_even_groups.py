"""Unit tests for tournament.standings.create_ranked_even_groups."""
from __future__ import annotations

from tournament.standings import agent_differential, compute_records, create_ranked_even_groups


class TestCreateRankedEvenGroups:
    def test_returns_dict(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        result = create_ranked_even_groups(recs)
        assert isinstance(result, dict)

    def test_all_output_groups_are_even(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        result = create_ranked_even_groups(recs)
        for k, v in result.items():
            assert len(v) % 2 == 0, f"Group {k} has odd size {len(v)}"

    def test_accepts_custom_rating_fn(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        result = create_ranked_even_groups(recs, rating_fn=agent_differential)
        assert isinstance(result, dict)
