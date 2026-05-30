"""Compute standings/records from the rounds played so far.

A pairing algorithm is a function of the previous ``n - 1`` rounds. In practice
it only needs a compact summary of those rounds: each player's record. This
module turns a :class:`~tournament.models.Tournament` into that summary.

Scoring is configurable so the study can compare, e.g., "match wins only" vs.
"agent differential as tiebreaker".
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import BYE, Tournament


@dataclass(slots=True)
class Record:
    """A player's cumulative record across the rounds considered so far."""

    pid: int
    match_wins: int = 0
    match_losses: int = 0
    agents_for: int = 0
    agents_against: int = 0
    byes: int = 0

    @property
    def matches_played(self) -> int:
        return self.match_wins + self.match_losses

    @property
    def agent_diff(self) -> int:
        return self.agents_for - self.agents_against

    @property
    def match_points(self) -> int:
        """Simple 3-points-per-win scheme (no draws are possible)."""
        return 3 * self.match_wins

    @property
    def record_str(self) -> str:
        """Human-readable ``wins-losses`` label used to form record groups."""
        return f"{self.match_wins}-{self.match_losses}"


def compute_records(tournament: Tournament, through_round: int | None = None) -> dict[int, Record]:
    """Aggregate per-player records.

    Parameters
    ----------
    tournament:
        The event to summarise.
    through_round:
        If given, only rounds with ``number <= through_round`` are counted.
        This makes it easy to ask "what did standings look like before round k?".
    """

    records: dict[int, Record] = {p.pid: Record(pid=p.pid) for p in tournament.players}

    for rnd in tournament.rounds:
        if through_round is not None and rnd.number > through_round:
            continue
        for m in rnd.matches:
            if m.is_bye:
                rec = records[m.player_a]
                rec.match_wins += 1
                rec.byes += 1
                # A bye is conventionally scored as a 2-0 win in agents.
                rec.agents_for += 2
                continue

            a, b = records[m.player_a], records[m.player_b]
            a.agents_for += m.agents_a
            a.agents_against += m.agents_b
            b.agents_for += m.agents_b
            b.agents_against += m.agents_a

            if m.winner == m.player_a:
                a.match_wins += 1
                b.match_losses += 1
            else:
                b.match_wins += 1
                a.match_losses += 1

    return records


def rank_key(record: Record) -> tuple[int, int, int]:
    """Default sort key: match points, then agent differential, then agents-for.

    Returns a tuple suitable for ``sorted(..., reverse=True)`` (higher is
    better). Swap this out to experiment with alternative tiebreakers.
    """

    return (record.match_points, record.agent_diff, record.agents_for)


def group_by_record(records: dict[int, Record]) -> dict[str, list[int]]:
    """Partition players into groups sharing the same ``wins-losses`` record.

    Groups are returned ordered from best record to worst.
    """

    groups: dict[str, list[int]] = {}
    ordered = sorted(records.values(), key=rank_key, reverse=True)
    for rec in ordered:
        groups.setdefault(rec.record_str, []).append(rec.pid)
    return groups
