from __future__ import annotations

"""
Example 04 — RAG pipeline eval

This example shows how to wrap a RAG pipeline as a callable and evaluate it.

Run:
  python examples/04_rag_eval.py
"""

import re

from openeval import EvalCase, run
from openeval.scorers import contains


def main() -> None:
    # "Corpus" (toy)
    docs = [
        "Paris is the capital of France.",
        "Tokyo is the capital of Japan.",
        "Mars is the fourth planet from the Sun.",
    ]

    def retrieve(query: str) -> str:
        q = query.lower()
        for d in docs:
            if any(w in d.lower() for w in re.findall(r"[a-z]+", q)):
                return d
        return ""

    def rag_model(prompt: str) -> str:
        context = retrieve(prompt)
        if not context:
            return "I don't know."
        # Simple "generator": just return the context sentence.
        return context

    cases = [
        EvalCase(input="What is the capital of France?", expected_output="Paris"),
        EvalCase(input="What is the capital of Japan?", expected_output="Tokyo"),
        EvalCase(input="Name the fourth planet from the Sun.", expected_output="Mars"),
    ]

    scorers = {"contains": contains}

    # If semantic_sim is available *and* the model is cached/downloadable, add it.
    # To keep this example runnable in offline environments, semantic scoring is opt-in.
    import os

    if os.environ.get("OPENEVAL_EXAMPLE_SEMANTIC") == "1":
        try:
            from openeval.scorers import semantic_sim

            scorers["semantic"] = semantic_sim
        except Exception:
            pass

    summary = run(rag_model, cases, scorers)
    print(f"Pass rate: {summary.pass_rate:.0%}")


if __name__ == "__main__":
    main()
