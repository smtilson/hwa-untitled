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

from .models import BYE, Game, Match, Player, Round, Tournament
from .standings import Record, compute_records

MATCH_FIELDS = [
    "round", "player_a", "player_b", "agents_a", "agents_b",
    "winner", "result_a", "result_b", "is_bye",
]
STANDINGS_FIELDS = [
    "through_round", "pid", "name", "match_wins", "match_losses",
    "agents_for", "agents_against", "agent_diff", "match_points", "record",
]


def write_matches(tournament: Tournament, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MATCH_FIELDS)
        w.writeheader()
        for rnd in tournament.rounds:
            for m in rnd.matches:
                w.writerow({
                    "round": rnd.number,
                    "player_a": m.player_a,
                    "player_b": m.player_b,
                    "agents_a": m.agents_a,
                    "agents_b": m.agents_b,
                    "winner": m.winner,
                    "result_a": f"{m.agents_a}-{m.agents_b}",
                    "result_b": f"{m.agents_b}-{m.agents_a}",
                    "is_bye": int(m.is_bye),
                })


def write_standings(tournament: Tournament, path: str | Path, every_round: bool = True) -> None:
    """Write standings. If ``every_round`` is True, emit a snapshot after each
    round (handy for studying how rankings evolve); otherwise only the final.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    names = {p.pid: p.name for p in tournament.players}
    rounds = range(1, len(tournament.rounds) + 1) if every_round else [len(tournament.rounds)]

    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=STANDINGS_FIELDS)
        w.writeheader()
        for through in rounds:
            records = compute_records(tournament, through_round=through)
            for rec in records.values():
                w.writerow({
                    "through_round": through,
                    "pid": rec.pid,
                    "name": names.get(rec.pid, ""),
                    "match_wins": rec.match_wins,
                    "match_losses": rec.match_losses,
                    "agents_for": rec.agents_for,
                    "agents_against": rec.agents_against,
                    "agent_diff": rec.agent_diff,
                    "match_points": rec.match_points,
                    "record": rec.record_str,
                })


def write_players(tournament: Tournament, path: str | Path) -> None:
    """Persist the player pool including the latent skill (ground truth)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pid", "name", "skill"])
        for p in tournament.players:
            w.writerow([p.pid, p.name, f"{p.skill:.6f}"])


def read_matches(path: str | Path, players: list[Player]) -> Tournament:
    """Reconstruct a :class:`Tournament` from a matches.csv file.

    Game-by-game detail is not stored in the flat CSV, so each non-bye match is
    rebuilt as a single aggregate :class:`Game`. Standings/metrics that depend
    only on agent totals are unaffected.
    """
    path = Path(path)
    tournament = Tournament(players=list(players))
    rounds: dict[int, Round] = {}
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            n = int(row["round"])
            rnd = rounds.setdefault(n, Round(number=n))
            if int(row["is_bye"]):
                rnd.matches.append(Match(player_a=int(row["player_a"]), player_b=BYE))
            else:
                game = Game(agents_a=int(row["agents_a"]), agents_b=int(row["agents_b"]))
                rnd.matches.append(Match(
                    player_a=int(row["player_a"]),
                    player_b=int(row["player_b"]),
                    games=[game],
                ))
    tournament.rounds = [rounds[k] for k in sorted(rounds)]
    return tournament
