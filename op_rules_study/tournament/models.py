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

# Sentinel player id used for a bye (odd number of players in a round).
# TODO: Windsurf: Add flag to disable byes
# Cascade reply: This constant isn't the right place for that flag -- byes are
# *created* in pairing (`_pair_sequence` appends `(odd_id, BYE)`) and consumed in
# `engine.run_tournament`. A "no byes" option is really a policy choice that lives
# there. Note: with an odd field you cannot avoid a bye without leaving someone
# unpaired, so "disable byes" likely means one of: (a) require even fields, (b)
# drop the odd player out for that round, or (c) use a fill/ghost player. Worth
# deciding which you mean (a decisions.md entry) before wiring a flag through
# engine/pairing.
BYE: int = -1


# Windsurf: I want a version of this class where skill can be an ignored trait.
# Cascade reply: `skill` already defaults to 0.0, and the pairing algorithms
# never read it (only the generators do) -- so it is effectively "ignored"
# wherever you don't simulate from it. If you want a hard guarantee, the cleanest
# options (no code here as requested) are: (1) make `skill: Optional[float] = None`
# and have generators reject/skip when it's None, or (2) keep one `Player` and add
# a generator/tournament-level switch "use_skill" rather than a second class --
# subclassing a frozen, slotted dataclass is awkward and would duplicate logic.
# A separate class is usually overkill versus an optional field + a flag.
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

    # Sean Update: Annotate as `-> tuple[bool, str]`; you return (validity,
    # error_msg), not a bool. `Match.is_valid` and `Round.is_valid` should use
    # the same return type for consistency.
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

    # Sean Update: Decorator order fixed -- `@property` is now outermost so it
    # wraps the validity-checked function (Cascade swapped these on request).
    # NB: `check_validity` in scripts/utils.py is still broken (bad import / name
    # shadow), so the check won't actually run until that is fixed.
    @property
    @check_validity
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

    # Sean Update: A bye match legitimately has 0 games (player_b == BYE), yet
    # this marks every bye as invalid. Guard with `if self.is_bye: return True, ""`
    # first. Consider also validating that agent totals are not tied (your rules
    # forbid a drawn match via sudden death).
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

    @property
    @check_validity
    def is_bye(self) -> bool:
        return self.player_b == BYE

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
        self._results = {
            self.player_a: {
                "id": self.player_a,
                "wins": 0,
                "losses": 0,
                "agents": 0,
                "opponent": self.player_b,
            },
            self.player_b: {
                "id": self.player_b,
                "wins": 0,
                "losses": 0,
                "agents": 0,
                "opponent": self.player_a,
            },
            "is_draw": self.is_draw,
            "is_bye": self.is_bye,
        }
        for game in self.games:
            self._results[self.player_a]["agents"] += game.agents_a
            self._results[self.player_b]["agents"] += game.agents_b
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
            if match.player_a == player_id or match.player_b == player_id:
                break
        else:
            raise ValueError(f"Player {player_id} not found in round {self.number}")

        results = match.results[player_id]
        return results

    # Sean Update: Re "what is a good pattern?" -- you currently have two
    # near-duplicate builders (`_compute_overall_results` and
    # `_calculate_overall_results`) plus the slots/caching bug. Suggested pattern:
    # keep ONE pure builder that returns a single agreed shape -- either a list of
    # per-match `match.results`, or a flat {player_id: result} map (NOT mapping
    # both players to the same `match.results` dict like the version below does).
    # Expose it once via `functools.cached_property`, delete the unused twin, and
    # reuse that shape in standings/io so there is a single source of truth.
    # TODO: I don't like this solution so far. I want something else here. What is a good pattern for that?
    def _compute_overall_results(self) -> dict:
        self._overall_results = {"round": self.number, "matches": {}}
        for match in self.matches:
            self._overall_results["matches"][match.player_a] = match.results
            self._overall_results["matches"][match.player_b] = match.results
        return self._overall_results

    @property
    @check_validity
    def overall_results(self) -> dict:
        """
        Returns a dictionary with the overall results of the round.
        """
        if not hasattr(self, "_overall_results"):
            self._overall_results = self._compute_overall_results()
        return self._overall_results

    def _calculate_overall_results(self) -> dict:
        """
        Calculates the overall results of the round.
        """
        return {
            "round": self.number,
            "matches": [match.results for match in self.matches],
        }


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

    # Windsurf: I am not sure if this is relevant
    # Cascade reply: It is relevant -- `engine.run_tournament` calls this to build
    # `PairingContext.past_opponents`, which `pairing._avoid_rematches` uses to
    # stop players from being paired against someone they already faced. If you
    # decide rematch avoidance is out of scope for the study, you could drop it;
    # otherwise keep it. (Caveat: it calls `Round.opponents()`, which is decorated
    # with `check_validity`, so it depends on the validity layer being fixed.)
    def past_opponents(self, pid: int) -> set[int]:
        """All opponents a player has already faced (excludes byes)."""
        seen: set[int] = set()
        for rnd in self.rounds:
            opp = rnd.opponents().get(pid)
            if opp is not None and opp != BYE:
                seen.add(opp)
        return seen
