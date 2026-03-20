# Show HN draft

Title:

```
Show HN: OpenEval – Model-agnostic LLM evaluation that feels like pytest
```

Body (draft):

Hi HN — I built OpenEval, a small Python library to make LLM evaluation feel like writing tests.

The core idea is intentionally boring: a “scorer” is just a Python function that takes `(input, output, expected)` and returns a float in `[0.0, 1.0]`. You can run the same evals against OpenAI/Anthropic/Ollama, or any callable, and get a single summary + optional HTML report.

It includes a Typer/Rich CLI (`openeval run`), a pytest plugin, and a GitHub Action that can run eval suites on PRs.

Benchmarks (measured 2026-03-20): OpenEval’s harness is lightweight compared to DeepEval on a small offline mock task; Promptfoo is supported in the harness but optional.

GitHub: <REPO_URL>
Docs: <DOCS_URL>
PyPI: https://pypi.org/project/openeval/

Limitations:
- `llm_judge` is BYO judge function (no hidden SaaS)
- semantic scoring is optional (downloads a local model)
- this is v0.1.0; API may evolve

I’d love feedback on missing scorers / suite ideas, and what would make this useful in your CI.

