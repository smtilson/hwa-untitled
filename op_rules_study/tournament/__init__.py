"""``tournament`` -- a small, efficient model of Hubworld: Aidalon organized play.

Sub-modules
-----------
* :mod:`tournament.models`     -- dataclasses: Player, Game, Match, Round, Tournament.
* :mod:`tournament.standings`  -- turn rounds into per-player records/groups.
* :mod:`tournament.pairing`    -- families of pairing functions (the study core).
* :mod:`tournament.generators` -- produce match/game results (skill / random).
* :mod:`tournament.engine`     -- run a full event, round by round.
* :mod:`tournament.metrics`    -- quality metrics for comparing algorithms.
* :mod:`tournament.io`         -- CSV read/write.
"""

from __future__ import annotations

# Sean Update: These imports still succeed, but several re-exported callables
# (compute_records, run_tournament, summary, the io helpers) fail at RUNTIME
# because they reference the old Match API (agents_a/agents_b/winner). Also, the
# very first import below pulls in models.py, which imports the broken
# scripts/utils.check_validity -- so right now `import tournament` raises before
# anything else runs. Fix utils + the Match-API references before relying on this.
from .models import AGENTS_TO_WIN, BYE, Game, Match, Player, Round, Tournament
from .standings import Record, compute_records, group_by_record, rank_key
from .pairing import PairingContext, PairingFunction, REGISTRY, get as get_pairing
from .generators import make_players, random_match, skilled_match, win_probability
from .engine import run_tournament
from .metrics import summary

__all__ = [
    "AGENTS_TO_WIN",
    "BYE",
    "Game",
    "Match",
    "Player",
    "Round",
    "Tournament",
    "Record",
    "compute_records",
    "group_by_record",
    "rank_key",
    "PairingContext",
    "PairingFunction",
    "REGISTRY",
    "get_pairing",
    "make_players",
    "random_match",
    "skilled_match",
    "win_probability",
    "run_tournament",
    "summary",
]
