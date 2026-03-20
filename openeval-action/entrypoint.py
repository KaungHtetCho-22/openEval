from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from openeval.adapters.registry import parse_model_string
from openeval.dataset import from_csv, from_jsonl
from openeval.report import generate_report
from openeval.runner import run as run_eval


@dataclass(frozen=True)
class Inputs:
    dataset: str | None
    suite: str | None
    model: str
    threshold: float
    fail_on_threshold: bool
    openai_api_key: str | None
    anthropic_api_key: str | None


def main() -> int:
    inputs = read_inputs()
    set_provider_keys(inputs)

    model_fn = parse_model_string(inputs.model)
    threshold = inputs.threshold

    if inputs.suite:
        suite_mod = load_suite(inputs.suite)
        summary = suite_mod.run_suite(model_fn, pass_threshold=threshold)
        title = f"OpenEval — suite={inputs.suite} model={inputs.model}"
    else:
        if not inputs.dataset:
            raise SystemExit("Provide either INPUT_SUITE or INPUT_DATASET.")
        cases = load_dataset(inputs.dataset)
        # Default to a lightweight baseline when running without a suite.
        from openeval.scorers import contains, exact_match

        summary = run_eval(model_fn, cases, {"exact_match": exact_match, "contains": contains}, pass_threshold=threshold)
        title = f"OpenEval — dataset={inputs.dataset} model={inputs.model}"

    report_path = str(Path(os.environ.get("GITHUB_WORKSPACE", ".")) / "openeval-report.html")
    generate_report(summary, report_path, title=title)

    passed = summary.pass_rate >= threshold
    write_outputs(pass_rate=summary.pass_rate, passed=passed, report_path=report_path)

    maybe_comment_on_pr(inputs=inputs, summary=summary, report_path=report_path, passed=passed)

    if inputs.fail_on_threshold and not passed:
        return 1
    return 0


def read_inputs() -> Inputs:
    dataset = os.getenv("INPUT_DATASET") or None
    suite = os.getenv("INPUT_SUITE") or None
    model = os.getenv("INPUT_MODEL")
    if not model:
        raise SystemExit("INPUT_MODEL is required.")

    threshold_s = os.getenv("INPUT_THRESHOLD", "0.7")
    try:
        threshold = float(threshold_s)
    except ValueError as exc:
        raise SystemExit(f"Invalid threshold: {threshold_s!r}") from exc

    fail_s = os.getenv("INPUT_FAIL_ON_THRESHOLD", "true")
    fail_on_threshold = str(fail_s).strip().lower() in {"1", "true", "yes", "y", "on"}

    return Inputs(
        dataset=dataset,
        suite=suite,
        model=model,
        threshold=threshold,
        fail_on_threshold=fail_on_threshold,
        openai_api_key=os.getenv("INPUT_OPENAI_API_KEY") or None,
        anthropic_api_key=os.getenv("INPUT_ANTHROPIC_API_KEY") or None,
    )


def set_provider_keys(inputs: Inputs) -> None:
    if inputs.openai_api_key and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = inputs.openai_api_key
    if inputs.anthropic_api_key and not os.getenv("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = inputs.anthropic_api_key


def load_dataset(path: str):
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Dataset not found: {p}")
    if p.suffix.lower() == ".csv":
        return from_csv(p)
    if p.suffix.lower() in {".jsonl", ".json"}:
        return from_jsonl(p)
    raise SystemExit("Dataset must be .csv or .jsonl")


def load_suite(name: str):
    norm = name.strip().lower().replace("-", "_")
    from openeval import suites

    if not hasattr(suites, norm):
        raise SystemExit(f"Unknown suite: {name}")
    return getattr(suites, norm)


def maybe_comment_on_pr(*, inputs: Inputs, summary, report_path: str, passed: bool) -> None:
    token = os.getenv("GITHUB_TOKEN")
    event_path = os.getenv("GITHUB_EVENT_PATH")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not token or not event_path or not repo:
        return

    try:
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except Exception:
        return

    pr = event.get("pull_request")
    if not isinstance(pr, dict):
        return

    pr_number = pr.get("number")
    if not isinstance(pr_number, int):
        return

    owner, repo_name = repo.split("/", 1)
    url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{pr_number}/comments"

    passed_emoji = "✅" if passed else "❌"
    md = render_comment(summary=summary, passed_emoji=passed_emoji, report_path=report_path, inputs=inputs)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    requests.post(url, headers=headers, json={"body": md}, timeout=20)


def render_comment(*, summary, passed_emoji: str, report_path: str, inputs: Inputs) -> str:
    total = summary.total
    passed = sum(1 for r in summary.results if r.passed)
    failed = total - passed
    pass_rate_pct = summary.pass_rate * 100.0

    rows = []
    for i, r in enumerate(summary.results[:50], start=1):
        status = "✅" if r.passed else "❌"
        inp = (r.case.input or "").replace("\n", " ")
        inp = inp[:80] + ("…" if len(inp) > 80 else "")
        scores = " ".join(f"{k}:{v:.2f}" for k, v in r.scores.items())
        rows.append(f"| {i} | {status} | {escape_md(inp)} | `{scores}` |")

    table = "\n".join(["| # | Pass | Input | Scores |", "|---:|:---:|-------|--------|", *rows])

    dataset_or_suite = inputs.suite or inputs.dataset or "-"
    return f"""## OpenEval Results

| Metric | Value |
|--------|-------|
| Pass Rate | {pass_rate_pct:.1f}% {passed_emoji} |
| Total Cases | {total} |
| Passed | {passed} |
| Failed | {failed} |
| Model | `{inputs.model}` |
| Dataset/Suite | `{dataset_or_suite}` |
| Report | `{report_path}` |

<details>
<summary>View full breakdown (first 50 rows)</summary>

{table}

</details>
"""


def escape_md(text: str) -> str:
    return text.replace("|", "\\|")


def write_outputs(*, pass_rate: float, passed: bool, report_path: str) -> None:
    out_path = os.getenv("GITHUB_OUTPUT")
    if not out_path:
        return
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(f"pass_rate={pass_rate}\n")
        f.write(f"passed={'true' if passed else 'false'}\n")
        f.write(f"report_path={report_path}\n")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"OpenEval Action failed: {exc}", file=sys.stderr)
        raise

