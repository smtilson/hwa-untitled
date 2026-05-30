"""Compare pairing algorithms head-to-head.

For each algorithm, simulate many independent events (same player pool per seed)
and report mean quality metrics. This is the workhorse for the study's primary
question: which pairing function best matches players by strength?

Also demonstrates *changing the pairing function from round to round* via the
``--schedule`` option (a comma-separated list, one algorithm per round).

Examples
--------
    python scripts/run_pairing.py --players 32 --rounds 5 --trials 200
    python scripts/run_pairing.py --algorithms adjacent,fold,random
    python scripts/run_pairing.py --schedule random,adjacent,adjacent,fold,fold
"""

from __future__ import annotations

import argparse
import csv
from random import Random
from statistics import fmean

import _bootstrap  # noqa: F401
from _bootstrap import DATA_DIR

from tournament import REGISTRY, get_pairing, make_players, run_tournament, summary


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare pairing algorithms over many simulated events.")
    p.add_argument("--players", type=int, default=32)
    p.add_argument("--rounds", type=int, default=5)
    p.add_argument("--trials", type=int, default=100, help="independent events per algorithm")
    p.add_argument("--skill-sd", type=float, default=1.0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--algorithms", default=",".join(REGISTRY),
                   help="comma-separated algorithm names to compare")
    p.add_argument("--schedule", default=None,
                   help="comma-separated per-round algorithms (overrides --algorithms with one entry 'schedule')")
    p.add_argument("--out", default=None, help="optional CSV path for the comparison table")
    return p.parse_args()


def evaluate(pairing_spec, args) -> dict[str, float]:
    metric_rows: list[dict[str, float]] = []
    for t in range(args.trials):
        rng = Random(args.seed * 100003 + t)
        players = make_players(args.players, rng, skill_sd=args.skill_sd)
        tour = run_tournament(players, args.rounds, pairing_spec, rng)
        metric_rows.append(summary(tour))
    keys = metric_rows[0].keys()
    return {k: fmean(r[k] for r in metric_rows) for k in keys}


def main() -> None:
    args = parse_args()

    specs: dict[str, object] = {}
    if args.schedule:
        specs["schedule"] = [get_pairing(name.strip()) for name in args.schedule.split(",")]
    else:
        for name in args.algorithms.split(","):
            specs[name.strip()] = get_pairing(name.strip())

    results = {label: evaluate(spec, args) for label, spec in specs.items()}

    metrics = next(iter(results.values())).keys()
    header = f"{'algorithm':>22} | " + " | ".join(f"{m:>22}" for m in metrics)
    print(header)
    print("-" * len(header))
    for label, vals in results.items():
        print(f"{label:>22} | " + " | ".join(f"{vals[m]:>22.4f}" for m in metrics))

    if args.out:
        out_path = DATA_DIR / args.out if "/" not in args.out else args.out
        with open(out_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["algorithm", *metrics])
            for label, vals in results.items():
                w.writerow([label, *(f"{vals[m]:.6f}" for m in metrics)])
        print(f"\nWrote comparison table to {out_path}")


if __name__ == "__main__":
    main()
