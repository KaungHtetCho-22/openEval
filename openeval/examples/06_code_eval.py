from __future__ import annotations

"""
Example 06 — Code generation eval

This shows:
- regex-based format checks
- a safe "compiles" scorer (AST parse) instead of executing code

Run:
  python examples/06_code_eval.py
"""

import ast

from openeval import EvalCase, run
from openeval.scorers import regex


def main() -> None:
    cases = [
        EvalCase(
            input="Write a Python function add(a, b) that returns a+b. Output only code.",
            expected_output="def add",
        ),
        EvalCase(
            input="Write a Python function is_even(n) that returns True if n is even. Output only code.",
            expected_output="def is_even",
        ),
    ]

    def code_model(prompt: str) -> str:
        if "add(" in prompt:
            return "def add(a, b):\n    return a + b\n"
        return "def is_even(n):\n    return n % 2 == 0\n"

    # Scorer 1: looks like Python code (very rough)
    looks_like_python = regex(r"^def\s+\w+\(.*\):", flags=0)

    # Scorer 2: valid Python syntax
    def parses(_input: str, output: str, _expected: str = "") -> float:
        try:
            ast.parse(output)
            return 1.0
        except SyntaxError:
            return 0.0

    summary = run(code_model, cases, {"format": looks_like_python, "parses": parses})
    print(f"Pass rate: {summary.pass_rate:.0%}")


if __name__ == "__main__":
    main()

