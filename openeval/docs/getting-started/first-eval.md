# Your First Eval

## The mental model

- A **model** is a callable: `prompt: str -> output: str`
- A **scorer** is a callable: `(input, output, expected) -> float` (0.0–1.0)
- A **dataset** is a list of `EvalCase`

## What you get back

`run()` returns `EvalSummary` with per-case results, scores, and a pass rate.

```python
from openeval import EvalCase, run
from openeval.scorers import contains

cases = [EvalCase(input="Say hello", expected_output="hello")]
summary = run(lambda _: "hello world", cases, {"contains": contains})
print(summary.results[0].scores)
```

