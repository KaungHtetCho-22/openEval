from __future__ import annotations

import re
from collections.abc import Callable

JudgeFn = Callable[[str], str]
ScorerFn = Callable[[str, str, str], float]


def llm_judge(judge_fn: JudgeFn, *, criteria: str = "") -> ScorerFn:
    def scorer(input: str, output: str, expected: str = "") -> float:
        prompt = _build_prompt(input=input, output=output, expected=expected, criteria=criteria)
        response = judge_fn(prompt)
        return _parse_score(response)

    return scorer


def _build_prompt(*, input: str, output: str, expected: str, criteria: str) -> str:
    criteria_block = f"\nCriteria:\n{criteria.strip()}\n" if criteria.strip() else ""
    expected_block = expected.strip() if expected.strip() else "(not provided)"
    return (
        "You are an impartial evaluator. Rate the model output on a scale from 0.0 to 1.0.\n"
        "Respond with ONLY a number between 0.0 and 1.0.\n\n"
        f"Input:\n{input}\n\n"
        f"Output:\n{output}\n\n"
        f"Expected Output:\n{expected_block}\n"
        f"{criteria_block}"
    )


def _parse_score(text: str) -> float:
    match = re.search(r"\b(0(?:\.\d+)?|1(?:\.0+)?)\b", text.strip())
    if not match:
        return 0.5
    try:
        value = float(match.group(1))
    except ValueError:
        return 0.5
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value
