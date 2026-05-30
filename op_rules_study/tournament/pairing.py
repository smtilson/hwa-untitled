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
* ``slide``      -- top of a bracket plays the next seed down ("slaughter").
* ``random``     -- shuffle the whole field, ignore records (control group).
* ``random_within_record`` -- shuffle inside each record group, then pair.

Each respects (best-effort) the rule that players should not be paired against a
past opponent.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Callable, Optional

from .models import BYE
from .standings import Record, group_by_record, rank_key

# A pairing is just an ordered pair of player ids (second may be BYE).
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
    """Pair an ordered list of ids 1-2, 3-4, ...; trailing odd id gets a bye."""
    pairs: list[Pairing] = []
    it = iter(order)
    for a in it:
        b = next(it, BYE)
        pairs.append((a, b))
    return pairs


def _ordered_ids(records: dict[int, Record]) -> list[int]:
    """All player ids sorted best-record-first by the default rank key."""
    return [r.pid for r in sorted(records.values(), key=rank_key, reverse=True)]


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


def _slide(group: list[int], rng: Random) -> list[int]:
    # Same neighbour pairing as adjacent but kept distinct for clarity/extension.
    return list(group)


def _shuffle(group: list[int], rng: Random) -> list[int]:
    g = list(group)
    rng.shuffle(g)
    return g


_WITHIN_GROUP = {
    "adjacent": _adjacent,
    "fold": _fold,
    "slide": _slide,
    "random_within_record": _shuffle,
}


def make_record_group_pairing(strategy: str = "adjacent") -> PairingFunction:
    """Build a pairing function that groups by record, orders within each group
    using ``strategy``, then pairs adjacent players across the flattened order.
    """
    if strategy not in _WITHIN_GROUP:
        raise ValueError(f"unknown strategy {strategy!r}; choose from {list(_WITHIN_GROUP)}")
    within = _WITHIN_GROUP[strategy]

    def _fn(records: dict[int, Record], rng: Random, ctx: PairingContext) -> list[Pairing]:
        groups = group_by_record(records)
        order: list[int] = []
        for _label, pids in groups.items():
            order.extend(within(pids, rng))
        order = _avoid_rematches(order, ctx)
        return _pair_sequence(order)

    _fn.__name__ = f"record_group__{strategy}"
    return _fn


def random_pairing(records: dict[int, Record], rng: Random, ctx: PairingContext) -> list[Pairing]:
    """Control group: ignore records entirely and pair at random."""
    order = list(records.keys())
    rng.shuffle(order)
    order = _avoid_rematches(order, ctx)
    return _pair_sequence(order)


# Convenience registry so scripts/notebooks can look algorithms up by name.
REGISTRY: dict[str, PairingFunction] = {
    "adjacent": make_record_group_pairing("adjacent"),
    "fold": make_record_group_pairing("fold"),
    "slide": make_record_group_pairing("slide"),
    "random_within_record": make_record_group_pairing("random_within_record"),
    "random": random_pairing,
}


def get(name: str) -> PairingFunction:
    if name not in REGISTRY:
        raise KeyError(f"unknown pairing {name!r}; choose from {list(REGISTRY)}")
    return REGISTRY[name]
