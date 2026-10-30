"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    GET_PROBLEM = "get_problem"
    GREEDY_CHANGE = "greedy_change"
    PROBLEM_RECORD = "problem_record"


class Task(Enum):
    GET_PROBLEM = "get-problem"
    MAKE_CHANGE = "make-change"


DENOMINATIONS = "The coin values available, each a distinct positive integer; any coin may be used any number of times"


GAVE_UP = (
    "True only if you could not solve it: then submit your best partial attempt, or empty values."
    " False when you believe your answer is right"
)


@dataclass
class PuzzleInput(Output):
    puzzle_id: Annotated[str, "The problem's id, e.g. coins-01"]


@dataclass
class ProblemOutput(Output):
    puzzle_id: Annotated[str, "The problem's id, as given"]
    denominations: Annotated[list[int], DENOMINATIONS]
    amount: Annotated[int, "The amount to make exactly, 0 or more"]


@dataclass
class ChangeInput(Output):
    denominations: Annotated[list[int], DENOMINATIONS]
    amount: Annotated[int, "The amount to make, 0 or more"]


@dataclass
class GreedyOutput(Output):
    coins: Annotated[list[int], "The coins taken, largest first, always taking the largest coin that still fits"]
    remainder: Annotated[int, "What is left that no coin fits; 0 when the greedy coins make the amount"]


@dataclass
class ChangeOutput(Output):
    possible: Annotated[bool, "Whether the amount can be made exactly from the coins at all"]
    coins: Annotated[list[int], "The fewest coins that make the amount exactly, in any order; empty if impossible"]
    gave_up: Annotated[bool, GAVE_UP]


TOOLS = {
    Tool.GET_PROBLEM: (PuzzleInput, ProblemOutput),
    Tool.GREEDY_CHANGE: (ChangeInput, GreedyOutput),
    Tool.PROBLEM_RECORD: (PuzzleInput, ProblemOutput),
}
TASKS = {
    Task.GET_PROBLEM: (PuzzleInput, ProblemOutput),
    Task.MAKE_CHANGE: (PuzzleInput, ChangeOutput),
}
