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

# Sean Update: This `..scripts.utils` relative import will raise ImportError at
# runtime. `_bootstrap.py` adds the module root to sys.path and imports
# `tournament` as a TOP-LEVEL package, so it has no parent package for `..` to
# resolve against. Fix: move `check_validity` into the package (e.g. create
# `tournament/utils.py`) and use `from .utils import check_validity`, or install
# `op_rules_study` as a proper package.
# Windsurf: Check that the above comment is addressed. If it is document the fix in the planning doc and delete this comment and your update comment.
from .utils import check_validity

# Number of agents a player must capture to win a single game.
AGENTS_TO_WIN: int = 3

# Windsurf: For the time being, let us just force the number of players to be even.
# TODO(Sean): Byes and the `BYE` sentinel were removed from the model. Follow up to
# check the downstream effects of this change -- `pairing._pair_sequence`,
# `engine.run_tournament`, `standings.compute_records`, `io.write_matches` /
# `read_matches`, and `tournament/__init__` still import/reference `BYE`, and the
# tests assume bye handling. These break until updated to require an even field.


# Windsurf: I want a version of this class where skill can be an ignored trait.
# Cascade reply: `skill` already defaults to 0.0, and the pairing algorithms
# never read it (only the generators do) -- so it is effectively "ignored"
# wherever you don't simulate from it. If you want a hard guarantee, the cleanest
# options (no code here as requested) are: (1) make `skill: Optional[float] = None`
# and have generators reject/skip when it's None, or (2) keep one `Player` and add
# a generator/tournament-level switch "use_skill" rather than a second class --
# subclassing a frozen, slotted dataclass is awkward and would duplicate logic.
# A separate class is usually overkill versus an optional field + a flag.
# Windsurf: I definitely didn't mean to use a separate class. I meant add flags in the relevant functions.
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
    # Cascade reply: A per-`Player` boolean here would be redundant -- whether
    # skill matters is a property of the *result model*, not of an individual
    # competitor. Prefer a single switch passed to the generator (e.g.
    # `random_match` already ignores skill; `skilled_match` uses it). If you do
    # want it on the data, `Optional[float] = None` (see reply above) signals
    # "unknown/ignored" more naturally than a paired bool + float.
    skill: float = 0.0


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


@dataclass(slots=True)
class Match:
    """A match between ``player_a`` and ``player_b`` (by id)."""

    player_a: int
    player_b: int
    games: list[Game] = field(default_factory=list)
    _results: dict | None = field(default=None, init=False, repr=False)

    @property
    def is_valid(self) -> tuple[bool, str]:
        valid = True
        error_msg = ""
        if len(self.games) != 2:
            valid = False
            error_msg += "Match does not have 2 games.\n"
        if self.player_a == self.player_b:
            valid = False
            error_msg += "Match players are the same.\n"
        if self.total_agents_a == self.total_agents_b:
            valid = False
            error_msg += "Total agents are the same.\n"
        return valid, error_msg

    @property
    def total_agents_a(self) -> int:
        return sum(g.agents_a for g in self.games)

    @property
    def total_agents_b(self) -> int:
        return sum(g.agents_b for g in self.games)

    @property
    @check_validity
    def game_1_winner(self) -> Optional[int]:
        return self.player_a if self.games[0].winner_is_a else self.player_b

    @property
    @check_validity
    def game_2_winner(self) -> Optional[int]:
        return self.player_a if self.games[1].winner_is_a else self.player_b

    # Sean Update: This flags a 1-1 game SPLIT as a draw, but a match is only a
    # true draw when the AGENT TOTALS tie (and your rules then force sudden death
    # so it shouldn't persist). Rename to `is_split`, or compute from
    # `self.total_agents_a == self.total_agents_b`. (Decorator order now fixed.)
    # Windsurf: This is false. The agent totals aren't actually determining the winner of the match, they will be used in other parts of the pairing algorithm. Please make sure to correct this in the readme, planning documents, and anywhere else as this is a key point.
    @property
    @check_validity
    def is_draw(self):
        return self.game_1_winner != self.game_2_winner

    @property
    @check_validity
    def agent_score(self):
        return (self.total_agents_a, self.total_agents_b)

    # Sean Update: `@dataclass(slots=True)` forbids setting attributes that are
    # not declared fields, so `self._results = ...` raises AttributeError at
    # runtime. Options: declare `_results: dict | None = field(default=None,
    # init=False, repr=False)`, drop `slots=True` for Match, or use
    # `functools.cached_property`. (Same problem hits `Round._overall_results`.)
    def _compute_results(self) -> dict:
        # Cascade: added "opponent_agents" to each player's entry so the per-player
        # result dict is self-contained (agents-for AND agents-against). This lets
        # standings.Record consume Round.player_results directly.
        self._results = {
            self.player_a: {
                "id": self.player_a,
                "wins": 0,
                "losses": 0,
                "player_agents": 0,
                "opponent_agents": 0,
                "opponent": self.player_b,
            },
            self.player_b: {
                "id": self.player_b,
                "wins": 0,
                "losses": 0,
                "player_agents": 0,
                "opponent_agents": 0,
                "opponent": self.player_a,
            },
            "is_draw": self.is_draw,
        }
        for game in self.games:
            self._results[self.player_a]["player_agents"] += game.agents_a
            self._results[self.player_b]["player_agents"] += game.agents_b
            # Cascade: each player's agents-against is the opponent's agents.
            self._results[self.player_a]["opponent_agents"] += game.agents_b
            self._results[self.player_b]["opponent_agents"] += game.agents_a
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


@dataclass(slots=True)
class Round:
    """A single round: a list of matches plus the round number (1-indexed)."""

    number: int
    matches: list[Match] = field(default_factory=list)
    _overall_results: dict | None = field(default=None, init=False, repr=False)

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
        return table

    def player_results(self, player_id: int) -> dict:
        """
        Returns a dictionary with the results of the player's matches in this round.
        """
        for match in self.matches:
            if match.player_a == player_id or match.player_b == player_id:
                break
        else:
            raise ValueError(f"Player {player_id} not found in round {self.number}")

        results = match.results[player_id]
        return results

    def _compute_overall_results(self) -> dict:
        self._overall_results = {"round": self.number, "matches": {}}
        for match in self.matches:
            self._overall_results["matches"][match.player_a] = match.results[
                match.player_a
            ]
            self._overall_results["matches"][match.player_b] = match.results[
                match.player_b
            ]
        return self._overall_results

    @property
    @check_validity
    def overall_results(self) -> dict:
        """
        Returns a dictionary with the overall results of the round.
        """
        if self._overall_results is None:
            self._overall_results = self._compute_overall_results()
        return self._overall_results


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
