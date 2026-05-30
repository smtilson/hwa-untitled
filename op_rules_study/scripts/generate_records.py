"""Generate tournament records and write them to CSV.

Runs a full event round-by-round (the realistic loop) using a chosen pairing
algorithm and result model, then writes ``players.csv``, ``matches.csv`` and
``standings.csv`` into the data directory.

Examples
--------
    python scripts/generate_records.py --players 32 --rounds 5 --pairing adjacent
    python scripts/generate_records.py --players 16 --rounds 4 --pairing fold --seed 7
    python scripts/generate_records.py --model random --tag null_model
"""

from __future__ import annotations

import argparse
from random import Random

import _bootstrap  # noqa: F401  (side effect: fixes sys.path)
from _bootstrap import DATA_DIR

from tournament import get_pairing, make_players, run_tournament, summary
from tournament.generators import MATCH_MODELS
from tournament.io import write_matches, write_players, write_standings


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Hubworld: Aidalon tournament records.")
    p.add_argument("--players", type=int, default=32, help="number of players")
    p.add_argument("--rounds", type=int, default=5, help="number of rounds")
    p.add_argument("--pairing", default="adjacent",
                   help="pairing algorithm: adjacent, fold, slide, random_within_record, random")
    p.add_argument("--model", default="skilled", choices=list(MATCH_MODELS),
                   help="result model used to play matches")
    p.add_argument("--skill-sd", type=float, default=1.0, help="std-dev of latent skill")
    p.add_argument("--seed", type=int, default=0, help="RNG seed for reproducibility")
    p.add_argument("--tag", default=None, help="filename prefix (defaults to the pairing name)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    rng = Random(args.seed)

    players = make_players(args.players, rng, skill_sd=args.skill_sd)
    tournament = run_tournament(
        players=players,
        n_rounds=args.rounds,
        pairing=get_pairing(args.pairing),
        rng=rng,
        match_model=MATCH_MODELS[args.model],
    )

    tag = args.tag or args.pairing
    write_players(tournament, DATA_DIR / f"{tag}_players.csv")
    write_matches(tournament, DATA_DIR / f"{tag}_matches.csv")
    write_standings(tournament, DATA_DIR / f"{tag}_standings.csv")

    print(f"Wrote {tag}_players.csv, {tag}_matches.csv, {tag}_standings.csv to {DATA_DIR}")
    for k, v in summary(tournament).items():
        print(f"  {k:>30}: {v:.4f}")


if __name__ == "__main__":
    main()
