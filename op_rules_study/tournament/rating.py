"""Rating functions for evaluating player performance.

These functions take an agent sequence (list of tuples representing agents scored
and agents against per round) and return a numeric rating. They can be used as
tiebreakers or metrics in the standings system.

All functions follow the same signature: they take a sequence of tuples
(agents_for, agents_against) and return an int or float.
"""

from __future__ import annotations

from typing import Sequence


def total_agents_scored(agent_seq: Sequence[tuple[int, int]]) -> int:
    """Total number of agents a player has scored across all rounds.

    Args:
        agent_seq: Sequence of (agents_for, agents_against) tuples.

    Returns:
        Total agents scored.
    """
    return sum(for_score for for_score, _ in agent_seq)


def total_agents_lost(agent_seq: Sequence[tuple[int, int]]) -> int:
    """Total number of agents a player has lost (times -1).

    Returns negative value representing agents lost.

    Args:
        agent_seq: Sequence of (agents_for, agents_against) tuples.

    Returns:
        Negative total agents lost.
    """
    return -sum(against_score for _, against_score in agent_seq)


def agent_differential(agent_seq: Sequence[tuple[int, int]]) -> int:
    """Agent differential (agents scored minus agents lost).

    Args:
        agent_seq: Sequence of (agents_for, agents_against) tuples.

    Returns:
        Agent differential.
    """
    return sum(for_score - against_score for for_score, against_score in agent_seq)


def agent_ratio(agent_seq: Sequence[tuple[int, int]]) -> float:
    """Ratio of agents scored to agents lost.

    Returns float('inf') when agents_against is 0 but agents_for > 0 (perfect
    record), and 0.0 when both are 0 (no data).

    Args:
        agent_seq: Sequence of (agents_for, agents_against) tuples.

    Returns:
        Ratio of agents scored to agents lost.
    """
    total_for = sum(for_score for for_score, _ in agent_seq)
    total_against = sum(against_score for _, against_score in agent_seq)
    if total_against == 0:
        # Does float really handle inf?
        return float("inf") if total_for > 0 else 0.0
    return total_for / total_against


def agent_total_ratio(agent_seq: Sequence[tuple[int, int]]) -> float:
    """Ratio of total agents to the sum of agents scored and agents lost.

    This represents the proportion of total agents that the player scored.

    Args:
        agent_seq: Sequence of (agents_for, agents_against) tuples.

    Returns:
        Ratio of agents scored to total agents in all matches.
    """
    total_for = sum(for_score for for_score, _ in agent_seq)
    total_against = sum(against_score for _, against_score in agent_seq)
    total_agents = total_for + total_against
    if total_agents == 0:
        return 0.0
    return total_for / total_agents


# Weighted versions


def weighted_total_agents_scored(
    agent_seq: Sequence[tuple[int, int]],
    weights: Sequence[float],
) -> float:
    """Weighted total agents scored.

    More recent rounds can be weighted higher by providing a weight sequence.

    Args:
        agent_seq: Sequence of (agents_for, agents_against) tuples.
        weights: Sequence of weights (same length as agent_seq).

    Returns:
        Weighted total agents scored.
    """
    if len(agent_seq) != len(weights):
        raise ValueError("agent_seq and weights must have the same length")
    return sum(for_score * weight for (for_score, _), weight in zip(agent_seq, weights))


def weighted_total_agents_lost(
    agent_seq: Sequence[tuple[int, int]],
    weights: Sequence[float],
) -> float:
    """Weighted total agents lost (times -1).

    More recent rounds can be weighted higher by providing a weight sequence.

    Args:
        agent_seq: Sequence of (agents_for, agents_against) tuples.
        weights: Sequence of weights (same length as agent_seq).

    Returns:
        Negative weighted total agents lost.
    """
    if len(agent_seq) != len(weights):
        raise ValueError("agent_seq and weights must have the same length")
    return -sum(
        against_score * weight for (_, against_score), weight in zip(agent_seq, weights)
    )


def weighted_agent_differential(
    agent_seq: Sequence[tuple[int, int]],
    weights: Sequence[float],
) -> float:
    """Weighted agent differential.

    More recent rounds can be weighted higher by providing a weight sequence.

    Args:
        agent_seq: Sequence of (agents_for, agents_against) tuples.
        weights: Sequence of weights (same length as agent_seq).

    Returns:
        Weighted agent differential.
    """
    if len(agent_seq) != len(weights):
        raise ValueError("agent_seq and weights must have the same length")
    return sum(
        (for_score - against_score) * weight
        for (for_score, against_score), weight in zip(agent_seq, weights)
    )


def weighted_agent_ratio(
    agent_seq: Sequence[tuple[int, int]],
    weights: Sequence[float],
) -> float:
    """Weighted ratio of agents scored to agents lost.

    More recent rounds can be weighted higher by providing a weight sequence.

    Args:
        agent_seq: Sequence of (agents_for, agents_against) tuples.
        weights: Sequence of weights (same length as agent_seq).

    Returns:
        Weighted ratio of agents scored to agents lost.
    """
    if len(agent_seq) != len(weights):
        raise ValueError("agent_seq and weights must have the same length")
    weighted_for = sum(
        for_score * weight for (for_score, _), weight in zip(agent_seq, weights)
    )
    weighted_against = sum(
        against_score * weight for (_, against_score), weight in zip(agent_seq, weights)
    )
    if weighted_against == 0:
        return float("inf") if weighted_for > 0 else 0.0
    return weighted_for / weighted_against


def weighted_agent_total_ratio(
    agent_seq: Sequence[tuple[int, int]],
    weights: Sequence[float],
) -> float:
    """Weighted ratio of total agents to the sum of agents scored and agents lost.

    More recent rounds can be weighted higher by providing a weight sequence.

    Args:
        agent_seq: Sequence of (agents_for, agents_against) tuples.
        weights: Sequence of weights (same length as agent_seq).

    Returns:
        Weighted ratio of agents scored to total agents in all matches.
    """
    if len(agent_seq) != len(weights):
        raise ValueError("agent_seq and weights must have the same length")
    weighted_for = sum(
        for_score * weight for (for_score, _), weight in zip(agent_seq, weights)
    )
    weighted_against = sum(
        against_score * weight for (_, against_score), weight in zip(agent_seq, weights)
    )
    weighted_total = weighted_for + weighted_against
    if weighted_total == 0:
        return 0.0
    return weighted_for / weighted_total


# Utility function to create common weight sequences
def constant_weights(n: int, weight: float = 1.0) -> list[float]:
    """Create constant weights.
    
    Useful for giving equal weight to all rounds.
    
    Args:
        n: Number of weights to generate.
        weight: Weight to assign to each round.
        
    Returns:
        List of n constant weights.
    """
    return [weight] * n

def drop_off_weights(n: int, drop_off: int) -> list[int]:
    """Create weights that drop off exponentially.
    
    Useful for giving more weight to recent rounds.
    
    Args:
        n: Number of weights to generate.
        drop_off: Drop off factor (e.g., 0.5 means each round gets half the weight of the previous round).
        
    Returns:
        List of n exponentially decreasing weights.
    """
    if drop_off > n or drop_off < 1:
        raise ValueError("drop_off must be between 1 and n")
    if n <= 0:
        return []
    weights = [1]
    for i in range(1, n):
        if i < drop_off:
            weights.append(0)
        else:
            weights.append(1)
    return weights

def extend_weights(weights: list[float], n: int) -> list[float]:
    """Extend weights to match the number of rounds.
    
    Args:
        weights: List of weights to extend.
        n: Number of weights to generate.
        
    Returns:
        List of n weights.
    """
    if len(weights) >= n:
        return weights
    return weights + [weights[-1]] * (n - len(weights))

def multiply_weights(weights_1: list[float], weights_2: list[float]) -> list[float]:
    """Multiply two weight lists element-wise.
    
    Args:
        weights_1: First list of weights.
        weights_2: Second list of weights.
        
    Returns:
        List of n multiplied weights.
    """
    if len(weights_1) > len(weights_2):
        weights_2 = extend_weights(weights_2, len(weights_1))
    elif len(weights_2) > len(weights_1):
        weights_1 = extend_weights(weights_1, len(weights_2))
    return [w1 * w2 for w1, w2 in zip(weights_1, weights_2)]

def linear_weights(n: int, start: float = 1.0, end: float = 2.0) -> list[float]:
    """Create linearly increasing weights.

    Useful for giving more weight to recent rounds.

    Args:
        n: Number of weights to generate.
        start: Starting weight (for earliest round).
        end: Ending weight (for most recent round).

    Returns:
        List of n linearly increasing weights.
    """
    if n <= 0:
        return []
    step = (end - start) / (n - 1) if n > 1 else 0
    return [start + i * step for i in range(n)]


def exponential_weights(n: int, base: float = 1.1) -> list[float]:
    """Create exponentially increasing weights.

    Useful for giving exponentially more weight to recent rounds.

    Args:
        n: Number of weights to generate.
        base: Exponential base (multiplier per round).

    Returns:
        List of n exponentially increasing weights.
    """
    return [base**i for i in range(n)]
