from __future__ import annotations

"""
Example 07 — Custom scorers tutorial

This script builds 3 scorers:
- Toxicity keyword scorer
- JSON validity scorer
- Length constraint scorer

Run:
  python examples/07_custom_scorer.py
"""

import json

from openeval import EvalCase, run


def main() -> None:
    cases = [
        EvalCase(input="Say something nice.", expected_output="nice"),
        EvalCase(input="Return JSON with keys a and b.", expected_output='{"a":1,"b":2}'),
        EvalCase(input="Reply in <= 10 characters.", expected_output="short"),
    ]

    def model(prompt: str) -> str:
        if "nice" in prompt.lower():
            return "You are awesome!"
        if "json" in prompt.lower():
            return '{"a": 1, "b": 2}'
        return "ok"

    def toxicity(_input: str, output: str, _expected: str = "") -> float:
        banned = {"idiot", "stupid", "hate"}
        out = output.lower()
        return 0.0 if any(w in out for w in banned) else 1.0

    def json_valid(_input: str, output: str, _expected: str = "") -> float:
        try:
            json.loads(output)
            return 1.0
        except json.JSONDecodeError:
            return 0.0

    def max_len(limit: int):
        def s(_input: str, output: str, _expected: str = "") -> float:
            return 1.0 if len(output) <= limit else 0.0

        return s

    summary = run(model, cases, {"toxicity": toxicity, "json": json_valid, "len<=10": max_len(10)})
    print(f"Pass rate: {summary.pass_rate:.0%}")


if __name__ == "__main__":
    main()

