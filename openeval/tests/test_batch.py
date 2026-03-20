from __future__ import annotations

from openeval import EvalCase
from openeval.batch import compare
from openeval.models import EvalResult, EvalSummary


def test_compare_builds_table_and_html() -> None:
    s1 = EvalSummary(
        results=[
            EvalResult(
                case=EvalCase(input="q", expected_output="a"),
                actual_output="a",
                scores={"exact": 1.0},
                passed=True,
            )
        ],
        mean_score=1.0,
        pass_rate=1.0,
        total=1,
    )
    s2 = EvalSummary(
        results=[
            EvalResult(
                case=EvalCase(input="q", expected_output="a"),
                actual_output="b",
                scores={"exact": 0.0},
                passed=False,
            )
        ],
        mean_score=0.0,
        pass_rate=0.0,
        total=1,
    )
    table = compare({"good": s1, "bad": s2})
    rich_table = table.to_rich_table()
    assert rich_table is not None
    html = table.to_html()
    assert "<html" in html.lower()
    assert "good" in html
