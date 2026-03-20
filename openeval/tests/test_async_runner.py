from __future__ import annotations

import asyncio
import time

import pytest

from openeval import EvalCase
from openeval.async_runner import arun
from openeval.scorers import exact_match


@pytest.mark.asyncio
async def test_arun_returns_summary_and_scores() -> None:
    cases = [EvalCase(input=f"q{i}", expected_output=f"a{i}") for i in range(5)]

    async def model_fn(prompt: str) -> str:
        await asyncio.sleep(0.01)
        return "a" + prompt[1:]

    summary = await arun(model_fn, cases, {"exact": exact_match}, pass_threshold=0.7, concurrency=3)
    assert summary.total == 5
    assert summary.pass_rate == 1.0


@pytest.mark.asyncio
async def test_arun_is_faster_with_concurrency() -> None:
    cases = [EvalCase(input=str(i), expected_output="ok") for i in range(20)]

    async def model_fn(_prompt: str) -> str:
        await asyncio.sleep(0.05)
        return "ok"

    t1 = time.perf_counter()
    await arun(model_fn, cases, {"exact": exact_match}, concurrency=1)
    sequential = time.perf_counter() - t1

    t2 = time.perf_counter()
    await arun(model_fn, cases, {"exact": exact_match}, concurrency=10)
    parallel = time.perf_counter() - t2

    # Allow for CI jitter but require a clear speedup.
    assert parallel < sequential * 0.6


@pytest.mark.asyncio
async def test_arun_respects_concurrency_limit() -> None:
    cases = [EvalCase(input=str(i), expected_output="ok") for i in range(25)]
    active = 0
    max_active = 0
    lock = asyncio.Lock()

    async def model_fn(_prompt: str) -> str:
        nonlocal active, max_active
        async with lock:
            active += 1
            max_active = max(max_active, active)
        await asyncio.sleep(0.03)
        async with lock:
            active -= 1
        return "ok"

    await arun(model_fn, cases, {"exact": exact_match}, concurrency=4)
    assert max_active <= 4

