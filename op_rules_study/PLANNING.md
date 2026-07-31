# OP Rules Study — Planning Document

A study of tournament **pairing algorithms** for Hubworld: Aidalon organized
play. Status: **In Progress** — scaffold complete; data model under active
revision (see §5b), with downstream modules pending re-sync.

## 1. The setup

An organized-play event (`Tournament`) is a sequence of **rounds** (`Round`). In
each round players are **paired**; each pair plays one **match** (`Match`). The
data model lives in `tournament/models.py`.

- **`Game`** (frozen dataclass) records the agents each player captured in one
  game: `agents_a`, `agents_b`. A game is won by the player who reaches **3
  agents** (`AGENTS_TO_WIN`); `winner_is_a` is true when player A reached 3. A
  game is *valid* (`is_valid`) when neither side exceeds 3 agents and the two
  counts differ (someone actually won).
- **`Match`** is **exactly two `Game`s** between `player_a` and `player_b` (by
  id). `is_valid` requires two games and distinct players. (Byes and the `BYE`
  sentinel have been **removed** from the model; tournaments now require an even
  number of players.) The match outcome is decided by the **games** — a win, a
  loss, or a **split** — read from `game_1_winner` / `game_2_winner`. Agent totals
  do **not** decide the match; they are surfaced for **downstream** use by the
  pairing/standings code (as tiebreakers/metrics). From the two games the match
  derives:
  - `total_agents_a` / `total_agents_b` — agents summed across both games;
  - `game_1_winner` / `game_2_winner` — the winning player id of each game;
  - `is_draw` — true when the two games are **split 1-1** (each player wins one);
  - `agent_score` — the pair `(total_agents_a, total_agents_b)`.
- A player's **match result** is a structured record, `Match.results[player_id]`:
  `{"id", "wins", "losses", "player_agents", "opponent_agents", "opponent"}`, where
  `wins`/`losses` are **games won/lost** (0–2), `player_agents` is the agents this
  player scored across the match and `opponent_agents` is the opponent's. The
  `results` dict also carries a top-level `is_draw` flag.
- **`Round`** holds a `number` and a list of `matches`, exposes `opponents()`
  (player → opponent map), `player_results(pid)` (that player's result dict for
  the round), and `overall_results` (a round-level summary).
- **`Tournament`** holds the `players`, the `rounds` played so far, and an
  assignable pairing algorithm (`assign_algorithm` / `_algorithm`). Helpers:
  `player_ids`, `player_by_id`, `past_opponents`.

> **Change from the original spec (important).** The model stores a match as
> *exactly two games* and **allows a drawn match** (a 1-1 game split, surfaced as
> `is_draw`). This replaces the original "play sudden-death agents until someone
> leads" rule. **Resolved (D7, Option A):** sudden death was removed from the
> generators and `Match.is_valid` no longer rejects tied agent totals, so a 1-1
> draw (which may tie on agents, e.g. 4-4) is valid. Agent totals do **not**
> decide the match — they are surfaced for standings/tiebreakers only.

After rounds `1..n-1`, players are paired for round `n`. The **primary** key is
record, which partitions players into **record groups**. With the new per-player
`results` shape the exact record definition (match wins vs. game wins vs. agent
totals) is itself a scoring decision — see `docs/decisions.md` **D4**. The open
question remains how to **order within and across those groups** so players meet
opponents of comparable strength.

## 2. What the study does

- Models a tournament with small, efficient dataclasses (`tournament/`).
- Treats a pairing algorithm as a **function of the previous `n-1` rounds** that
  returns an **ordering of players** (equivalently, a pairing).
- Provides a **family** of such functions (`tournament/pairing.py`):
  `adjacent`, `fold`, `strong_weak`, `random_within_record`, and a `random` control.
- Generates results either **round-by-round** (realistic; pairing matters) or
  over **pre-generated** results (isolates a single decision). See
  `docs/decisions.md`.
- Scores each algorithm with **quality metrics** (`tournament/metrics.py`):
  mean skill gap between paired players, rank correlation of final standings vs.
  true skill, and rematch counts.

## 3. What the study wants to do

- [x] Compare rating functions across player counts, round counts, and seeds (`notebooks/Study.ipynb`). Outputs produced; presentation and interpretation pending review.
- [ ] Compare the pairing families across player counts and round counts.
- [ ] Study **changing the pairing function between rounds** (`--schedule`).
- [ ] Examine **manipulability**: can a player improve expected placement by
      controlling their own result (e.g. intentional draws/agent dumping)?
- [ ] Weigh **player comprehensibility** of each algorithm (qualitative — for us
      to discuss, not auto-generated).
- [ ] Investigate alternative tiebreakers in `standings.make_rank_key`.

## 4. Modeling decisions (open — see `docs/decisions.md`)

- How to generate results: random vs. skill-based (Bradley-Terry) vs. empirical.
- Round-by-round simulation vs. whole-tournament pre-generation.
- Scoring system (match points, agent differential, strength-of-schedule).
- Rematch avoidance policy (bye assignment removed — even fields required).

## 5. Components

Status key: ☑ in place · ✎ revised, under active iteration · ⚠ needs re-sync to
the revised model API.

| Component | Location | Status |
|---|---|---|
| Tournament model (dataclasses) | `tournament/models.py` | ☑ (results dict, validity layer, draws, `assign_algorithm`) |
| Validity decorator (`check_validity`) | `tournament/utils.py` | ☑ fixed (`wraps`; property-aware); moved into package |
| Standings / records | `tournament/standings.py` | ☑ `bonus_agents_won`; `make_rank_key` (wins+metric); `group_by_record` → `sort_groups` → `make_groups_even` API; `create_ranked_even_groups` convenience |
| Pairing function families | `tournament/pairing.py` | ☑ `_slide` → `_strong_weak`; uses `create_ranked_even_groups` (`group_by_record` → `sort_groups` → `make_groups_even`); metric threading |
| Result generators | `tournament/generators.py` | ☑ D7 Option A; bonus-agent tie-break (`_tie_break_bonus`, passed into `Match`) |
| Event engine (round loop, per-round swaps) | `tournament/engine.py` | ☑ byes removed |
| Quality metrics | `tournament/metrics.py` | ☑ `is_bye` checks removed |
| CSV I/O | `tournament/io.py` | ☑ per-game CSV; new `Record` fields |
| Presentation/display functions | `tournament/presentation.py` | ⚠ round, summary, stacked rounds, match details, player performance, skill stats, metrics display — **needs review** |
| Rating functions | `tournament/rating.py` | ⚠ basic and weighted rating functions — **needs review** |
| CLI scripts | `scripts/` | ☑ |
| Tests | `tests/test_smoke.py` | ☑ updated to new API (6 pass) |
| Notebook walkthrough | `notebooks/` | ✎ `reference/` module notebooks created (`1_models` … `7_metrics`); reviewed: `1_models` ✓ `2_generators` ✓ `3_standings` ✓; `4_pairing`–`7_metrics` pending; `pairing_study.ipynb` still on old `Match` API (update pending) |
| Rating-function study | `notebooks/Study.ipynb` | ✎ seed parameter integrated; players generated per `(n_players, seed)`; analysis run across 10 seeds; summary now presents top 5 by correlation and top 5 by mean skill gap with round-by-round displays. Presentation and interpretation pending review. |
| Decision log (prompts + pros/cons) | `docs/decisions.md` | ☑ |

## 5b. Recent changes

**By Sean (model redesign):**

- Reworked `Match`: renamed totals to `total_agents_a` / `total_agents_b`;
  removed `winner` / `loser` / `agents_for()` / `agents_against()`; added
  `game_1_winner`, `game_2_winner`, `is_draw`, `agent_score`, and a structured
  per-player `results` dict (games won/lost, `player_agents` / `opponent_agents`,
  opponent).
- Added a **validity layer**: `is_valid` on `Game`/`Match`/`Round` plus a
  `check_validity` decorator (`scripts/utils.py`).
- `Round` gained `player_results` and `overall_results`.
- `Tournament` can hold an assigned pairing algorithm (`assign_algorithm`).
- Game win is now "reached exactly 3 agents"; matches may be **draws**.
- **Removed byes**: deleted the `BYE` sentinel and all bye handling from
  `models.py` (the `is_valid` short-circuit, `is_bye`, `results["is_bye"]`, and
  the `opponents()` / `past_opponents` bye filters). Tournaments now assume an
  **even number of players**; downstream modules still referencing `BYE` need
  re-sync (`pairing`, `engine`, `standings`, `io`, `__init__`, tests).

**By Cascade:**

- Built the initial scaffold (model, standings, pairing, generators, engine,
  metrics, io, scripts, notebook, docs).
- Added an inventory (`CORRECTIONS.md`) and `# Sean Update:` review comments
  flagging the downstream modules that still reference the old `Match` API and
  the `scripts/utils.py` decorator bug.

**Done (package now imports, runs, and passes its smoke tests):**

- Fixed `check_validity` (`from functools import wraps`, `@wraps`) and moved it
  to `tournament/utils.py`; `models.py` imports it via `from .utils import ...`.
- Removed all `BYE` references downstream (`pairing`, `engine`, `standings`,
  `io`, `__init__`) and the `is_bye` checks in `metrics`; an even field is now
  required (`_pair_sequence` raises on odd counts).
- Resolved D7 (Option A): generators produce exactly two games; `Match.is_valid`
  no longer rejects tied agent totals.
- Re-synced `io.py` to a per-game CSV layout and the new `Record` fields
  (`game_wins`/`game_losses`/`agent_ratio`), and updated `tests/test_smoke.py`.
- Tie-break: a 1-1 split stays a draw, but a **bonus agent**
  (`Match.bonus_agents_a/b`, a constructor arg computed by
  `generators._tie_break_bonus`) breaks a tied *agent score* so standings can
  rank tied players. Both `skilled_match` and `random_match` apply it
  (skill-weighted vs. fair coin). Bonus agents fold into `total_agents_*` /
  `player_agents`; the matches CSV stores `bonus_agents_a/b`.
- Refactored `notebooks/Study.ipynb` to include a `seed` parameter in the
  tournament context (`TOUR_CTX = (n_players, n_rounds, seed)`), generate players
  per `(n_players, seed)`, and add `seed` to the `Result` dataclass. Ran the
  analysis across 10 seeds, updated the summary to present top 5 by skill
  correlation and top 5 by mean skill gap, and added round-by-round tournament
  displays for each top result.

**Still pending:**

- Update `notebooks/pairing_study.ipynb` to the new `Match` API.
- Decide scoring/record granularity (D4) and evaluation metrics.

## 5c. Result model (skill → result)

The skill-based generator (`skilled_match`) plays each agent as a Bernoulli
trial whose probability comes from `score_agent_probability(skill_a, skill_b) =
1 / (1 + exp(-(skill_a - skill_b)))` — a logistic (Bradley–Terry) function of the
skill gap. Properties: equal skill → 0.5; symmetric; the gap (not absolute
skill) drives the odds. Alternatives worth comparing: a **temperature**-scaled
logistic `1/(1+exp(-(s_a-s_b)/T))` to sharpen/soften skill's effect; a **Gaussian
(Thurstone)** model `Φ(s_a-s_b)`; **matchup/rock-paper-scissors** effects that
break transitivity; or a purely **empirical** distribution fitted to real event
data. The skill-free control is `random_match` (selectable via the engine's
`match_model`), which is the mechanism for "ignoring skill" — no per-`Player` flag.

## 6. Testing

Unit tests are in `tests/` (one file per module). See `docs/testing.md` for the full
test inventory and the 8 integration tests that still need to be written.

**Test suite summary:**

| File | Module | Approx. assertions |
|---|---|---|
| `test_models.py` | `models.py` | ~55 |
| `test_generators.py` | `generators.py` | ~34 |
| `test_standings.py` | `standings.py` | ~46 |
| `test_pairing.py` | `pairing.py` | ~44 |
| `test_engine.py` | `engine.py` | ~15 |
| `test_metrics.py` | `metrics.py` | ~19 |
| `test_io.py` | `io.py` | ~19 |
| `test_smoke.py` | end-to-end | 6 |

Run with: `python -m pytest tests/ -v` (from `op_rules_study/`).

**Recent test/design cleanup:**

1. `group_by_record` handles game win/loss buckets and orders those buckets from
   best record to worst.
2. `make_rank_key` returns only the selected agent metric for sorting players
   within an already-formed record group; `sort_groups` applies it.
3. `make_groups_even` now raises for odd total player counts and preserves all
   players for even totals.
4. Current suite status: `/home/smtilson/repos/hwa-untitled/.venv/bin/python -m pytest tests/ -q`
   from `op_rules_study/` → **234 passed**.

## 7. Glossary

- **Record group**: set of players with the same record (definition is a scoring
  choice — game wins-losses, match points, or agent totals; see D4).
- **Ordering**: total order on players; pairing = consecutive pairs of it.
- **Skill**: latent strength used only by generators; pairing never sees it.
- **Draw (`is_draw`)**: a match whose two games are split 1-1 (each player wins
  one game). Newly representable in the model.
