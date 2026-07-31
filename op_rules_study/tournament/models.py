# I think I have addressed the contents of this file adequately.

"""Core data model for Hubworld: Aidalon organized-play simulations.

The objects here are deliberately small, immutable where possible, and use
``slots=True`` so that simulating thousands of tournaments stays cheap in both
time and memory.

Domain recap
------------
* A **game** is won by the first player to capture ``AGENTS_TO_WIN`` (3) agents.
  We still record how many agents *each* player captured in that game.
* A **match** is two games. Its outcome is decided by the **games**
  (``game_1_winner`` / ``game_2_winner``): a win, a loss, or a 1-1 **split**
  (``is_draw``). The per-player agent totals (``player_agents`` /
  ``opponent_agents`` in ``results``; ``total_agents_a`` / ``total_agents_b`` /
  ``agent_score`` on the match) do **not** decide the match -- they are surfaced
  for the pairing/standings code to use as tiebreakers/metrics.
* A player's **match result** is reported as the dict ``Match.results[pid]`` =
  ``{"id", "wins", "losses", "player_agents", "opponent_agents", "opponent"}``
  (``wins``/``losses`` are games won/lost, 0-2). This is the summary used to
  compute the next round of the tournament.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Callable

from .utils import check_validity

# Number of agents a player must capture to win a single game.
AGENTS_TO_WIN: int = 3

# Byes are not modeled: tournaments require an even number of players (enforced
# in `engine.run_tournament`). See PLANNING.md D5.


# Skill is "ignorable" via the result model, not a per-Player flag: `random_match`
# ignores skill, `skilled_match` uses it (selectable in engine via `match_model`).
@dataclass(slots=True, frozen=True)
class Player:
    """A competitor.

    ``skill`` is a latent "true strength" parameter (integer 1–100). It is only
    ever consumed by the result *generators* (see ``generators.py``); the
    pairing algorithms must never look at it -- they only see results/records.
    """

    pid: int
    name: str
    skill: int = 50

    def to_dict(self) -> dict:
        return {"pid": self.pid, "name": self.name, "skill": self.skill}

    @classmethod
    def from_dict(cls, d: dict) -> "Player":
        return cls(pid=d["pid"], name=d["name"], skill=d["skill"])


@dataclass(slots=True, frozen=True)
class Game:
    """The outcome of a single game: agents captured by each side."""

    agents_a: int
    agents_b: int

    @property
    def is_valid(self) -> tuple[bool, str]:
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

    @property
    @check_validity
    def winner_is_a(self) -> bool:
        return self.agents_a == AGENTS_TO_WIN

    def to_dict(self) -> dict:
        return {"agents_a": self.agents_a, "agents_b": self.agents_b}

    @classmethod
    def from_dict(cls, d: dict) -> "Game":
        return cls(agents_a=d["agents_a"], agents_b=d["agents_b"])


@dataclass(slots=True)
class Match:
    """A match between ``player_a`` and ``player_b`` (by id)."""

    player_a: int
    player_b: int
    games: list[Game] = field(default_factory=list)
    # Tie-break award, decided by the result generator and fixed at construction
    # (a constructor arg, no post-hoc mutation). Breaks a tied agent score without
    # changing the game-win-based winner. See generators / PLANNING.md D7.
    bonus_agents_a: int = field(default=0, repr=False)
    bonus_agents_b: int = field(default=0, repr=False)
    _results: dict | None = field(default=None, init=False, repr=False)

    @property
    def is_valid(self) -> tuple[bool, str]:
        valid = True
        error_msg = ""
        # Sean tie breaker attention: a match is exactly two games. The tie-break
        # no longer appends a third game -- it awards bonus agents (set at
        # construction by the result generator) instead.
        if len(self.games) != 2:
            valid = False
            error_msg += "Match must have 2 games.\n"
        if self.player_a == self.player_b:
            valid = False
            error_msg += "Match players are the same.\n"
        return valid, error_msg

    @property
    def total_agents_a(self) -> int:
        return sum(g.agents_a for g in self.games) + self.bonus_agents_a

    @property
    def total_agents_b(self) -> int:
        return sum(g.agents_b for g in self.games) + self.bonus_agents_b

    @property
    @check_validity
    def game_1_winner(self) -> Optional[int]:
        return self.player_a if self.games[0].winner_is_a else self.player_b

    @property
    @check_validity
    def game_2_winner(self) -> Optional[int]:
        return self.player_a if self.games[1].winner_is_a else self.player_b

    def _game_win_counts(self) -> tuple[int, int]:
        """(games won by A, games won by B) across all games in the match."""
        wins_a = sum(1 for g in self.games if g.winner_is_a)
        return wins_a, len(self.games) - wins_a

    # A match is decided by its games (game wins), NOT by agent totals -- agent
    # totals are surfaced for standings/tiebreakers downstream. A two-game match
    # split 1-1 stays a draw; the bonus-agent tie-break (see generators) only
    # breaks a tied agent score, it does not create a match winner. See
    # PLANNING.md D7.
    @property
    @check_validity
    def is_draw(self):
        wins_a, wins_b = self._game_win_counts()
        return wins_a == wins_b

    @property
    @check_validity
    def winner(self) -> Optional[int]:
        """Winning player id by game wins, or ``None`` for a draw."""
        wins_a, wins_b = self._game_win_counts()
        if wins_a == wins_b:
            return None
        return self.player_a if wins_a > wins_b else self.player_b

    @property
    @check_validity
    def agent_score(self):
        return (self.total_agents_a, self.total_agents_b)

    def _compute_results(self) -> dict:
        # Each player's entry carries both agents-for ("player_agents") and
        # agents-against ("opponent_agents") so standings.Record can consume
        # Round.player_results directly.
        self._results = {
            self.player_a: {
                "id": self.player_a,
                "wins": 0,
                "losses": 0,
                "player_agents": self.total_agents_a,
                "opponent_agents": self.total_agents_b,
                "bonus_agents": self.bonus_agents_a,
                "opponent": self.player_b,
            },
            self.player_b: {
                "id": self.player_b,
                "wins": 0,
                "losses": 0,
                "player_agents": self.total_agents_b,
                "opponent_agents": self.total_agents_a,
                "bonus_agents": self.bonus_agents_b,
                "opponent": self.player_a,
            },
            "is_draw": self.is_draw,
        }
        for game in self.games:
            if game.winner_is_a:
                self._results[self.player_a]["wins"] += 1
                self._results[self.player_b]["losses"] += 1
            else:
                self._results[self.player_b]["wins"] += 1
                self._results[self.player_a]["losses"] += 1

        return self._results

    @property
    @check_validity
    def results(self) -> dict:
        if self._results is None:
            self._compute_results()
        return self._results

    def to_dict(self) -> dict:
        return {
            "player_a": self.player_a,
            "player_b": self.player_b,
            "games": [g.to_dict() for g in self.games],
            "bonus_agents_a": self.bonus_agents_a,
            "bonus_agents_b": self.bonus_agents_b,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Match":
        return cls(
            player_a=d["player_a"],
            player_b=d["player_b"],
            games=[Game.from_dict(g) for g in d["games"]],
            bonus_agents_a=d.get("bonus_agents_a", 0),
            bonus_agents_b=d.get("bonus_agents_b", 0),
        )


@dataclass(slots=True)
class Round:
    """A single round: a list of matches plus the round number (1-indexed)."""

    number: int
    matches: list[Match] = field(default_factory=list)
    _overall_results: dict | None = field(default=None, init=False, repr=False)

    @property
    def is_valid(self) -> tuple[bool, str]:
        valid = True
        error_msg = ""
        for match in self.matches:
            match_valid, match_msg = match.is_valid
            if not match_valid:
                valid = False
                error_msg += f"Round {self.number} match between {match.player_a} and {match.player_b} is invalid because:\n"
                error_msg += match_msg

        return valid, error_msg

    @property
    def players(self):
        """Return a set of all player IDs in this round."""
        return {match.player_a for match in self.matches} | {
            match.player_b for match in self.matches
        }

    @check_validity
    def opponents(self) -> dict[int, int]:
        """Map every player id to the id they faced this round."""
        table: dict[int, int] = {}
        for m in self.matches:
            table[m.player_a] = m.player_b
            table[m.player_b] = m.player_a
        return table

    def player_results(self, player_id: int) -> dict:
        """
        Returns a dictionary with the results of the player's matches in this round.
        """
        return self.overall_results["matches"][player_id]

    def _compute_overall_results(self) -> None:
        self._overall_results = {"round": self.number, "matches": {}}
        for match in self.matches:
            self._overall_results["matches"][match.player_a] = match.results[
                match.player_a
            ]
            self._overall_results["matches"][match.player_b] = match.results[
                match.player_b
            ]

    @property
    @check_validity
    def overall_results(self) -> dict:
        """
        Returns a dictionary with the overall results of the round.
        """
        if self._overall_results is None:
            self._compute_overall_results()
        return self._overall_results

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "matches": [m.to_dict() for m in self.matches],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Round":
        return cls(
            number=d["number"],
            matches=[Match.from_dict(m) for m in d["matches"]],
        )


@dataclass(slots=True)
class Tournament:
    """A full event: the player pool plus the rounds played so far."""

    players: list[Player]
    rounds: list[Round] = field(default_factory=list)
    _algorithm: Optional[Callable] = None

    def assign_algorithm(self, algorithm: Callable) -> None:
        self._algorithm = algorithm

    @property
    def player_ids(self) -> list[int]:
        return [p.pid for p in self.players]

    def player_by_id(self, pid: int) -> Optional[Player]:
        for p in self.players:
            if p.pid == pid:
                return p
        return None

    def past_opponents(self, pid: int) -> set[int]:
        """All opponents a player has already faced."""
        seen: set[int] = set()
        for rnd in self.rounds:
            opp = rnd.opponents().get(pid)
            if opp is not None:
                seen.add(opp)
        return seen

    def to_dict(self) -> dict:
        return {
            "players": [p.to_dict() for p in self.players],
            "rounds": [r.to_dict() for r in self.rounds],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Tournament":
        return cls(
            players=[Player.from_dict(p) for p in d["players"]],
            rounds=[Round.from_dict(r) for r in d["rounds"]],
        )
