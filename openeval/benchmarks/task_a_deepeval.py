from __future__ import annotations

import time

MODEL_LATENCY_S = 0.01


def run_benchmark() -> dict:
    # DeepEval installs as "deepeval"
    from deepeval.metrics import ExactMatchMetric
    from deepeval.test_case import LLMTestCase

    cases = [
        ("What is 2+2?", "4"),
        ("Capital of France?", "Paris"),
        ("Capital of Japan?", "Tokyo"),
        ("Largest planet?", "Jupiter"),
        ("Chemical symbol for water?", "H2O"),
        ("Square root of 81?", "9"),
        ("How many continents?", "7"),
        ("Primary language in Brazil?", "Portuguese"),
        ("Freezing point of water (C)?", "0"),
        ("Who wrote 1984?", "George Orwell"),
        ("Capital of Canada?", "Ottawa"),
        ("Largest ocean?", "Pacific"),
        ("3*3?", "9"),
        ("Opposite of hot?", "cold"),
        ("Color of a clear daytime sky?", "blue"),
        ("First month of the year?", "January"),
        ("How many days in a week?", "7"),
        ("What is 10/2?", "5"),
        ("What is the capital of Italy?", "Rome"),
        ("What is the chemical symbol for oxygen?", "O"),
    ]

    mapping = {q: a for q, a in cases}

    def model(prompt: str) -> str:
        time.sleep(MODEL_LATENCY_S)
        return mapping.get(prompt, "I don't know")

    metric = ExactMatchMetric()

    t0 = time.perf_counter()
    passed = 0
    for q, a in cases:
        tc = LLMTestCase(input=q, actual_output=model(q), expected_output=a)
        metric.measure(tc)
        if getattr(metric, "score", 0.0) == 1.0:
            passed += 1
    run_s = time.perf_counter() - t0

    return {"pass_rate": passed / len(cases), "total": len(cases), "run_s": run_s}


if __name__ == "__main__":
    print(run_benchmark())
