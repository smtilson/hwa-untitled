"""Generating match/game results.

The prompt is intentionally agnostic about *how* results should be produced, so
this module offers three approaches that the study can compare. See
``docs/decisions.md`` for the full pros/cons discussion.

1. ``random_match``        -- draw a match result with no notion of skill.
                              Cheap, but pairing quality is meaningless because
                              there is no "true strength" to recover.
2. ``skilled_match``       -- each agent is a Bernoulli trial whose probability
                              comes from the two players' latent ``skill`` via a
                              logistic (Bradley-Terry style) model. This gives a
                              ground truth that pairing algorithms try to track.
3. round-by-round vs. whole-tournament -- whether we (a) generate one round,
                              pair, generate the next, ... (the realistic loop,
                              implemented in ``engine.py``) or (b) pre-generate
                              every result and replay different pairings over it.
                              Approach (a) is what makes pairing *matter*; (b) is
                              useful for isolating a single decision.

A single game ends when one player reaches :data:`AGENTS_TO_WIN`. A match is
exactly two games; a 1-1 game split is a draw (see PLANNING.md D7). Agent totals
do not decide the match -- they are surfaced for standings/tiebreakers.
"""

from __future__ import annotations

import math
from random import Random

from .models import AGENTS_TO_WIN, Game, Match, Player


# The skill->result mapping is a modeling choice; see PLANNING.md "Result model".
# Sean -- review: this is the central modeling assumption of the whole study.
# Motivation: a logistic of the skill *gap* is the Bradley-Terry standard --
# equal skill -> 0.5, symmetric, and only the difference matters (absolute skill
# is irrelevant). It is parameter-free, which keeps the null vs. skilled
# comparison clean. To decide: (1) do you want a temperature/scale knob
# `exp(-(s_a-s_b)/T)` to tune how decisive skill is? (2) is a per-AGENT (not
# per-game) probability the right granularity -- it makes blowouts more likely
# for large gaps. Alternatives are listed in PLANNING.md section 5c.
def score_agent_probability(
    skill_a: float, skill_b: float, temperature: float = 30.0
) -> float:
    """Probability that A captures the next agent, logistic in the skill gap.

    ``temperature`` scales the gap: larger values make skill differences less
    decisive.  The default (30) is calibrated so that integer skills on a 1–100
    scale reproduce the same probability distribution as the original
    ``N(0, 0.5)`` float skills with implicit temperature 1.
    """
    return 1.0 / (1.0 + math.exp(-(skill_a - skill_b) / temperature))


def _tie_break_bonus(
    games: list[Game], rng: Random, score_agent_prob: float = 0.5
) -> tuple[int, int]:
    """Bonus agents (a, b) to break a tied agent score; (0, 0) if not tied.
    ``score_agent_prob`` is the probability the bonus goes to player A.
    """
    agents_a = sum(g.agents_a for g in games)
    agents_b = sum(g.agents_b for g in games)
    if agents_a != agents_b:
        return 0, 0
    return (1, 0) if rng.random() < score_agent_prob else (0, 1)


def skill_game(
    skill_a: float, skill_b: float, rng: Random, temperature: float = 30.0
) -> Game:
    """Play agents one at a time until someone reaches ``AGENTS_TO_WIN``."""
    # Sean -- review: `p` is fixed for the whole game (no momentum / no
    # score-dependent swing). Motivation: matches the i.i.d. Bernoulli reading of
    # the model and keeps the loser's agent count a clean function of the gap. If
    # you want comeback dynamics or "the trailing player tries harder", `p` would
    # need to be recomputed inside the loop -- flagging in case that realism
    # matters to you.
    p = score_agent_probability(skill_a, skill_b, temperature)
    a = b = 0
    while a < AGENTS_TO_WIN and b < AGENTS_TO_WIN:
        if rng.random() < p:
            a += 1
        else:
            b += 1
    return Game(agents_a=a, agents_b=b)


def random_game(rng: Random) -> Game:
    """Play agents one at a time until someone reaches ``AGENTS_TO_WIN``."""
    # Sean -- review: `p` is fixed for the whole game (no momentum / no
    # score-dependent swing). Motivation: matches the i.i.d. Bernoulli reading of
    # the model and keeps the loser's agent count a clean function of the gap. If
    # you want comeback dynamics or "the trailing player tries harder", `p` would
    # need to be recomputed inside the loop -- flagging in case that realism
    # matters to you.
    a = b = 0
    while a < AGENTS_TO_WIN and b < AGENTS_TO_WIN:
        if rng.random() < 0.5:
            a += 1
        else:
            b += 1
    return Game(agents_a=a, agents_b=b)


def skilled_match(
    player_a: Player, player_b: Player, rng: Random, temperature: float = 30.0
) -> Match:
    """Two skill-driven games. A 1-1 split is a draw; a tied agent score is
    broken by a skill-weighted bonus agent (see ``_tie_break_bonus``)."""
    games = [
        skill_game(player_a.skill, player_b.skill, rng, temperature),
        skill_game(player_a.skill, player_b.skill, rng, temperature),
    ]
    bonus_a, bonus_b = _tie_break_bonus(
        games, rng, score_agent_probability(player_a.skill, player_b.skill, temperature)
    )
    return Match(
        player_a=player_a.pid,
        player_b=player_b.pid,
        games=games,
        bonus_agents_a=bonus_a,
        bonus_agents_b=bonus_b,
    )


def random_match(player_a: Player, player_b: Player, rng: Random) -> Match:
    """Skill-free baseline: each game is a coin flip for the winner, loser gets
    0-2 agents at random. A 1-1 split is a draw. Useful as a null model.
    """
    games = [
        random_game(rng),
        random_game(rng),
    ]
    bonus_a, bonus_b = _tie_break_bonus(games, rng)
    return Match(
        player_a=player_a.pid,
        player_b=player_b.pid,
        games=games,
        bonus_agents_a=bonus_a,
        bonus_agents_b=bonus_b,
    )


# Registry mirrors pairing.REGISTRY so scripts can select a model by name.
MATCH_MODELS = {
    "skilled": skilled_match,
    "random": random_match,
}


def make_players(
    n: int,
    rng: Random,
    skill_mean: int = 50,
    skill_sd: float = 15.0,
    skill_min: int = 1,
    skill_max: int = 100,
) -> list[Player]:
    """Create ``n`` players with normally-distributed latent skill.

    ``n`` must be even: tournaments are paired without byes (see PLANNING.md D5).

    Skills are integers on ``[skill_min, skill_max]`` drawn from a rounded
    normal distribution ``N(skill_mean, skill_sd)``.  With the defaults
    (mean=50, sd=15) ~99.7% of values fall in [5, 95], so clipping is rare.
    The default ``skill_sd=15`` paired with ``temperature=30`` in
    :func:`score_agent_probability` reproduces the same per-agent probability
    distribution as the original ``N(0, 0.5)`` float skills.
    """
    if n % 2 != 0:
        raise ValueError(f"make_players requires an even number of players, got {n}.")
    return [
        Player(
            pid=i,
            name=f"P{i:03d}",
            skill=max(
                skill_min, min(skill_max, round(rng.gauss(skill_mean, skill_sd)))
            ),
        )
        for i in range(n)
    ]
