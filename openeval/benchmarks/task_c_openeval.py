from __future__ import annotations

import time

from openeval import EvalCase
from openeval.batch import batch_run, compare
from openeval.scorers import exact_match

MODEL_LATENCY_S = 0.01


def run_benchmark() -> dict:
    cases = [
        EvalCase(input="Capital of France?", expected_output="Paris"),
        EvalCase(input="Capital of Japan?", expected_output="Tokyo"),
        EvalCase(input="Largest planet?", expected_output="Jupiter"),
        EvalCase(input="Chemical symbol for water?", expected_output="H2O"),
        EvalCase(input="Square root of 81?", expected_output="9"),
        EvalCase(input="How many continents?", expected_output="7"),
        EvalCase(input="Freezing point of water (C)?", expected_output="0"),
        EvalCase(input="What is 10/2?", expected_output="5"),
        EvalCase(input="What is the capital of Italy?", expected_output="Rome"),
        EvalCase(input="What is the chemical symbol for oxygen?", expected_output="O"),
    ]

    answers = {c.input: (c.expected_output or "") for c in cases}

    def good_model(prompt: str) -> str:
        time.sleep(MODEL_LATENCY_S)
        return answers.get(prompt, "I don't know")

    def bad_model(_prompt: str) -> str:
        time.sleep(MODEL_LATENCY_S)
        return "I don't know"

    t0 = time.perf_counter()
    summaries = batch_run({"good": good_model, "bad": bad_model}, cases, {"exact": exact_match})
    table = compare(summaries)
    run_s = time.perf_counter() - t0
    return {
        "models": {k: v.pass_rate for k, v in summaries.items()},
        "run_s": run_s,
        "table_html_len": len(table.to_html()),
    }


if __name__ == "__main__":
    print(run_benchmark())
