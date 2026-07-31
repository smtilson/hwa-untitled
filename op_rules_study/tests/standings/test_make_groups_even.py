"""Unit tests for tournament.standings.make_groups_even."""

from __future__ import annotations

import pytest

from tournament.models import Player
from tournament.standings import Record, make_groups_even


class TestMakeGroupsEven:
    def _groups_from_records(self, size_map: dict[str, int]) -> dict[str, list[Record]]:
        """Build artificial groups for testing."""
        counter = [0]
        result = {}
        for key, n in size_map.items():
            recs = []
            for _ in range(n):
                counter[0] += 1
                recs.append(
                    Record(
                        player=Player(pid=counter[0], name=f"P{counter[0]}", skill=0.0)
                    )
                )
            result[key] = recs
        return result

    def test_all_even_groups_unchanged_size(self):
        groups = self._groups_from_records({"4-0": 4, "2-2": 4})
        even = make_groups_even(groups)
        for v in even.values():
            assert len(v) % 2 == 0

    def test_odd_total_raises(self):
        groups = self._groups_from_records({"3-3": 3, "4-2": 4})
        with pytest.raises(ValueError):
            make_groups_even(groups)

    def test_odd_group_carries_player_to_next_group(self):
        groups = self._groups_from_records({"4-2": 3, "2-4": 3})
        original_pids = {rec.pid for recs in groups.values() for rec in recs}
        even = make_groups_even(groups)
        output_pids = {rec.pid for recs in even.values() for rec in recs}
        assert output_pids == original_pids

    def test_all_output_groups_are_even(self):
        groups = self._groups_from_records({"2-4": 3, "4-2": 3, "6-0": 2})
        even = make_groups_even(groups)
        for k, v in even.items():
            assert len(v) % 2 == 0, f"Group {k} has odd size {len(v)}"

    def test_keys_have_tilde_appended(self):
        groups = self._groups_from_records({"4-0": 2})
        even = make_groups_even(groups)
        for k in even:
            assert k.endswith("~")
