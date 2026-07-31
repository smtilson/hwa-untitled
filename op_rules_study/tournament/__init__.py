"""``tournament`` -- a small, efficient model of Hubworld: Aidalon organized play.

Sub-modules
-----------
* :mod:`tournament.models`       -- dataclasses: Player, Game, Match, Round, Tournament.
* :mod:`tournament.standings`    -- turn rounds into per-player records/groups.
* :mod:`tournament.pairing`      -- families of pairing functions (the study core).
* :mod:`tournament.generators`   -- produce match/game results (skill / random).
* :mod:`tournament.engine`       -- run a full event, round by round.
* :mod:`tournament.metrics`      -- quality metrics for comparing algorithms.
* :mod:`tournament.io`           -- CSV read/write.
* :mod:`tournament.presentation` -- display functions for tournament results.
"""

from __future__ import annotations

from .models import AGENTS_TO_WIN, Game, Match, Player, Round, Tournament
from .standings import (
    Record,
    compute_records,
    create_ranked_even_groups,
    group_by_record,
    make_groups_even,
    make_rank_key,
    sort_groups,
)
from .pairing import PairingContext, PairingFunction, REGISTRY, get as get_pairing
from .generators import (
    make_players,
    random_match,
    skilled_match,
    score_agent_probability,
)
from .engine import run_tournament
from .metrics import summary
from .presentation import (
    display_match_details,
    display_metrics,
    display_metrics_comparison,
    display_player_performance,
    display_round,
    display_skill_statistics,
    display_stacked_rounds,
    display_tournament_summary,
)
from .rating import (
    agent_differential,
    agent_ratio,
    agent_total_ratio,
    exponential_weights,
    linear_weights,
    total_agents_lost,
    total_agents_scored,
    weighted_agent_differential,
    weighted_agent_ratio,
    weighted_agent_total_ratio,
    weighted_total_agents_lost,
    weighted_total_agents_scored,
)

__all__ = [
    "AGENTS_TO_WIN",
    "Game",
    "Match",
    "Player",
    "Round",
    "Tournament",
    "Record",
    "compute_records",
    "create_ranked_even_groups",
    "group_by_record",
    "make_groups_even",
    "make_rank_key",
    "sort_groups",
    "PairingContext",
    "PairingFunction",
    "REGISTRY",
    "get_pairing",
    "make_players",
    "random_match",
    "skilled_match",
    "score_agent_probability",
    "run_tournament",
    "summary",
    "display_round",
    "display_tournament_summary",
    "display_stacked_rounds",
    "display_match_details",
    "display_player_performance",
    "display_skill_statistics",
    "display_metrics",
    "display_metrics_comparison",
    "total_agents_scored",
    "total_agents_lost",
    "agent_differential",
    "agent_ratio",
    "agent_total_ratio",
    "weighted_total_agents_scored",
    "weighted_total_agents_lost",
    "weighted_agent_differential",
    "weighted_agent_ratio",
    "weighted_agent_total_ratio",
    "linear_weights",
    "exponential_weights",
]
