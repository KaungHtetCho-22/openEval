from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..async_runner import arun as arun_eval
from ..models import EvalCase, EvalSummary
from ..runner import run as run_eval
from ..scorers import regex

ModelFn = Callable[[str], str]


CASES: list[EvalCase] = [
    EvalCase(
        input="Respond only with a number.",
        expected_output=r"^\d+$",
        metadata={"example_output": "42"},
    ),
    EvalCase(
        input="Answer in exactly three words: describe the ocean.",
        expected_output=r"^\w+\s+\w+\s+\w+$",
        metadata={"example_output": "vast blue expanse"},
    ),
    EvalCase(
        input="Respond with YES or NO only. Is 2+2=4?",
        expected_output=r"^(YES|NO)$",
        metadata={"example_output": "YES"},
    ),
    EvalCase(
        input="Respond only with a lowercase hex color code (e.g. #1a2b3c).",
        expected_output=r"^#[0-9a-f]{6}$",
        metadata={"example_output": "#1a2b3c"},
    ),
    EvalCase(
        input="Return a JSON object with keys 'a' and 'b' as integers. No extra text.",
        expected_output=r"^\{\s*\"a\"\s*:\s*\d+\s*,\s*\"b\"\s*:\s*\d+\s*\}$",
        metadata={"example_output": '{"a": 1, "b": 2}'},
    ),
    EvalCase(
        input="Reply with exactly one emoji and nothing else.",
        expected_output=r"^[^\w\s]{1,2}$",
        metadata={"example_output": "👍"},
    ),
    EvalCase(
        input="Answer with an email address only.",
        expected_output=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        metadata={"example_output": "test@example.com"},
    ),
    EvalCase(
        input="Return a UUID v4 only.",
        expected_output=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        metadata={"example_output": "123e4567-e89b-42d3-a456-556642440000"},
    ),
    EvalCase(
        input="Reply with two bullet points, each starting with '- ' (dash+space).",
        expected_output=r"^-\s+.+\n-\s+.+$",
        metadata={"example_output": "- one\n- two"},
    ),
    EvalCase(
        input="Respond with 'OK' followed by a space and a 2-digit number.",
        expected_output=r"^OK\s+\d{2}$",
        metadata={"example_output": "OK 07"},
    ),
    EvalCase(
        input="Respond with a single word in ALL CAPS.",
        expected_output=r"^[A-Z]+$",
        metadata={"example_output": "HELLO"},
    ),
    EvalCase(
        input="Respond with a date in YYYY-MM-DD format.",
        expected_output=r"^\d{4}-\d{2}-\d{2}$",
        metadata={"example_output": "2026-03-20"},
    ),
    EvalCase(
        input="Respond with exactly 5 characters (any).",
        expected_output=r"^.{5}$",
        metadata={"example_output": "abcde"},
    ),
    EvalCase(
        input="Return a markdown heading level 2 only (starts with '## ').",
        expected_output=r"^##\s+.+$",
        metadata={"example_output": "## Title"},
    ),
    EvalCase(
        input="Respond with a comma-separated list of exactly 3 items.",
        expected_output=r"^[^,]+,\s*[^,]+,\s*[^,]+$",
        metadata={"example_output": "a, b, c"},
    ),
]


def get_scorers() -> dict[str, Callable[[str, str, str], float]]:
    cache: dict[str, Callable[[str, str, str], float]] = {}

    def format_scorer(input: str, output: str, expected: str = "") -> float:
        if not expected:
            return 0.0
        scorer = cache.get(expected)
        if scorer is None:
            scorer = regex(expected)
            cache[expected] = scorer
        return scorer(input, output, "")

    return {"format": format_scorer}


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
