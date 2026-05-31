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

A single game ends when one player reaches :data:`AGENTS_TO_WIN`. A match is two
games; ties are broken by sudden-death agents.
"""

from __future__ import annotations

import math
from random import Random

from .models import AGENTS_TO_WIN, Game, Match, Player

# Windsurf: I want to be agnostic as to how skill is used. Please add a section to the planning document explaining the choice of this function and what other potential functions could be.
def score_agent_probability(skill_a: float, skill_b: float) -> float:
    """Probability that A captures the next agent, logistic in the skill gap."""
    return 1.0 / (1.0 + math.exp(-(skill_a - skill_b)))


def simulate_game(skill_a: float, skill_b: float, rng: Random) -> Game:
    """Play agents one at a time until someone reaches ``AGENTS_TO_WIN``."""
    p = win_probability(skill_a, skill_b)
    a = b = 0
    while a < AGENTS_TO_WIN and b < AGENTS_TO_WIN:
        if rng.random() < p:
            a += 1
        else:
            b += 1
    return Game(agents_a=a, agents_b=b)


def skilled_match(player_a: Player, player_b: Player, rng: Random) -> Match:
    """Two skill-driven games plus sudden-death agents to break agent ties."""
    games = [
        simulate_game(player_a.skill, player_b.skill, rng),
        simulate_game(player_a.skill, player_b.skill, rng),
    ]
    match = Match(player_a=player_a.pid, player_b=player_b.pid, games=games)

    # Sudden death: keep adding single agents until the totals differ.
    p = win_probability(player_a.skill, player_b.skill)
    # Sean Update: `match.agents_a`/`agents_b` were renamed to
    # `total_agents_a`/`total_agents_b`, so this comparison now AttributeErrors
    # and match simulation is broken. Update both references.
    while match.agents_a == match.agents_b:
        if rng.random() < p:
            match.games.append(Game(agents_a=1, agents_b=0))
        else:
            match.games.append(Game(agents_a=0, agents_b=1))
    return match


def random_match(player_a: Player, player_b: Player, rng: Random) -> Match:
    """Skill-free baseline: each game is a coin flip for the winner, loser gets
    0-2 agents at random. Useful as a null model.
    """
    games: list[Game] = []
    for _ in range(2):
        loser_agents = rng.randint(0, AGENTS_TO_WIN - 1)
        if rng.random() < 0.5:
            games.append(Game(agents_a=AGENTS_TO_WIN, agents_b=loser_agents))
        else:
            games.append(Game(agents_a=loser_agents, agents_b=AGENTS_TO_WIN))
    match = Match(player_a=player_a.pid, player_b=player_b.pid, games=games)
    # Sean Update: same rename issue -- use `total_agents_a`/`total_agents_b`.
    while match.agents_a == match.agents_b:
        if rng.random() < 0.5:
            match.games.append(Game(agents_a=1, agents_b=0))
        else:
            match.games.append(Game(agents_a=0, agents_b=1))
    return match


# Registry mirrors pairing.REGISTRY so scripts can select a model by name.
MATCH_MODELS = {
    "skilled": skilled_match,
    "random": random_match,
}


def make_players(n: int, rng: Random, skill_sd: float = 1.0) -> list[Player]:
    """Create ``n`` players with normally-distributed latent skill."""
    return [
        Player(pid=i, name=f"P{i:03d}", skill=rng.gauss(0.0, skill_sd))
        for i in range(n)
    ]
