"""Unit tests for tournament.io.write_standings."""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from tournament.io import STANDINGS_FIELDS, write_standings


class TestWriteStandings:
    def test_creates_file(self, small_tournament):
        _, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "standings.csv"
            write_standings(tour, p)
            assert p.exists()

    def test_every_round_true_emits_snapshot_per_round(self, small_tournament):
        _, tour = small_tournament()
        n_players = len(tour.players)
        n_rounds = len(tour.rounds)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "standings.csv"
            write_standings(tour, p, every_round=True)
            with p.open() as f:
                rows = list(csv.DictReader(f))
            assert len(rows) == n_players * n_rounds

    def test_every_round_false_emits_only_final(self, small_tournament):
        _, tour = small_tournament()
        n_players = len(tour.players)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "final.csv"
            write_standings(tour, p, every_round=False)
            with p.open() as f:
                rows = list(csv.DictReader(f))
            assert len(rows) == n_players

    def test_header_matches_fields(self, small_tournament):
        _, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "standings.csv"
            write_standings(tour, p)
            with p.open() as f:
                header = next(csv.reader(f))
            assert header == STANDINGS_FIELDS
