from __future__ import annotations

import asyncio
import time

from openeval import EvalCase, arun, run
from openeval.scorers import exact_match


def main() -> None:
    cases = [EvalCase(input=f"q{i}", expected_output="ok") for i in range(50)]

    def sync_model(_prompt: str) -> str:
        time.sleep(0.05)
        return "ok"

    async def async_model(_prompt: str) -> str:
        await asyncio.sleep(0.05)
        return "ok"

    t1 = time.perf_counter()
    run(sync_model, cases, {"exact": exact_match}, pass_threshold=0.7)
    sync_s = time.perf_counter() - t1

    t2 = time.perf_counter()
    asyncio.run(arun(async_model, cases, {"exact": exact_match}, pass_threshold=0.7, concurrency=10))
    async_s = time.perf_counter() - t2

    speedup = sync_s / async_s if async_s else float("inf")
    print(f"sync:  {sync_s:.2f}s")
    print(f"async: {async_s:.2f}s (concurrency=10)")
    print(f"speedup: {speedup:.2f}x")


if __name__ == "__main__":
    main()

