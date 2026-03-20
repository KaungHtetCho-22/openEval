from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .models import EvalSummary


@dataclass(frozen=True)
class _ReportStats:
    total: int
    passed: int
    failed: int
    pass_rate: float
    mean_score: float
    scorer_means: dict[str, float]
    distribution: list[tuple[str, int]]  # label -> count


def generate_report(summary: EvalSummary, output_path: str, title: str = "OpenEval Report") -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    stats = _compute_stats(summary)
    created_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>{_escape(title)}</title>
    <style>
      :root {{
        --bg: #0b1020;
        --panel: rgba(255,255,255,0.06);
        --panel2: rgba(255,255,255,0.08);
        --text: rgba(255,255,255,0.92);
        --muted: rgba(255,255,255,0.68);
        --border: rgba(255,255,255,0.12);
        --green: #21c55d;
        --red: #ef4444;
        --amber: #f59e0b;
        --cyan: #22d3ee;
        --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        --sans: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
      }}

      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: radial-gradient(1200px 700px at 20% 0%, rgba(34,211,238,0.18), transparent 55%),
                    radial-gradient(1000px 600px at 90% 10%, rgba(33,197,93,0.18), transparent 55%),
                    var(--bg);
        color: var(--text);
        font-family: var(--sans);
        line-height: 1.35;
      }}

      .container {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 42px; }}
      .topbar {{ display:flex; align-items:flex-start; justify-content:space-between; gap: 16px; }}
      .title {{
        font-size: 22px;
        font-weight: 750;
        letter-spacing: -0.01em;
        margin: 0;
      }}
      .meta {{ color: var(--muted); font-size: 13px; margin-top: 6px; }}
      .pill {{
        display:inline-flex;
        align-items:center;
        gap: 8px;
        background: var(--panel);
        border: 1px solid var(--border);
        padding: 10px 12px;
        border-radius: 999px;
        font-family: var(--mono);
        font-size: 12px;
        color: var(--muted);
        white-space: nowrap;
      }}

      .hero {{
        margin-top: 16px;
        background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 18px 18px 16px;
        position: relative;
        overflow: hidden;
      }}
      .hero-grid {{ display:grid; grid-template-columns: 1.2fr 0.8fr; gap: 16px; }}
      .hero h2 {{ margin: 0 0 10px; font-size: 15px; color: var(--muted); font-weight: 650; }}
      .kpi {{
        font-size: 54px;
        line-height: 1.0;
        margin: 0;
        font-weight: 850;
        letter-spacing: -0.03em;
      }}
      .kpi-sub {{ margin-top: 8px; color: var(--muted); font-size: 14px; }}
      .kpi-badge {{
        display:inline-block;
        margin-left: 10px;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: var(--panel);
        font-size: 13px;
        vertical-align: middle;
      }}

      .cards {{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 14px; }}
      .card {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 12px 12px 10px;
      }}
      .card .label {{ color: var(--muted); font-size: 12px; }}
      .card .value {{ font-size: 18px; font-weight: 750; margin-top: 6px; }}

      .section {{ margin-top: 18px; }}
      .section h3 {{ margin: 0 0 10px; font-size: 14px; color: var(--muted); font-weight: 700; }}

      .grid2 {{ display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
      .panel {{
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 12px;
      }}

      .bars {{ display:flex; gap: 10px; align-items:flex-end; height: 110px; }}
      .bar {{
        width: 100%;
        border-radius: 10px;
        background: rgba(255,255,255,0.08);
        border: 1px solid var(--border);
        position: relative;
        overflow: hidden;
      }}
      .bar > .fill {{
        position:absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 0%;
        background: linear-gradient(180deg, rgba(34,211,238,0.65), rgba(33,197,93,0.65));
      }}
      .bar-label {{ margin-top: 8px; color: var(--muted); font-size: 11px; text-align:center; font-family: var(--mono); }}

      table {{ width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 14px; }}
      thead th {{
        position: sticky; top: 0;
        background: rgba(10,14,28,0.75);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid var(--border);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: .08em;
        color: var(--muted);
        padding: 10px 10px;
        text-align: left;
      }}
      tbody td {{
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding: 10px 10px;
        vertical-align: top;
        font-size: 13px;
      }}
      tbody tr.pass {{ background: rgba(33,197,93,0.06); }}
      tbody tr.fail {{ background: rgba(239,68,68,0.06); }}
      .mono {{ font-family: var(--mono); color: var(--muted); }}
      .status {{
        display:inline-flex; align-items:center; gap: 8px;
        padding: 6px 10px; border-radius: 999px; border: 1px solid var(--border);
        background: rgba(255,255,255,0.05);
        font-weight: 700; font-size: 12px;
      }}
      .status.pass {{ color: var(--green); }}
      .status.fail {{ color: var(--red); }}
      details summary {{
        cursor: pointer;
        color: var(--text);
        list-style: none;
      }}
      details summary::-webkit-details-marker {{ display:none; }}
      .muted {{ color: var(--muted); }}
      .score-chip {{
        display:inline-block;
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 4px 8px;
        font-family: var(--mono);
        font-size: 12px;
        margin-right: 6px;
        margin-bottom: 6px;
        background: rgba(255,255,255,0.04);
        color: var(--muted);
      }}
      .footer {{ margin-top: 18px; color: var(--muted); font-size: 12px; }}
      @media (max-width: 900px) {{
        .hero-grid {{ grid-template-columns: 1fr; }}
        .cards {{ grid-template-columns: repeat(2, 1fr); }}
        .grid2 {{ grid-template-columns: 1fr; }}
        .kpi {{ font-size: 44px; }}
      }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="topbar">
        <div>
          <h1 class="title">{_escape(title)}</h1>
          <div class="meta">Generated {created_at} • OpenEval</div>
        </div>
        <div class="pill">pass_rate={stats.pass_rate:.4f} mean_score={stats.mean_score:.4f}</div>
      </div>

      <div class="hero">
        <div class="hero-grid">
          <div>
            <h2>Pass Rate</h2>
            <div class="kpi">{stats.pass_rate*100.0:.1f}% <span class="kpi-badge" style="color:{_color(stats.pass_rate)}">{_badge(stats.pass_rate)}</span></div>
            <div class="kpi-sub">Total: {stats.total} • Passed: <span style="color:var(--green)">{stats.passed}</span> • Failed: <span style="color:var(--red)">{stats.failed}</span></div>
          </div>
          <div>
            <h2>Score Distribution</h2>
            {_render_distribution(stats)}
          </div>
        </div>

        <div class="cards">
          <div class="card"><div class="label">Total Cases</div><div class="value">{stats.total}</div></div>
          <div class="card"><div class="label">Passed</div><div class="value" style="color:var(--green)">{stats.passed}</div></div>
          <div class="card"><div class="label">Failed</div><div class="value" style="color:var(--red)">{stats.failed}</div></div>
          <div class="card"><div class="label">Mean Score</div><div class="value">{stats.mean_score:.2f}</div></div>
        </div>
      </div>

      <div class="section">
        <div class="grid2">
          <div class="panel">
            <h3>Mean Scores per Scorer</h3>
            {_render_scorer_means(stats)}
          </div>
          <div class="panel">
            <h3>Notes</h3>
            <div class="muted">This report is self-contained (no external CSS/JS). Share it in PRs, docs, or team chats.</div>
          </div>
        </div>
      </div>

      <div class="section">
        <h3>Results</h3>
        {_render_results_table(summary)}
      </div>

      <div class="footer">Tip: use <span class="mono">--output report.html</span> to generate this report from the CLI.
      </div>
    </div>
  </body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def _compute_stats(summary: EvalSummary) -> _ReportStats:
    total = summary.total
    passed = sum(1 for r in summary.results if r.passed)
    failed = total - passed
    scorer_means: dict[str, float] = {}
    scorer_counts: dict[str, int] = {}
    case_means: list[float] = []

    for r in summary.results:
        if r.scores:
            case_mean = sum(r.scores.values()) / len(r.scores)
        else:
            case_mean = 0.0
        case_means.append(case_mean)
        for name, score in r.scores.items():
            scorer_means[name] = scorer_means.get(name, 0.0) + float(score)
            scorer_counts[name] = scorer_counts.get(name, 0) + 1

    scorer_means = {k: (scorer_means[k] / scorer_counts[k]) for k in sorted(scorer_means)}

    buckets = [0, 0, 0, 0, 0]  # 0-20, 20-40, 40-60, 60-80, 80-100
    for s in case_means:
        idx = min(4, max(0, int(s * 5)))
        buckets[idx] += 1
    labels = ["0–20", "20–40", "40–60", "60–80", "80–100"]
    distribution = list(zip(labels, buckets, strict=False))

    return _ReportStats(
        total=total,
        passed=passed,
        failed=failed,
        pass_rate=float(summary.pass_rate),
        mean_score=float(summary.mean_score),
        scorer_means=scorer_means,
        distribution=distribution,
    )


def _render_scorer_means(stats: _ReportStats) -> str:
    if not stats.scorer_means:
        return '<div class="muted">No scorer breakdown available.</div>'
    chips = []
    for name, mean in stats.scorer_means.items():
        chips.append(f'<span class="score-chip">{_escape(name)}: {mean:.2f}</span>')
    return "<div>" + "".join(chips) + "</div>"


def _render_distribution(stats: _ReportStats) -> str:
    max_count = max((c for _, c in stats.distribution), default=1)
    bars = []
    labels = []
    for label, count in stats.distribution:
        pct = 0.0 if max_count == 0 else (count / max_count) * 100.0
        bars.append(f'<div class="bar"><div class="fill" style="height:{pct:.1f}%"></div></div>')
        labels.append(f'<div class="bar-label">{label}<br/><span class="muted">{count}</span></div>')
    return (
        '<div class="bars">' + "".join(bars) + "</div>"
        + '<div class="bars" style="height:auto; align-items:flex-start;">'
        + "".join(labels)
        + "</div>"
    )


def _render_results_table(summary: EvalSummary) -> str:
    # Collect scorer names to produce stable columns
    scorer_names: list[str] = sorted({k for r in summary.results for k in r.scores.keys()})

    header_cols = (
        "<th>#</th><th>Status</th><th>Input</th><th>Expected</th><th>Output</th>"
        + "".join(f"<th>{_escape(n)}</th>" for n in scorer_names)
    )

    rows = []
    for i, r in enumerate(summary.results, start=1):
        status_class = "pass" if r.passed else "fail"
        status_text = "PASS" if r.passed else "FAIL"
        status = f'<span class="status {status_class}">{status_text}</span>'

        inp = _details_cell(r.case.input)
        exp = _details_cell(r.case.expected_output or "")
        out = _details_cell(r.actual_output or "")

        score_cells = []
        for name in scorer_names:
            score = r.scores.get(name)
            if score is None:
                score_cells.append('<td class="mono">—</td>')
            else:
                score_cells.append(f'<td class="mono">{float(score):.2f}</td>')

        rows.append(
            f'<tr class="{status_class}">'
            f"<td class=\"mono\">{i}</td>"
            f"<td>{status}</td>"
            f"<td>{inp}</td>"
            f"<td>{exp}</td>"
            f"<td>{out}</td>"
            + "".join(score_cells)
            + "</tr>"
        )

    return (
        '<div class="panel" style="padding:0; overflow:auto;">'
        "<table>"
        "<thead><tr>"
        + header_cols
        + "</tr></thead>"
        "<tbody>"
        + "".join(rows)
        + "</tbody>"
        "</table>"
        "</div>"
    )


def _details_cell(text: str, *, preview_len: int = 120) -> str:
    t = (text or "").strip()
    if len(t) <= preview_len:
        return f"<span>{_escape(t)}</span>"
    preview = t[:preview_len].rstrip() + "…"
    return (
        "<details>"
        f"<summary>{_escape(preview)}</summary>"
        "<div class=\"muted\" style=\"margin-top:8px; font-family:var(--mono); white-space:pre-wrap;\">"
        f"{_escape(t)}</div>"
        "</details>"
    )


def _escape(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _color(pass_rate: float) -> str:
    if pass_rate >= 0.8:
        return "var(--green)"
    if pass_rate >= 0.6:
        return "var(--amber)"
    return "var(--red)"


def _badge(pass_rate: float) -> str:
    if pass_rate >= 0.8:
        return "STRONG"
    if pass_rate >= 0.6:
        return "OK"
    return "LOW"
