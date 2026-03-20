from __future__ import annotations

from openeval.suites import factuality, hallucination, instruction_following


def test_hallucination_suite_runs() -> None:
    def model_fn(_prompt: str) -> str:
        return "I don't know."

    summary = hallucination.run(model_fn)
    assert summary.total == len(hallucination.CASES)
    assert summary.pass_rate == 1.0


def test_factuality_suite_runs() -> None:
    def model_fn(prompt: str) -> str:
        for case in factuality.CASES:
            if case.input == prompt:
                assert case.expected_output is not None
                return case.expected_output
        return "unknown"

    summary = factuality.run(model_fn)
    assert summary.total == len(factuality.CASES)
    assert summary.pass_rate == 1.0


def test_instruction_following_suite_runs() -> None:
    def model_fn(prompt: str) -> str:
        for case in instruction_following.CASES:
            if case.input == prompt:
                return str(case.metadata.get("example_output", ""))
        return ""

    summary = instruction_following.run(model_fn)
    assert summary.total == len(instruction_following.CASES)
    assert summary.pass_rate == 1.0

