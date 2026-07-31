"""Drive a full event: pair a round, play it, repeat.

This is approach (a) from ``generators.py`` -- the realistic loop where each
round's pairing depends on the results of all previous rounds. Crucially,
``run_tournament`` accepts *either* a single pairing function (used every round)
*or* a list/dict of functions keyed by round, so we can study what happens when
the pairing algorithm changes from one round to the next.
"""

from __future__ import annotations

from random import Random
from typing import Callable, Mapping, Sequence, Union

from .generators import skilled_match
from .models import Match, Player, Round, Tournament
from .pairing import PairingContext, PairingFunction
from .standings import compute_records

# How a match is produced from two players + rng.
MatchModel = Callable[[Player, Player, Random], Match]

# Round 1 has no records, so we need a way to seed the first pairing.
PairingSpec = Union[
    PairingFunction, Sequence[PairingFunction], Mapping[int, PairingFunction]
]


def _pairing_for_round(spec: PairingSpec, round_number: int) -> PairingFunction:
    """Resolve which pairing function to use for ``round_number`` (1-indexed)."""
    if callable(spec):
        return spec  # single function reused every round
    if isinstance(spec, Mapping):
        if round_number in spec:
            return spec[round_number]
        # fall back to the latest specified round <= round_number
        keys = [k for k in spec if k <= round_number]
        return spec[max(keys)] if keys else spec[min(spec)]
    # Sequence: index by round (clamp to the last entry).
    idx = min(round_number - 1, len(spec) - 1)
    return spec[idx]


def run_tournament(
    players: list[Player],
    n_rounds: int,
    pairing: PairingSpec,
    rng: Random,
    match_model: MatchModel = skilled_match,
) -> Tournament:
    """Simulate ``n_rounds`` rounds, pairing with ``pairing`` and playing matches
    with ``match_model``. Returns the completed :class:`Tournament`.
    """
    tournament = Tournament(players=list(players))
    by_id = {p.pid: p for p in players}

    for n in range(1, n_rounds + 1):
        records = compute_records(tournament)  # uses rounds 1..n-1
        ctx = PairingContext(
            past_opponents={pid: tournament.past_opponents(pid) for pid in by_id},
            round_number=n,
        )
        fn = _pairing_for_round(pairing, n)
        pairs = fn(records, rng, ctx)

        rnd = Round(number=n)
        for a, b in pairs:
            rnd.matches.append(match_model(by_id[a], by_id[b], rng))
        tournament.rounds.append(rnd)

    return tournament
