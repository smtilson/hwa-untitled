"""Compute standings/records from the rounds played so far.

A pairing algorithm is a function of the previous ``n - 1`` rounds. In practice
it only needs a compact summary of those rounds: each player's record. This
module turns a :class:`~tournament.models.Tournament` into that summary.

Scoring is configurable so the study can compare, e.g., "match wins only" vs.
"agent differential as tiebreaker".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .models import BYE, Tournament


@dataclass(slots=True)
class Record:
    """A player's cumulative record across the rounds considered so far."""

    pid: int
    wins: int = 0
    losses: int = 0
    tie_breaks_won: int = 0
    agents_for: int = 0
    agents_against: int = 0
    # Sean remove byes
    byes: int = 0
    _raw_results: list[dict[str, int]] = field(default_factory=list)
    _agent_seq: list[tuple[int, int]] = field(default_factory=list)

    @property
    def matches_played(self) -> int:
        return (self.wins + self.losses) // 2

    @property
    def agent_diff(self) -> int:
        return self.agents_for - self.agents_against

    @property
    def agent_ratio(self) -> float:
        if self.agents_against + self.agents_for == 0:
            return 0.0
        return self.agents_for / (self.agents_against + self.agents_for)

    @property
    def record_str(self) -> str:
        """Human-readable ``wins-losses`` label used to form record groups."""
        return f"{self.wins}-{self.losses}, {self.agent_ratio:.3f}, {self.agent_diff}"

    @property
    def agent_seq(self) -> list[tuple[int, int]]:
        # Cascade: implemented -- build the (agents_for, agents_against) sequence
        # lazily from the stored per-round result dicts.
        if not self._agent_seq:
            self._agent_seq = [
                (r["player_agents"], r["opponent_agents"]) for r in self._raw_results
            ]
        return self._agent_seq

    def agent_score(self, metric: Callable) -> float:
        # Cascade: added -- score the agent sequence with a pluggable metric.
        return metric(self.agent_seq)

    def process_result(self, result: dict[str, int]) -> None:
        # Cascade: rewritten -- now consumes the per-player dict returned by
        # Round.player_results / Match.results[pid]:
        #   {"id", "wins", "losses", "player_agents", "opponent_agents", "opponent"}.
        self.wins += result["wins"]
        self.losses += result["losses"]
        self.agents_for += result["player_agents"]
        self.agents_against += result["opponent_agents"]
        self._raw_results.append(result)
        # Invalidate the cached agent sequence so it is rebuilt on next access.
        self._agent_seq = []

    @classmethod
    def from_raw_results(cls, raw_results: list[dict[str, int]]) -> "Record":
        # Cascade: implemented -- rebuild a Record from a list of per-player
        # result dicts (all sharing the same "id").
        if not raw_results:
            raise ValueError("from_raw_results requires at least one result")
        record = cls(pid=raw_results[0]["id"])
        for result in raw_results:
            record.process_result(result)
        return record


def compute_records(
    tournament: Tournament, through_round: int | None = None
) -> dict[int, Record]:
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
            # Sean remove byes
            # Cascade: check the BYE sentinel directly rather than `m.is_bye`,
            # which is validity-checked and would raise on a 0-game bye match.
            if m.player_b == BYE:
                # Cascade: rewritten for the new result-dict shape. A bye is
                # scored as a 2-0 win: two game wins, two agents-for, none against.
                rec = records[m.player_a]
                rec.byes += 1
                rec.process_result(
                    {
                        "id": m.player_a,
                        "wins": 2,
                        "losses": 0,
                        "player_agents": 2,
                        "opponent_agents": 0,
                        "opponent": BYE,
                    }
                )
                continue

            # Cascade: rewritten -- feed each player their per-player result dict
            # from Match.results (which now includes "opponent_agents").
            results = m.results
            records[m.player_a].process_result(results[m.player_a])
            records[m.player_b].process_result(results[m.player_b])

    return records


def rank_key(record: Record) -> tuple[int, float, int]:
    """Default sort key: game wins, then agent ratio, then agent differential.

    Returns a tuple suitable for ``sorted(..., reverse=True)`` (higher is
    better). Swap this out to experiment with alternative tiebreakers.
    """

    # Cascade: updated -- `match_points` was removed; rank by wins, then the
    # agent ratio, then the agent differential.
    return (record.wins, record.agent_ratio, record.agent_diff)


def group_by_record(records: dict[int, Record]) -> dict[str, list[int]]:
    """Partition players into groups sharing the same ``wins-losses`` record.

    Groups are returned ordered from best record to worst.
    """

    groups: dict[str, list[int]] = {}
    ordered = sorted(records.values(), key=rank_key, reverse=True)
    for rec in ordered:
        groups.setdefault(rec.record_str, []).append(rec.pid)
    return groups
