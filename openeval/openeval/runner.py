from __future__ import annotations

from collections.abc import Callable, Iterable

from .models import EvalCase, EvalResult, EvalSummary

ModelFn = Callable[[str], str]
ScorerFn = Callable[[str, str, str], float]


def run(
    model_fn: ModelFn,
    dataset: Iterable[EvalCase],
    scorers: dict[str, ScorerFn],
    pass_threshold: float = 0.7,
) -> EvalSummary:
    if not scorers:
        raise ValueError("scorers must be a non-empty dict of {name: scorer_fn}")

    results: list[EvalResult] = []
    case_scores: list[float] = []

    for case in dataset:
        actual_output = model_fn(case.input)
        expected = case.expected_output or ""

        scores: dict[str, float] = {}
        for name, scorer_fn in scorers.items():
            raw_score = float(scorer_fn(case.input, actual_output, expected))
            score = 0.0 if raw_score < 0.0 else 1.0 if raw_score > 1.0 else raw_score
            scores[name] = score

        mean_case_score = sum(scores.values()) / len(scores)
        passed = mean_case_score >= pass_threshold
        case_scores.append(mean_case_score)
        results.append(
            EvalResult(case=case, actual_output=actual_output, scores=scores, passed=passed)
        )

    total = len(results)
    mean_score = (sum(case_scores) / total) if total else 0.0
    pass_rate = (sum(1 for r in results if r.passed) / total) if total else 0.0

    return EvalSummary(results=results, mean_score=mean_score, pass_rate=pass_rate, total=total)
