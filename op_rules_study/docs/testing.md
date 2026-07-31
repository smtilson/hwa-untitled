# Testing Guide — op_rules_study

Run all tests from the `op_rules_study/` directory:

```bash
python -m pytest tests/ -v
```

Run a single file:

```bash
python -m pytest tests/test_models.py -v
```

---

## Unit Tests

Seven test files cover every public function and class in `tournament/`. The existing
`test_smoke.py` contains end-to-end integration smoke tests and is kept separate.

### `tests/test_models.py` — `models.py`

| Class | Tests |
|---|---|
| `TestPlayer` | Field storage, default `skill=0.0`, frozen (mutation raises), inequality of different pids |
| `TestGame` | Valid game (A wins, B wins), invalid (A > 3, B > 3, tie), `winner_is_a` True/False/raises on invalid |
| `TestMatchValidity` | Valid 2-game match, invalid with 1 game, 0 games, same player |
| `TestMatchAgentTotals` | `total_agents_a/b` without bonus, with `bonus_agents_a`, with `bonus_agents_b` |
| `TestMatchOutcome` | `game_1_winner`/`game_2_winner` for A-wins and B-wins cases, `is_draw` True/False, `winner` A/B/None, `agent_score` tuple |
| `TestMatchResults` | Both players in dict, game wins/losses for winner and loser and draw, `player_agents`/`opponent_agents`, `opponent` field, `bonus_agents` field, caching |
| `TestRound` | `is_valid` propagates match invalidity, `opponents()` full map, `player_results()`, `overall_results` structure |
| `TestTournament` | `player_ids`, `player_by_id` found/missing, `past_opponents` after 2 rounds, empty before rounds, `assign_algorithm` |

**Total: ~55 assertions**

---

### `tests/test_generators.py` — `generators.py`

| Class | Tests |
|---|---|
| `TestScoreAgentProbability` | Equal skills → 0.5, A stronger → > 0.5, B stronger → < 0.5, result in (0,1), symmetric |
| `TestTieBreakBonus` | No tie → (0,0), tied → sum=1, prob=1.0 always awards A, prob=0.0 always awards B |
| `TestSkillGame` | Always has a winner at AGENTS_TO_WIN, no tied agents, game is valid, strong player wins more often |
| `TestRandomGame` | Always has winner, no tied agents, game is valid |
| `TestSkilledMatch` | Two games, match is valid, agent totals never tied, strong player wins more (200 trials), player ids set, result keys are pids |
| `TestRandomMatch` | Two games, valid, totals never tied, win rate ~50% despite extreme skill difference |
| `TestMakePlayers` | Correct count, pids start from 0 and are sequential, raises on odd `n`, skills ~Normal(0,1) |
| `TestMatchModels` | Registry contains "skilled" and "random", all values callable |

**Total: ~34 assertions**

---

### `tests/test_standings.py` — `standings.py`

| Class | Tests |
|---|---|
| `TestRecordProperties` | Default zeros, `matches_played` for wins/draws, `agent_diff`, `agent_ratio`, ratio=0 on no games, `record_str` format |
| `TestRecordAgentSeq` | Built from raw results, empty for new record, cached, invalidated by `process_result`, `agent_score` applies metric |
| `TestRecordProcessResult` | Wins/losses/agents/bonus all accumulate correctly |
| `TestRecordFromRawResults` | Builds from list, raises on empty list |
| `TestAgentDifferential` | Positive, negative, empty sequence, symmetric (zero-diff) |
| `TestMakeRankKey` | Returns callable, default returns `agent_differential`, custom metric used, None falls back to default, sorting order |
| `TestComputeRecords` | All players returned, match count after all rounds, winner has more game wins, `through_round` limits data, empty tournament zeros |
| `TestGroupByRecord` | Groups by wins-losses format, best group first, all players present |
| `TestSortGroups` | Within-group sorted best first, custom metric applied, keys unchanged |
| `TestMakeGroupsEven` | All-even groups produce even output, odd total raises, odd groups carry players forward without dropping them, all output groups even, keys get `~` appended |
| `TestCreateRankedEvenGroups` | Returns dict, all groups even, accepts custom `rating_fn` |

**Total: ~47 assertions**

> **Current policy:** `group_by_record` forms and orders win/loss record buckets.
> Metric-based ordering is only for sorting within those buckets via `sort_groups` /
> `make_rank_key`, and `make_groups_even` preserves all players for even-sized fields
> or raises for odd totals.

---

### `tests/test_pairing.py` — `pairing.py`

| Class | Tests |
|---|---|
| `TestPairingContext` | Stores `past_opponents` and `round_number` |
| `TestPairSequence` | Basic pairing, 6 players, odd length raises, empty input |
| `TestOrderedIds` | Returns all pids, higher agent_diff first |
| `TestAvoidRematches` | No rematches → unchanged, rematch → swapped, same length, does not mutate input |
| `TestAdjacent` | Identity order, does not mutate |
| `TestFold` | 4-player layout [0,2,1,3], 6-player layout, output length |
| `TestStrongWeak` | 4-player layout [0,3,1,2], 6-player layout, output length |
| `TestShuffle` | Same elements, does not mutate input |
| `TestMakeRecordGroupPairing` | Returns callable, unknown strategy raises, correct pair count, all players appear, no self-pairing, function name reflects strategy, custom metric accepted |
| `TestRandomPairing` | Correct pair count, all players appear exactly once, no self-pairing |
| `TestRegistry` | Expected keys present, all values callable, `get` returns correct fn, `get` raises for unknown, all strategies produce valid pairings |

**Total: ~44 assertions**

---

### `tests/test_engine.py` — `engine.py`

| Class | Tests |
|---|---|
| `TestPairingForRound` | Callable → itself (any round), sequence indexed by round, sequence clamped at last, mapping exact match, mapping fallback to latest key, mapping fallback before any key |
| `TestRunTournament` | Correct round count, match count per round, each player once per round, sequential round numbers, list spec accepted, dict spec accepted, custom `match_model` used, records consistent with round count, all strategies run without error |

**Total: ~15 assertions**

---

### `tests/test_metrics.py` — `metrics.py`

| Class | Tests |
|---|---|
| `TestMeanSkillGap` | Returns float, empty tournament → 0.0, non-negative, equal-skill players → gap=0, random pairing > skill-based pairing over 30 trials |
| `TestStandingsSkillCorrelation` | Returns float, value in [-1,1], single player → 0.0, positive for skill-based simulation, perfect correlation known case |
| `TestRematchCount` | Returns int, zero for single round, counts extra meetings correctly, triple meeting counts as 2 |
| `TestSummary` | Returns dict, expected keys present, `rounds` matches actual, `players` matches count, values match individual functions |

**Total: ~19 assertions**

---

### `tests/test_io.py` — `io.py`

| Class | Tests |
|---|---|
| `TestMatchWinner` | Returns player id for win, returns `""` for draw |
| `TestFieldConstants` | `MATCH_FIELDS`/`STANDINGS_FIELDS` are non-empty lists, required columns present |
| `TestWriteMatches` | Creates file, header matches MATCH_FIELDS, row count equals total matches, bonus agents stored, creates parent directories |
| `TestWriteStandings` | Creates file, `every_round=True` → n_players × n_rounds rows, `every_round=False` → n_players rows, header matches STANDINGS_FIELDS |
| `TestWritePlayers` | Creates file, row count equals player count, header contains "skill" |
| `TestReadMatches` | Round-trip round count, match count, bonus agents preserved, player ids preserved, restored matches are valid |

**Total: ~19 assertions**

---

## Integration Tests — Outstanding (to be written by you)

These tests cross module boundaries and verify the full simulation pipeline. They are
not yet implemented but should be before the study results are considered final.

### I1 — Full pipeline correctness
Verify that a complete `run_tournament` → `compute_records` → `group_by_record` →
pairing cycle produces sensible output at scale (e.g. 32 players, 6 rounds).  
Check: no player appears in two groups, no group is empty, total players in groups == field size.

### I2 — CSV round-trip with full standings
`run_tournament` → `write_matches` + `write_standings` + `write_players` →
`read_matches` → `compute_records`.  
Check that the recomputed records from the CSV-restored tournament match the
original records field-by-field.

### I3 — Per-round schedule changes
Run a tournament with `pairing={1: random, 2: adjacent, 3: fold}` and verify that
the pairing function actually changed each round (e.g. by checking that round 1
pairs are not record-ordered while round 2 pairs are).

### I4 — make_groups_even feeding into pairing
Call `create_ranked_even_groups` and pass the result to a pairing strategy.  
Check: no `ValueError` from `_pair_sequence`, total pairs == len(players) // 2,
no player appears twice.

### I5 — Metrics monotonicity over rounds
For `adjacent` pairing, verify that `mean_skill_gap` decreases (or stays stable) as
more rounds are played — i.e. the pairing gets better as records differentiate.

### I6 — Rematch avoidance effectiveness
Run a 4-player tournament for 3 rounds (where rematches are mathematically unavoidable)
and verify that `_avoid_rematches` reduces rematches compared to a naive pairing
(no swap pass) on the same sorted order.

### I7 — summary vs. individual metrics idempotency
Call `summary(tour)` twice; both calls should return identical values. (Guards against
mutable state bugs in `compute_records` or the metric functions.)

### I8 — Skill-blind vs. skilled match model
Run two identical tournaments (same seed, same pairing, same players) — one with
`skilled_match` and one with `random_match`. Verify that:
- `standings_skill_correlation` is higher for the skilled run.
- Both runs produce the same number of rounds and matches.
