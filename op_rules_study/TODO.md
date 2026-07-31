# TODO — op_rules_study

Working task list for the tournament pairing study. Scoped to `op_rules_study/`
only. See `CORRECTIONS.md` for the per-file inventory and `PLANNING.md` for the
study design / open decisions.

Legend: `[ ]` todo · `[~]` in progress · `[x]` done.

---

## 1. Review Cascade-written code not yet reviewed

These files were written by Cascade and you have **not** yet reviewed or marked
them (no `# Sean Update` / edits). Read them against the revised model
(`results` dict, validity layer, no byes) and flag anything to change.

Ordered **bottom-up by dependency / code flow** — start at the foundation
(`models` → generators/standings → pairing → engine) and finish at the entry
points (`__init__` → scripts → tests → notebook).

- [x] `tournament/generators.py` — reviewed; `_tie_break_bonus`, `skilled_match`,
      `random_match` aligned and layout-matched; bonus agents passed to `Match`
      constructor.
- [x] `tournament/standings.py` — reviewed; `bonus_agents_won` added to `Record`;
      `make_rank_key` (wins primary, agent metric secondary); two-step API:
      `group_by_record` (pure grouping, numeric group ordering) + `sort_groups`
      (ranks within each group by metric).
- [x] `tournament/pairing.py` — reviewed; `_slide` replaced with `_strong_weak`
      (best vs. worst within group); `strong_weak` added to `_WITHIN_GROUP` and
      `REGISTRY`; `make_record_group_pairing` uses `create_ranked_even_groups`
      (`group_by_record` → `sort_groups` → `make_groups_even`) so every bracket
      has an even number of players before the within-group strategy is applied.
- [ ] `tournament/engine.py` — orchestrates generators + pairing + standings.
      `run_tournament`, `_pairing_for_round`. Confirm the round loop matches the
      intended event flow.
- [ ] `tournament/metrics.py` — evaluates a finished tournament. `mean_skill_gap`,
      `standings_skill_correlation`, `rematch_count`, `summary`. Decide which
      metrics you actually want.
- [ ] `tournament/io.py` — persists a finished tournament. `write_matches` /
      `write_standings` / `write_players` / `read_matches` and the CSV field schemas.
- [x] `tournament/presentation.py` — display functions for tournament results.
      `display_round`, `display_tournament_summary`, `display_stacked_rounds`,
      `display_match_details`, `display_player_performance`, `display_skill_statistics`,
      `display_metrics`, `display_metrics_comparison`. Added to package exports.
      **Needs review** — verify display functions work correctly and formatting is appropriate.
- [ ] `tournament/rating.py` — rating functions for player performance.
      Basic functions: `total_agents_scored`, `total_agents_lost`, `agent_differential`,
      `agent_ratio`, `agent_total_ratio`. Weighted versions with weight sequences.
      Utility functions: `linear_weights`, `exponential_weights`. Added to package exports.
      **Needs review** — verify rating functions produce correct values and weighted versions work properly.
- [~] `tournament/__init__.py` — re-exports the whole package surface; `BYE`/
      `win_probability` removed; `make_rank_key`, `sort_groups`, `make_groups_even`,
      and `create_ranked_even_groups` added; presentation and rating functions added.
      Review once remaining leaf modules (`engine`, `metrics`, `io`) settle.
- [ ] `scripts/_bootstrap.py`, `scripts/generate_records.py`,
      `scripts/run_pairing.py` — CLI entry points over the package. Behaviour and
      arg surfaces.
- [ ] `tests/test_smoke.py` — confirm the assertions reflect the rules you want.
- [~] `tests/test_*.py` — **unit tests written** (7 files, ~230 assertions across all modules). **Review required** — see §6.
- [x] `notebooks/reference/` — one demo notebook per module, created and
      executed successfully against the current API. Reviewed:
  - [x] `1_models.ipynb`
  - [x] `2_generators.ipynb`
  - [x] `3_standings.ipynb` — includes `Record.player` / `skill` / `name` demo
  - [ ] `4_pairing.ipynb`
  - [ ] `5_engine.ipynb`
  - [ ] `6_rating.ipynb`
  - [ ] `7_metrics.ipynb`
- [ ] `notebooks/pairing_study.ipynb` — walkthrough; review after the API settles.
- [x] `notebooks/Study.ipynb` — rating-function study. Refactored to include a `seed` parameter and swept across 10 seeds; analysis outputs updated. Needs review of presentation and interpretation.
- [ ] `requirements.txt` — confirm pinned deps are acceptable.

---

## 2. Make the package import / run again

Currently `import tournament` fails. Fix the modules **in dependency order**
(same bottom-up flow as §1) so each layer compiles before the one above it.
Details in `CORRECTIONS.md` → "Still open". Settle the blocking design decisions
in §3 first (draws/sudden-death affects `generators`; even-field affects
`pairing`/`engine`).

- [x] **`generators.py`.** Sudden death removed (D7 Option A); `skilled_match` /
      `random_match` produce exactly two games via `score_agent_probability`.
- [x] **`standings.py`.** Removed `from .models import BYE`, the bye branch in
      `compute_records`, and the `byes` field.
- [x] **`pairing.py`.** `BYE` import removed; `_pair_sequence` now raises on an
      odd order (even field required).
- [x] **`engine.py`.** `BYE` import and `if b == BYE` branch removed.
- [x] **`metrics.py`.** `m.is_bye` checks removed in `mean_skill_gap` /
      `rematch_count`.
- [x] **`io.py`.** Rewrote `MATCH_FIELDS` (per-game) / `STANDINGS_FIELDS`
      (`game_wins`/`game_losses`/`agent_ratio`) and the read/write functions;
      `read_matches` rebuilds valid two-game matches.
- [x] **`__init__.py`.** `BYE` / `win_probability` removed from re-exports.
- [x] **`tests/test_smoke.py`.** Updated to the new API; suite is green (6 pass).
- [ ] **`notebooks/pairing_study.ipynb`.** Update once the API is stable.

---

## 3. Open design decisions to settle

- [x] **Draws vs. sudden death (D7).** RESOLVED — Option A: draws allowed, no
      sudden death. Generators produce exactly two games; `Match.is_valid` no
      longer rejects tied agent totals. Updated `models.py`, `generators.py`,
      `decisions.md`, `PLANNING.md`, `README.md`.
- [x] **Scoring / record definition (D4).** RESOLVED — records aggregate
      game-level wins/losses; `group_by_record` orders win/loss buckets, and
      `make_rank_key` returns only the within-group agent metric.
- [x] **Even-field policy.** RESOLVED — byes are removed; `make_players` rejects
      odd player counts and `_pair_sequence` raises on odd orders.
- [x] **Skill-ignore flag.** RESOLVED — `random_match` is the skill-blind result
      model; `skilled_match` is the skill-aware model, selectable via `match_model`.
- [ ] **Evaluation metrics.** Decide which metrics matter (the `metrics.py`
      `# Windsurf:` note); prune or extend `summary`.

---

## 4. Documentation follow-ups (pending `# Windsurf:` comments)

- [x] Documented the resolved import/decorator fix (`tournament/utils.py`,
      `models.py`) in `PLANNING.md` §5b; deleted the resolved review comments.
- [x] Added `PLANNING.md` §5c explaining `score_agent_probability` (logistic
      skill→agent model) and alternative functions.
- [x] `README.md` / `PLANNING.md` state that **agent totals do not decide the
      match**; dropped the `is_draw` `# Windsurf:` comment in `models.py`.
- [ ] Keep `CORRECTIONS.md` in sync as files are fixed (move items to Finished).

---

## 6. Testing — review and complete

Unit tests have been reorganized into module-specific directories with class-based groupings:
- `tests/models/` — Player, Game, Match, Round, Tournament
- `tests/generators/` — score_agent_probability, tie_break_bonus, skill_game, random_game, skilled_match, random_match, make_players, MATCH_MODELS
- `tests/standings/` — Record, agent_differential, make_rank_key, compute_records, group_by_record, sort_groups, make_groups_even, create_ranked_even_groups
- `tests/pairing/` — PairingContext, pair_sequence, ordered_ids, avoid_rematches, ordering_strategies, make_record_group_pairing, random_pairing, registry
- `tests/engine/` — pairing_for_round, run_tournament
- `tests/metrics/` — mean_skill_gap, standings_skill_correlation, rematch_count, summary
- `tests/io_tests/` — match_winner, field_constants, write_matches, write_standings, write_players, read_matches

- [x] **Review/fix standings unit tests** against the source — `Record.wins` /
      `losses` are game-level; `make_rank_key` returns only the within-group
      agent metric; the unused `group_by_record` `rating_fn` test was removed.
- [x] **Fix or remove tests that encoded unintended behaviour** for standings.
- [x] **Reorganize tests into module-specific directories** with class-based groupings for better digestibility.
- [ ] **Review each test file** to verify it is testing the correct behavior after the reorganization.
- [ ] **Write the 8 integration tests** outlined in `docs/testing.md` §"Integration Tests".
- [x] **Run the full suite** and confirm all tests pass:
      `/home/smtilson/repos/hwa-untitled/.venv/bin/python -m pytest tests/ -q`
      from `op_rules_study/` → 234 passed.
- [x] **Investigate `make_groups_even` edge case** — odd total player counts now
      raise instead of silently dropping a player; even totals preserve all players.
- [x] **Investigate `group_by_record` `rating_fn` parameter** — removed the unused
      parameter; within-group ranking belongs in `sort_groups`.

---

## 7. Build out the study (after the package runs)

From `PLANNING.md` §3:

- [x] Compare rating functions across player counts, round counts, and seeds (`notebooks/Study.ipynb`). Analysis outputs produced; presentation and interpretation still need review.
- [ ] Compare pairing families across player counts and round counts.
- [ ] Study changing the pairing function between rounds (`--schedule`).
- [ ] Examine manipulability (can a player game placement via intentional
      draws / agent dumping?).
- [ ] Weigh player comprehensibility of each algorithm (qualitative).
- [ ] Investigate alternative tiebreakers in `standings.make_rank_key`.
