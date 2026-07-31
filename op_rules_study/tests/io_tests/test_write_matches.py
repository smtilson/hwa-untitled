"""Unit tests for tournament.io.write_matches."""
from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from tournament.io import MATCH_FIELDS, write_matches


class TestWriteMatches:
    def test_creates_file(self, small_tournament):
        _, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "matches.csv"
            write_matches(tour, p)
            assert p.exists()

    def test_header_matches_fields(self, small_tournament):
        _, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "matches.csv"
            write_matches(tour, p)
            with p.open() as f:
                header = next(csv.reader(f))
            assert header == MATCH_FIELDS

    def test_row_count_equals_total_matches(self, small_tournament):
        _, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "matches.csv"
            write_matches(tour, p)
            total = sum(len(r.matches) for r in tour.rounds)
            with p.open() as f:
                rows = list(csv.DictReader(f))
            assert len(rows) == total

    def test_bonus_agents_stored(self, small_tournament):
        """Bonus agents (from tie-breaks) must appear in the CSV."""
        _, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "matches.csv"
            write_matches(tour, p)
            with p.open() as f:
                rows = list(csv.DictReader(f))
            assert all("bonus_agents_a" in row for row in rows)

    def test_creates_parent_directories(self, small_tournament):
        _, tour = small_tournament()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sub" / "dir" / "matches.csv"
            write_matches(tour, p)
            assert p.exists()
