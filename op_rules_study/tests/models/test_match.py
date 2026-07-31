"""Unit tests for tournament.models.Match."""
from __future__ import annotations

import pytest

from tournament.models import Game, Match


class TestMatchValidity:
    def test_valid_match(self, a_wins_match_factory):
        valid, msg = a_wins_match_factory().is_valid
        assert valid, msg

    def test_invalid_one_game_only(self):
        m = Match(player_a=1, player_b=2, games=[Game(3, 1)])
        valid, _ = m.is_valid
        assert not valid

    def test_invalid_zero_games(self):
        m = Match(player_a=1, player_b=2, games=[])
        valid, _ = m.is_valid
        assert not valid

    def test_invalid_same_player(self):
        m = Match(player_a=1, player_b=1, games=[Game(3, 1), Game(3, 2)])
        valid, _ = m.is_valid
        assert not valid


class TestMatchAgentTotals:
    def test_total_a_no_bonus(self, a_wins_match_factory):
        m = a_wins_match_factory()  # games (3,1) + (3,2)
        assert m.total_agents_a == 6

    def test_total_b_no_bonus(self, a_wins_match_factory):
        m = a_wins_match_factory()
        assert m.total_agents_b == 3

    def test_bonus_a_added(self):
        m = Match(
            player_a=1,
            player_b=2,
            games=[Game(3, 2), Game(2, 3)],
            bonus_agents_a=1,
            bonus_agents_b=0,
        )
        assert m.total_agents_a == 6  # 3+2+1
        assert m.total_agents_b == 5  # 2+3+0

    def test_bonus_b_added(self):
        m = Match(
            player_a=1,
            player_b=2,
            games=[Game(3, 2), Game(2, 3)],
            bonus_agents_a=0,
            bonus_agents_b=1,
        )
        assert m.total_agents_b == 6


class TestMatchOutcome:
    def test_game_1_winner_is_a(self, a_wins_match_factory):
        assert a_wins_match_factory().game_1_winner == 1

    def test_game_1_winner_is_b(self, b_wins_match_factory):
        assert b_wins_match_factory().game_1_winner == 2

    def test_game_2_winner_is_a(self, a_wins_match_factory):
        assert a_wins_match_factory().game_2_winner == 1

    def test_game_2_winner_is_b(self, b_wins_match_factory):
        assert b_wins_match_factory().game_2_winner == 2

    def test_is_draw_false_when_a_wins(self, a_wins_match_factory):
        assert a_wins_match_factory().is_draw is False

    def test_is_draw_true_on_split(self, draw_match_factory):
        assert draw_match_factory().is_draw is True

    def test_winner_a_wins(self, a_wins_match_factory):
        assert a_wins_match_factory().winner == 1

    def test_winner_b_wins(self, b_wins_match_factory):
        assert b_wins_match_factory().winner == 2

    def test_winner_none_on_draw(self, draw_match_factory):
        assert draw_match_factory().winner is None

    def test_agent_score_tuple(self, a_wins_match_factory):
        m = a_wins_match_factory()  # (3+3, 1+2) = (6, 3)
        assert m.agent_score == (6, 3)


class TestMatchResults:
    def test_results_contains_both_players(self, a_wins_match_factory):
        r = a_wins_match_factory().results
        assert 1 in r and 2 in r

    def test_results_game_wins_for_winner(self, a_wins_match_factory):
        assert a_wins_match_factory().results[1]["wins"] == 2

    def test_results_game_losses_for_winner(self, a_wins_match_factory):
        assert a_wins_match_factory().results[1]["losses"] == 0

    def test_results_game_wins_for_loser(self, a_wins_match_factory):
        assert a_wins_match_factory().results[2]["wins"] == 0

    def test_results_game_losses_for_loser(self, a_wins_match_factory):
        assert a_wins_match_factory().results[2]["losses"] == 2

    def test_results_draw_split_wins(self, draw_match_factory):
        r = draw_match_factory().results
        assert r[1]["wins"] == 1 and r[1]["losses"] == 1
        assert r[2]["wins"] == 1 and r[2]["losses"] == 1

    def test_results_player_agents_a(self, a_wins_match_factory):
        m = a_wins_match_factory()
        assert m.results[1]["player_agents"] == m.total_agents_a

    def test_results_opponent_agents_a(self, a_wins_match_factory):
        m = a_wins_match_factory()
        assert m.results[1]["opponent_agents"] == m.total_agents_b

    def test_results_opponent_field(self, a_wins_match_factory):
        r = a_wins_match_factory().results
        assert r[1]["opponent"] == 2
        assert r[2]["opponent"] == 1

    def test_results_bonus_agents_stored(self):
        m = Match(
            player_a=1,
            player_b=2,
            games=[Game(3, 2), Game(2, 3)],
            bonus_agents_a=1,
            bonus_agents_b=0,
        )
        assert m.results[1]["bonus_agents"] == 1
        assert m.results[2]["bonus_agents"] == 0

    def test_results_cached_same_object(self, a_wins_match_factory):
        m = a_wins_match_factory()
        assert m.results is m.results
