# I think I have addressed the contents of this file adequately.

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
* A player's **match result** is reported as ``((wins,losses),(agents_for,agents_against))``
  (e.g. ``5-4``). This is the output for computing the next round of the tournament.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from ..scripts.utils import check_validity

# Number of agents a player must capture to win a single game.
AGENTS_TO_WIN: int = 3

# Sentinel player id used for a bye (odd number of players in a round).
# TODO: Windsurf: Add flag to disable byes
BYE: int = -1


# Windsurf: I want a version of this class where skill can be an ignored trait.
@dataclass(slots=True, frozen=True)
class Player:
    """A competitor.

    ``skill`` is a latent "true strength" parameter. It is only ever consumed
    by the result *generators* (see ``generators.py``); the pairing algorithms
    must never look at it -- they only see results/records.
    """

    pid: int
    name: str
    # TODO: Windsurf: Add flag to ignore skill
    skill: float = 0.0


@dataclass(slots=True, frozen=True)
class Game:
    """The outcome of a single game: agents captured by each side."""

    agents_a: int
    agents_b: int

    @property
    def is_valid(self) -> bool:
        validity = True
        error_msg = ""
        if self.agents_a > AGENTS_TO_WIN:
            validity = False
            error_msg += "Player A has more agents than allowed.\n"
        if self.agents_b > AGENTS_TO_WIN:
            validity = False
            error_msg += "Player B has more agents than allowed.\n"
        if self.agents_a == self.agents_b:
            validity = False
            error_msg += "Both players have the same number of agents."
        return validity, error_msg

    @check_validity
    @property
    def winner_is_a(self) -> bool:
        return self.agents_a == AGENTS_TO_WIN


@dataclass(slots=True)
class Match:
    """A match between ``player_a`` and ``player_b`` (by id).

    A bye is encoded as ``player_b == BYE`` with no games played.
    """

    player_a: int
    player_b: int
    games: list[Game] = field(default_factory=list)

    @property
    def is_valid(self):
        valid = True
        error_msg = ""
        if len(self.games) != 2:
            valid = False
            error_msg += "Match does not have 2 games.\n"
        if self.player_a == self.player_b:
            valid = False
            error_msg += "Match players are the same.\n"
        return valid, error_msg

    @check_validity
    @property
    def is_bye(self) -> bool:
        return self.player_b == BYE

    @property
    def total_agents_a(self) -> int:
        return sum(g.agents_a for g in self.games)

    @property
    def total_agents_b(self) -> int:
        return sum(g.agents_b for g in self.games)

    @check_validity
    @property
    def game_1_winner(self) -> Optional[int]:
        return self.player_a if self.games[0].winner_is_a else self.player_b

    @check_validity
    @property
    def game_2_winner(self) -> Optional[int]:
        return self.player_a if self.games[1].winner_is_a else self.player_b

    @check_validity
    @property
    def is_draw(self):
        return self.game_1_winner != self.game_2_winner

    @check_validity
    @property
    def agent_score(self):
        return (self.total_agents_a, self.total_agents_b)

    def _compute_results(self) -> dict:
        self._results = {
            self.player_a: self._player_a_result(),
            self.player_b: self._player_b_result(),
            f"{self.player_a}_agents": self.total_agents_a,
            f"{self.player_b}_agents": self.total_agents_b,
            f"{self.player_a}_wins": 0,
            f"{self.player_b}_wins": 0,
            "is_draw": self.is_draw,
            "is_bye": self.is_bye,
        }
        for game in self.games:
            if game.winner_is_a:
                self._results[f"{self.player_a}_wins"] += 1
            else:
                self._results[f"{self.player_b}_wins"] += 1
        return self._results

    @check_validity
    @property
    def results(self) -> dict:
        if not hasattr(self, "_results"):
            self._compute_results()
        return self._results


@dataclass(slots=True)
class Round:
    """A single round: a list of matches plus the round number (1-indexed)."""

    number: int
    matches: list[Match] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        valid = True
        error_msg = ""
        for match in self.matches:
            match_valid, match_msg = match.is_valid
            if not match_valid:
                valid = False
                error_msg += f"Round {self.number} match between {match.player_a} and {match.player_b} is invalid because:\n"
                error_msg += match_msg

        return valid, error_msg

    @check_validity
    def opponents(self) -> dict[int, int]:
        """Map every player id to the id they faced this round."""
        table: dict[int, int] = {}
        for m in self.matches:
            table[m.player_a] = m.player_b
            if not m.is_bye:
                table[m.player_b] = m.player_a
        return table

    def player_results(self, player_id: int) -> dict:
        """
        Returns a dictionary with the results of the player's matches in this round.
        """
        for match in self.matches:
            if match.player_a == player_id:
                opponent = match.player_b
                break
            elif match.player_b == player_id:
                opponent = match.player_a
                break
        else:
            raise ValueError(f"Player {player_id} not found in round {self.number}")

        results = {
            "player": {
                "id": player_id,
                "wins": match.results.get(f"{player_id}_wins", 0),
                "losses": match.results.get(f"{opponent}_wins", 0),
                "agents": match.results.get(f"{player_id}_agents", 0),
            },
            "opponent": {
                "id": opponent,
                "wins": match.results.get(f"{opponent}_wins", 0),
                "losses": match.results.get(f"{player_id}_wins", 0),
                "agents": match.results.get(f"{opponent}_agents", 0),
            },
        }
        return results


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

    # Windsurf: I am not sure if this is relevant
    def past_opponents(self, pid: int) -> set[int]:
        """All opponents a player has already faced (excludes byes)."""
        seen: set[int] = set()
        for rnd in self.rounds:
            opp = rnd.opponents().get(pid)
            if opp is not None and opp != BYE:
                seen.add(opp)
        return seen
