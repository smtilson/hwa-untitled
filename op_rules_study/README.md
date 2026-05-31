# OP Rules Study

A simulation study of **tournament pairing algorithms** for Hubworld: Aidalon
organized play. The goal is to compare different ways of pairing players so they
face opponents of **comparable strength**, and to lay the groundwork for later
studying how those algorithms can be manipulated.

> **Status:** In Progress. See [`PLANNING.md`](PLANNING.md) for scope and
> [`docs/decisions.md`](docs/decisions.md) for the open design questions.

## The core idea

A pairing algorithm is a **function of the previous `n-1` rounds** that returns
an **ordering of the players**. Walking that ordering two-at-a-time gives the
pairing for round `n`, so an ordering and a pairing are the same thing. This
project compares **families** of such functions.

Match rules modeled here (`tournament/models.py`):

- A **`Game`** records the agents each side captured (`agents_a`, `agents_b`).
  It is won by the player who reaches **3 agents** (`winner_is_a`).
- A **`Match`** is **two games** between `player_a` and `player_b`. It derives
  `total_agents_a` / `total_agents_b`, the per-game winners, `agent_score`, and
  `is_draw` (true when the two games are split **1-1**). A **bye** is
  `player_b == BYE`.
- A player's **match result** is the dict `Match.results[player_id]` =
  `{"id", "wins", "losses", "agents", "opponent"}`, where `wins`/`losses` are
  **games won/lost** (0–2) and `agents` is total agents scored; the dict also
  carries `is_draw` / `is_bye`.
- A **`Round`** bundles matches and exposes `opponents()`, `player_results(pid)`,
  and `overall_results`. A **`Tournament`** holds players, rounds, and an
  assignable pairing algorithm (`assign_algorithm`).

> **Note (in flux):** the model now permits **drawn matches** (1-1 game splits)
> and validates a match as exactly two games. This differs from the original
> "sudden-death, never tied" rule, and some downstream modules still reference
> the older `Match` API. See `PLANNING.md` §5b and `docs/decisions.md` **D7**.

## Layout

```
op_rules_study/
├── README.md              # this file
├── PLANNING.md            # study scope, goals, status
├── CORRECTIONS.md         # inventory of created files + review notes
├── requirements.txt       # notebook/analysis deps (core sim is stdlib-only)
├── tournament/            # the model + algorithms (pure stdlib)
│   ├── models.py          #   Player, Game, Match, Round, Tournament (dataclasses)
│   ├── standings.py       #   records & record groups from rounds
│   ├── pairing.py         #   families of pairing functions  <-- study core
│   ├── generators.py      #   result models (skill-based / random)
│   ├── engine.py          #   round-by-round event loop (per-round swaps)
│   ├── metrics.py         #   quality metrics for comparing algorithms
│   └── io.py              #   CSV read/write
├── scripts/               # CLI entry points
│   ├── generate_records.py
│   ├── run_pairing.py
│   └── utils.py           #   validity decorator (check_validity)
├── notebooks/             # follow-along Jupyter analysis
│   └── pairing_study.ipynb
├── data/                  # generated CSVs (see data/README.md)
├── tests/                 # sanity tests
└── docs/
    └── decisions.md       # prompts + pros/cons at each decision point
```

## Setup

The core simulation uses **only the Python standard library**. Extra packages
are needed only for the notebook/plots.

```bash
# from the repo root
source .venv/bin/activate
pip install -r op_rules_study/requirements.txt
```

## Quick start

Run commands from the module directory (`op_rules_study/`):

```bash
# 1) Generate a tournament's records as CSVs in data/
python scripts/generate_records.py --players 32 --rounds 5 --pairing adjacent --seed 1

# 2) Compare pairing algorithms over many simulated events
python scripts/run_pairing.py --players 32 --rounds 5 --trials 200 \
    --algorithms adjacent,fold,random_within_record,random --out comparison.csv

# 3) Study changing the algorithm from round to round
python scripts/run_pairing.py --schedule random,adjacent,adjacent,fold,fold
```

Then open the notebook:

```bash
jupyter notebook notebooks/pairing_study.ipynb
```

## Using the package directly

```python
from random import Random
from tournament import make_players, run_tournament, get_pairing, summary

rng = Random(0)
players = make_players(32, rng)
tour = run_tournament(players, n_rounds=5, pairing=get_pairing("fold"), rng=rng)
print(summary(tour))
```

## Available pairing algorithms

`adjacent`, `fold`, `slide`, `random_within_record`, `random`
(see [`tournament/pairing.py`](tournament/pairing.py) and
[`docs/decisions.md`](docs/decisions.md) for the trade-offs).

## Metrics

- **mean_skill_gap** — average true-skill difference between paired players
  (lower = better matched).
- **standings_skill_correlation** — rank correlation of final standings vs. true
  skill (higher = standings recover strength better).
- **rematch_count** — number of repeated pairings (lower = better).

## Tests

```bash
python -m pytest tests/
```
