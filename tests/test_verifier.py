from __future__ import annotations

from pathlib import Path

import pytest
from slimconfig import build_output, plain_output

import verifier
from contract import TASKS, TOOLS, PuzzleInput, Task, Tool
from plugin import get_problem, problem_record

# Fewest coins, found independently by dynamic programming over every amount.
FEWEST = {
    "coins-01": [25] * 11 + [10, 1, 1, 1, 1],
    "coins-02": [3, 3],
    "coins-03": [25] * 12 + [15, 15],
    "coins-04": [20, 20, 20, 14, 9, 9, 9],
    "coins-06": [29, 23, 23, 23, 1, 1],
    "coins-07": [],
}


# The verifier gets contract instances, as NanoAgent's sandbox builds them from JSON.
def verify_input(tool: str, value: dict) -> dict:
    return verifier.verify_input(tool, build_output(value, TOOLS[Tool(tool)][0]))


def verify_output(tool: str, given: dict, made: dict, workspace: Path) -> dict:
    classes = TOOLS[Tool(tool)]
    return verifier.verify_output(tool, build_output(given, classes[0]), build_output(made, classes[1]), str(workspace))


def solve(workspace: Path, puzzle_id: str, output: dict, pin: bool = True) -> dict:
    given, made = TASKS[Task.MAKE_CHANGE]
    record = plain_output(problem_record(PuzzleInput(puzzle_id=puzzle_id), workspace))
    pinned = build_output(record, TOOLS[Tool.PROBLEM_RECORD][1]) if pin else None
    return verifier.verify_task(
        "make-change",
        build_output({"puzzle_id": puzzle_id}, given),
        build_output({"gave_up": False} | output, made),
        pinned,
        str(workspace),
    )


@pytest.mark.parametrize(("puzzle_id", "coins"), list(FEWEST.items()))
def test_approves_the_fewest_coins(tmp_path: Path, puzzle_id: str, coins: list[int]) -> None:
    verdict = solve(tmp_path, puzzle_id, {"possible": True, "coins": coins})
    assert verdict["valid"] is True and verdict["score"] == 1.0 and verdict["details"]["fewest"] == len(coins)


def test_any_order_and_any_equally_short_set_counts(tmp_path: Path) -> None:
    assert solve(tmp_path, "coins-06", {"possible": True, "coins": [1, 23, 29, 23, 1, 23]})["valid"] is True
    # 4 x 23 + 7 + 1 is another 6-coin way to make 100.
    assert solve(tmp_path, "coins-06", {"possible": True, "coins": [23, 23, 23, 23, 7, 1]})["valid"] is True


def test_the_greedy_answer_is_too_many_coins(tmp_path: Path) -> None:
    verdict = solve(tmp_path, "coins-02", {"possible": True, "coins": [4, 1, 1]})
    assert verdict["valid"] is False and verdict["score"] == round(2 / 3, 4) and "more coins" in verdict["message"]


@pytest.mark.parametrize(
    ("coins", "message"),
    [
        ([3, 2, 1], "not a coin"),
        ([3, 4], "add up to 7"),
        ([], "add up to 0"),
        ([3, -3, 3, 3], "not a coin"),
    ],
)
def test_wrong_coins_score_zero(tmp_path: Path, coins: list[int], message: str) -> None:
    verdict = solve(tmp_path, "coins-02", {"possible": True, "coins": coins})
    assert verdict["valid"] is False and verdict["score"] == 0.0 and message in verdict["message"]


def test_impossible_amount(tmp_path: Path) -> None:
    assert solve(tmp_path, "coins-05", {"possible": False, "coins": []})["valid"] is True
    verdict = solve(tmp_path, "coins-05", {"possible": True, "coins": [11, 11, 11, 11, 7, 7]})
    assert verdict["valid"] is False and verdict["score"] == 0.0
    verdict = solve(tmp_path, "coins-05", {"possible": False, "coins": [7]})
    assert verdict["valid"] is False and "empty" in verdict["message"]


def test_calling_a_possible_amount_impossible_is_invalid(tmp_path: Path) -> None:
    # Greedy gets stuck on coins-04, but 7 coins make it.
    verdict = solve(tmp_path, "coins-04", {"possible": False, "coins": []})
    assert verdict["valid"] is False and verdict["score"] == 0.0 and "can be made" in verdict["message"]


def test_refuses_to_judge_without_the_problem(tmp_path: Path) -> None:
    verdict = solve(tmp_path, "coins-02", {"possible": True, "coins": [3, 3]}, pin=False)
    assert verdict["valid"] is False and "problem" in verdict["message"]


def test_tool_task_and_tool_checks(tmp_path: Path) -> None:
    given = {"puzzle_id": "coins-02"}
    made = plain_output(get_problem(PuzzleInput(**given), tmp_path))
    task_given, task_made = TASKS[Task.GET_PROBLEM]
    check = verifier.verify_task(
        "get-problem", build_output(given, task_given), build_output(made, task_made), None, ""
    )
    assert check["valid"] is True
    assert verify_output("get_problem", given, made | {"amount": -1}, tmp_path)["valid"] is False
    change = {"denominations": [1, 3, 4], "amount": 6}
    assert verify_input("greedy_change", change)["valid"] is True
    assert verify_input("greedy_change", change | {"denominations": [0, 1]})["valid"] is False
    assert verify_output("greedy_change", change, {"coins": [4, 1, 1], "remainder": 0}, tmp_path)["valid"] is True
    assert verify_output("greedy_change", change, {"coins": [3, 3], "remainder": 0}, tmp_path)["valid"] is False


def test_giving_up_is_a_failure_with_the_attempt_kept_in_details(tmp_path: Path) -> None:
    verdict = solve(tmp_path, "coins-02", {"possible": True, "coins": [3, 3], "gave_up": True})
    assert verdict["valid"] is False and verdict["score"] == 0.0 and "gave up" in verdict["message"]
    assert verdict["details"]["attempt_score"] == 1.0
    verdict = solve(tmp_path, "coins-02", {"possible": True, "coins": [], "gave_up": True})
    assert verdict["valid"] is False and verdict["score"] == 0.0 and verdict["details"]["gave_up"] is True
