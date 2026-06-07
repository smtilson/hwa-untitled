# Corrections / Inventory

Inventory of everything **Cascade created** for `op_rules_study/`, with a status
flag for whether **you (the user) have since modified it**.

Legend:
- **Unmodified** — still as Cascade wrote it.
- **Modified** — edited since (by you or Cascade; noted).
- **User-created** — file you added yourself (not by Cascade), listed for context.
- ✅ — a previously-flagged issue is now resolved.
- ⚠️ — still needs attention; a change here breaks something elsewhere.

_Updated to reflect the current state of the files: the model redesign (draws,
the `results` dict, the validity layer), the **bye removal**, and the
`standings.py` re-sync. Entries are split into **Finished** (no further action
needed on that file) and **Unfinished** (still breaks something / needs work).
Both sections use the same internal organization._

---

# Finished ✅

Files whose flagged corrections are fully resolved and need no further edits.

## Top-level files

| Path | Status | Notes |
|---|---|---|
| `README.md` | Modified (Cascade) | Model section rewritten for the revised `Game`/`Match`/`Round`/`Tournament`; `results` keys updated to `player_agents`/`opponent_agents`; clarified that agent totals don't decide the match. Retains `<!-- Sean Bye comment -->` markers for your pending bye decision. |
| `PLANNING.md` | Modified (Cascade) | §1 rewritten for the new model; §5b changelog incl. bye removal; D4/D7 refs. |
| `requirements.txt` | Unmodified | Notebook/analysis deps; core is stdlib-only. |
| `CORRECTIONS.md` | (this file) | Reorganised into Finished / Unfinished. |
| `prompt_for_garbagebread.txt` | User-created | Your copy of the original prompt. |

## `tournament/` package

### `tournament/utils.py` — **User-created (moved here from `scripts/`)** ✅
- `check_validity(func)` decorator. **Fixed:** `from functools import wraps`
  and `@wraps(func)`; the import + decorator now work.
- The earlier `is_bye`/bye-match validity caveat is **obsolete** (byes removed).
- Only remaining item is a cosmetic `# Windsurf:` request to delete resolved
  review comments (tracked under Pending requests below).

## `scripts/`

| Path | Status | Notes |
|---|---|---|
| `scripts/_bootstrap.py` | Unmodified | Adds module root to `sys.path`; exposes `DATA_DIR`. No changes needed. |
| `scripts/generate_records.py` | Unmodified | CLI: `parse_args`, `main`. No file-level changes needed; only blocked transitively by the `tournament` import errors (see Unfinished). |
| `scripts/run_pairing.py` | Unmodified | CLI: `parse_args`, `evaluate`, `main`. Same transitive block. |
| `scripts/utils.py` | **Moved → `tournament/utils.py`** ✅ | No longer here. |

## `notebooks/` and `data/`

| Path | Status | Notes |
|---|---|---|
| `data/README.md` | Modified (Cascade) | CSV layouts + `results`-shape note; agents keys updated to `player_agents`/`opponent_agents`. Retains a `<!-- Sean Bye comment -->`. |
| `data/*.csv` | Generated | `adjacent_*`, `comparison.csv` from a sample run. |

## `docs/`

| Path | Status | Notes |
|---|---|---|
| `docs/decisions.md` | Modified (Cascade) | Prompts + pros/cons **D1–D7** (D4/D5 updated for the results shape; D7: draws vs. sudden death). D5 flagged that byes were removed; retains a `<!-- Sean Bye comment -->`. |

---

# Unfinished ⚠️

Files that still break something or have open items, organised the same way.

## `tournament/` package

### `tournament/__init__.py` — Unmodified ⚠️
Two import-time failures on `import tournament`:
- imports `BYE` from `models`, but `BYE` was **removed** → `ImportError`.
- imports (and `__all__` lists) `win_probability` from `generators`, which was
  renamed to `score_agent_probability` → `ImportError`.
It also re-exports `compute_records`/`run_tournament`/`summary`, which break at
runtime (old `Match` API + removed `BYE`).

### `tournament/models.py` — **Modified (heavily)** ⚠️
Importable on its own (given `utils.py`). Most prior issues are now fixed; only
documentation/review-comment items remain:
- ✅ **Caching guards fixed.** `results` / `overall_results` now guard on
  `if self._results is None:` / `if self._overall_results is None:` (the old
  `hasattr` check was always true under `slots`, so the value never computed).
- ✅ **Stale bye references removed.** The `BYE` constant + its long review
  comment, the `Match` docstring's `player_b == BYE` line, the `is_valid`
  `# Sean Update` bye note, and the `past_opponents` "(excludes byes)" docstring
  are all gone.
- Pending `# Windsurf:` requests (document the import/decorator fix in the
  planning doc then delete the resolved review comments; the `is_draw` naming
  debate near the `is_draw` property; the skill-ignoring-flag discussion).

| Symbol | Kind | Status |
|---|---|---|
| `AGENTS_TO_WIN` | constant | Unmodified |
| `BYE` | constant | **Removed by Sean** — byes deleted from the model |
| `Player` | dataclass | Modified — added `TODO: flag to ignore skill`; requested a skill-ignoring variant |
| `Player.pid/name/skill` | fields | Unmodified |
| `Game` | dataclass | Modified |
| `Game.is_valid` | property | **Added by you** (returns `(bool, msg)`) |
| `Game.winner_is_a` | property | Modified — now `agents_a == AGENTS_TO_WIN`; decorated `@check_validity` |
| `Match` | dataclass | Modified (substantially) |
| `Match.is_valid` | property | **Added by you** |
| `Match.is_bye` | property | **Removed by Sean** — byes deleted |
| `Match.agents_a` / `agents_b` | property | **Removed** → renamed to `total_agents_a` / `total_agents_b` |
| `Match.winner` | property | **Removed by you** |
| `Match.loser` | property | **Removed by you** |
| `Match.agents_for(pid)` | method | **Removed by you** |
| `Match.agents_against(pid)` | method | **Removed by you** |
| `Match.game_1_winner` / `game_2_winner` | property | **Added by you** |
| `Match.is_draw` | property | **Added by you** |
| `Match.agent_score` | property | **Added by you** |
| `Match._compute_results` / `results` | method/property | **Added by you** — `results` dict keys: `id`, `wins`, `losses`, `player_agents`, `opponent_agents`, `opponent` (+ top-level `is_draw`) |
| `Round` | dataclass | Modified |
| `Round.is_valid` | property | **Added by you** |
| `Round.opponents` | method | Modified — decorated `@check_validity`; bye branch removed |
| `Round.player_results(pid)` | method | **Added by you** |
| `Round._compute_overall_results` / `overall_results` | method/property | **Added by you** (sole builder; the old `_calculate_overall_results` duplicate is gone) |
| `Tournament` | dataclass | Modified |
| `Tournament._algorithm` | field | **Added by you** |
| `Tournament.assign_algorithm` | method | **Added by you** |
| `Tournament.player_ids` | property | Unmodified |
| `Tournament.player_by_id` | method | Unmodified |
| `Tournament.past_opponents` | method | Modified — bye filter removed |

### `tournament/standings.py` — **Modified (Cascade)** ⚠️
Re-synced to the new per-player `results` dict (`player_agents` /
`opponent_agents`) and the new `rank_key` (`wins`, `agent_ratio`, `agent_diff`).
**But** it still `from .models import BYE` and contains bye handling
(`# Sean remove byes`), and `BYE` no longer exists → `ImportError`. Resolve when
byes are removed downstream.
- `Record` (dataclass) + props `matches_played`, `agent_diff`, `agent_ratio`,
  `record_str`, `agent_seq`; methods `agent_score`, `process_result`,
  `from_raw_results` (no more `match_points`)
- `compute_records(tournament, through_round)`
- `rank_key(record)`
- `group_by_record(records)`

### `tournament/pairing.py` — Unmodified ⚠️
`from .models import BYE` and `_pair_sequence` assigns `BYE` to a trailing odd
player — `BYE` was removed → `ImportError`. Otherwise unchanged.
- `Pairing` (type alias), `PairingContext` (dataclass), `PairingFunction` (type)
- Helpers: `_pair_sequence`, `_ordered_ids`, `_avoid_rematches`
- Within-group orderings: `_adjacent`, `_fold`, `_slide`, `_shuffle`
- `make_record_group_pairing(strategy)`, `random_pairing`
- `REGISTRY`, `get(name)`

### `tournament/generators.py` — **Modified** ⚠️
- `win_probability` was **renamed to `score_agent_probability`**, but
  `simulate_game` and `skilled_match` still **call `win_probability`** →
  `NameError` at call time.
- Sudden-death loops still use the old `match.agents_a`/`agents_b`
  (now `total_agents_a`/`total_agents_b`) → `AttributeError`.
- A `# Windsurf:` comment requests a planning-doc section explaining the choice
  of `score_agent_probability` and possible alternatives (TODO).
- Symbols: `score_agent_probability`, `simulate_game`, `skilled_match`,
  `random_match`, `MATCH_MODELS`, `make_players`.

### `tournament/engine.py` — Unmodified ⚠️
`from .models import BYE` and `if b == BYE` in the round loop — `BYE` removed →
`ImportError`. Also depends on `standings`/`generators`, which are broken.
- `MatchModel` (type), `PairingSpec` (type)
- `_pairing_for_round(spec, round_number)`
- `run_tournament(players, n_rounds, pairing, rng, match_model)`

### `tournament/metrics.py` — Unmodified ⚠️
`mean_skill_gap` and `rematch_count` call `m.is_bye`, which was **removed** from
`Match` → `AttributeError`. Depends on `compute_records` (standings). A new
`# Windsurf:` comment notes you're undecided on which evaluation metrics to use.
- `mean_skill_gap`, `standings_skill_correlation`, `rematch_count`, `summary`

### `tournament/io.py` — Unmodified ⚠️
- `from .models import BYE` (removed) → `ImportError`.
- `write_matches` reads `m.agents_a`/`agents_b`/`winner`/`is_bye` (renamed/removed).
- `write_standings` reads `rec.match_wins`/`match_losses`/`match_points`, none of
  which exist on the current `Record` (use `wins`/`losses`/`agent_*`).
- `MATCH_FIELDS` / `STANDINGS_FIELDS` schemas need updating to the `results` shape.
- `write_matches`, `write_standings`, `write_players`, `read_matches`

## `tests/`

| Path | Status | Notes |
|---|---|---|
| `tests/test_smoke.py` | Unmodified ⚠️ | `test_match_never_ties` asserts `m.agents_a`/`m.winner` (removed); every test using `run_tournament`/`compute_records` fails until `generators`/`standings`/`BYE` are fixed. |

Tests: `test_game_always_has_a_winner_with_three_agents`, `test_match_never_ties`,
`test_each_player_plays_once_per_round`, `test_records_match_count_consistent`,
`test_all_registered_algorithms_run`, `test_per_round_schedule`.

## `notebooks/`

| Path | Status | Notes |
|---|---|---|
| `notebooks/pairing_study.ipynb` | Unmodified ⚠️ | Uses `m.agents_a/agents_b/winner` and `match_points`; update after the API settles. |

---

## Cross-cutting status (updated)

**Resolved ✅**
1. **Validity decorator** — `scripts/utils.py` moved to `tournament/utils.py`
   and fixed (`wraps` + `@wraps(func)`); no longer fails on import.
2. **Relative import** — `models.py` now uses `from .utils import check_validity`
   instead of the broken `..scripts.utils`.
3. **Decorator order** — `@property` is now outermost everywhere in `models.py`.
4. **`slots=True` attribute error** — fixed by declaring `_results` /
   `_overall_results` as `field(default=None, init=False)`.
5. **`models.py` caching guards** — `results` / `overall_results` now use
   `is None` checks, so the cached dicts are actually computed.
6. **Stale bye references in `models.py`** — `BYE`, the `Match` docstring/`is_valid`
   bye notes, and the `past_opponents` bye docstring were all removed.
7. **Duplicate round-result builders** — only `_compute_overall_results` remains.
8. **Docs + standings re-sync** — `README`, `PLANNING`, `docs/decisions.md`,
   `data/README` updated for the new model; `standings.py` re-synced to
   `player_agents`/`opponent_agents` and the new `rank_key`.

**Still open ⚠️**
1. **`BYE` removal fallout.** `__init__`, `standings`, `pairing`, `engine`, `io`
   still `import BYE`; `metrics` calls `m.is_bye`; tests assume byes. All break
   until they require an even field / drop bye handling.
2. **`generators.py` rename fallout.** `win_probability` →
   `score_agent_probability` not propagated to `simulate_game` / `skilled_match`
   or to `__init__.py` → `NameError` / `ImportError`.
3. **Old `Match` API.** `generators` sudden-death (`agents_a/b`), `io`, tests, and
   the notebook still use `agents_a`/`agents_b`/`winner`.
4. **`io` ↔ `Record` schema drift.** `write_standings` reads `match_wins` /
   `match_losses` / `match_points`; the current `Record` exposes `wins` /
   `losses` / `agent_ratio` / `agent_diff`. CSV schemas need a rewrite.

**Pending requests embedded as `# Windsurf:` comments (not yet actioned):**
- `tournament/utils.py` & `models.py`: document the import/decorator fix in the
  planning doc, then delete the resolved review comments; resolve the `is_draw`
  naming debate.
- `generators.py`: add a planning-doc section on `score_agent_probability` and
  alternative skill→result functions.
- `metrics.py`: decide on evaluation metrics (you noted you're agnostic).

> This file is an inventory only — no code behaviour was changed while updating it.
