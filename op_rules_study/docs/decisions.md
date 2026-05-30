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

Options: match-wins only; match points (3/win); agent differential; agents-for;
strength-of-schedule (opponents' win %). Trade-off between **rewarding margins**
(agent diff) and **incentivising odd play** (running up agents). Currently:
`(match_points, agent_diff, agents_for)`.

---

## D5. Rematch avoidance & byes

- Rematch avoidance is **greedy/best-effort** (`pairing._avoid_rematches`). A
  perfect constraint solve (max-weight matching) is possible but heavier and
  harder for players to follow. Worth studying how often greedy fails.
- Byes: odd field → lowest available seed gets a bye, scored as a 2-0 win.
  Alternative policies (random bye, no repeat byes) are future work.

---

## D6. Changing the pairing function between rounds

**Prompt:** What happens if the algorithm changes from one round to the next?

`engine.run_tournament` accepts a single function, a per-round sequence, or a
round→function map (`run_pairing.py --schedule`). Hypotheses to test: e.g.
`random` round 1 (no info) then `adjacent` later; or `fold` early to separate
the field then `adjacent` to fine-tune. Record findings here.
