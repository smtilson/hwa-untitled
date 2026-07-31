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
- A **`Match`** is **two games** between `player_a` and `player_b`. The outcome is
  decided by the **games** (`game_1_winner` / `game_2_winner`); `is_draw` is a 1-1
  game split. It also derives `total_agents_a` / `total_agents_b` and `agent_score`,
  but **agent totals do not decide the match** — they are surfaced for downstream
  pairing/standings use (tiebreakers/metrics). A tied agent score is broken by a
  **bonus agent** (`bonus_agents_a` / `bonus_agents_b`, a constructor arg set by
  the result generator), folded into the agent totals without changing the winner.
  <!-- Sean Bye comment --> (Byes and the `BYE` sentinel have been removed from
  the model; tournaments now require an even number of players.)
- A player's **match result** is the dict `Match.results[player_id]` =
  `{"id", "wins", "losses", "player_agents", "opponent_agents", "opponent"}`, where
  `wins`/`losses` are **games won/lost** (0–2), `player_agents` is this player's
  agent total and `opponent_agents` the opponent's; the dict also carries `is_draw`.
  <!-- Sean Bye comment --> (`is_bye` removed.)
- A **`Round`** bundles matches and exposes `opponents()`, `player_results(pid)`,
  and `overall_results`. A **`Tournament`** holds players, rounds, and an
  assignable pairing algorithm (`assign_algorithm`).

> **Note:** the model permits **drawn matches** (1-1 game splits) and validates a
> match as exactly two games. This differs from the original "sudden-death, never
> tied" rule; a tied agent score is instead broken by a bonus agent (no third
> game). See `PLANNING.md` §5b and `docs/decisions.md` **D7**.

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
│   ├── presentation.py    #   display functions for tournament results
│   ├── rating.py          #   rating functions for player performance
│   └── io.py              #   CSV read/write
├── scripts/               # CLI entry points
│   ├── generate_records.py
│   ├── run_pairing.py
│   └── utils.py           #   validity decorator (check_validity)
├── notebooks/             # follow-along Jupyter analysis
│   ├── pairing_study.ipynb
│   ├── presentation_demo.ipynb
│   └── reference/         # one notebook per tournament module
│       ├── 1_models.ipynb
│       ├── 2_generators.ipynb
│       ├── 3_standings.ipynb
│       ├── 4_pairing.ipynb
│       ├── 5_engine.ipynb
│       ├── 6_rating.ipynb
│       └── 7_metrics.ipynb
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
from tournament import (
    make_players,
    run_tournament,
    get_pairing,
    summary,
    display_tournament_summary,
    display_metrics,
)

rng = Random(0)
players = make_players(32, rng)
tour = run_tournament(players, n_rounds=5, pairing=get_pairing("fold"), rng=rng)
print(display_tournament_summary(tour))
print(display_metrics(tour))
```

## Available pairing algorithms

`adjacent`, `fold`, `strong_weak`, `random_within_record`, `random`
(see [`tournament/pairing.py`](tournament/pairing.py) and
[`docs/decisions.md`](docs/decisions.md) for the trade-offs).

Each record-based algorithm first partitions players by their win-loss record,
orders the players inside each bracket, and then balances odd-sized brackets via
`standings.make_groups_even` (so every bracket contains an even number of players
before pairings are formed).

## Metrics

- **mean_skill_gap** — average true-skill difference between paired players
  (lower = better matched).
- **standings_skill_correlation** — rank correlation of final standings vs. true
  skill (higher = standings recover strength better).
- **rematch_count** — number of repeated pairings (lower = better).

## Presentation module

The `tournament/presentation.py` module provides display functions for visualizing tournament results:

- **`display_round`** — Shows detailed information for a specific round, including pairings, skills, previous records, and agent totals.
- **`display_tournament_summary`** — Shows final standings with rankings, records, agent differentials, and ratios.
- **`display_stacked_rounds`** — Shows a matrix view with players as rows and rounds as columns, tracking player progression.
- **`display_match_details`** — Shows detailed game-by-game results for a specific match.
- **`display_player_performance`** — Shows a player's performance over the tournament, including opponent information and group assignments.
- **`display_skill_statistics`** — Shows basic statistics about player skill levels (mean, median, std dev).
- **`display_metrics`** — Shows evaluation metrics for the tournament (skill gap, correlation, rematches).
- **`display_metrics_comparison`** — Compares metrics across multiple tournaments.

## Rating module

The `tournament/rating.py` module provides rating functions for evaluating player performance:

- **Basic functions** (unweighted): `total_agents_scored`, `total_agents_lost`, `agent_differential`, `agent_ratio`, `agent_total_ratio`
- **Weighted functions**: `weighted_total_agents_scored`, `weighted_total_agents_lost`, `weighted_agent_differential`, `weighted_agent_ratio`, `weighted_agent_total_ratio`
- **Weight utilities**: `linear_weights`, `exponential_weights` for creating weight sequences

These functions take an agent sequence (list of tuples) and return a numeric rating, useful for tiebreakers or custom metrics.

## Tests

```bash
python -m pytest tests/
```
