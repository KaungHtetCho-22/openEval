from __future__ import annotations

import re
from collections.abc import Callable

ScorerFn = Callable[[str, str, str], float]


def make_exact_match(*, case_sensitive: bool = False) -> ScorerFn:
    def scorer(_input: str, output: str, expected: str = "") -> float:
        if case_sensitive:
            return 1.0 if output == expected else 0.0
        return 1.0 if output.strip().lower() == expected.strip().lower() else 0.0

    return scorer


exact_match: ScorerFn = make_exact_match(case_sensitive=False)


def contains(_input: str, output: str, expected: str = "") -> float:
    if not expected:
        return 0.0
    return 1.0 if expected.strip().lower() in output.lower() else 0.0


def regex(pattern: str, *, flags: int = 0) -> ScorerFn:
    compiled = re.compile(pattern, flags=flags)

    def scorer(_input: str, output: str, _expected: str = "") -> float:
        return 1.0 if compiled.search(output) is not None else 0.0

    return scorer

