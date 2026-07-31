"""Display functions for tournament results.

This module provides various ways to visualize tournament results, including
round-by-round pairings, tournament summaries, and stacked round views.
"""

from __future__ import annotations

from statistics import fmean, median, pstdev
from typing import Callable, Optional

from .models import Player, Tournament
from .standings import compute_records, group_by_record, sort_groups


def display_round(
    tournament: Tournament,
    round_number: int,
    *,
    extra_fields: Optional[Callable[[int, Player, dict], dict]] = None,
) -> str:
    """Display the results of a specific round.

    Shows for each match:
    - Player pairing (names and IDs)
    - Skill levels
    - Previous record (before this round)
    - Agent totals for and against

    Args:
        tournament: The tournament to display.
        round_number: The round number to display (1-indexed).
        extra_fields: Optional function that takes (pid, player, record) and returns
            a dict of additional fields to display. This allows easy extension.

    Returns:
        A formatted string with the round results.
    """
    if round_number < 1 or round_number > len(tournament.rounds):
        return f"Round {round_number} not found (tournament has {len(tournament.rounds)} rounds)."

    round_obj = tournament.rounds[round_number - 1]
    records_before = compute_records(tournament, through_round=round_number - 1)

    lines = [
        f"{'=' * 80}",
        f"Round {round_number}",
        f"{'=' * 80}",
    ]

    for match in round_obj.matches:
        a_pid = match.player_a
        b_pid = match.player_b
        player_a = next(p for p in tournament.players if p.pid == a_pid)
        player_b = next(p for p in tournament.players if p.pid == b_pid)

        rec_a = records_before.get(a_pid)
        rec_b = records_before.get(b_pid)

        lines.append(
            f"\nMatch: {player_a.name} (ID: {a_pid}) vs {player_b.name} (ID: {b_pid})"
        )
        lines.append(f"  Skills: {player_a.skill} vs {player_b.skill}")

        if rec_a and rec_b:
            lines.append(
                f"  Records before: {rec_a.wins}-{rec_a.losses} (diff: {rec_a.agent_diff}) "
                f"vs {rec_b.wins}-{rec_b.losses} (diff: {rec_b.agent_diff})"
            )
        else:
            lines.append("  Records before: (first round)")

        # Get results from this match
        result_a = match.results.get(a_pid, {})
        result_b = match.results.get(b_pid, {})

        lines.append(
            f"  Result: {result_a.get('wins', 0)}-{result_a.get('losses', 0)} "
            f"(agents: {result_a.get('player_agents', 0)}-{result_a.get('opponent_agents', 0)}) "
            f"vs {result_b.get('wins', 0)}-{result_b.get('losses', 0)} "
            f"(agents: {result_b.get('player_agents', 0)}-{result_b.get('opponent_agents', 0)})"
        )

        # Add extra fields if provided
        if extra_fields:
            for pid, player, rec in [
                (a_pid, player_a, rec_a),
                (b_pid, player_b, rec_b),
            ]:
                if rec:
                    fields = extra_fields(pid, player, rec)
                    if fields:
                        lines.append(
                            f"  {player.name}: {', '.join(f'{k}={v}' for k, v in fields.items())}"
                        )

    return "\n".join(lines)


def display_tournament_summary(tournament: Tournament) -> str:
    """Display a summary of the tournament results.

    Shows final standings with records and agent differentials.

    Args:
        tournament: The tournament to summarize.

    Returns:
        A formatted string with the tournament summary.
    """
    final_records = compute_records(tournament)
    sorted_players = sorted(
        tournament.players,
        key=lambda p: (
            -final_records[p.pid].wins,
            final_records[p.pid].losses,
            -final_records[p.pid].agent_diff,
        ),
    )

    lines = [
        f"{'=' * 80}",
        f"Tournament Summary ({len(tournament.players)} players, {len(tournament.rounds)} rounds)",
        f"{'=' * 80}",
        "",
        f"{'Rank':<6} {'Player':<20} {'Skill':<8} {'Record':<12} {'Agent Diff':<12} {'Agent Ratio':<12}",
        f"{'-' * 80}",
    ]

    for rank, player in enumerate(sorted_players, start=1):
        rec = final_records[player.pid]
        lines.append(
            f"{rank:<6} {player.name:<20} {player.skill:<8} {rec.wins}-{rec.losses:<9} "
            f"{rec.agent_diff:<12} {rec.agent_total_ratio:<12.3f}"
        )

    return "\n".join(lines)


def display_stacked_rounds(
    tournament: Tournament,
    *,
    show_groups: bool = True,
    rating_fn: Optional[Callable] = None,
) -> str:
    """Display rounds stacked side-by-side with player rows and round columns.

    Each row represents a player, each column represents a round. Shows
    which group the player is in at each stage if show_groups is True.

    Args:
        tournament: The tournament to display.
        show_groups: If True, show the record group for each player at each round.
        rating_fn: Optional rating function for sorting within groups (defaults to agent differential).

    Returns:
        A formatted string with the stacked rounds view.
    """
    if not tournament.rounds:
        return "No rounds to display."

    # Column width constants
    PLAYER_WIDTH = 20
    ROUND_WIDTH = 25

    lines = [
        f"{'=' * 100}",
        f"Stacked Rounds View ({len(tournament.players)} players, {len(tournament.rounds)} rounds)",
        f"{'=' * 100}",
    ]

    # Sort players by final record for consistent ordering
    final_records = compute_records(tournament)
    sorted_players = sorted(
        tournament.players,
        key=lambda p: (
            -final_records[p.pid].wins,
            final_records[p.pid].losses,
            -final_records[p.pid].agent_diff,
        ),
    )

    # Header row
    header = f"{'Player':<{PLAYER_WIDTH}}"
    for r in range(1, len(tournament.rounds) + 1):
        header += f"{'Round ' + str(r):<{ROUND_WIDTH}}"
    header += "Final"
    lines.append(header)
    lines.append("-" * 100)

    # Build records for each round
    round_records = {}
    for r in range(1, len(tournament.rounds) + 1):
        round_records[r] = compute_records(tournament, through_round=r)

    # Get groups for each round if requested
    round_groups = {}
    if show_groups:
        for r in range(1, len(tournament.rounds) + 1):
            recs = round_records[r]
            groups = group_by_record(recs)
            sorted_groups = sort_groups(groups, rating_fn=rating_fn)
            # Build a mapping from pid to group
            pid_to_group = {}
            for group_key, recs_in_group in sorted_groups.items():
                for rec in recs_in_group:
                    pid_to_group[rec.pid] = group_key.split("-")[0]
            round_groups[r] = pid_to_group

    # Player rows
    for player in sorted_players:
        row = f"{player.name:<{PLAYER_WIDTH}}"
        for r in range(1, len(tournament.rounds) + 1):
            rec = round_records[r][player.pid]
            if show_groups:
                cell = f"{rec.wins}-{rec.losses} (diff:{rec.agent_diff}) group:{round_groups[r].get(player.pid, '')}"
            else:
                cell = f"{rec.wins}-{rec.losses} (diff:{rec.agent_diff})"
            row += f"{cell:<{ROUND_WIDTH}}"
        # Final record
        final_rec = final_records[player.pid]
        row += f"{final_rec.wins}-{final_rec.losses} (diff:{final_rec.agent_diff})"
        lines.append(row)

    return "\n".join(lines)


def display_match_details(
    tournament: Tournament,
    round_number: int,
    match_index: int,
) -> str:
    """Display detailed information about a specific match.

    Shows game-by-game results and agent totals.

    Args:
        tournament: The tournament containing the match.
        round_number: The round number (1-indexed).
        match_index: The match index within the round (0-indexed).

    Returns:
        A formatted string with match details.
    """
    if round_number < 1 or round_number > len(tournament.rounds):
        return f"Round {round_number} not found."

    round_obj = tournament.rounds[round_number - 1]
    if match_index < 0 or match_index >= len(round_obj.matches):
        return f"Match {match_index} not found in round {round_number}."

    match = round_obj.matches[match_index]
    player_a = next(p for p in tournament.players if p.pid == match.player_a)
    player_b = next(p for p in tournament.players if p.pid == match.player_b)

    lines = [
        f"{'=' * 80}",
        f"Match Details: Round {round_number}, Match {match_index + 1}",
        f"{'=' * 80}",
        f"{player_a.name} (ID: {player_a.pid}, skill: {player_a.skill}) "
        f"vs {player_b.name} (ID: {player_b.pid}, skill: {player_b.skill})",
        "",
        "Games:",
    ]

    for i, game in enumerate(match.games, start=1):
        lines.append(f"  Game {i}: {game.agents_a}-{game.agents_b}")

    lines.append("")
    lines.append("Totals:")
    lines.append(f"  {player_a.name}: {match.total_agents_a} agents")
    lines.append(f"  {player_b.name}: {match.total_agents_b} agents")
    lines.append("")
    lines.append("Results:")
    result_a = match.results.get(match.player_a, {})
    result_b = match.results.get(match.player_b, {})
    lines.append(
        f"  {player_a.name}: {result_a.get('wins', 0)} wins, {result_a.get('losses', 0)} losses"
    )
    lines.append(
        f"  {player_b.name}: {result_b.get('wins', 0)} wins, {result_b.get('losses', 0)} losses"
    )

    return "\n".join(lines)


def display_player_performance(
    tournament: Tournament,
    player_pid: int,
    *,
    rating_fn: Optional[Callable] = None,
) -> str:
    """Display a player's performance over the course of the tournament.

    Each row represents a round, showing:
    - Opponent PID
    - Opponent's record before the match
    - Opponent's total agents scored up to that point
    - Opponent's agents taken (agents against)
    - Opponent's agent differential
    - Opponent's agent ratio
    - The group the player is in that round

    Args:
        tournament: The tournament to analyze.
        player_pid: The player ID to display performance for.
        rating_fn: Optional rating function for sorting within groups (defaults to agent differential).

    Returns:
        A formatted string with the player's performance over the tournament.
    """
    player = next((p for p in tournament.players if p.pid == player_pid), None)
    if player is None:
        return f"Player {player_pid} not found in tournament."

    if not tournament.rounds:
        return "No rounds to display."

    # Column width constants
    COL_WIDTH = 12

    lines = [
        f"{'=' * 100}",
        f"Player Performance: {player.name} (ID: {player_pid}, skill: {player.skill})",
        f"{'=' * 100}",
    ]

    # Header row
    header = (
        f"{'Round':<{COL_WIDTH}} {'Opponent':<{COL_WIDTH}} {'Opp Record':<{COL_WIDTH}} "
    )
    header += f"{'Opp Agents For':<{COL_WIDTH}} {'Opp Agents Against':<{COL_WIDTH}} "
    header += f"{'Opp Diff':<{COL_WIDTH}} {'Opp Ratio':<{COL_WIDTH}} {'Your Group':<{COL_WIDTH}}"
    lines.append(header)
    lines.append("-" * 100)

    # Build records for each round
    round_records = {}
    for r in range(1, len(tournament.rounds) + 1):
        round_records[r] = compute_records(tournament, through_round=r)

    # Get groups for each round
    round_groups = {}
    for r in range(1, len(tournament.rounds) + 1):
        recs = round_records[r]
        groups = group_by_record(recs)
        sorted_groups = sort_groups(groups, rating_fn=rating_fn)
        # Build a mapping from pid to group
        pid_to_group = {}
        for group_key, recs_in_group in sorted_groups.items():
            for rec in recs_in_group:
                pid_to_group[rec.pid] = group_key
        round_groups[r] = pid_to_group

    # Build player's opponent for each round
    for r in range(1, len(tournament.rounds) + 1):
        round_obj = tournament.rounds[r - 1]
        opponent = None

        # Find the match this player participated in
        for match in round_obj.matches:
            if match.player_a == player_pid:
                opponent = match.player_b
                break
            elif match.player_b == player_pid:
                opponent = match.player_a
                break

        if opponent is None:
            lines.append(
                f"{r:<{COL_WIDTH}} {'(no match)':<{COL_WIDTH}} {'-':<{COL_WIDTH}} {'-':<{COL_WIDTH}} {'-':<{COL_WIDTH}} {'-':<{COL_WIDTH}} {'-':<{COL_WIDTH}} {'-':<{COL_WIDTH}}"
            )
            continue

        # Get opponent's record before this round
        opponent_rec_before = round_records[r - 1].get(opponent) if r > 1 else None

        if opponent_rec_before:
            row = f"{r:<{COL_WIDTH}} {opponent:<{COL_WIDTH}} "
            row += f"{f'{opponent_rec_before.wins}-{opponent_rec_before.losses}':<{COL_WIDTH}} "
            row += f"{opponent_rec_before.agents_for:<{COL_WIDTH}} "
            row += f"{opponent_rec_before.agents_against:<{COL_WIDTH}} "
            row += f"{opponent_rec_before.agent_diff:<{COL_WIDTH}} "
            row += f"{opponent_rec_before.agent_total_ratio:<{COL_WIDTH}.3f} "
            row += f"{round_groups[r].get(player_pid, 'N/A'):<{COL_WIDTH}}"
        else:
            row = f"{r:<{COL_WIDTH}} {opponent:<{COL_WIDTH}} {'(first round)':<{COL_WIDTH}} {'0':<{COL_WIDTH}} {'0':<{COL_WIDTH}} {'0':<{COL_WIDTH}} {'0.000':<{COL_WIDTH}} {round_groups[r].get(player_pid, 'N/A'):<{COL_WIDTH}}"

        lines.append(row)

    # Final summary
    final_rec = round_records[len(tournament.rounds)][player_pid]
    lines.append("")
    lines.append(f"Final Record: {final_rec.wins}-{final_rec.losses}")
    lines.append(f"Final Agent Differential: {final_rec.agent_diff}")
    lines.append(f"Final Agent Total Ratio: {final_rec.agent_total_ratio:.3f}")

    return "\n".join(lines)


def display_skill_statistics(tournament: Tournament) -> str:
    """Display basic statistics about the skill levels of players in the tournament.

    Shows mean, median, and standard deviation of player skills.

    Args:
        tournament: The tournament to analyze.

    Returns:
        A formatted string with skill statistics.
    """
    skills = [p.skill for p in tournament.players]

    if not skills:
        return "No players in tournament."

    mean_skill = fmean(skills)
    median_skill = median(skills)
    std_skill = pstdev(skills) if len(skills) > 1 else 0.0
    min_skill = min(skills)
    max_skill = max(skills)

    lines = [
        f"{'=' * 80}",
        f"Skill Statistics ({len(tournament.players)} players)",
        f"{'=' * 80}",
        f"Mean skill: {mean_skill:.4f}",
        f"Median skill: {median_skill:.4f}",
        f"Standard deviation: {std_skill:.4f}",
        f"Min skill: {min_skill:.4f}",
        f"Max skill: {max_skill:.4f}",
        f"Range: {max_skill - min_skill:.4f}",
    ]

    return "\n".join(lines)


def display_metrics(tournament: Tournament) -> str:
    """Display evaluation metrics for the tournament.

    Shows the metrics from tournament.metrics to evaluate pairing algorithm quality:
    - Mean skill gap (lower = better matched)
    - Standings-skill correlation (higher = better)
    - Rematch count (lower = better)

    Args:
        tournament: The tournament to evaluate.

    Returns:
        A formatted string with evaluation metrics.
    """
    from .metrics import mean_skill_gap, rematch_count, standings_skill_correlation

    lines = [
        f"{'=' * 80}",
        f"Tournament Evaluation Metrics ({len(tournament.players)} players, {len(tournament.rounds)} rounds)",
        f"{'=' * 80}",
    ]

    mean_gap = mean_skill_gap(tournament)
    correlation = standings_skill_correlation(tournament)
    rematches = rematch_count(tournament)

    lines.append(f"Mean skill gap: {mean_gap:.4f}")
    lines.append(f"  (Average absolute skill difference between paired players)")
    lines.append(f"  Lower values indicate better-matched opponents")
    lines.append("")
    lines.append(f"Standings-skill correlation: {correlation:.4f}")
    lines.append(f"  (Correlation between final standings and true skill)")
    lines.append(f"  +1 = perfect recovery of skill order, 0 = no relation")
    lines.append("")
    lines.append(f"Rematch count: {rematches}")
    lines.append(f"  (Number of times any pair was paired more than once)")
    lines.append(f"  Lower values indicate more variety in pairings")

    return "\n".join(lines)


def display_metrics_comparison(tournaments: dict[str, Tournament]) -> str:
    """Display a comparison of metrics across multiple tournaments.

    Useful for comparing different pairing strategies or parameters.

    Args:
        tournaments: A dictionary mapping names to Tournament objects.

    Returns:
        A formatted string comparing metrics across tournaments.
    """
    from .metrics import mean_skill_gap, rematch_count, standings_skill_correlation

    if not tournaments:
        return "No tournaments to compare."

    # Column width constants
    NAME_WIDTH = 20
    COL_WIDTH = 15

    lines = [
        f"{'=' * 100}",
        f"Metrics Comparison ({len(tournaments)} tournaments)",
        f"{'=' * 100}",
    ]

    # Header row
    header = (
        f"{'Strategy':<{NAME_WIDTH}} {'Players':<{COL_WIDTH}} {'Rounds':<{COL_WIDTH}} "
    )
    header += f"{'Mean Skill Gap':<{COL_WIDTH}} {'Correlation':<{COL_WIDTH}} {'Rematches':<{COL_WIDTH}}"
    lines.append(header)
    lines.append("-" * 100)

    # Data rows
    for name, tour in tournaments.items():
        mean_gap = mean_skill_gap(tour)
        correlation = standings_skill_correlation(tour)
        rematches = rematch_count(tour)

        row = f"{name:<{NAME_WIDTH}} {len(tour.players):<{COL_WIDTH}} {len(tour.rounds):<{COL_WIDTH}} "
        row += f"{mean_gap:<{COL_WIDTH}.4f} {correlation:<{COL_WIDTH}.4f} {rematches:<{COL_WIDTH}}"
        lines.append(row)

    return "\n".join(lines)
