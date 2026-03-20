from __future__ import annotations

"""
Example 02 — OpenAI eval + HTML report

This runs with OpenAI if you have:
  - pip install "openeval[openai]"
  - export OPENAI_API_KEY=...

Otherwise, it falls back to a deterministic mock model so the script still runs.

Run:
  python examples/02_openai_eval.py
"""

import os
from pathlib import Path

from openeval import generate_report, run
from openeval.dataset import from_jsonl
from openeval.scorers import contains, exact_match


def main() -> None:
    dataset_path = Path(__file__).parent / "data" / "basic_qa.jsonl"
    cases = from_jsonl(dataset_path)

    model_name = "openai:gpt-4o-mini"
    model = None

    if os.getenv("OPENAI_API_KEY"):
        try:
            from openeval.adapters import openai_adapter

            model = openai_adapter(model="gpt-4o-mini")
        except ModuleNotFoundError:
            model = None

    if model is None:
        # Fallback mock model to keep the example runnable without keys.
        def model(prompt: str) -> str:
            p = prompt.lower()
            if "capital of france" in p:
                return "Paris"
            if "capital of japan" in p:
                return "Tokyo"
            if "2+2" in p:
                return "4"
            return "I don't know"

        model_name = "callable:mock"

    summary = run(model, cases, {"exact": exact_match, "contains": contains})

    out = Path(__file__).parent / "reports" / "openai_eval.html"
    generate_report(summary, str(out), title=f"OpenEval Report — {model_name}")
    print(f"Pass rate: {summary.pass_rate:.0%}")
    print(f"Wrote report: {out}")


if __name__ == "__main__":
    main()

