"""Sanity tests for the tournament simulation.

Run with: python -m pytest tests/   (from the module directory)
"""

from __future__ import annotations

import sys
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tournament import (  # noqa: E402
    AGENTS_TO_WIN,
    REGISTRY,
    get_pairing,
    make_players,
    run_tournament,
    summary,
)
from tournament.generators import skill_game, skilled_match  # noqa: E402
from tournament.standings import compute_records  # noqa: E402


def test_game_always_has_a_winner_with_three_agents():
    rng = Random(1)
    for _ in range(200):
        g = skill_game(60, 40, rng)
        assert max(g.agents_a, g.agents_b) == AGENTS_TO_WIN
        assert g.agents_a != g.agents_b


def test_match_is_two_games_with_consistent_outcome():
    rng = Random(2)
    players = make_players(2, rng)
    pids = {players[0].pid, players[1].pid}
    for _ in range(200):
        m = skilled_match(players[0], players[1], rng)
        valid, msg = m.is_valid
        assert valid, msg
        assert len(m.games) == 2
        # A match either has a clear winner (2-0) or is a 1-1 draw.
        if m.is_draw:
            assert m.game_1_winner != m.game_2_winner
        else:
            assert m.game_1_winner == m.game_2_winner
            assert m.game_1_winner in pids
        # The bonus-agent tie-break ensures the agent score is never tied.
        assert m.total_agents_a != m.total_agents_b


def test_each_player_plays_once_per_round():
    rng = Random(3)
    players = make_players(16, rng)
    tour = run_tournament(players, n_rounds=4, pairing=get_pairing("adjacent"), rng=rng)
    for rnd in tour.rounds:
        seen: set[int] = set()
        for m in rnd.matches:
            assert m.player_a not in seen
            assert m.player_b not in seen
            seen.add(m.player_a)
            seen.add(m.player_b)
        assert len([p for p in players if p.pid in seen]) == len(players)


def test_records_match_count_consistent():
    rng = Random(4)
    players = make_players(16, rng)
    tour = run_tournament(players, n_rounds=5, pairing=get_pairing("fold"), rng=rng)
    recs = compute_records(tour)
    for rec in recs.values():
        assert rec.matches_played == 5


def test_all_registered_algorithms_run():
    for name in REGISTRY:
        rng = Random(5)
        players = make_players(12, rng)
        tour = run_tournament(players, n_rounds=3, pairing=get_pairing(name), rng=rng)
        s = summary(tour)
        assert s["rounds"] == 3
        assert s["players"] == 12


def test_per_round_schedule():
    rng = Random(6)
    players = make_players(8, rng)
    schedule = [get_pairing("random"), get_pairing("adjacent"), get_pairing("fold")]
    tour = run_tournament(players, n_rounds=3, pairing=schedule, rng=rng)
    assert len(tour.rounds) == 3
