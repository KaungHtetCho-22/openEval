# r/MachineLearning post (draft)

Title options:
- OpenEval: model-agnostic LLM evaluation that feels like pytest (scorers are functions)
- OpenEval (Python): lightweight LLM evals + CLI + GitHub Action

Post:

I built **OpenEval**, a small Python library for LLM evaluation that aims to be *code-first* and model-agnostic.

Key idea: scorers are plain Python functions with signature:

`scorer(input: str, output: str, expected: str = "") -> float` in `[0, 1]`.

It ships with a CLI (`openeval run`), pytest plugin, HTML report, and a GitHub Action for running eval suites in CI.

Benchmark comparison (measured 2026-03-20): on a small offline mock task, OpenEval’s harness is lightweight vs DeepEval. Promptfoo is optional in the benchmark harness.

Repo: <REPO_URL>
Docs: <DOCS_URL>
PyPI: https://pypi.org/project/openeval/

Feedback welcome — especially on which built-in suites/scorers you’d expect for v0.1.x.

