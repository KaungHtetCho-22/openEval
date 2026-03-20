# Quick Start (5 minutes)

This page gets you to your first eval with **no API keys**.

## 1) Install

```bash
pip install openeval
```

## 2) Run a minimal eval

```python
from openeval import EvalCase, run
from openeval.adapters import callable_adapter
from openeval.scorers import exact_match, contains

cases = [
    EvalCase(input="What is 2+2?", expected_output="4"),
    EvalCase(input="What is the capital of France?", expected_output="Paris"),
]

mock_model = callable_adapter(lambda p: "4" if "2+2" in p else "Paris")
summary = run(mock_model, cases, {"exact": exact_match, "contains": contains})

print(f"Pass rate: {summary.pass_rate:.0%}")
```

## Next steps

- Learn built-in suites: **Guides → Eval Suites**
- Run from terminal: **Guides → CLI Reference**
- Speed up large datasets: **Guides → Async Evaluation**

