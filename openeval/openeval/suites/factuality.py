from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..async_runner import arun as arun_eval
from ..models import EvalCase, EvalSummary
from ..runner import run as run_eval
from ..scorers import contains, exact_match

ModelFn = Callable[[str], str]


CASES: list[EvalCase] = [
    EvalCase(input="What is the capital of France?", expected_output="Paris"),
    EvalCase(input="What is the capital of Japan?", expected_output="Tokyo"),
    EvalCase(input="What is the largest planet in our solar system?", expected_output="Jupiter"),
    EvalCase(input="What gas do plants absorb from the atmosphere?", expected_output="carbon dioxide"),
    EvalCase(input="What is the chemical symbol for water?", expected_output="H2O"),
    EvalCase(input="How many continents are there on Earth?", expected_output="7"),
    EvalCase(input="Who wrote '1984'?", expected_output="George Orwell"),
    EvalCase(input="In which year did the Apollo 11 moon landing occur?", expected_output="1969"),
    EvalCase(input="What is the square root of 81?", expected_output="9"),
    EvalCase(input="What is the freezing point of water in Celsius?", expected_output="0"),
    EvalCase(input="What is the capital of Canada?", expected_output="Ottawa"),
    EvalCase(input="Which ocean is the largest?", expected_output="Pacific"),
    EvalCase(input="What is the speed of light in vacuum (approx, km/s)?", expected_output="300000"),
    EvalCase(input="Who painted the Mona Lisa?", expected_output="Leonardo da Vinci"),
    EvalCase(input="What is the primary language spoken in Brazil?", expected_output="Portuguese"),
]


def get_scorers() -> dict[str, Callable[[str, str, str], float]]:
    return {"exact_match": exact_match, "contains": contains}


def run_suite(model_fn: ModelFn, *, pass_threshold: float = 0.7) -> EvalSummary:
    return run_eval(model_fn, CASES, get_scorers(), pass_threshold=pass_threshold)


def run(model_fn: ModelFn) -> EvalSummary:  # noqa: A001
    return run_suite(model_fn)


async def arun_suite(
    model_fn: Callable[[str], Any], *, pass_threshold: float = 0.7, concurrency: int = 10
) -> EvalSummary:
    return await arun_eval(
        model_fn, CASES, get_scorers(), pass_threshold=pass_threshold, concurrency=concurrency
    )


async def arun(model_fn: Callable[[str], Any], *, concurrency: int = 10) -> EvalSummary:  # noqa: A001
    return await arun_suite(model_fn, concurrency=concurrency)
