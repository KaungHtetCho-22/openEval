from openeval import EvalCase, run


def test_run_smoke_perfect_model_passes_all() -> None:
    dataset = [
        EvalCase(input="2+2", expected_output="4"),
        EvalCase(input="capital of france", expected_output="Paris"),
        EvalCase(input="say hello", expected_output="hello"),
    ]

    def model_fn(prompt: str) -> str:
        for case in dataset:
            if case.input == prompt:
                assert case.expected_output is not None
                return case.expected_output
        raise AssertionError("Unexpected prompt")

    def exact_match_scorer(_input: str, output: str, expected: str | None) -> float:
        return 1.0 if expected is not None and output == expected else 0.0

    summary = run(
        model_fn=model_fn,
        dataset=dataset,
        scorers={"exact_match": exact_match_scorer},
        pass_threshold=0.7,
    )

    assert summary.total == 3
    assert summary.pass_rate == 1.0

