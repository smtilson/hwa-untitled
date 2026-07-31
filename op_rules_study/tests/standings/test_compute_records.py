"""Unit tests for tournament.standings.compute_records."""

from __future__ import annotations

from tournament.standings import compute_records
from tournament.models import Player, Tournament


class TestComputeRecords:
    def test_returns_all_players(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        assert set(recs.keys()) == {1, 2, 3, 4}

    def test_match_count_after_all_rounds(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        for r in recs.values():
            assert r.matches_played == 2

    def test_winner_has_more_game_wins(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        # Player 1 wins round 1 (2-0) and draws round 2 (1-1) = 3 wins total
        assert recs[1].wins == 3

    def test_through_round_limits_data(self, simple_tournament):
        t = simple_tournament()
        recs_r1 = compute_records(t, through_round=1)
        assert recs_r1[1].matches_played == 1

    def test_empty_tournament_all_zero(self):
        players = [Player(pid=1, name="A"), Player(pid=2, name="B")]
        t = Tournament(players=players)
        recs = compute_records(t)
        assert recs[1].wins == 0 and recs[1].losses == 0

    def test_attaches_player_to_records(self, simple_tournament):
        t = simple_tournament()
        recs = compute_records(t)
        for p in t.players:
            rec = recs[p.pid]
            assert rec.player is p
            assert rec.name == p.name
            assert rec.skill == p.skill
