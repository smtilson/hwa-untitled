"""Families of pairing algorithms.

A *pairing function* is the central object of this study. Formally it is a
function of the previous ``n - 1`` rounds (summarised as per-player
:class:`~tournament.standings.Record` objects) that returns an **ordering** of
the players. Walking that ordering two-at-a-time yields the **pairing** for the
next round, so an ordering and a pairing are interchangeable.

    PairingFunction : (records, rng, context) -> list[Pairing]

All functions share the same signature so they can be swapped freely -- including
*changing the function from one round to the next* (see ``engine.py``).

Within a record group the interesting design choices live. We provide several
classic Swiss "within-bracket" strategies plus randomised baselines:

* ``adjacent``   -- sort by rank, pair neighbours (1v2, 3v4, ...).
* ``fold``       -- top half vs. bottom half (1vN/2, 2v..., a.k.a. "fold").
* ``strong_weak`` -- pair strongest with weakest, then second strongest with second weakest, etc.
* ``random``     -- shuffle the whole field, ignore records (control group).
* ``random_within_record`` -- shuffle inside each record group, then pair.

Each respects (best-effort) the rule that players should not be paired against a
past opponent.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Callable

from .standings import (
    Record,
    create_ranked_even_groups,
    group_by_record,
    make_rank_key,
    sort_groups,
)

Pairing = tuple[int, int]


@dataclass(slots=True)
class PairingContext:
    """Extra information a pairing function may consult.

    ``past_opponents`` lets an algorithm avoid rematches. ``round_number`` lets
    a single function behave differently over the course of an event.
    """

    past_opponents: dict[int, set[int]]
    round_number: int


# A pairing function maps records (+ rng + context) to a list of pairings.
PairingFunction = Callable[[dict[int, Record], Random, PairingContext], list[Pairing]]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _pair_sequence(order: list[int]) -> list[Pairing]:
    """Pair an ordered list of ids 1-2, 3-4, ..."""
    if len(order) % 2:
        raise ValueError(f"odd number of players: {order!r}")
    pairs: list[Pairing] = []
    it = iter(order)
    for a in it:
        b = next(it, None)
        pairs.append((a, b))
    return pairs


# devin: what is the point of this function?
def _ordered_ids(records: dict[int, Record]) -> list[int]:
    """All player ids sorted best-record-first by the default rank key."""
    return [r.pid for r in sorted(records.values(), key=make_rank_key(), reverse=True)]


# devin: what is the point of this function?
def _avoid_rematches(order: list[int], ctx: PairingContext) -> list[int]:
    """Greedy fix-up: if a pair are past opponents, swap the second player with
    the next available id. Best-effort only -- not guaranteed for pathological
    fields, which is itself a phenomenon worth studying.
    """
    order = list(order)
    for i in range(0, len(order) - 1, 2):
        a, b = order[i], order[i + 1]
        if b in ctx.past_opponents.get(a, ()):  # try to break the rematch
            for j in range(i + 2, len(order)):
                cand = order[j]
                if cand not in ctx.past_opponents.get(a, ()):
                    order[i + 1], order[j] = order[j], order[i + 1]
                    break
    return order


# --------------------------------------------------------------------------- #
# Within-group orderings (the part the study compares)
# --------------------------------------------------------------------------- #


def _adjacent(group: list[int], rng: Random) -> list[int]:
    return list(group)


def _fold(group: list[int], rng: Random) -> list[int]:

    half = len(group) // 2
    top, bottom = group[:half], group[half:]
    out: list[int] = []
    for i in range(half):
        out.append(top[i])
        out.append(bottom[i])
    if len(group) % 2:  # leftover middle seed
        out.append(bottom[-1])
    return out


def _strong_weak(group: list[int], rng: Random) -> list[int]:
    # Pair strongest with weakest, then second strongest with second weakest, etc.
    # This is a different approach to pairing players within a group.
    group = list(group)
    out: list[int] = []
    for i in range(len(group) // 2):
        out.append(group[i])
        out.append(group[-(i + 1)])
    if len(group) % 2:
        out.append(group[len(group) // 2])
    return out


def _shuffle(group: list[int], rng: Random) -> list[int]:
    g = list(group)
    rng.shuffle(g)
    return g


_WITHIN_GROUP = {
    "adjacent": _adjacent,
    "fold": _fold,
    "random_within_record": _shuffle,
    "strong_weak": _strong_weak,
}


def make_record_group_pairing(
    strategy: str = "adjacent", rating_fn: Callable | None = None
) -> PairingFunction:
    """Build a pairing function that groups by record, orders within each group
    using ``strategy``, then pairs adjacent players across the flattened order.

    ``rating_fn`` is forwarded to :func:`standings.sort_groups` to score the
    agent sequence when ranking tied records (``None`` uses the default).
    """
    if strategy not in _WITHIN_GROUP:
        raise ValueError(
            f"unknown strategy {strategy!r}; choose from {list(_WITHIN_GROUP)}"
        )
    within = _WITHIN_GROUP[strategy]

    def _fn(
        records: dict[int, Record], rng: Random, ctx: PairingContext
    ) -> list[Pairing]:
        groups = create_ranked_even_groups(records, rating_fn)
        order: list[int] = []
        for _label, recs in groups.items():
            pids = [r.pid for r in recs]
            order.extend(within(pids, rng))
        order = _avoid_rematches(order, ctx)
        return _pair_sequence(order)

    _fn.__name__ = f"record_group__{strategy}"
    return _fn


def random_pairing(
    records: dict[int, Record], rng: Random, ctx: PairingContext
) -> list[Pairing]:
    """Control group: ignore records entirely and pair at random."""
    order = list(records.keys())
    rng.shuffle(order)
    order = _avoid_rematches(order, ctx)
    return _pair_sequence(order)


# Convenience registry so scripts/notebooks can look algorithms up by name.
REGISTRY: dict[str, PairingFunction] = {
    "adjacent": make_record_group_pairing("adjacent"),
    "fold": make_record_group_pairing("fold"),
    "strong_weak": make_record_group_pairing("strong_weak"),
    "random_within_record": make_record_group_pairing("random_within_record"),
    "random": random_pairing,
}


def get(name: str) -> PairingFunction:
    if name not in REGISTRY:
        raise KeyError(f"unknown pairing {name!r}; choose from {list(REGISTRY)}")
    return REGISTRY[name]
