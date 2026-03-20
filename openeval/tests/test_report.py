from __future__ import annotations

from pathlib import Path

from openeval.models import EvalCase, EvalResult, EvalSummary
from openeval.report import generate_report


def test_generate_report_creates_html(tmp_path: Path) -> None:
    summary = EvalSummary(
        results=[
            EvalResult(
                case=EvalCase(input="Q1", expected_output="A1"),
                actual_output="A1",
                scores={"exact": 1.0},
                passed=True,
            ),
            EvalResult(
                case=EvalCase(input="Q2", expected_output="A2"),
                actual_output="no",
                scores={"exact": 0.0},
                passed=False,
            ),
        ],
        mean_score=0.5,
        pass_rate=0.5,
        total=2,
    )

    out = tmp_path / "report.html"
    generate_report(summary, str(out), title="My Report")

    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "<html" in text.lower()
    assert "My Report" in text
    assert "Pass Rate" in text
    assert "Results" in text
    assert "class=\"pass\"" in text
    assert "class=\"fail\"" in text
