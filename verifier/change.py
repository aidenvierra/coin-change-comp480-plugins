"""Checks for each tool's calls and for the make-change submission, against the pinned problem."""

import re

from .checks import gave_up_verdict, result

PUZZLE_ID = re.compile(r"^coins-\d{2}$")


def coins_problem(coins, amount):
    if not coins or min(coins) <= 0 or len(set(coins)) != len(coins):
        return "denominations must be distinct positive integers, at least one"
    if amount < 0:
        return "amount must be 0 or more"
    return None


def fewest(coins, amount):
    """The fewest coins that make the amount, by dynamic programming over 0..amount; None if impossible."""
    best = [0] + [None] * amount
    for value in range(1, amount + 1):
        options = [best[value - coin] for coin in coins if coin <= value and best[value - coin] is not None]
        best[value] = min(options) + 1 if options else None
    return best[amount]


def greedy(coins, amount):
    taken, left = [], amount
    for coin in sorted(coins, reverse=True):
        count, left = divmod(left, coin)
        taken += [coin] * count
    return taken, left


def _puzzle_input(value):
    if not PUZZLE_ID.fullmatch(value.puzzle_id):
        return result(False, f"puzzle_id {value.puzzle_id!r} is not of the form coins-NN")
    return result(True, "input is valid")


class GetProblem:
    verify_input = staticmethod(_puzzle_input)

    @staticmethod
    def verify_output(input_value, output_value, workspace):
        if output_value.puzzle_id != input_value.puzzle_id:
            return result(False, "the problem is for a different id")
        problem = coins_problem(output_value.denominations, output_value.amount)
        return result(False, problem) if problem else result(True, "problem returned")


class GreedyChange:
    @staticmethod
    def verify_input(value):
        problem = coins_problem(value.denominations, value.amount)
        return result(False, problem) if problem else result(True, "input is valid")

    @staticmethod
    def verify_output(input_value, output_value, workspace):
        if (output_value.coins, output_value.remainder) != greedy(input_value.denominations, input_value.amount):
            return result(False, "the output is not the greedy change")
        return result(True, "greedy change is right")


def verify_get_problem(arguments, output, reference, workspace):
    return GetProblem.verify_output(arguments, output, workspace)


def _judge(arguments, output, reference, workspace):
    """Valid for the right possible flag and coins that are real denominations, add up to the amount and
    are as few as the fewest; more coins than needed scores fewest/count."""
    if reference is None or coins_problem(reference.denominations, reference.amount):
        return result(False, "no usable problem was pinned, so the submission cannot be judged")
    coins, amount = reference.denominations, reference.amount
    best = fewest(coins, amount)
    details = {"fewest": best, "submitted_count": len(output.coins)}
    if not output.possible:
        if output.coins:
            return result(False, "an impossible claim must leave coins empty", score=0.0, **details)
        if best is not None:
            return result(False, f"the amount can be made, with {best} coins", score=0.0, **details)
        return result(True, "correct: the amount cannot be made from these coins", **details)
    if best is None:
        return result(False, "the amount cannot be made from these coins, but possible is true", score=0.0, **details)
    strange = [coin for coin in output.coins if coin not in coins]
    if strange:
        return result(False, f"{strange[0]} is not a coin in {coins}", score=0.0, **details)
    if sum(output.coins) != amount:
        return result(False, f"the coins add up to {sum(output.coins)}, not {amount}", score=0.0, **details)
    if len(output.coins) > best:
        score = round(best / len(output.coins), 4)
        return result(
            False, f"the coins make {amount} but use more coins than the fewest ({best})", score=score, **details
        )
    return result(True, f"correct: {best} coins, the fewest that make {amount}", **details)


def verify_change(arguments, output, reference, workspace):
    return gave_up_verdict(_judge(arguments, output, reference, workspace), output)
