# Async Evaluation

Use `arun()` to evaluate many cases in parallel.

```python
import asyncio
from openeval import EvalCase, arun
from openeval.scorers import exact_match

cases = [EvalCase(input="2+2", expected_output="4")]

async def model(_prompt: str) -> str:
    return "4"

summary = asyncio.run(arun(model, cases, {"exact": exact_match}, concurrency=20))
print(summary.pass_rate)
```

Tip: set `concurrency` based on your provider rate limits.

