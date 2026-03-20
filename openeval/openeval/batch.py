from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from rich import box
from rich.table import Table

from .models import EvalCase, EvalSummary
from .runner import run

ModelFn = Callable[[str], str]
ScorerFn = Callable[[str, str, str], float]


def batch_run(
    model_configs: dict[str, ModelFn],
    dataset: Iterable[EvalCase],
    scorers: dict[str, ScorerFn],
    *,
    pass_threshold: float = 0.7,
) -> dict[str, EvalSummary]:
    summaries: dict[str, EvalSummary] = {}
    for name, model_fn in model_configs.items():
        summaries[name] = run(model_fn, dataset, scorers, pass_threshold=pass_threshold)
    return summaries


def compare(summaries: dict[str, EvalSummary]) -> ComparisonTable:
    return ComparisonTable.from_summaries(summaries)


@dataclass(frozen=True)
class ComparisonTable:
    total_cases: int
    rows: list[dict[str, Any]]
    scorer_names: list[str]

    @classmethod
    def from_summaries(cls, summaries: dict[str, EvalSummary]) -> ComparisonTable:
        scorer_names: set[str] = set()
        for s in summaries.values():
            for r in s.results:
                scorer_names.update(r.scores.keys())
        ordered = sorted(scorer_names)

        rows: list[dict[str, Any]] = []
        total_cases = next(iter(summaries.values())).total if summaries else 0
        for model_name, summary in summaries.items():
            per_scorer: dict[str, float] = {k: 0.0 for k in ordered}
            counts: dict[str, int] = {k: 0 for k in ordered}
            for res in summary.results:
                for k, v in res.scores.items():
                    per_scorer[k] += float(v)
                    counts[k] += 1
            means = {k: (per_scorer[k] / counts[k]) if counts[k] else 0.0 for k in ordered}
            rows.append(
                {
                    "model": model_name,
                    "pass_rate": float(summary.pass_rate),
                    "mean_score": float(summary.mean_score),
                    "scorers": means,
                }
            )

        rows.sort(key=lambda r: r["pass_rate"], reverse=True)
        return cls(total_cases=total_cases, rows=rows, scorer_names=ordered)

    def to_rich_table(self, *, title: str | None = None) -> Table:
        t = Table(title=title or f"Model Comparison — {self.total_cases} cases", box=box.SIMPLE_HEAVY)
        t.add_column("Model", style="bold")
        t.add_column("Pass Rate", justify="right")
        t.add_column("Mean", justify="right")
        for s in self.scorer_names:
            t.add_column(s, justify="right")

        for row in self.rows:
            pass_rate = row["pass_rate"]
            color = "green" if pass_rate >= 0.8 else "yellow" if pass_rate >= 0.6 else "red"
            t.add_row(
                str(row["model"]),
                f"[{color}]{pass_rate*100.0:5.1f}%[/{color}]",
                f"{row['mean_score']:.2f}",
                *[f"{row['scorers'].get(s, 0.0):.2f}" for s in self.scorer_names],
            )
        return t

    def to_html(self, *, title: str = "OpenEval Comparison") -> str:
        headers = ["Model", "Pass Rate", "Mean"] + self.scorer_names
        head = "".join(f"<th>{_escape(h)}</th>" for h in headers)

        body_rows = []
        for r in self.rows:
            pr = float(r["pass_rate"])
            klass = "good" if pr >= 0.8 else "ok" if pr >= 0.6 else "bad"
            cols = [
                f"<td><strong>{_escape(str(r['model']))}</strong></td>",
                f"<td class='{klass}'>{pr*100.0:.1f}%</td>",
                f"<td>{float(r['mean_score']):.2f}</td>",
            ]
            cols.extend(f"<td>{float(r['scorers'].get(s, 0.0)):.2f}</td>" for s in self.scorer_names)
            body_rows.append("<tr>" + "".join(cols) + "</tr>")

        return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>{_escape(title)}</title>
    <style>
      body {{ font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto; padding: 24px; }}
      h1 {{ margin: 0 0 12px; }}
      .muted {{ color: #555; margin-bottom: 16px; }}
      table {{ width: 100%; border-collapse: collapse; }}
      th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
      th {{ background: #fafafa; }}
      .good {{ color: #0a7; font-weight: 700; }}
      .ok {{ color: #b75; font-weight: 700; }}
      .bad {{ color: #d33; font-weight: 700; }}
    </style>
  </head>
  <body>
    <h1>{_escape(title)}</h1>
    <div class="muted">Total cases: {self.total_cases}</div>
    <table>
      <thead><tr>{head}</tr></thead>
      <tbody>
        {''.join(body_rows)}
      </tbody>
    </table>
  </body>
</html>
"""


def _escape(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
