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

> **Change from the original spec (important).** The model now stores a match as
> *exactly two games* and **allows a drawn match** (a 1-1 game split, surfaced as
> `is_draw`). The original "play sudden-death agents until someone leads, so a
> match never ends tied" rule is **not currently represented** in the
> dataclasses. The result generators still *append* sudden-death games, which
> conflicts with the two-game `is_valid` check. This tension is tracked in
> `docs/decisions.md` **D7**.

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
  `adjacent`, `fold`, `slide`, `random_within_record`, and a `random` control.
- Generates results either **round-by-round** (realistic; pairing matters) or
  over **pre-generated** results (isolates a single decision). See
  `docs/decisions.md`.
- Scores each algorithm with **quality metrics** (`tournament/metrics.py`):
  mean skill gap between paired players, rank correlation of final standings vs.
  true skill, and rematch counts.

## 3. What the study wants to do

- [ ] Compare the pairing families across player counts and round counts.
- [ ] Study **changing the pairing function between rounds** (`--schedule`).
- [ ] Examine **manipulability**: can a player improve expected placement by
      controlling their own result (e.g. intentional draws/agent dumping)?
- [ ] Weigh **player comprehensibility** of each algorithm (qualitative — for us
      to discuss, not auto-generated).
- [ ] Investigate alternative tiebreakers in `standings.rank_key`.

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
| Tournament model (dataclasses) | `tournament/models.py` | ✎ revised (results dict, validity layer, draws, `assign_algorithm`) |
| Validity decorator (`check_validity`) | `scripts/utils.py` | ⚠ broken import/decorator; needs fix |
| Standings / records | `tournament/standings.py` | ⚠ uses old `Match` API (`agents_a/b`, `winner`) |
| Pairing function families | `tournament/pairing.py` | ☑ |
| Result generators | `tournament/generators.py` | ⚠ sudden-death loop uses old `agents_a/b` |
| Event engine (round loop, per-round swaps) | `tournament/engine.py` | ☑ (depends on standings) |
| Quality metrics | `tournament/metrics.py` | ☑ (depends on standings) |
| CSV I/O | `tournament/io.py` | ⚠ writes old `Match` fields; CSV schema will change |
| CLI scripts | `scripts/` | ☑ |
| Tests | `tests/test_smoke.py` | ⚠ assert old `Match` API |
| Notebook walkthrough | `notebooks/` | ⚠ uses old `Match` API |
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

**Follow-ups needed (to make the package runnable again):**
- Fix `scripts/utils.py` (`from functools import wraps`; rename inner function;
  make the decorator property-aware) and relocate it so `models.py` can import
  it without the failing `..scripts` relative import.
- Re-sync `standings.py`, `generators.py`, `io.py`, `tests/`, and the notebook
  to the new `Match` API / `results` shape.
- Resolve the two-games-vs-sudden-death tension (D7).

## 6. Glossary

- **Record group**: set of players with the same record (definition is a scoring
  choice — game wins-losses, match points, or agent totals; see D4).
- **Ordering**: total order on players; pairing = consecutive pairs of it.
- **Skill**: latent strength used only by generators; pairing never sees it.
- **Draw (`is_draw`)**: a match whose two games are split 1-1 (each player wins
  one game). Newly representable in the model.
- **Bye (`BYE`)**: *removed.* Byes are no longer modeled; tournaments require an
  even number of players.
