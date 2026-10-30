"""The deterministic verifier: each tool's checks live in its own class, on contract instances."""

from contract import Task, Tool

from .change import GetProblem, GreedyChange, verify_change, verify_get_problem

TOOLS = {
    Tool.GET_PROBLEM: GetProblem,
    Tool.GREEDY_CHANGE: GreedyChange,
    Tool.PROBLEM_RECORD: GetProblem,
}
# task -> its output's check, verify_task(arguments, output, reference, workspace)
TASKS = {
    Task.GET_PROBLEM: verify_get_problem,
    Task.MAKE_CHANGE: verify_change,
}


def verify_input(tool, value):
    return TOOLS[Tool(tool)].verify_input(value)


def verify_output(tool, input_value, output_value, workspace):
    return TOOLS[Tool(tool)].verify_output(input_value, output_value, workspace)


def verify_task(task, arguments, output, reference, workspace):
    return TASKS[Task(task)](arguments, output, reference, workspace)
