from __future__ import annotations

from pathlib import Path

from contract import ChangeInput, GreedyOutput, ProblemOutput, PuzzleInput

# Fixed problems (coins, amount). Greedy is right for coins-01 only; it uses too many coins for 02, 03
# and 06, gets stuck on 04 although 7 coins work, and 05 cannot be made at all (59 is the largest amount
# 7s and 11s cannot make). coins-07 asks for 0, made with no coins.
PROBLEMS = {
    "coins-01": ([1, 5, 10, 25], 289),
    "coins-02": ([1, 3, 4], 6),
    "coins-03": ([1, 15, 25], 330),
    "coins-04": ([9, 14, 20], 101),
    "coins-05": ([7, 11], 59),
    "coins-06": ([1, 7, 23, 29], 100),
    "coins-07": ([2, 5], 0),
}


def get_problem(given: PuzzleInput, workspace: Path) -> ProblemOutput:
    if given.puzzle_id not in PROBLEMS:
        raise ValueError(f"unknown puzzle {given.puzzle_id!r}: the problems are {', '.join(PROBLEMS)}")
    coins, amount = PROBLEMS[given.puzzle_id]
    return ProblemOutput(puzzle_id=given.puzzle_id, denominations=list(coins), amount=amount)


def problem_record(given: PuzzleInput, workspace: Path) -> ProblemOutput:
    return get_problem(given, workspace)


def greedy_change(given: ChangeInput, workspace: Path) -> GreedyOutput:
    coins = given.denominations
    if not coins or min(coins) <= 0 or len(set(coins)) != len(coins):
        raise ValueError("denominations must be distinct positive integers, at least one")
    if given.amount < 0:
        raise ValueError("amount must be 0 or more")
    taken, left = [], given.amount
    for coin in sorted(coins, reverse=True):
        count, left = divmod(left, coin)
        taken += [coin] * count
    return GreedyOutput(coins=taken, remainder=left)
