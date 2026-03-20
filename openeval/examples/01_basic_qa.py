from __future__ import annotations

"""
Example 01 — Basic QA eval (no API keys needed)

Run:
  python examples/01_basic_qa.py
"""

from openeval import EvalCase, run
from openeval.adapters import callable_adapter
from openeval.scorers import contains, exact_match


def main() -> None:
    cases = [
        EvalCase(input="What is 2+2?", expected_output="4"),
        EvalCase(input="What is the capital of France?", expected_output="Paris"),
        EvalCase(input="Name a planet.", expected_output="Mars"),
        EvalCase(input="What is the chemical symbol for water?", expected_output="H2O"),
        EvalCase(input="How many continents are there?", expected_output="7"),
        EvalCase(input="Square root of 81?", expected_output="9"),
        EvalCase(input="Largest planet in the solar system?", expected_output="Jupiter"),
        EvalCase(input="Primary language spoken in Brazil?", expected_output="Portuguese"),
        EvalCase(input="Who wrote '1984'?", expected_output="George Orwell"),
        EvalCase(input="Freezing point of water in Celsius?", expected_output="0"),
    ]

    # A tiny deterministic "model" for demo purposes.
    def model(prompt: str) -> str:
        p = prompt.lower()
        if "2+2" in p:
            return "4"
        if "capital of france" in p:
            return "Paris"
        if "planet" in p:
            return "Mars"
        if "symbol for water" in p:
            return "H2O"
        if "continents" in p:
            return "7"
        if "square root of 81" in p:
            return "9"
        if "largest planet" in p:
            return "Jupiter"
        if "brazil" in p:
            return "Portuguese"
        if "wrote '1984'" in p or "wrote 1984" in p:
            return "George Orwell"
        if "freezing point" in p:
            return "0"
        return "I don't know"

    summary = run(callable_adapter(model), cases, {"exact": exact_match, "contains": contains})
    print(f"Pass rate: {summary.pass_rate:.0%} ({sum(r.passed for r in summary.results)}/{summary.total})")


if __name__ == "__main__":
    main()

