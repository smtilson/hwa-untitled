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

- [ ] `tournament/generators.py` — produces results from `Player`s (imported by
      `engine`). Review `score_agent_probability`, `simulate_game`,
      `skilled_match`, `random_match`, `make_players`.
- [ ] `tournament/standings.py` — turns a `Tournament` into per-player `Record`s.
      Cascade **re-synced** this to the new `results` keys and `rank_key`; review
      that the `Record` definition and ranking match your scoring (`decisions.md` D4).
- [ ] `tournament/pairing.py` — consumes `standings` (`Record`, `group_by_record`,
      `rank_key`). `PairingContext`, the ordering strategies
      (`_adjacent`/`_fold`/`_slide`/`_shuffle`), `make_record_group_pairing`,
      `REGISTRY`, `get`. Check `_pair_sequence` / `_avoid_rematches` logic.
- [ ] `tournament/engine.py` — orchestrates generators + pairing + standings.
      `run_tournament`, `_pairing_for_round`. Confirm the round loop matches the
      intended event flow.
- [ ] `tournament/metrics.py` — evaluates a finished tournament. `mean_skill_gap`,
      `standings_skill_correlation`, `rematch_count`, `summary`. Decide which
      metrics you actually want.
- [ ] `tournament/io.py` — persists a finished tournament. `write_matches` /
      `write_standings` / `write_players` / `read_matches` and the CSV field schemas.
- [~] `tournament/__init__.py` — re-exports the whole package surface (review
      after the leaf modules settle). Still references removed `BYE` and renamed
      `win_probability`. Confirm the intended public API surface.
- [ ] `scripts/_bootstrap.py`, `scripts/generate_records.py`,
      `scripts/run_pairing.py` — CLI entry points over the package. Behaviour and
      arg surfaces.
- [ ] `tests/test_smoke.py` — confirm the assertions reflect the rules you want.
- [ ] `notebooks/pairing_study.ipynb` — walkthrough; review after the API settles.
- [ ] `requirements.txt` — confirm pinned deps are acceptable.

---

## 2. Make the package import / run again

Currently `import tournament` fails. Fix the modules **in dependency order**
(same bottom-up flow as §1) so each layer compiles before the one above it.
Details in `CORRECTIONS.md` → "Still open". Settle the blocking design decisions
in §3 first (draws/sudden-death affects `generators`; even-field affects
`pairing`/`engine`).

- [ ] **`generators.py`.** Replace the remaining `win_probability` calls in
      `simulate_game` / `skilled_match` with `score_agent_probability`; update the
      sudden-death loops to use `total_agents_a` / `total_agents_b` instead of
      `agents_a` / `agents_b`.
- [ ] **`standings.py`.** Remove `from .models import BYE` and the bye branch in
      `compute_records` (and the `byes` field) once byes are dropped.
- [ ] **`pairing.py`.** Remove the `BYE` import and rewrite `_pair_sequence` so a
      trailing odd player no longer gets a bye (require an even order).
- [ ] **`engine.py`.** Remove the `BYE` import and the `if b == BYE` branch in
      `run_tournament`; enforce an **even player count** when seeding the field.
- [ ] **`metrics.py`.** Remove the `m.is_bye` checks in `mean_skill_gap` /
      `rematch_count`.
- [ ] **`io.py`.** Rewrite `MATCH_FIELDS` / `STANDINGS_FIELDS` and the read/write
      functions for the new `results` shape and `Record` fields
      (`wins`/`losses`/`agent_*`, not `match_wins`/`match_points`); drop `is_bye`.
- [~] **`__init__.py`.** Finish removing `BYE` / `win_probability` from the
      re-exports and `__all__` (in progress).
- [ ] **`tests/test_smoke.py`.** Update to the new API (drop `m.agents_a` /
      `m.winner` / `m.is_bye`); get the smoke suite green.
- [ ] **`notebooks/pairing_study.ipynb`.** Update once the API is stable.

---

## 3. Open design decisions to settle

- [ ] **Draws vs. sudden death (D7).** The generators still *append* sudden-death
      games, which conflicts with `Match.is_valid` requiring exactly two games.
      Decide: allow drawn matches (current model) **or** restore sudden death and
      relax the two-game check. Update `models.py` + `decisions.md` accordingly.
- [ ] **Scoring / record definition (D4).** Lock down what a "record" is (game
      wins vs. match points vs. agent totals) and align `standings.Record` /
      `rank_key`.
- [ ] **Even-field policy.** Confirm the "force even number of players" rule and
      where it is enforced/validated.
- [ ] **Skill-ignore flag.** Resolve the `models.py` `# Windsurf:` request — add a
      `use_skill`-style flag in the relevant generator functions (or document the
      `random_match` vs `skilled_match` registry as the mechanism).
- [ ] **Evaluation metrics.** Decide which metrics matter (the `metrics.py`
      `# Windsurf:` note); prune or extend `summary`.

---

## 4. Documentation follow-ups (pending `# Windsurf:` comments)

- [ ] Document the resolved import/decorator fix (`tournament/utils.py`,
      `models.py`) in `PLANNING.md`, then delete the resolved review comments.
- [ ] Add a `PLANNING.md` section explaining `score_agent_probability` (the
      logistic skill→agent model) and possible alternative functions.
- [ ] Verify `README.md` / `PLANNING.md` state clearly that **agent totals do not
      decide the match** (only the games do); then drop the `is_draw`
      `# Windsurf:` comment in `models.py`.
- [ ] Keep `CORRECTIONS.md` in sync as files are fixed (move items to Finished).

---

## 5. Build out the study (after the package runs)

From `PLANNING.md` §3:

- [ ] Compare pairing families across player counts and round counts.
- [ ] Study changing the pairing function between rounds (`--schedule`).
- [ ] Examine manipulability (can a player game placement via intentional
      draws / agent dumping?).
- [ ] Weigh player comprehensibility of each algorithm (qualitative).
- [ ] Investigate alternative tiebreakers in `standings.rank_key`.
