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

from .models import Player, Tournament
from .rating import agent_differential


@dataclass(slots=True)
class Record:
    """A player's cumulative record across the rounds considered so far.

    The optional ``player`` argument links the record back to the source
    :class:`~tournament.models.Player`, giving access to ``record.skill`` and
    ``record.name`` for display without extra lookups.
    """

    player: Player | None = None
    wins: int = 0
    losses: int = 0
    bonus_agents_won: int = 0
    agents_for: int = 0
    agents_against: int = 0
    _raw_results: list[dict[str, int]] = field(default_factory=list)
    _agent_seq: list[tuple[int, int]] = field(default_factory=list)

    @property
    def skill(self) -> float | None:
        return self.player.skill if self.player else None

    @property
    def name(self) -> str | None:
        return self.player.name if self.player else None

    @property
    def pid(self) -> int:
        return self.player.pid if self.player else -1

    @property
    def matches_played(self) -> int:
        return (self.wins + self.losses) // 2

    @property
    def agent_diff(self) -> int:
        return self.agents_for - self.agents_against

    @property
    def agent_total_ratio(self) -> float:
        if self.agents_against + self.agents_for == 0:
            return 0.0
        return self.agents_for / (self.agents_against + self.agents_for)

    @property
    def record_str(self) -> str:
        """Human-readable ``wins-losses`` label used to form record groups."""
        return f"{self.wins}-{self.losses}, {self.agent_total_ratio:.3f}, {self.agent_diff}"

    @property
    def agent_seq(self) -> list[tuple[int, int]]:
        # Cascade: implemented -- build the (agents_for, agents_against) sequence
        # lazily from the stored per-round result dicts.
        if not self._agent_seq:
            self._agent_seq = [
                (r["player_agents"], r["opponent_agents"]) for r in self._raw_results
            ]
        return self._agent_seq

    def agent_score(self, rating_fn: Callable) -> float:
        # Cascade: added -- score the agent sequence with a pluggable rating_fn.
        return rating_fn(self.agent_seq)

    def process_result(self, result: dict[str, int]) -> None:
        # Cascade: rewritten -- now consumes the per-player dict returned by
        # Round.player_results / Match.results[pid]:
        #   {"id", "wins", "losses", "player_agents", "opponent_agents",
        #    "bonus_agents", "opponent"}.
        self.wins += result["wins"]
        self.losses += result["losses"]
        self.bonus_agents_won += result.get("bonus_agents", 0)
        self.agents_for += result["player_agents"]
        self.agents_against += result["opponent_agents"]
        self._raw_results.append(result)
        # Invalidate the cached agent sequence so it is rebuilt on next access.
        self._agent_seq = []

    @classmethod
    def from_raw_results(
        cls, raw_results: list[dict[str, int]], player: Player | None = None
    ) -> "Record":
        # Cascade: implemented -- rebuild a Record from a list of per-player
        # result dicts (all sharing the same "id"). The player may be supplied
        # directly; otherwise a minimal Player is synthesized from the result id.
        if not raw_results:
            raise ValueError("from_raw_results requires at least one result")
        if player is None:
            raise ValueError("A player must be passed.")
        record = cls(player=player)
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

    records: dict[int, Record] = {p.pid: Record(player=p) for p in tournament.players}

    for rnd in tournament.rounds:
        if through_round is not None and rnd.number > through_round:
            continue
        for m in rnd.matches:
            # Cascade: rewritten -- feed each player their per-player result dict
            # from Match.results (which now includes "opponent_agents").
            results = m.results
            records[m.player_a].process_result(results[m.player_a])
            records[m.player_b].process_result(results[m.player_b])

    return records


def make_rank_key(
    rating_fn: Callable[[list[tuple[int, int]]], float] | None = None,
) -> Callable[[Record], float]:
    """Build a sort key: game wins, then ``rating_fn`` applied to the agent sequence.

    Returns a one-argument callable suitable for ``sorted(..., reverse=True)``
    (higher is better). ``rating_fn`` defaults to :func:`agent_differential`; pass a
    different one (or ``None`` to fall back to the default) to experiment with
    alternative tiebreakers.
    """

    rating_fn = rating_fn or agent_differential

    def rank_key(record: Record) -> float:
        return record.agent_score(rating_fn)

    return rank_key


def group_by_record(records: dict[int, Record]) -> dict[str, list[Record]]:
    """Partition players into groups sharing the same ``wins-losses`` record.

    Groups are returned ordered from best record to worst. Within each group
    the order is unspecified -- call :func:`sort_groups` to rank by a rating_fn.
    """

    def _group_key(wl: str) -> tuple[int, int]:
        w, losses = wl.split("-")
        return (int(w), -int(losses))

    groups: dict[str, list[Record]] = {}
    for rec in records.values():
        record_key = f"{rec.wins}-{rec.losses}"
        groups.setdefault(record_key, []).append(rec)

    return dict(
        sorted(groups.items(), key=lambda item: _group_key(item[0]), reverse=True)
    )


def sort_groups(
    groups: dict[str, list[Record]], rating_fn: Callable | None = None
) -> dict[str, list[Record]]:
    """Sort each record group by rank key (best first).

    ``rating_fn`` is forwarded to :func:`make_rank_key`; ``None`` uses the default.
    """
    rank_key = make_rank_key(rating_fn)
    return {k: sorted(v, key=rank_key, reverse=True) for k, v in groups.items()}


def make_groups_even(groups: dict[str, list[Record]]) -> dict[str, list[Record]]:
    if sum(len(v) for v in groups.values()) % 2:
        raise ValueError("Cannot make groups even with an odd total player count")

    ordered_groups = [(k, list(v)) for k, v in groups.items()]
    ordered_groups.sort(key=lambda x: x[0], reverse=True)
    new_groups: dict[str, list[Record]] = {}
    carry: Record | None = None

    for k, v in ordered_groups:
        if carry is not None:
            v.insert(0, carry)
            carry = None
        if len(v) % 2:
            carry = v.pop()
        new_groups[f"{k}~"] = v

    if carry is not None:
        raise ValueError("Failed to place final odd player into an even group")

    return new_groups


def create_ranked_even_groups(
    records: dict[int, Record], rating_fn: Callable | None = None
) -> dict[str, list[Record]]:
    groups = group_by_record(records)
    groups = sort_groups(groups, rating_fn)
    groups = make_groups_even(groups)
    return groups
