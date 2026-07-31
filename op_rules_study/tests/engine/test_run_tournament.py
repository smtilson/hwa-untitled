"""Unit tests for tournament.engine.run_tournament."""
from __future__ import annotations

from random import Random

from tournament.engine import run_tournament
from tournament.generators import make_players, random_match
from tournament.pairing import get as get_pairing
from tournament.standings import compute_records


class TestRunTournament:
    def _players(self, n: int = 8, seed: int = 0) -> list:
        return make_players(n, Random(seed))

    def test_returns_tournament_with_correct_rounds(self):
        players = self._players()
        tour = run_tournament(players, n_rounds=3, pairing=get_pairing("adjacent"), rng=Random(1))
        assert len(tour.rounds) == 3

    def test_each_round_has_correct_match_count(self):
        players = self._players(8)
        tour = run_tournament(players, n_rounds=4, pairing=get_pairing("fold"), rng=Random(2))
        for rnd in tour.rounds:
            assert len(rnd.matches) == 4

    def test_each_player_appears_once_per_round(self):
        players = self._players(8)
        tour = run_tournament(players, n_rounds=3, pairing=get_pairing("adjacent"), rng=Random(3))
        for rnd in tour.rounds:
            seen = set()
            for m in rnd.matches:
                assert m.player_a not in seen and m.player_b not in seen
                seen.update([m.player_a, m.player_b])
            assert seen == {p.pid for p in players}

    def test_round_numbers_are_sequential(self):
        players = self._players()
        tour = run_tournament(players, n_rounds=4, pairing=get_pairing("random"), rng=Random(4))
        assert [r.number for r in tour.rounds] == [1, 2, 3, 4]

    def test_list_pairing_spec_accepted(self):
        players = self._players()
        spec = [get_pairing("random"), get_pairing("adjacent"), get_pairing("fold")]
        tour = run_tournament(players, n_rounds=3, pairing=spec, rng=Random(5))
        assert len(tour.rounds) == 3

    def test_dict_pairing_spec_accepted(self):
        players = self._players()
        spec = {1: get_pairing("random"), 2: get_pairing("adjacent")}
        tour = run_tournament(players, n_rounds=4, pairing=spec, rng=Random(6))
        assert len(tour.rounds) == 4

    def test_custom_match_model_used(self):
        """random_match should also produce valid matches."""
        players = self._players()
        tour = run_tournament(players, n_rounds=2, pairing=get_pairing("adjacent"),
                              rng=Random(7), match_model=random_match)
        for rnd in tour.rounds:
            for m in rnd.matches:
                valid, msg = m.is_valid
                assert valid, msg

    def test_records_consistent_with_round_count(self):
        players = self._players(8)
        n_rounds = 4
        tour = run_tournament(players, n_rounds=n_rounds, pairing=get_pairing("fold"), rng=Random(8))
        recs = compute_records(tour)
        for rec in recs.values():
            assert rec.matches_played == n_rounds

    def test_all_strategies_run_without_error(self):
        players = self._players(8)
        for name in ("adjacent", "fold", "strong_weak", "random_within_record", "random"):
            tour = run_tournament(players, n_rounds=3, pairing=get_pairing(name), rng=Random(9))
            assert len(tour.rounds) == 3
