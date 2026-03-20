from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from typing import cast

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from .models import EvalCase, EvalResult, EvalSummary

SyncModelFn = Callable[[str], str]
AsyncModelFn = Callable[[str], Awaitable[str]]
ModelFn = SyncModelFn | AsyncModelFn
ScorerFn = Callable[[str, str, str], float]


async def arun(
    model_fn: ModelFn,
    dataset: Iterable[EvalCase],
    scorers: dict[str, ScorerFn],
    pass_threshold: float = 0.7,
    concurrency: int = 10,
) -> EvalSummary:
    if not scorers:
        raise ValueError("scorers must be a non-empty dict of {name: scorer_fn}")
    if concurrency < 1:
        raise ValueError("concurrency must be >= 1")

    semaphore = asyncio.Semaphore(concurrency)
    cases = list(dataset)
    executor = ThreadPoolExecutor(max_workers=concurrency)

    async def run_one(case: EvalCase) -> EvalResult:
        async with semaphore:
            actual_output = await _call_model(model_fn, case.input, executor)
        expected = case.expected_output or ""

        scores: dict[str, float] = {}
        for name, scorer_fn in scorers.items():
            raw_score = float(scorer_fn(case.input, actual_output, expected))
            score = 0.0 if raw_score < 0.0 else 1.0 if raw_score > 1.0 else raw_score
            scores[name] = score

        mean_case_score = sum(scores.values()) / len(scores)
        passed = mean_case_score >= pass_threshold
        return EvalResult(case=case, actual_output=actual_output, scores=scores, passed=passed)

    results: list[EvalResult] = []

    progress_console = Console()
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold]Evaluating[/bold]"),
        BarColumn(bar_width=None),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        transient=True,
        console=progress_console,
        disable=not progress_console.is_terminal,
    )
    try:
        with progress:
            task_id = progress.add_task("eval", total=len(cases))

            async def run_and_advance(case: EvalCase) -> EvalResult:
                res = await run_one(case)
                progress.advance(task_id, 1)
                return res

            results = list(await asyncio.gather(*(run_and_advance(c) for c in cases)))
    finally:
        executor.shutdown(wait=True, cancel_futures=True)

    total = len(results)
    mean_score = (
        sum((sum(r.scores.values()) / len(r.scores)) for r in results) / total if total else 0.0
    )
    pass_rate = (sum(1 for r in results if r.passed) / total) if total else 0.0
    return EvalSummary(results=results, mean_score=mean_score, pass_rate=pass_rate, total=total)


async def _call_model(model_fn: ModelFn, prompt: str, executor: ThreadPoolExecutor) -> str:
    # Support:
    # - async def model_fn(prompt) -> str
    # - def model_fn(prompt) -> str (run in thread for concurrency)
    # - def model_fn(prompt) -> awaitable (await it)
    if asyncio.iscoroutinefunction(model_fn):
        out = await cast(AsyncModelFn, model_fn)(prompt)
        if not isinstance(out, str):
            raise TypeError("model_fn must return a string")
        return out

    loop = asyncio.get_running_loop()
    out_obj = await loop.run_in_executor(executor, cast(Callable[[str], object], model_fn), prompt)
    if inspect.isawaitable(out_obj):
        out_obj = await cast(Awaitable[object], out_obj)
    if not isinstance(out_obj, str):
        raise TypeError("model_fn must return a string")
    return out_obj
