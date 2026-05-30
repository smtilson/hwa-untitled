# OP Rules Study — Planning Document

A study of tournament **pairing algorithms** for Hubworld: Aidalon organized
play. Status: **In Progress** (scaffolding complete).

## 1. The setup

An organized-play event is a sequence of **rounds**. In each round players are
**paired**; each pair plays one **match**.

- A **game** is won by the first player to capture **3 agents**. We still record
  how many agents each player captured.
- A **match** is two games. After two games the players' total agents are
  compared. If tied, sudden-death agents are played until one player leads, so
  **a match never ends tied**.
- A player's **match result** is reported as `agents_for-agents_against`
  (e.g. `5-4`); more agents wins the match.

After rounds `1..n-1`, players are paired for round `n`. The **primary** key is
record (`wins-losses`), which partitions players into **record groups**. The
open question is how to **order within and across those groups** so players meet
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
- Rematch avoidance policy and bye assignment.

## 5. Components

| Component | Location | Status |
|---|---|---|
| Tournament model (dataclasses) | `tournament/models.py` | ☑ |
| Standings / records | `tournament/standings.py` | ☑ |
| Pairing function families | `tournament/pairing.py` | ☑ |
| Result generators | `tournament/generators.py` | ☑ |
| Event engine (round loop, per-round swaps) | `tournament/engine.py` | ☑ |
| Quality metrics | `tournament/metrics.py` | ☑ |
| CSV I/O | `tournament/io.py` | ☑ |
| CLI scripts | `scripts/` | ☑ |
| Notebook walkthrough | `notebooks/` | ☑ |
| Decision log (prompts + pros/cons) | `docs/decisions.md` | ☑ |

## 6. Glossary

- **Record group**: set of players with identical `wins-losses`.
- **Ordering**: total order on players; pairing = consecutive pairs of it.
- **Skill**: latent strength used only by generators; pairing never sees it.
