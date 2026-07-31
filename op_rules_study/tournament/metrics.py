"""Quality metrics for comparing pairing algorithms.

The goal of a pairing algorithm is to pair players of comparable strength and to
let the final standings reflect true skill. These metrics quantify that against
the latent ``skill`` we know in simulation (but which the algorithms never see).
"""

# Windsurf: I am currently agnostic about how I want to evaluate the different pairing algorithms

from __future__ import annotations

from statistics import fmean, pstdev

from .models import Tournament
from .standings import compute_records, make_rank_key


def gap_list(tournament: Tournament) -> list[float]:
    """List of absolute skill differences between paired players."""
    gaps: list[float] = []
    by_id = {p.pid: p for p in tournament.players}
    for rnd in tournament.rounds:
        for m in rnd.matches:
            gaps.append(abs(by_id[m.player_a].skill - by_id[m.player_b].skill))
    return gaps


def mean_skill_gap(tournament: Tournament) -> float:
    """Average absolute skill difference between paired players (lower = better
    matched).
    """
    gaps = gap_list(tournament)
    return fmean(gaps) if gaps else 0.0

    

def weighted_skill_gap_score(tournament: Tournament) -> float:
    """Weighted average of skill gaps, weighted by the number of matches played."""
    gaps = gap_list(tournament)
    weighted_gaps = [gap * i / len(gaps) for i, gap in enumerate(gaps)]
    return fmean(weighted_gaps) if gaps else 0.0



def standings_skill_correlation(tournament: Tournament) -> float:
    """Spearman-style rank correlation between final standings and true skill.

    +1 means standings perfectly recover the skill order; 0 means no relation.
    Implemented without SciPy to keep dependencies light.
    """
    records = compute_records(tournament)
    by_id = {p.pid: p for p in tournament.players}

    final_order = [
        r.pid for r in sorted(records.values(), key=make_rank_key(), reverse=True)
    ]
    skill_order = sorted(by_id, key=lambda pid: by_id[pid].skill, reverse=True)

    standings_rank = {pid: i for i, pid in enumerate(final_order)}
    skill_rank = {pid: i for i, pid in enumerate(skill_order)}

    pids = list(by_id)
    n = len(pids)
    if n < 2:
        return 0.0
    xs = [standings_rank[p] for p in pids]
    ys = [skill_rank[p] for p in pids]
    mx, my = fmean(xs), fmean(ys)
    cov = fmean([(x - mx) * (y - my) for x, y in zip(xs, ys)])
    sx, sy = pstdev(xs), pstdev(ys)
    return cov / (sx * sy) if sx and sy else 0.0


def rematch_count(tournament: Tournament) -> int:
    """How many times any pair of players was paired more than once."""
    seen: dict[frozenset[int], int] = {}
    for rnd in tournament.rounds:
        for m in rnd.matches:
            key = frozenset((m.player_a, m.player_b))
            seen[key] = seen.get(key, 0) + 1
    return sum(c - 1 for c in seen.values() if c > 1)


def summary(tournament: Tournament) -> dict[str, float]:
    """Bundle the headline metrics for one tournament."""
    return {
        "mean_skill_gap": mean_skill_gap(tournament),
        "weighted_skill_gap_score": weighted_skill_gap_score(tournament),
        "standings_skill_correlation": standings_skill_correlation(tournament),
        "rematch_count": float(rematch_count(tournament)),
        "rounds": float(len(tournament.rounds)),
        "players": float(len(tournament.players)),
    }
