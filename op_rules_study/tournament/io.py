"""Read/write tournaments and standings as CSV.

Two long/tidy CSV layouts are used so that any script or notebook can reload
what was produced:

* **matches.csv** -- one row per match (the raw results).
* **standings.csv** -- one row per player per "through round" snapshot.

These are deliberately flat and tool-agnostic (Excel, pandas, R, ...).
"""

from __future__ import annotations

import csv
from pathlib import Path

from .models import Game, Match, Player, Round, Tournament
from .standings import compute_records

# One row per match, storing both games so a match can be rebuilt exactly.
# Sean tie breaker attention: the tie-break is stored as bonus agents
# (`bonus_agents_a/b`), not a third game; they must be restored on read or the
# tied-agent tiebreak is lost. `winner` is the winning player id, or empty for a
# draw.
MATCH_FIELDS = [
    "round",
    "player_a",
    "player_b",
    "g1_agents_a",
    "g1_agents_b",
    "g2_agents_a",
    "g2_agents_b",
    "bonus_agents_a",
    "bonus_agents_b",
    "total_agents_a",
    "total_agents_b",
    "winner",
    "is_draw",
]
STANDINGS_FIELDS = [
    "through_round",
    "pid",
    "name",
    "game_wins",
    "game_losses",
    "agents_for",
    "agents_against",
    "agent_diff",
    "agent_total_ratio",
    "record",
]


def _match_winner(m: Match) -> int | str:
    """Winning player id, or "" for a draw."""
    w = m.winner
    return "" if w is None else w


def write_matches(tournament: Tournament, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MATCH_FIELDS)
        w.writeheader()
        for rnd in tournament.rounds:
            for m in rnd.matches:
                g1, g2 = m.games[0], m.games[1]
                w.writerow(
                    {
                        "round": rnd.number,
                        "player_a": m.player_a,
                        "player_b": m.player_b,
                        "g1_agents_a": g1.agents_a,
                        "g1_agents_b": g1.agents_b,
                        "g2_agents_a": g2.agents_a,
                        "g2_agents_b": g2.agents_b,
                        # Sean tie breaker attention: persist bonus agents.
                        "bonus_agents_a": m.bonus_agents_a,
                        "bonus_agents_b": m.bonus_agents_b,
                        "total_agents_a": m.total_agents_a,
                        "total_agents_b": m.total_agents_b,
                        "winner": _match_winner(m),
                        "is_draw": int(m.is_draw),
                    }
                )


def write_standings(
    tournament: Tournament, path: str | Path, every_round: bool = True
) -> None:
    """Write standings. If ``every_round`` is True, emit a snapshot after each
    round (handy for studying how rankings evolve); otherwise only the final.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    names = {p.pid: p.name for p in tournament.players}
    rounds = (
        range(1, len(tournament.rounds) + 1)
        if every_round
        else [len(tournament.rounds)]
    )

    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=STANDINGS_FIELDS)
        w.writeheader()
        for through in rounds:
            records = compute_records(tournament, through_round=through)
            for rec in records.values():
                w.writerow(
                    {
                        "through_round": through,
                        "pid": rec.pid,
                        "name": names.get(rec.pid, ""),
                        "game_wins": rec.wins,
                        "game_losses": rec.losses,
                        "agents_for": rec.agents_for,
                        "agents_against": rec.agents_against,
                        "agent_diff": rec.agent_diff,
                        "agent_total_ratio": f"{rec.agent_total_ratio:.6f}",
                        "record": rec.record_str,
                    }
                )


def write_players(tournament: Tournament, path: str | Path) -> None:
    """Persist the player pool including the latent skill (ground truth)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pid", "name", "skill"])
        for p in tournament.players:
            w.writerow([p.pid, p.name, str(p.skill)])


def read_matches(path: str | Path, players: list[Player]) -> Tournament:
    """Reconstruct a :class:`Tournament` from a matches.csv file.

    Both games are stored per row, so each match is rebuilt as a valid two-game
    :class:`Match`.
    """
    path = Path(path)
    tournament = Tournament(players=list(players))
    rounds: dict[int, Round] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            n = int(row["round"])
            rnd = rounds.setdefault(n, Round(number=n))
            games = [
                Game(
                    agents_a=int(row["g1_agents_a"]), agents_b=int(row["g1_agents_b"])
                ),
                Game(
                    agents_a=int(row["g2_agents_a"]), agents_b=int(row["g2_agents_b"])
                ),
            ]
            # Sean tie breaker attention: restore bonus agents so totals round-trip.
            match = Match(
                player_a=int(row["player_a"]),
                player_b=int(row["player_b"]),
                games=games,
                bonus_agents_a=int(row.get("bonus_agents_a") or 0),
                bonus_agents_b=int(row.get("bonus_agents_b") or 0),
            )
            rnd.matches.append(match)
    tournament.rounds = [rounds[k] for k in sorted(rounds)]
    return tournament
