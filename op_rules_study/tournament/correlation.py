"""Pairwise correlation analysis between rating functions.

For a given tournament context (same players, rounds, seed), each rating
function produces a final ordering of players.  This module quantifies how
similar those orderings are, both in terms of **rank positions** (Spearman)
and **raw rating scores** (Pearson), and provides tools to visualise the
results as a heatmap.
"""

from __future__ import annotations

from statistics import fmean, pstdev
from typing import Callable, Sequence

from .models import Tournament
from .standings import compute_records, make_rank_key, Record


# ---------------------------------------------------------------------------
#  Low-level correlation primitives
# ---------------------------------------------------------------------------


def _pearson(xs: list[float], ys: list[float]) -> float:
    """Pearson correlation coefficient for two equal-length lists."""
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = fmean(xs), fmean(ys)
    cov = fmean([(x - mx) * (y - my) for x, y in zip(xs, ys)])
    sx, sy = pstdev(xs), pstdev(ys)
    return cov / (sx * sy) if sx and sy else 0.0


def _rank_order(tournament: Tournament, rating_fn: Callable) -> list[int]:
    """Return pids sorted best-first by (wins, rating_fn score)."""
    records = compute_records(tournament)
    key = make_rank_key(rating_fn)
    ranked = sorted(records.values(), key=lambda r: (-r.wins, -key(r)))
    return [r.pid for r in ranked]


def _score_vector(tournament: Tournament, rating_fn: Callable) -> dict[int, float]:
    """Map pid -> rating_fn score for every player in *tournament*."""
    records = compute_records(tournament)
    key = make_rank_key(rating_fn)
    return {pid: key(rec) for pid, rec in records.items()}


# ---------------------------------------------------------------------------
#  Public API
# ---------------------------------------------------------------------------


def standings_rank_correlation(
    tour_a: Tournament,
    tour_b: Tournament,
    rating_fn_a: Callable,
    rating_fn_b: Callable,
) -> float:
    """Spearman-style rank correlation between two tournaments' final standings.

    Each tournament is ranked with its own *rating_fn*.  The correlation is
    computed on the rank positions of shared player IDs, so it measures whether
    the two functions order players the same way.

    Returns a float in [-1, +1]; +1 means identical ordering.
    """
    order_a = _rank_order(tour_a, rating_fn_a)
    order_b = _rank_order(tour_b, rating_fn_b)

    rank_a = {pid: i for i, pid in enumerate(order_a)}
    rank_b = {pid: i for i, pid in enumerate(order_b)}

    pids = list(rank_a)
    xs = [rank_a[p] for p in pids]
    ys = [rank_b[p] for p in pids]
    return _pearson(xs, ys)


def score_correlation(
    tour_a: Tournament,
    tour_b: Tournament,
    rating_fn_a: Callable,
    rating_fn_b: Callable,
) -> float:
    """Pearson correlation between the raw rating *scores* two functions assign.

    Unlike :func:`standings_rank_correlation`, this captures magnitude
    differences, not just ordering.  Useful for detecting functions that agree
    on order but disagree on how far apart players are.
    """
    scores_a = _score_vector(tour_a, rating_fn_a)
    scores_b = _score_vector(tour_b, rating_fn_b)

    pids = list(scores_a)
    xs = [scores_a[p] for p in pids]
    ys = [scores_b[p] for p in pids]
    return _pearson(xs, ys)


def correlation_matrix(
    results_for_ctx: list,
    mode: str = "rank",
) -> dict[tuple[str, str], float]:
    """Pairwise correlation matrix across all rating functions for one context.

    Parameters
    ----------
    results_for_ctx:
        A ``list[Result]`` for a single ``(n_players, n_rounds, seed)`` context.
        Each ``Result`` must expose ``.label``, ``.tour``, and ``.rating_fn``.
    mode:
        ``"rank"`` for Spearman-style rank correlation,
        ``"score"`` for Pearson on raw rating scores.

    Returns
    -------
    dict keyed by ``(label_a, label_b)`` with the correlation coefficient.
    Only unique unordered pairs are included (i.e. ``(A, B)`` but not ``(B, A)``).
    """
    if mode not in ("rank", "score"):
        raise ValueError(f"mode must be 'rank' or 'score', got {mode!r}")

    corr_fn = standings_rank_correlation if mode == "rank" else score_correlation

    matrix: dict[tuple[str, str], float] = {}
    n = len(results_for_ctx)
    for i in range(n):
        for j in range(i + 1, n):
            a = results_for_ctx[i]
            b = results_for_ctx[j]
            matrix[(a.label, b.label)] = corr_fn(
                a.tour, b.tour, a.rating_fn, b.rating_fn
            )
    return matrix


def display_correlation_matrix(
    matrix: dict[tuple[str, str], float],
    labels: list[str],
    title: str,
) -> str:
    """Format a correlation matrix as a readable text table.

    *matrix* is the output of :func:`correlation_matrix`.
    *labels* should list the rating-function labels in the desired row/column order.
    """
    # Build a lookup so we can find either (a, b) or (b, a).
    lookup: dict[tuple[str, str], float] = {}
    for (la, lb), val in matrix.items():
        lookup[(la, lb)] = val
        lookup[(lb, la)] = val

    col_w = 10
    label_w = max(len(l) for l in labels) + 2

    lines = [
        title,
        "=" * len(title),
        f"{'':<{label_w}}" + "".join(f"{l[:col_w-2]:>{col_w}}" for l in labels),
        "-" * (label_w + col_w * len(labels)),
    ]
    for row_label in labels:
        row = f"{row_label:<{label_w}}"
        for col_label in labels:
            if row_label == col_label:
                row += f"{'1.000':>{col_w}}"
            else:
                val = lookup.get((row_label, col_label))
                row += f"{val:>{col_w}.3f}" if val is not None else f"{'':>{col_w}}"
        lines.append(row)
    return "\n".join(lines)


def plot_correlation_heatmap(
    matrix: dict[tuple[str, str], float],
    labels: list[str],
    title: str,
    mode: str = "rank",
) -> "object":
    """Render a seaborn heatmap of the correlation matrix.

    Returns a matplotlib ``Figure`` object.

    .. note::
        ``matplotlib`` and ``seaborn`` are imported lazily so that the rest of
        this module works without them installed.
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Build symmetric lookup.
    lookup: dict[tuple[str, str], float] = {}
    for (la, lb), val in matrix.items():
        lookup[(la, lb)] = val
        lookup[(lb, la)] = val

    n = len(labels)
    data = np.ones((n, n), dtype=float)
    for i, li in enumerate(labels):
        for j, lj in enumerate(labels):
            if i == j:
                data[i, j] = 1.0
            else:
                val = lookup.get((li, lj))
                if val is not None:
                    data[i, j] = val

    fig, ax = plt.subplots(figsize=(max(8, n * 0.8), max(6, n * 0.7)))
    sns.heatmap(
        data,
        annot=True,
        fmt=".2f",
        xticklabels=labels,
        yticklabels=labels,
        cmap="RdBu_r",
        center=0.0,
        vmin=-1.0,
        vmax=1.0,
        square=True,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title(title)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    fig.tight_layout()
    return fig
