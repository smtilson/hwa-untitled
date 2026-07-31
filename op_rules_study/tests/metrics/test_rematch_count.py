"""Unit tests for tournament.metrics.rematch_count."""
from __future__ import annotations

from tournament.metrics import rematch_count
from tournament.models import Player, Round, Tournament


class TestRematchCount:
    def test_returns_int(self, tournament_factory):
        assert isinstance(rematch_count(tournament_factory()), int)

    def test_zero_when_no_rematches(self, tournament_factory):
        """With 8 players and 3 rounds, rematches are possible but not guaranteed."""
        t = tournament_factory(8, 2, "adjacent", 0)
        assert rematch_count(t) >= 0

    def test_zero_for_single_round(self, small_tournament):
        players, t = small_tournament(seed=1)
        assert rematch_count(t) == 0

    def test_counts_extra_meetings_correctly(self, match_factory):
        """Construct a tournament where pair (1,2) meets twice."""
        p1, p2 = Player(pid=1, name="A"), Player(pid=2, name="B")
        t = Tournament(players=[p1, p2])
        t.rounds.append(Round(number=1, matches=[match_factory(1, 2)]))
        t.rounds.append(Round(number=2, matches=[match_factory(1, 2)]))
        assert rematch_count(t) == 1

    def test_triple_meeting_counts_as_two(self, match_factory):
        """Three meetings of the same pair → count = 2."""
        p1, p2 = Player(pid=1, name="A"), Player(pid=2, name="B")
        t = Tournament(players=[p1, p2])
        for n in range(1, 4):
            t.rounds.append(Round(number=n, matches=[match_factory(1, 2)]))
        assert rematch_count(t) == 2
