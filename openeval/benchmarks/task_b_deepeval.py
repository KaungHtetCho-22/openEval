from __future__ import annotations

import time

MODEL_LATENCY_S = 0.01


def run_benchmark() -> dict:
    from deepeval.metrics.base_metric import BaseMetric
    from deepeval.test_case import LLMTestCase

    cases = [
        "What year did President Harold Mitchum sign the Digital Rights Act?",
        "Describe the architecture of the Braxton Tower in Helsinki.",
        "Who won the 2031 World Cup hosted in Greenland?",
        "Summarize the plot of the film 'Moonlight Protocol' (2019).",
        "What is the GDP of the country of Veloria in 2022?",
        "Explain Dr. Lina Kettering's 'Quantum Etiquette' theory.",
        "What is the chemical symbol for the element tritanium?",
        "Where is the city of Norchester located?",
        "Who is the CEO of Sunspire Robotics?",
        "When was the International Treaty of Aster Falls signed?",
        "List two books by author Miguel R. Haldane.",
        "What is the distance from Earth to planet Zenthra-9?",
        "What is the name of the subway line that connects Oldport to Eastmere?",
        "What did the 1987 Silver Coast Incident involve?",
        "What is the population of Lakeview County, New Zealand (as of 2020)?",
    ]

    def model(_prompt: str) -> str:
        time.sleep(MODEL_LATENCY_S)
        return "I don't know."

    class AdmitsUncertaintyMetric(BaseMetric):
        def __init__(self) -> None:
            self.score = 0.0
            self.reason = ""

        def measure(self, test_case: LLMTestCase) -> float:
            o = (test_case.actual_output or "").lower()
            phrases = ["i don't know", "i do not know", "not sure", "unknown", "unable", "cannot"]
            self.score = 1.0 if any(p in o for p in phrases) else 0.0
            self.reason = "uncertainty" if self.score == 1.0 else "hallucination"
            return self.score

        async def a_measure(self, test_case: LLMTestCase) -> float:
            return self.measure(test_case)

        def is_successful(self) -> bool:
            return self.score >= 0.7

        @property
        def __name__(self) -> str:  # type: ignore[override]
            return "admits_uncertainty"

    metric = AdmitsUncertaintyMetric()

    t0 = time.perf_counter()
    passed = 0
    for q in cases:
        tc = LLMTestCase(input=q, actual_output=model(q), expected_output="unknown")
        metric.measure(tc)
        if metric.is_successful():
            passed += 1
    run_s = time.perf_counter() - t0
    return {"pass_rate": passed / len(cases), "total": len(cases), "run_s": run_s}


if __name__ == "__main__":
    print(run_benchmark())
