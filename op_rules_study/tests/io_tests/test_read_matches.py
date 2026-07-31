"""Unit tests for tournament.io.read_matches (round-trip)."""
from __future__ import annotations

import tempfile
from pathlib import Path

from tournament.io import read_matches, write_matches


class TestReadMatches:
    def test_round_trip_round_count(self, small_tournament):
        players, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "matches.csv"
            write_matches(tour, p)
            tour2 = read_matches(p, players)
        assert len(tour2.rounds) == len(tour.rounds)

    def test_round_trip_match_count(self, small_tournament):
        players, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "matches.csv"
            write_matches(tour, p)
            tour2 = read_matches(p, players)
        orig_matches = sum(len(r.matches) for r in tour.rounds)
        rest_matches = sum(len(r.matches) for r in tour2.rounds)
        assert orig_matches == rest_matches

    def test_round_trip_bonus_agents_preserved(self, small_tournament):
        players, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "matches.csv"
            write_matches(tour, p)
            tour2 = read_matches(p, players)
        for rnd_orig, rnd_rest in zip(tour.rounds, tour2.rounds):
            for m_orig, m_rest in zip(rnd_orig.matches, rnd_rest.matches):
                assert m_orig.total_agents_a == m_rest.total_agents_a
                assert m_orig.total_agents_b == m_rest.total_agents_b

    def test_round_trip_player_ids_preserved(self, small_tournament):
        players, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "matches.csv"
            write_matches(tour, p)
            tour2 = read_matches(p, players)
        for rnd_orig, rnd_rest in zip(tour.rounds, tour2.rounds):
            pairs_orig = {(m.player_a, m.player_b) for m in rnd_orig.matches}
            pairs_rest = {(m.player_a, m.player_b) for m in rnd_rest.matches}
            assert pairs_orig == pairs_rest

    def test_restored_matches_are_valid(self, small_tournament):
        players, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "matches.csv"
            write_matches(tour, p)
            tour2 = read_matches(p, players)
        for rnd in tour2.rounds:
            for m in rnd.matches:
                valid, msg = m.is_valid
                assert valid, msg
