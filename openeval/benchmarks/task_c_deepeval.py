from __future__ import annotations

import time

MODEL_LATENCY_S = 0.01


def run_benchmark() -> dict:
    from deepeval.metrics import ExactMatchMetric
    from deepeval.test_case import LLMTestCase

    cases = [
        ("Capital of France?", "Paris"),
        ("Capital of Japan?", "Tokyo"),
        ("Largest planet?", "Jupiter"),
        ("Chemical symbol for water?", "H2O"),
        ("Square root of 81?", "9"),
        ("How many continents?", "7"),
        ("Freezing point of water (C)?", "0"),
        ("What is 10/2?", "5"),
        ("What is the capital of Italy?", "Rome"),
        ("What is the chemical symbol for oxygen?", "O"),
    ]
    mapping = {q: a for q, a in cases}

    def good_model(prompt: str) -> str:
        time.sleep(MODEL_LATENCY_S)
        return mapping.get(prompt, "I don't know")

    def bad_model(_prompt: str) -> str:
        time.sleep(MODEL_LATENCY_S)
        return "I don't know"

    metric = ExactMatchMetric()

    def score(model) -> float:
        passed = 0
        for q, a in cases:
            tc = LLMTestCase(input=q, actual_output=model(q), expected_output=a)
            metric.measure(tc)
            if getattr(metric, "score", 0.0) == 1.0:
                passed += 1
        return passed / len(cases)

    t0 = time.perf_counter()
    good = score(good_model)
    bad = score(bad_model)
    run_s = time.perf_counter() - t0
    return {"models": {"good": good, "bad": bad}, "run_s": run_s}


if __name__ == "__main__":
    print(run_benchmark())
