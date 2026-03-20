from __future__ import annotations

import time

from openeval import EvalCase, run
from openeval.scorers import exact_match

MODEL_LATENCY_S = 0.01


def run_benchmark() -> dict:
    cases = [
        EvalCase(input="What is 2+2?", expected_output="4"),
        EvalCase(input="Capital of France?", expected_output="Paris"),
        EvalCase(input="Capital of Japan?", expected_output="Tokyo"),
        EvalCase(input="Largest planet?", expected_output="Jupiter"),
        EvalCase(input="Chemical symbol for water?", expected_output="H2O"),
        EvalCase(input="Square root of 81?", expected_output="9"),
        EvalCase(input="How many continents?", expected_output="7"),
        EvalCase(input="Primary language in Brazil?", expected_output="Portuguese"),
        EvalCase(input="Freezing point of water (C)?", expected_output="0"),
        EvalCase(input="Who wrote 1984?", expected_output="George Orwell"),
        EvalCase(input="Capital of Canada?", expected_output="Ottawa"),
        EvalCase(input="Largest ocean?", expected_output="Pacific"),
        EvalCase(input="3*3?", expected_output="9"),
        EvalCase(input="Opposite of hot?", expected_output="cold"),
        EvalCase(input="Color of a clear daytime sky?", expected_output="blue"),
        EvalCase(input="First month of the year?", expected_output="January"),
        EvalCase(input="How many days in a week?", expected_output="7"),
        EvalCase(input="What is 10/2?", expected_output="5"),
        EvalCase(input="What is the capital of Italy?", expected_output="Rome"),
        EvalCase(input="What is the chemical symbol for oxygen?", expected_output="O"),
    ]

    mapping = {c.input: (c.expected_output or "") for c in cases}

    def model(prompt: str) -> str:
        time.sleep(MODEL_LATENCY_S)
        return mapping.get(prompt, "I don't know")

    t0 = time.perf_counter()
    summary = run(model, cases, {"exact": exact_match}, pass_threshold=0.7)
    run_s = time.perf_counter() - t0
    return {"pass_rate": summary.pass_rate, "total": summary.total, "run_s": run_s}


if __name__ == "__main__":
    print(run_benchmark())
