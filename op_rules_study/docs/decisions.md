# Decision Log — prompts, options, pros & cons

This file is a living record of the design choices the study must make. Each
section states the decision, the options, and pros/cons. **Conclusions are left
open on purpose** — fill them in as the study progresses.

---

## D1. How should results be generated?

**Prompt:** Should records be essentially random, drawn from a distribution, or
simulated round-by-round from latent skill?

### Option A — Pure random results (`generators.random_match`)

- **Pros:** Trivial; no assumptions; good null model to check that "good"
  pairing metrics aren't an artifact of the metric itself.
- **Cons:** No ground-truth strength exists, so "pairing people of comparable
  strength" is undefined — can only measure structural properties (rematches).

### Option B — Skill-based simulation (`generators.skilled_match`)

- **Pros:** Each player has a latent `skill`; agents are Bernoulli trials with a
  logistic (Bradley-Terry) probability. Gives a **ground truth** so we can ask
  whether standings recover the true skill order.
- **Cons:** Results depend on the chosen model; conclusions may not transfer if
  real Hubworld outcomes are non-logistic (e.g. matchup/rock-paper-scissors).

### Option C — Empirical / fitted distribution

- **Pros:** Most realistic if we have real event data to fit.
- **Cons:** Requires data we don't yet have.

**Default in code:** Option B (skilled). Option A available as a control.

---

## D2. Whole-tournament pre-generation vs. round-by-round loop

**Prompt:** Generate all results up front and replay different pairings, or
generate a round, pair, generate the next round, …?

### Option A — Whole-tournament, then apply pairings

- **Pros:** Isolates a single pairing decision on identical data; low variance
  when comparing.
- **Cons:** **Incoherent** — a player's round-3 result can't depend on a round-3
  opponent that a different algorithm would have assigned. Only valid for
  one-shot "given these standings, who plays whom?" questions.

### Option B — Round-by-round loop (`engine.run_tournament`)

- **Pros:** Realistic; pairing genuinely affects who plays whom and therefore
  the standings. This is what makes the comparison meaningful.
- **Cons:** Higher variance; needs many trials to compare algorithms.

**Default in code:** Option B. Use shared seeds + many trials (`run_pairing.py`)
to control variance.

---

## D3. Within-record-group ordering (the heart of the study)

**Prompt:** Once players are grouped by record, how do we order them so pairs
are of comparable strength?

| Strategy | Idea | Pros | Cons |
|---|---|---|---|
| `adjacent` | sort by rank, pair neighbours (1v2, 3v4) | closest-strength pairs; familiar | top seeds meet early; reduces separation |
| `fold` | top half vs. bottom half (1 vs N/2+1) | classic Swiss; spreads strong players | early pairs can be lopsided |
| `slide` | top seed plays next seed down | simple to explain | similar issues to adjacent |
| `random_within_record` | shuffle inside each group | unmanipulable ordering; fair | wastes within-group info |
| `random` | ignore records entirely | pure control/baseline | not a real OP system |

**Secondary axis — comprehensibility:** how easily can a player predict their
own next opponent? Random methods are unpredictable (resistant to manipulation
but opaque); adjacent/fold are predictable (transparent but gameable). *This is
for us to weigh — do not auto-conclude.*

---

## D4. Scoring & tiebreakers (`standings.rank_key`)

**Updated for the revised model.** `Match.results[pid]` now reports, per player,
**games won/losses** (0–2), **total agents**, the opponent, and `is_draw` /
`is_bye` flags. So "record" can be defined at several granularities:

- **Game record** — games won vs. lost across the event (0–2 per match; a 1-1
  split is a draw). This is the most direct reading of the new `results` shape.
- **Match points** — e.g. 3/win, 1/draw, 0/loss (draws are now possible, so a
  draw value must be chosen).
- **Agent differential / agents-for** — from `total_agents_a/total_agents_b`.
- **Strength-of-schedule** — opponents' win %.

Trade-off between **rewarding margins** (agent diff) and **incentivising odd
play** (running up agents), plus the new question of **how much a draw is worth**.

> **Pending:** `standings.py` still computes the old `(match_points, agent_diff,
> agents_for)` from the removed `Match.winner` API and must be rewritten against
> `Match.results`. Decide the record granularity here first, then implement once.

---

## D5. Rematch avoidance & byes

<!-- Sean Bye comment -->
> **Byes removed.** The `BYE` sentinel and all bye handling were removed from
> `models.py`; tournaments now require an even number of players. The bye bullets
> below are obsolete and need reworking.

- Rematch avoidance is **greedy/best-effort** (`pairing._avoid_rematches`). A
  perfect constraint solve (max-weight matching) is possible but heavier and
  harder for players to follow. Worth studying how often greedy fails.
- Byes: odd field → lowest available seed gets a bye (`player_b == BYE`),
  conventionally scored as a 2-0 win. Alternative policies (random bye, no
  repeat byes) are future work. There is also a `# TODO` to add a flag to
  **disable byes** entirely.
- **Model note:** a bye `Match` has **zero games**, but `Match.is_valid` now
  requires exactly two games, so every bye is currently flagged invalid. The
  validity check needs an `is_bye` short-circuit (see the `# Sean Update` note in
  `models.py`).

---

## D6. Changing the pairing function between rounds

**Prompt:** What happens if the algorithm changes from one round to the next?

`engine.run_tournament` accepts a single function, a per-round sequence, or a
round→function map (`run_pairing.py --schedule`). A `Tournament` can also carry
its own algorithm via `assign_algorithm`. Hypotheses to test: e.g. `random`
round 1 (no info) then `adjacent` later; or `fold` early to separate the field
then `adjacent` to fine-tune. Record findings here.

---

## D7. Draws vs. sudden death (NEW — raised by the model revision)

**Prompt:** Should a match be allowed to end in a draw, or must it always have a
winner?

The original spec said: after two games, if agent totals are tied, play
sudden-death agents "until the next agent is scored", so **a match never ends
tied**. The revised model takes a different stance:

- `Match` is defined as **exactly two games** (`is_valid` rejects more/fewer).
- `is_draw` is true when the two games are **split 1-1** (each player wins one),
  i.e. a draw is defined by *game split*, not by tied agent totals.
- The result generators (`skilled_match`, `random_match`) still **append**
  sudden-death `Game`s until agent totals differ — which produces matches with
  3+ games and therefore *fails* the new two-game `is_valid` check.

### Option A — Embrace draws (no sudden death)

- **Pros:** Simpler match object (always two games); `is_draw` is meaningful;
  matches a common "best-of-two, draws allowed" OP format.
- **Cons:** Standings must define a draw's value (D4); pairing/record groups grow
  a middle tier; diverges from the original written rule.

### Option B — Keep sudden death (no draws)

- **Pros:** Matches the original spec; standings stay win/loss only.
- **Cons:** A match can have a variable number of games → relax `is_valid`
  (e.g. `len(games) >= 2`); `is_draw` should be computed from tied agent totals
  *before* sudden death, or removed.

### Option C — Distinguish *game split* from *match draw*

- Track a 1-1 **game split** separately from a true **agent tie**; a split that
  is not an agent tie still has a match winner (more agents), and only an agent
  tie triggers sudden death.

**Status: RESOLVED — Option A (draws allowed) with a bonus-agent tie-break for
tied agent scores.** A `Match` is always exactly two games with outcomes 2-0 /
0-2 / 1-1 (`is_draw`). Agent totals do **not** decide the match (game wins do);
they are surfaced for standings/tiebreakers only. The tie-break does **not** add
a game or change the winner — it awards a **bonus agent** to break a tied *agent
score* so standings can separate otherwise-tied players. Applied consistently:

- `models.py`: `Match.is_valid` requires exactly two games. `is_draw` / `winner`
  are computed from **game-win counts**, not agent totals (a 1-1 draw can tie on
  agents, e.g. 4-4). `Match` takes `bonus_agents_a/b` as **constructor args**
  (decided by the generator, fixed at creation — no post-hoc mutation), folded
  into `total_agents_*` and `results["player_agents"]`.
- `generators.py`: `skilled_match` / `random_match` always produce exactly two
  games (draws allowed); `_tie_break_bonus` computes the bonus to break a tied
  agent score (passed into the `Match`) — `skilled_match` weights it by
  `score_agent_probability`, `random_match` uses a fair coin.
- `standings.py` / `io.py`: consume the `results` shape; the matches CSV stores
  `bonus_agents_a/b` (restored on read) so totals round-trip.
