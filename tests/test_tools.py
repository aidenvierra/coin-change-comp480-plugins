from __future__ import annotations

from pathlib import Path

import pytest

from contract import ChangeInput, PuzzleInput, Tool
from plugin import get_problem, greedy_change, problem_record
from plugin.budget import Budget, BudgetSpent
from plugin.problems import PROBLEMS


def test_get_problem_returns_coins_and_amount(tmp_path: Path) -> None:
    problem = get_problem(PuzzleInput(puzzle_id="coins-02"), tmp_path)
    assert (problem.denominations, problem.amount) == ([1, 3, 4], 6)
    assert problem_record(PuzzleInput(puzzle_id="coins-02"), tmp_path) == problem
    with pytest.raises(ValueError, match="unknown puzzle"):
        get_problem(PuzzleInput(puzzle_id="coins-99"), tmp_path)


def test_bank_has_positive_distinct_coins() -> None:
    assert len(PROBLEMS) == 7
    for coins, amount in PROBLEMS.values():
        assert len(set(coins)) == len(coins) and min(coins) > 0 and amount >= 0


@pytest.mark.parametrize(
    ("coins", "amount", "used", "remainder"),
    [
        ([1, 3, 4], 6, [4, 1, 1], 0),  # greedy, not the fewest (3 + 3)
        ([9, 14, 20], 101, [20, 20, 20, 20, 20], 1),  # greedy gets stuck
        ([5, 1], 7, [5, 1, 1], 0),
        ([2, 5], 0, [], 0),
    ],
)
def test_greedy_takes_the_largest_coin_each_time(
    tmp_path: Path, coins: list[int], amount: int, used: list[int], remainder: int
) -> None:
    output = greedy_change(ChangeInput(denominations=coins, amount=amount), tmp_path)
    assert (output.coins, output.remainder) == (used, remainder)


@pytest.mark.parametrize(("coins", "amount"), [([], 5), ([0, 1], 5), ([1, 1], 5), ([1], -1)])
def test_greedy_refuses_bad_input(tmp_path: Path, coins: list[int], amount: int) -> None:
    with pytest.raises(ValueError):
        greedy_change(ChangeInput(denominations=coins, amount=amount), tmp_path)


def test_budget_allows_twelve_calls_per_problem() -> None:
    budget = Budget(limit=12)
    budget.charge(Tool.GET_PROBLEM, {"puzzle_id": "coins-01"})
    for _ in range(11):
        budget.charge(Tool.GREEDY_CHANGE, {})
    with pytest.raises(BudgetSpent, match="submit your best answer now, or set gave_up"):
        budget.charge(Tool.GREEDY_CHANGE, {})
    budget.charge(Tool.PROBLEM_RECORD, {})
    budget.charge(Tool.GET_PROBLEM, {"puzzle_id": "coins-02"})
    assert budget.used == 1
