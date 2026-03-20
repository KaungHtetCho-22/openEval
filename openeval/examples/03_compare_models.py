from __future__ import annotations

"""
Example 03 — Compare two models (cost vs quality)

Run:
  python examples/03_compare_models.py
"""

import os
from pathlib import Path

from rich.console import Console

from openeval.batch import batch_run, compare
from openeval.dataset import from_jsonl
from openeval.scorers import contains, exact_match


def main() -> None:
    console = Console()

    cases = from_jsonl(Path(__file__).parent / "data" / "basic_qa.jsonl")
    scorers = {"exact": exact_match, "contains": contains}

    models: dict[str, object] = {}

    if os.getenv("OPENAI_API_KEY"):
        try:
            from openeval.adapters import openai_adapter

            models = {
                "gpt-4o-mini": openai_adapter(model="gpt-4o-mini"),
                "gpt-4o": openai_adapter(model="gpt-4o"),
            }
        except ModuleNotFoundError:
            models = {}

    if not models:
        # Fallback: compare a "good" mock and a "bad" mock.
        models = {
            "good-mock": (lambda prompt: "Paris" if "France" in prompt else "4" if "2+2" in prompt else "Tokyo"),
            "bad-mock": (lambda _prompt: "I don't know"),
        }

    summaries = batch_run(models, cases, scorers)
    table = compare(summaries)
    console.print(table.to_rich_table())


if __name__ == "__main__":
    main()

