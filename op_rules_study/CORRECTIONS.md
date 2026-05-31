# Corrections / Inventory

Inventory of everything **Cascade created** for `op_rules_study/`, with a status
flag for whether **you (the user) have since modified it**.

Legend:
- **Unmodified** — still as Cascade wrote it.
- **Modified** — you have edited it (details listed).
- **User-created** — file you added yourself (not by Cascade), listed for context.
- ⚠️ — needs attention; a change here breaks something elsewhere.

---

## Top-level files

| Path | Status | Notes |
|---|---|---|
| `README.md` | Unmodified | Module overview / quick start. |
| `PLANNING.md` | Unmodified | Study scope, goals, status. |
| `requirements.txt` | Unmodified | Notebook/analysis deps; core is stdlib-only. |
| `CORRECTIONS.md` | (this file) | — |
| `prompt_for_garbagebread.txt` | User-created | Your copy of the original prompt. |

---

## `tournament/` package

### `tournament/__init__.py` — Unmodified ⚠️
Re-exports names from the sub-modules. **Currently stale**: it imports and lists
symbols that no longer exist after your `models.py` edits (e.g. it re-exports
things that depend on the removed `Match.winner`). Will need updating once the
model API settles.

### `tournament/models.py` — **Modified (heavily)** ⚠️
Cascade originally created these objects; your changes are noted per item.

| Symbol | Kind | Status |
|---|---|---|
| `AGENTS_TO_WIN` | constant | Unmodified |
| `BYE` | constant | Modified — added `TODO: add flag to disable byes` |
| `Player` | dataclass | Modified — added `TODO: flag to ignore skill`; requested a skill-ignoring variant |
| `Player.pid/name/skill` | fields | Unmodified |
| `Game` | dataclass | Modified |
| `Game.is_valid` | property | **Added by you** (returns `(bool, msg)`) |
| `Game.winner_is_a` | property | Modified — now `agents_a == AGENTS_TO_WIN`; decorated `@check_validity` |
| `Match` | dataclass | Modified (substantially) |
| `Match.is_valid` | property | **Added by you** |
| `Match.is_bye` | property | Modified — decorated `@check_validity` |
| `Match.agents_a` / `agents_b` | property | **Removed** → renamed to `total_agents_a` / `total_agents_b` |
| `Match.winner` | property | **Removed by you** |
| `Match.loser` | property | **Removed by you** |
| `Match.agents_for(pid)` | method | **Removed by you** |
| `Match.agents_against(pid)` | method | **Removed by you** |
| `Match.game_1_winner` / `game_2_winner` | property | **Added by you** |
| `Match.is_draw` | property | **Added by you** |
| `Match.agent_score` | property | **Added by you** |
| `Match._compute_results` / `results` | method/property | **Added by you** |
| `Round` | dataclass | Modified |
| `Round.is_valid` | property | **Added by you** |
| `Round.opponents` | method | Modified — decorated `@check_validity` |
| `Round.player_results(pid)` | method | **Added by you** |
| `Tournament` | dataclass | Modified |
| `Tournament._algorithm` | field | **Added by you** |
| `Tournament.assign_algorithm` | method | **Added by you** |
| `Tournament.player_ids` | property | Unmodified |
| `Tournament.player_by_id` | method | Unmodified |
| `Tournament.past_opponents` | method | Unmodified — you flagged "not sure if relevant" |

### `tournament/standings.py` — Unmodified ⚠️
Depends on the **old** `Match` API (`m.agents_a`, `m.agents_b`, `m.winner`).
These were renamed/removed in your `models.py`, so `compute_records` will break
until updated.
- `Record` (dataclass) + props `matches_played`, `agent_diff`, `match_points`, `record_str`
- `compute_records(tournament, through_round)`
- `rank_key(record)`
- `group_by_record(records)`

### `tournament/pairing.py` — Unmodified
- `Pairing` (type alias), `PairingContext` (dataclass), `PairingFunction` (type)
- Helpers: `_pair_sequence`, `_ordered_ids`, `_avoid_rematches`
- Within-group orderings: `_adjacent`, `_fold`, `_slide`, `_shuffle`
- `make_record_group_pairing(strategy)`, `random_pairing`
- `REGISTRY`, `get(name)`

### `tournament/generators.py` — Unmodified
- `win_probability`, `simulate_game`, `skilled_match`, `random_match`
- `MATCH_MODELS`, `make_players`

### `tournament/engine.py` — Unmodified ⚠️
Builds matches and reads `m.winner` indirectly via standings; relies on the old
`Match` API. Review after the model changes.
- `MatchModel` (type), `PairingSpec` (type)
- `_pairing_for_round(spec, round_number)`
- `run_tournament(players, n_rounds, pairing, rng, match_model)`

### `tournament/metrics.py` — Unmodified ⚠️
Uses `m.player_a/player_b` (fine) and `compute_records` (depends on standings).
- `mean_skill_gap`, `standings_skill_correlation`, `rematch_count`, `summary`

### `tournament/io.py` — Unmodified ⚠️
Reads `m.agents_a`, `m.agents_b`, `m.winner` — all renamed/removed. Will break.
- `write_matches`, `write_standings`, `write_players`, `read_matches`

---

## `scripts/`

| Path | Status | Notes |
|---|---|---|
| `scripts/_bootstrap.py` | Unmodified | Adds module root to `sys.path`; exposes `DATA_DIR`. |
| `scripts/generate_records.py` | Unmodified | CLI: `parse_args`, `main`. |
| `scripts/run_pairing.py` | Unmodified | CLI: `parse_args`, `evaluate`, `main`. |
| `scripts/utils.py` | **User-created** ⚠️ | Adds `check_validity` decorator, now imported by `models.py`. See note below. |

---

## `tests/`

| Path | Status | Notes |
|---|---|---|
| `tests/test_smoke.py` | Unmodified ⚠️ | Asserts removed API (`m.agents_a`, `m.winner`, `m.agents_b`); will fail until updated. |

Tests: `test_game_always_has_a_winner_with_three_agents`, `test_match_never_ties`,
`test_each_player_plays_once_per_round`, `test_records_match_count_consistent`,
`test_all_registered_algorithms_run`, `test_per_round_schedule`.

---

## `notebooks/` and `data/`

| Path | Status | Notes |
|---|---|---|
| `notebooks/pairing_study.ipynb` | Unmodified ⚠️ | Uses `m.agents_a/agents_b/winner`; update after model API settles. |
| `data/README.md` | Unmodified | Describes CSV layouts. |
| `data/*.csv` | Generated | `adjacent_*`, `comparison.csv` from a sample run. |

---

## `docs/`

| Path | Status | Notes |
|---|---|---|
| `docs/decisions.md` | Unmodified | Prompts + pros/cons (D1–D6). |

---

## Cross-cutting issues introduced by the model changes (for your awareness)

These are **factual consequences** of the renames/removals in `models.py`, not
new opinions:

1. **Removed `Match` API still referenced elsewhere.** `standings.py`, `io.py`,
   `engine.py` (indirectly), `tests/test_smoke.py`, and the notebook use
   `agents_a` / `agents_b` / `winner` / `agents_for` / `agents_against`. They
   need updating to `total_agents_a` / `total_agents_b` and the new `results`.
2. **`tournament/__init__.py` re-exports** symbols affected above and is stale.
3. **`scripts/utils.py`** — `from functools import wrapper` is not valid (it is
   `wraps`), and the inner function is also named `wrapper`, shadowing the import.
   As written, importing `models.py` (which imports `check_validity`) will raise
   `ImportError`.
4. **Relative import `from ..scripts.utils import check_validity`** in
   `models.py` requires `op_rules_study` to be a package and the import to be
   run as part of that package; running scripts via `_bootstrap` (which adds the
   module root to `sys.path`) makes `tournament` a top-level package with no
   parent, so `..scripts` will fail. Worth confirming the intended layout.
5. **`@check_validity` over `@property`** — decorator order means `check_validity`
   wraps the `property` object, not the underlying function; verify it behaves
   as intended.

> I have **not** changed any of your edits or fixed the items above — this file
> is purely an inventory. Tell me which of these you want me to address.
