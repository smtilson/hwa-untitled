# Data directory

Generated CSVs land here. They are produced by `scripts/generate_records.py`
and `scripts/run_pairing.py`, and consumed by the notebook and any analysis
scripts. Nothing here is hand-edited.

## File types

- **`<tag>_players.csv`** — the player pool with latent `skill` (ground truth).
  Columns: `pid, name, skill`.
- **`<tag>_matches.csv`** — one row per match (raw results).
  Columns: `round, player_a, player_b, agents_a, agents_b, winner, result_a, result_b, is_bye`.
- **`<tag>_standings.csv`** — per-player record snapshot after each round.
  Columns: `through_round, pid, name, match_wins, match_losses, agents_for, agents_against, agent_diff, match_points, record`.
- **`*_comparison.csv`** — algorithm-vs-algorithm metric tables from `run_pairing.py`.

`<tag>` defaults to the pairing algorithm name (e.g. `adjacent_matches.csv`).

> **Schema change pending.** The columns above reflect the *original* `Match`
> API. The revised model (`tournament/models.py`) reports each match as a
> per-player `results` dict (`wins`/`losses` = games won/lost 0–2, `agents` =
> total agents, plus `opponent`, `is_draw`, `is_bye`) and renamed totals to
> `total_agents_a` / `total_agents_b`. `tournament/io.py` has **not** been
> re-synced yet, so the match CSV will gain game-record and draw columns once it
> is. See `PLANNING.md` §5b and `docs/decisions.md` D4/D7.

## Reproducibility

Every file is produced from an explicit `--seed`. Re-running with the same seed
and arguments reproduces the file exactly.
