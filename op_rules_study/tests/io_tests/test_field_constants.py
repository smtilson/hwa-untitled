"""Unit tests for tournament.io.MATCH_FIELDS and STANDINGS_FIELDS."""
from __future__ import annotations

from tournament.io import MATCH_FIELDS, STANDINGS_FIELDS


class TestFieldConstants:
    def test_match_fields_are_list(self):
        assert isinstance(MATCH_FIELDS, list)
        assert len(MATCH_FIELDS) > 0

    def test_match_fields_contain_required_columns(self):
        for col in (
            "round",
            "player_a",
            "player_b",
            "bonus_agents_a",
            "bonus_agents_b",
            "winner",
            "is_draw",
        ):
            assert col in MATCH_FIELDS, f"missing column: {col}"

    def test_standings_fields_are_list(self):
        assert isinstance(STANDINGS_FIELDS, list)
        assert len(STANDINGS_FIELDS) > 0

    def test_standings_fields_contain_required_columns(self):
        for col in ("through_round", "pid", "game_wins", "game_losses", "agent_diff"):
            assert col in STANDINGS_FIELDS, f"missing column: {col}"
