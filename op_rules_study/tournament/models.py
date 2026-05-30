"""Core data model for Hubworld: Aidalon organized-play simulations.

The objects here are deliberately small, immutable where possible, and use
``slots=True`` so that simulating thousands of tournaments stays cheap in both
time and memory.

Domain recap
------------
* A **game** is won by the first player to capture ``AGENTS_TO_WIN`` (3) agents.
  We still record how many agents *each* player captured in that game.
* A **match** is a best-of-two-games affair. After two games the players'
  agent totals are compared. If those totals are tied, play continues
  (sudden-death agents) until someone is ahead -- so a match never ends tied.
* A player's **match result** is reported as ``agents_for-agents_against``
  (e.g. ``5-4``), and the player with more agents is the match winner.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Number of agents a player must capture to win a single game.
AGENTS_TO_WIN: int = 3

# Sentinel player id used for a bye (odd number of players in a round).
BYE: int = -1


@dataclass(slots=True, frozen=True)
class Player:
    """A competitor.

    ``skill`` is a latent "true strength" parameter. It is only ever consumed
    by the result *generators* (see ``generators.py``); the pairing algorithms
    must never look at it -- they only see results/records.
    """

    pid: int
    name: str
    skill: float = 0.0


@dataclass(slots=True, frozen=True)
class Game:
    """The outcome of a single game: agents captured by each side."""

    agents_a: int
    agents_b: int

    @property
    def winner_is_a(self) -> bool:
        return self.agents_a > self.agents_b


@dataclass(slots=True)
class Match:
    """A match between ``player_a`` and ``player_b`` (by id).

    A bye is encoded as ``player_b == BYE`` with no games played.
    """

    player_a: int
    player_b: int
    games: list[Game] = field(default_factory=list)

    @property
    def is_bye(self) -> bool:
        return self.player_b == BYE

    @property
    def agents_a(self) -> int:
        return sum(g.agents_a for g in self.games)

    @property
    def agents_b(self) -> int:
        return sum(g.agents_b for g in self.games)

    @property
    def winner(self) -> int:
        """Player id of the match winner (``player_a`` always wins a bye)."""
        if self.is_bye:
            return self.player_a
        return self.player_a if self.agents_a > self.agents_b else self.player_b

    @property
    def loser(self) -> int:
        if self.is_bye:
            return BYE
        return self.player_b if self.winner == self.player_a else self.player_a

    def agents_for(self, pid: int) -> int:
        return self.agents_a if pid == self.player_a else self.agents_b

    def agents_against(self, pid: int) -> int:
        return self.agents_b if pid == self.player_a else self.agents_a


@dataclass(slots=True)
class Round:
    """A single round: a list of matches plus the round number (1-indexed)."""

    number: int
    matches: list[Match] = field(default_factory=list)

    def opponents(self) -> dict[int, int]:
        """Map every player id to the id they faced this round."""
        table: dict[int, int] = {}
        for m in self.matches:
            table[m.player_a] = m.player_b
            if not m.is_bye:
                table[m.player_b] = m.player_a
        return table


@dataclass(slots=True)
class Tournament:
    """A full event: the player pool plus the rounds played so far."""

    players: list[Player]
    rounds: list[Round] = field(default_factory=list)

    @property
    def player_ids(self) -> list[int]:
        return [p.pid for p in self.players]

    def player_by_id(self, pid: int) -> Optional[Player]:
        for p in self.players:
            if p.pid == pid:
                return p
        return None

    def past_opponents(self, pid: int) -> set[int]:
        """All opponents a player has already faced (excludes byes)."""
        seen: set[int] = set()
        for rnd in self.rounds:
            opp = rnd.opponents().get(pid)
            if opp is not None and opp != BYE:
                seen.add(opp)
        return seen
