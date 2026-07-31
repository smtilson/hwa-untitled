"""Unit tests for tournament.standings.Record."""

from __future__ import annotations

import pytest

from tournament.models import Player
from tournament.standings import Record, agent_differential


class TestRecordProperties:
    def test_default_zeros(self):
        r = Record()
        assert r.wins == 0 and r.losses == 0
        assert r.agents_for == 0 and r.agents_against == 0
        assert r.bonus_agents_won == 0
        assert r.player is None
        assert r.skill is None
        assert r.name is None
        assert r.pid == -1

    def test_record_exposes_player_skill_and_name(self):
        player = Player(pid=1, name="Alice", skill=12.5)
        r = Record(player=player)
        assert r.skill == 12.5
        assert r.name == "Alice"
        assert r.player is player
        assert r.pid == 1

    def test_matches_played_after_two_results(self, record_factory):
        # Each match contributes 2 game-decisions (wins+losses=2 per match)
        r = record_factory([(2, 0, 6, 3), (0, 2, 3, 6)])
        assert r.matches_played == 2

    def test_matches_played_with_draws(self, record_factory):
        r = record_factory([(1, 1, 5, 5)])
        assert r.matches_played == 1

    def test_agent_diff(self, record_factory):
        r = record_factory([(2, 0, 6, 3)])
        assert r.agent_diff == 3

    def test_agent_diff_negative(self, record_factory):
        r = record_factory([(0, 2, 3, 6)])
        assert r.agent_diff == -3

    def test_agent_total_ratio(self, record_factory):
        r = record_factory([(2, 0, 6, 3)])
        expected = 6 / (6 + 3)
        assert r.agent_total_ratio == pytest.approx(expected)

    def test_agent_total_ratio_zero_when_no_games(self):
        assert Record().agent_total_ratio == 0.0

    def test_record_str_format(self):
        r = Record()
        # record_str is "wins-losses, ratio, diff"
        assert "-" in r.record_str


class TestRecordAgentSeq:
    def test_agent_seq_built_from_results(self, record_factory):
        r = record_factory([(2, 0, 6, 3), (0, 2, 2, 5)])
        seq = r.agent_seq
        assert seq == [(6, 3), (2, 5)]

    def test_agent_seq_empty_for_new_record(self):
        assert Record().agent_seq == []

    def test_agent_seq_cached(self, record_factory):
        r = record_factory([(2, 0, 6, 3)])
        seq1 = r.agent_seq
        seq2 = r.agent_seq
        assert seq1 is seq2

    def test_agent_seq_invalidated_by_process_result(
        self, record_factory, result_factory
    ):
        r = record_factory([(2, 0, 6, 3)])
        _ = r.agent_seq  # build cache
        r.process_result(result_factory(0, 2, 2, 5))
        assert r.agent_seq == [(6, 3), (2, 5)]  # rebuilt

    def test_agent_score_applies_metric(self, record_factory):
        r = record_factory([(2, 0, 6, 3)])
        assert r.agent_score(agent_differential) == 3


class TestRecordProcessResult:
    def test_wins_accumulate(self, result_factory):
        r = Record(player=Player(pid=1, name="P1", skill=0.0))
        r.process_result(result_factory(2, 0, 6, 3))
        r.process_result(result_factory(2, 0, 5, 2))
        assert r.wins == 4

    def test_losses_accumulate(self, result_factory):
        r = Record(player=Player(pid=1, name="P1", skill=0.0))
        r.process_result(result_factory(0, 2, 3, 6))
        assert r.losses == 2

    def test_agents_accumulate(self, result_factory):
        r = Record(player=Player(pid=1, name="P1", skill=0.0))
        r.process_result(result_factory(2, 0, 6, 3))
        r.process_result(result_factory(0, 2, 2, 5))
        assert r.agents_for == 8
        assert r.agents_against == 8

    def test_bonus_accumulates(self, result_factory):
        r = Record(player=Player(pid=1, name="P1", skill=0.0))
        r.process_result(result_factory(1, 1, 5, 5, bonus=1))
        assert r.bonus_agents_won == 1


class TestRecordFromRawResults:
    def test_builds_from_list(self, result_factory):
        player = Player(pid=1, name="P1", skill=0.0)
        raw = [result_factory(2, 0, 6, 3, pid=1), result_factory(1, 1, 5, 5, pid=1)]
        r = Record.from_raw_results(raw, player=player)
        assert r.pid == 1
        assert r.wins == 3
        assert r.matches_played == 2

    def test_from_raw_results_with_player(self, result_factory):
        player = Player(pid=1, name="Bob", skill=7.0)
        raw = [result_factory(2, 0, 6, 3, pid=1), result_factory(1, 1, 5, 5, pid=1)]
        r = Record.from_raw_results(raw, player=player)
        assert r.pid == 1
        assert r.player is player
        assert r.skill == 7.0

    def test_raises_on_empty_list(self):
        with pytest.raises(ValueError):
            Record.from_raw_results([])
