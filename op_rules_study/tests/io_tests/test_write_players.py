"""Unit tests for tournament.io.write_players."""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from tournament.io import write_players


class TestWritePlayers:
    def test_creates_file(self, small_tournament):
        _, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "players.csv"
            write_players(tour, p)
            assert p.exists()

    def test_row_count_equals_player_count(self, small_tournament):
        _, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "players.csv"
            write_players(tour, p)
            with p.open() as f:
                rows = list(csv.reader(f))
            assert len(rows) - 1 == len(tour.players)  # -1 for header

    def test_header_contains_skill(self, small_tournament):
        _, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "players.csv"
            write_players(tour, p)
            with p.open() as f:
                header = next(csv.reader(f))
            assert "skill" in header
