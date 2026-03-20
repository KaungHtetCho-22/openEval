from __future__ import annotations

import time
from collections.abc import Awaitable, Callable, Coroutine, Iterable
from pathlib import Path
from typing import Any, Protocol, cast

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .adapters.registry import parse_model_string, parse_model_string_async
from .async_runner import arun as arun_eval
from .dataset import from_csv, from_jsonl
from .models import EvalCase, EvalSummary
from .report import generate_report
from .runner import run as run_eval
from .scorers import contains, exact_match

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()

SyncModelFn = Callable[[str], str]
AsyncModelFn = Callable[[str], Awaitable[str]]
AnyModelFn = SyncModelFn | AsyncModelFn
ScorerFn = Callable[[str, str, str], float]

class SuiteModule(Protocol):
    CASES: Iterable[EvalCase]

    def get_scorers(self) -> dict[str, ScorerFn]: ...

    def run_suite(self, model_fn: SyncModelFn, *, pass_threshold: float = 0.7) -> EvalSummary: ...

    def arun_suite(
        self, model_fn: AnyModelFn, *, pass_threshold: float = 0.7, concurrency: int = 10
    ) -> Coroutine[Any, Any, EvalSummary]: ...


@app.callback()
def main() -> None:
    """OpenEval CLI."""


@app.command()
def run(  # noqa: A001
    dataset: Path | None = typer.Option(
        None, "--dataset", "-d", exists=True, dir_okay=False, readable=True, help="CSV or JSONL dataset path."
    ),
    suite: str | None = typer.Option(
        None,
        "--suite",
        "-s",
        help="Built-in suite: hallucination, factuality, instruction_following.",
    ),
    model: str = typer.Option(
        ...,
        "--model",
        "-m",
        help="Model string: openai:gpt-4o | anthropic:... | ollama:... | callable:module:fn",
    ),
    threshold: float = typer.Option(0.7, "--threshold", "-t", help="Pass threshold (0.0–1.0)."),
    async_mode: bool = typer.Option(False, "--async", help="Use async runner (parallel)."),
    concurrency: int = typer.Option(10, "--concurrency", help="Max concurrent calls for --async mode."),
    output: Path | None = typer.Option(None, "--output", "-o", help="Optional path to save an HTML report."),
) -> None:
    start = time.perf_counter()

    summary: EvalSummary
    title_detail = f"Model: {model}"

    if suite:
        suite_mod = _load_suite(suite)
        if dataset is None:
            if async_mode:
                model_fn_async = parse_model_string_async(model)
                summary = _run_async_suite(suite_mod, model_fn_async, threshold=threshold, concurrency=concurrency)
            else:
                model_fn_sync = parse_model_string(model)
                summary = suite_mod.run_suite(model_fn_sync, pass_threshold=threshold)
            title_detail += f" | Suite: {suite}"
        else:
            cases = _load_dataset(dataset)
            scorers = suite_mod.get_scorers()
            if async_mode:
                model_fn_async = parse_model_string_async(model)
                summary = _run_async(model_fn_async, cases, scorers, threshold=threshold, concurrency=concurrency)
            else:
                model_fn_sync = parse_model_string(model)
                summary = run_eval(model_fn_sync, cases, scorers, pass_threshold=threshold)
            title_detail += f" | Suite: {suite} | Dataset: {dataset}"
    else:
        if dataset is None:
            raise typer.BadParameter("Provide either --suite or --dataset.")
        cases = _load_dataset(dataset)
        scorers = {"exact_match": exact_match, "contains": contains}
        if async_mode:
            model_fn_async = parse_model_string_async(model)
            summary = _run_async(model_fn_async, cases, scorers, threshold=threshold, concurrency=concurrency)
        else:
            model_fn_sync = parse_model_string(model)
            summary = run_eval(model_fn_sync, cases, scorers, pass_threshold=threshold)
        title_detail += f" | Dataset: {dataset}"

    elapsed = time.perf_counter() - start
    _render(summary=summary, header=title_detail, threshold=threshold, elapsed_s=elapsed)

    if output is not None:
        generate_report(summary, str(output), title=f"OpenEval Report — {title_detail}")
        console.print(f"[dim]Wrote HTML report to[/dim] {output}")


def _run_async(
    model_fn: AnyModelFn,
    cases: Iterable[EvalCase],
    scorers: dict[str, ScorerFn],
    *,
    threshold: float,
    concurrency: int,
) -> EvalSummary:
    import asyncio

    return asyncio.run(arun_eval(model_fn, cases, scorers, pass_threshold=threshold, concurrency=concurrency))


def _run_async_suite(
    suite_mod: SuiteModule, model_fn: AnyModelFn, *, threshold: float, concurrency: int
) -> EvalSummary:
    import asyncio

    return asyncio.run(suite_mod.arun_suite(model_fn, pass_threshold=threshold, concurrency=concurrency))


def _load_dataset(path: Path) -> list[EvalCase]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return from_csv(path)
    if suffix in {".jsonl", ".json"}:
        return from_jsonl(path)
    raise typer.BadParameter("Dataset must be a .csv or .jsonl file.")


def _load_suite(name: str) -> SuiteModule:
    norm = name.strip().lower().replace("-", "_")
    if norm not in {"hallucination", "factuality", "instruction_following"}:
        raise typer.BadParameter("Unknown suite. Use: hallucination, factuality, instruction_following.")
    from . import suites

    return cast(SuiteModule, getattr(suites, norm))


def _render(*, summary: EvalSummary, header: str, threshold: float, elapsed_s: float) -> None:
    total = summary.total
    passed = sum(1 for r in summary.results if r.passed)
    failed = total - passed

    header_panel = Panel(
        Text(f"OpenEval Run\n{header}\nThreshold: {threshold:.2f}", justify="left"),
        title="openeval",
        box=box.ROUNDED,
    )
    console.print(header_panel)

    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Input", overflow="fold")
    table.add_column("Output", overflow="fold")
    table.add_column("Scores", overflow="fold")
    table.add_column("Pass", justify="center", width=6)

    for i, r in enumerate(summary.results, start=1):
        scores_text = Text()
        for j, (name, score) in enumerate(r.scores.items()):
            if j:
                scores_text.append("  ")
            color = "green" if score >= threshold else "yellow" if score >= threshold * 0.5 else "red"
            scores_text.append(f"{name}: {score:.2f}", style=color)

        status = Text("✓", style="green") if r.passed else Text("✗", style="red")
        table.add_row(
            str(i),
            _truncate(r.case.input, 60),
            _truncate(r.actual_output, 60),
            scores_text,
            status,
        )

    console.print(table)

    scorer_means = _mean_scores(summary)
    means_line = "  ".join(f"{k}: {v:.2f}" for k, v in scorer_means.items()) if scorer_means else "-"
    pass_rate_pct = summary.pass_rate * 100.0

    summary_panel = Panel(
        Text(
            f"Results: {passed}/{total} passed ({pass_rate_pct:.1f}%)\n"
            f"Failed: {failed}\n"
            f"Mean scores: {means_line}\n"
            f"Time: {elapsed_s:.2f}s"
        ),
        box=box.ROUNDED,
    )
    console.print(summary_panel)


def _mean_scores(summary: EvalSummary) -> dict[str, float]:
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    for r in summary.results:
        for name, score in r.scores.items():
            totals[name] = totals.get(name, 0.0) + score
            counts[name] = counts.get(name, 0) + 1
    return {k: (totals[k] / counts[k]) for k in sorted(totals)}


def _truncate(text: str, max_len: int) -> str:
    s = (text or "").replace("\n", " ").strip()
    return s if len(s) <= max_len else s[: max_len - 1] + "…"
