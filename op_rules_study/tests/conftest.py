"""Shared pytest configuration: make the package importable from tests/."""

from __future__ import annotations

import sys
from pathlib import Path
from random import Random

import pytest

from tournament.models import Game, Match, Player, Round, Tournament
from tournament.engine import run_tournament
from tournament.generators import make_players
from tournament.pairing import get as get_pairing
from tournament.standings import Record

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------------------------------------------------------------------
# Common fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def match_factory():
    """Factory for creating simple matches."""

    def _match(a: int, b: int, a_wins: bool = True) -> Match:
        if a_wins:
            return Match(player_a=a, player_b=b, games=[Game(3, 1), Game(3, 2)])
        return Match(player_a=a, player_b=b, games=[Game(1, 3), Game(2, 3)])

    return _match


@pytest.fixture
def simple_tournament():
    """Factory for creating a simple 4-player, 2-round tournament."""

    def _simple_tournament() -> Tournament:
        players = [Player(pid=i, name=f"P{i}", skill=float(i)) for i in range(1, 5)]
        t = Tournament(players=players)
        t.rounds.append(
            Round(
                number=1,
                matches=[
                    Match(player_a=1, player_b=2, games=[Game(3, 1), Game(3, 2)]),
                    Match(player_a=3, player_b=4, games=[Game(3, 1), Game(3, 2)]),
                ],
            )
        )
        t.rounds.append(
            Round(
                number=2,
                matches=[
                    Match(player_a=1, player_b=3, games=[Game(3, 2), Game(2, 3)]),
                    Match(player_a=2, player_b=4, games=[Game(3, 1), Game(3, 2)]),
                ],
            )
        )
        return t

    return _simple_tournament


@pytest.fixture
def small_tournament():
    """Factory for creating a generated 8-player tournament."""

    def _small_tour(seed: int = 42) -> tuple[list[Player], Tournament]:
        rng = Random(seed)
        players = make_players(8, rng)
        tour = run_tournament(
            players, n_rounds=3, pairing=get_pairing("adjacent"), rng=rng
        )
        return players, tour

    return _small_tour


@pytest.fixture
def result_factory():
    """Factory for creating result dicts in Match.results shape."""

    def _result(
        wins: int,
        losses: int,
        player_agents: int,
        opponent_agents: int,
        bonus: int = 0,
        pid: int = 1,
        opp: int = 2,
    ) -> dict:
        return {
            "id": pid,
            "wins": wins,
            "losses": losses,
            "player_agents": player_agents,
            "opponent_agents": opponent_agents,
            "bonus_agents": bonus,
            "opponent": opp,
        }

    return _result


@pytest.fixture
def record_factory(result_factory):
    """Factory for creating Records from win/agent sequences."""

    def _make_record(
        wins_list: list[tuple[int, int, int, int]], pid: int = 1
    ) -> Record:
        rec = Record(player=Player(pid=pid, name=f"P{pid}", skill=0.0))
        for gw, gl, af, aa in wins_list:
            rec.process_result(result_factory(gw, gl, af, aa, pid=pid))
        return rec

    return _make_record


@pytest.fixture
def pairing_context_factory():
    """Factory for creating PairingContext objects."""
    from tournament.pairing import PairingContext

    def _empty_ctx(pids: list[int], round_number: int = 1) -> PairingContext:
        return PairingContext(
            past_opponents={pid: set() for pid in pids},
            round_number=round_number,
        )

    return _empty_ctx


@pytest.fixture
def records_factory():
    """Factory for creating Record dictionaries."""

    def _make_records(n: int, wins_seq: list[int] | None = None) -> dict[int, Record]:
        records: dict[int, Record] = {}
        for i in range(n):
            r = Record(player=Player(pid=i, name=f"P{i}", skill=0.0))
            if wins_seq and i < len(wins_seq):
                r.wins = wins_seq[i]
            records[i] = r
        return records

    return _make_records


@pytest.fixture
def tournament_factory():
    """Factory for creating generated tournaments with configurable strategy."""
    from tournament.engine import run_tournament
    from tournament.generators import make_players
    from tournament.pairing import get as get_pairing

    def _tour(
        n_players: int = 8,
        n_rounds: int = 3,
        strategy: str = "adjacent",
        seed: int = 42,
    ) -> Tournament:
        rng = Random(seed)
        players = make_players(n_players, rng)
        return run_tournament(players, n_rounds, get_pairing(strategy), rng)

    return _tour


@pytest.fixture
def a_wins_match_factory():
    """Factory for creating matches where player A wins both games (2-0)."""

    def _a_wins_match(a: int = 1, b: int = 2) -> Match:
        return Match(player_a=a, player_b=b, games=[Game(3, 1), Game(3, 2)])

    return _a_wins_match


@pytest.fixture
def draw_match_factory():
    """Factory for creating 1-1 draw matches."""

    def _draw_match(a: int = 1, b: int = 2) -> Match:
        return Match(player_a=a, player_b=b, games=[Game(3, 2), Game(2, 3)])

    return _draw_match


@pytest.fixture
def b_wins_match_factory():
    """Factory for creating matches where player B wins both games (0-2)."""

    def _b_wins_match(a: int = 1, b: int = 2) -> Match:
        return Match(player_a=a, player_b=b, games=[Game(1, 3), Game(2, 3)])

    return _b_wins_match
