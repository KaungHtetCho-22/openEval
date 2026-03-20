<div align="center">

```
 ██████╗ ██████╗ ███████╗███╗   ██╗███████╗██╗   ██╗ █████╗ ██╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔════╝██║   ██║██╔══██╗██║
██║   ██║██████╔╝█████╗  ██╔██╗ ██║█████╗  ██║   ██║███████║██║
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██╔══╝  ╚██╗ ██╔╝██╔══██║██║
╚██████╔╝██║     ███████╗██║ ╚████║███████╗ ╚████╔╝ ██║  ██║███████╗
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚══════╝  ╚═══╝  ╚═╝  ╚═╝╚══════╝
```

**Model-agnostic LLM evaluation that feels like pytest.**

[![PyPI version](https://img.shields.io/pypi/v/openeval?color=blue&label=pypi)](https://pypi.org/project/openeval/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/andydev/openeval?style=social)](https://github.com/andydev/openeval)

[**Docs**](https://andydev.github.io/openeval) · [**Quick Start**](#quick-start) · [**Examples**](#examples) · [**GitHub Action**](#github-action)

</div>

---

## The problem

Every team building with LLMs ends up writing the same messy eval boilerplate from scratch.

```python
# What every dev ends up writing themselves 😩
results = []
for case in test_cases:
    output = my_model(case["input"])
    score = some_custom_function(output, case["expected"])
    results.append({"input": case["input"], "output": output, "score": score})

pass_rate = sum(r["score"] > 0.7 for r in results) / len(results)
print(f"Pass rate: {pass_rate:.0%}")
# ...and then you need to do this for 5 different models, async, with a report...
```

Existing tools make it worse. DeepEval pushes you toward a paid cloud platform. Promptfoo requires 45 lines of YAML for a simple test. RAGAS only works for RAG pipelines. LangSmith isn't open source.

**OpenEval is the tool you wished existed.**

---

## The solution

```python
from openeval import run, EvalCase
from openeval.scorers import exact_match, semantic_sim
from openeval.adapters import openai_adapter

# 1. Define your test cases
cases = [
    EvalCase(input="What is the capital of France?", expected_output="Paris"),
    EvalCase(input="Who wrote Hamlet?", expected_output="William Shakespeare"),
    EvalCase(input="What is 2 + 2?", expected_output="4"),
]

# 2. Pick a model
model = openai_adapter(model="gpt-4o-mini")

# 3. Run evals
summary = run(model, cases, scorers={"exact": exact_match, "semantic": semantic_sim})

# 4. See results
print(f"Pass rate: {summary.pass_rate:.0%}")   # Pass rate: 100%
print(f"Mean score: {summary.mean_score:.2f}") # Mean score: 0.97
```

That's it. No config files. No YAML. No cloud account. Just Python.

---

## Quick Start

### Install

```bash
pip install openeval
```

With optional extras:

```bash
pip install openeval[openai]      # OpenAI adapter
pip install openeval[anthropic]   # Anthropic adapter
pip install openeval[semantic]    # Semantic similarity scorer (sentence-transformers)
pip install openeval[all]         # Everything
```

### Run your first eval in 60 seconds

```bash
# No API key needed — uses a local callable as the model
python -c "
from openeval import run, EvalCase
from openeval.scorers import exact_match
from openeval.adapters import callable_adapter

model = callable_adapter(lambda prompt: '4' if '2+2' in prompt else 'Paris')
cases = [
    EvalCase(input='What is 2+2?', expected_output='4'),
    EvalCase(input='Capital of France?', expected_output='Paris'),
]
summary = run(model, cases, {'exact': exact_match})
print(f'Pass rate: {summary.pass_rate:.0%}')
"
```

### Or use the CLI

```bash
openeval run --dataset my_cases.jsonl --model ollama:llama3.2 --suite hallucination
```

---

## Core concepts

### Scorers are just Python functions

A scorer takes `(input, output, expected)` and returns a float between `0.0` and `1.0`. That's the entire contract.

```python
# The simplest possible scorer
def my_scorer(input: str, output: str, expected: str) -> float:
    return 1.0 if expected.lower() in output.lower() else 0.0

# Use it directly
summary = run(model, cases, scorers={"my_scorer": my_scorer})
```

No classes to inherit. No decorators. No YAML. Just a function.

### Models are callables

OpenEval never calls your model directly. You give it a callable. This means it works with literally anything.

```python
# OpenAI
from openeval.adapters import openai_adapter
model = openai_adapter(model="gpt-4o")

# Anthropic
from openeval.adapters import anthropic_adapter
model = anthropic_adapter(model="claude-sonnet-4-20250514")

# Ollama (local)
from openeval.adapters import ollama_adapter
model = ollama_adapter(model="llama3.2")

# Any Python function
from openeval.adapters import callable_adapter
model = callable_adapter(lambda prompt: my_custom_inference(prompt))

# All use the exact same interface
summary = run(model, cases, scorers)
```

### Datasets are CSV or JSONL

```python
from openeval.dataset import from_jsonl, from_csv

cases = from_jsonl("my_cases.jsonl")
cases = from_csv("my_cases.csv", input_col="question", output_col="answer")
```

JSONL format:
```jsonl
{"input": "What is the capital of France?", "expected_output": "Paris"}
{"input": "Who wrote Hamlet?", "expected_output": "William Shakespeare"}
```

---

## Built-in scorers

| Scorer | Import | What it does |
|---|---|---|
| `exact_match` | `from openeval.scorers import exact_match` | `1.0` if output matches expected (case-insensitive) |
| `contains` | `from openeval.scorers import contains` | `1.0` if expected string appears in output |
| `regex` | `from openeval.scorers import regex` | `1.0` if output matches a regex pattern |
| `semantic_sim` | `from openeval.scorers import semantic_sim` | Cosine similarity using sentence-transformers |
| `llm_judge` | `from openeval.scorers import llm_judge` | Asks an LLM to score output quality `0.0`–`1.0` |

### Combining scorers

Run multiple scorers on every case — each gets its own column in the results:

```python
from openeval.scorers import exact_match, contains, semantic_sim

summary = run(
    model,
    cases,
    scorers={
        "exact":    exact_match,
        "contains": contains,
        "semantic": semantic_sim,
    },
    pass_threshold=0.7,
)

# Access per-scorer results
for result in summary.results:
    print(result.scores)
    # {"exact": 0.0, "contains": 1.0, "semantic": 0.87}
```

### Writing a custom scorer

```python
import json

def json_validity(input: str, output: str, expected: str = "") -> float:
    """Score 1.0 if output is valid JSON, else 0.0."""
    try:
        json.loads(output)
        return 1.0
    except json.JSONDecodeError:
        return 0.0

def length_constraint(max_words: int):
    """Factory: returns a scorer that checks output word count."""
    def scorer(input: str, output: str, expected: str = "") -> float:
        word_count = len(output.split())
        return 1.0 if word_count <= max_words else max(0.0, 1.0 - (word_count - max_words) / max_words)
    return scorer

summary = run(
    model,
    cases,
    scorers={
        "json":   json_validity,
        "length": length_constraint(max_words=50),
    },
)
```

### LLM-as-judge

Use a language model to evaluate output quality when exact scoring isn't enough:

```python
from openeval.scorers import llm_judge
from openeval.adapters import openai_adapter

judge = openai_adapter(model="gpt-4o-mini")

helpfulness = llm_judge(
    judge_fn=judge,
    criteria="Is the response helpful, accurate, and well-explained?"
)

summary = run(model, cases, scorers={"helpfulness": helpfulness})
```

---

## Built-in eval suites

Run a complete evaluation with one line — no dataset required:

```python
from openeval.suites import hallucination, factuality, instruction_following
from openeval.adapters import ollama_adapter

model = ollama_adapter("llama3.2")

# Test if the model hallucinates facts about things that don't exist
summary = hallucination.run(model)
print(f"Hallucination resistance: {summary.pass_rate:.0%}")

# Test factual accuracy on 15 common knowledge questions
summary = factuality.run(model)
print(f"Factuality: {summary.pass_rate:.0%}")

# Test if the model follows formatting and constraint instructions
summary = instruction_following.run(model)
print(f"Instruction following: {summary.pass_rate:.0%}")
```

| Suite | Cases | Tests for |
|---|---|---|
| `hallucination` | 15 | Does the model make up facts about non-existent things? |
| `factuality` | 15 | Does the model know basic verifiable facts? |
| `instruction_following` | 15 | Does the model follow format and constraint instructions? |

---

## Async evaluation

For large datasets, run eval calls in parallel with `arun()`:

```python
import asyncio
from openeval import arun
from openeval.adapters import openai_async_adapter

model = openai_async_adapter(model="gpt-4o-mini")

# 100 cases in parallel — ~10x faster than sequential
summary = asyncio.run(
    arun(model, cases, scorers, concurrency=20)
)
```

Concurrency control:
```python
# Be gentle with rate-limited APIs
summary = asyncio.run(arun(model, cases, scorers, concurrency=5))

# Full speed for local models
summary = asyncio.run(arun(model, cases, scorers, concurrency=50))
```

Or use the CLI flag:
```bash
openeval run -d cases.jsonl -m openai:gpt-4o --async --concurrency 20
```

---

## Compare multiple models

Evaluate several models against the same dataset side by side:

```python
from openeval import batch_run
from openeval.adapters import openai_adapter, ollama_adapter
from openeval.scorers import exact_match, semantic_sim

models = {
    "gpt-4o":      openai_adapter("gpt-4o"),
    "gpt-4o-mini": openai_adapter("gpt-4o-mini"),
    "llama3.2":    ollama_adapter("llama3.2"),
}

comparison = batch_run(models, cases, scorers={"exact": exact_match, "semantic": semantic_sim})
comparison.print()
```

```
┌─────────────────────────────────────────────────────┐
│  Model Comparison — 50 cases                        │
├───────────────────┬──────────┬─────────┬───────────┤
│ Model             │ Pass Rate│ exact   │ semantic  │
├───────────────────┼──────────┼─────────┼───────────┤
│ gpt-4o            │   96.0%  │  0.91   │   0.96    │
│ gpt-4o-mini       │   88.0%  │  0.83   │   0.90    │
│ llama3.2          │   74.0%  │  0.68   │   0.79    │
└───────────────────┴──────────┴─────────┴───────────┘
```

---

## CLI

```bash
# Run against a dataset
openeval run --dataset cases.jsonl --model openai:gpt-4o

# Run a built-in suite
openeval run --suite hallucination --model ollama:llama3.2

# Generate an HTML report
openeval run -d cases.jsonl -m openai:gpt-4o --output report.html

# Async with concurrency control
openeval run -d cases.jsonl -m openai:gpt-4o --async --concurrency 20

# Set pass threshold
openeval run -d cases.jsonl -m ollama:llama3.2 --threshold 0.85
```

Model string format:
- `openai:gpt-4o` — OpenAI API (requires `OPENAI_API_KEY`)
- `anthropic:claude-sonnet-4-20250514` — Anthropic API (requires `ANTHROPIC_API_KEY`)
- `ollama:llama3.2` — Local Ollama model (requires Ollama running at `localhost:11434`)

---

## GitHub Action

Add LLM evals to every pull request. OpenEval posts results as a PR comment automatically.

```yaml
# .github/workflows/eval.yml
name: LLM Eval

on: [pull_request]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: andydev/openeval-action@v1
        with:
          suite: hallucination
          model: openai:gpt-4o-mini
          threshold: "0.80"
          fail_on_threshold: "true"
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

What you get on every PR:

```
## OpenEval Results ✅

| Metric     | Value  |
|------------|--------|
| Pass Rate  | 87.5%  |
| Passed     | 14/16  |
| Threshold  | 80.0%  |
| Status     | ✅ Pass |

<details>
<summary>View per-case breakdown</summary>
...
</details>
```

---

## pytest plugin

Use OpenEval inside your existing test suite — no new tools to learn:

```python
# test_my_model.py
import pytest

@pytest.mark.eval
def test_factuality(eval_model):
    from openeval.suites import factuality
    summary = factuality.run(eval_model)
    assert summary.pass_rate >= 0.80, f"Factuality too low: {summary.pass_rate:.0%}"

@pytest.mark.eval
def test_no_hallucination(eval_model):
    from openeval.suites import hallucination
    summary = hallucination.run(eval_model)
    assert summary.pass_rate >= 0.90
```

```bash
# Run with any model
pytest tests/ --eval-model ollama:llama3.2

# Skip eval tests in fast CI
pytest tests/ -m "not eval"
```

---

## HTML reports

Generate a self-contained HTML report — shareable, no server required:

```python
from openeval import run
from openeval.report import generate_report

summary = run(model, cases, scorers)
generate_report(summary, output_path="report.html", title="My Model Eval — March 2026")
```

Open `report.html` in any browser. Contains: pass rate hero number, per-scorer breakdown charts, full results table with color-coded pass/fail rows, and collapsible long outputs.

---

## Examples

All examples are in the [`examples/`](examples/) folder — copy-paste runnable with no setup beyond `pip install openeval`.

| Example | What it shows |
|---|---|
| [`01_basic_qa.py`](examples/01_basic_qa.py) | Simplest possible eval — no API key needed |
| [`02_openai_eval.py`](examples/02_openai_eval.py) | Evaluate GPT-4o on factuality with HTML report |
| [`03_compare_models.py`](examples/03_compare_models.py) | Compare GPT-4o-mini vs GPT-4o cost/quality tradeoff |
| [`04_rag_eval.py`](examples/04_rag_eval.py) | Evaluate a RAG pipeline with semantic scoring |
| [`05_chatbot_eval.py`](examples/05_chatbot_eval.py) | Multi-turn conversation quality evaluation |
| [`06_code_eval.py`](examples/06_code_eval.py) | Code generation correctness with execution scoring |
| [`07_custom_scorer.py`](examples/07_custom_scorer.py) | Build toxicity, JSON validity, and length scorers |
| [`08_cicd_integration.py`](examples/08_cicd_integration.py) | Full CI/CD integration with pytest + GitHub Action |

---

## Comparison

Measured on Task A: 20-case Q&A eval with one custom scorer. See [`benchmarks/`](benchmarks/) for full methodology.

| | OpenEval | DeepEval | Promptfoo |
|---|---|---|---|
| Lines of code (setup + run) | **8** | 31 | 45 (YAML) |
| Custom scorer | Python function | Class inheritance | JavaScript |
| Multi-model comparison | Built-in | Manual | Plugin |
| pytest integration | Built-in plugin | Manual | No |
| GitHub Action | Official | No | No |
| Works fully offline | ✅ | ⚠️ Partial | ✅ |
| Self-hostable | ✅ | ⚠️ Cloud push | ✅ |
| Open source | ✅ | ✅ | ✅ |

> These are honest comparisons. DeepEval and Promptfoo are great tools with larger ecosystems. OpenEval is optimized for developer simplicity and works-anywhere deployment.

---

## Project structure

```
openeval/
├── openeval/
│   ├── runner.py              # Core sync eval loop
│   ├── async_runner.py        # Async parallel eval loop
│   ├── batch.py               # Multi-model comparison
│   ├── dataset.py             # CSV/JSONL loaders
│   ├── report.py              # HTML report generator
│   ├── cli.py                 # typer CLI (openeval run)
│   ├── scorers/
│   │   ├── basic.py           # exact_match, contains, regex
│   │   ├── semantic.py        # semantic_sim
│   │   └── llm_judge.py       # llm_judge
│   ├── adapters/
│   │   ├── openai.py          # OpenAI + async
│   │   ├── anthropic.py       # Anthropic + async
│   │   ├── ollama.py          # Ollama + async
│   │   └── callable.py        # Any Python callable
│   └── suites/
│       ├── hallucination.py   # 15-case hallucination suite
│       ├── factuality.py      # 15-case factuality suite
│       └── instruction_following.py
├── pytest_openeval/
│   └── plugin.py              # pytest plugin
├── openeval-action/
│   └── action.yml             # GitHub Action
├── docs/                      # MkDocs Material site
├── examples/                  # 8 runnable examples
├── benchmarks/                # Comparison benchmarks
└── tests/
```

---

## Architecture

```
                        ┌─────────────────────┐
     Your prompt ──────▶│    Model Adapter     │──────▶ model response
                        │  (OpenAI/Anthropic/  │
                        │   Ollama/callable)   │
                        └─────────────────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │    Eval Runner       │
                        │  (sync or async)     │
                        └─────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼               ▼
             ┌──────────┐  ┌──────────┐  ┌──────────────┐
             │  Scorer 1 │  │  Scorer 2 │  │   Scorer N   │
             │exact_match│  │ semantic  │  │  llm_judge   │
             └──────────┘  └──────────┘  └──────────────┘
                    │              │               │
                    └──────────────┼───────────────┘
                                   ▼
                        ┌─────────────────────┐
                        │    EvalSummary       │
                        │  pass_rate: 0.87     │
                        │  mean_score: 0.91    │
                        └─────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼               ▼
             ┌──────────┐  ┌──────────┐  ┌──────────────┐
             │  CLI      │  │  HTML    │  │  GitHub      │
             │  output   │  │  Report  │  │  Action PR   │
             └──────────┘  └──────────┘  └──────────────┘
```

---

## Contributing

Contributions are welcome. OpenEval is designed to be extended — new scorers, new adapters, and new eval suites are the most impactful areas.

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Dev environment setup (takes ~2 minutes with `uv`)
- How to add a new scorer
- How to add a new model adapter
- PR checklist and code style guide

```bash
# Setup
git clone https://github.com/andydev/openeval
cd openeval
uv venv && source .venv/bin/activate
uv add --dev pytest pytest-asyncio ruff mypy

# Run tests
uv run pytest tests/ -v

# Lint
uv run ruff check openeval/
```

---

## Roadmap

- [ ] Streaming eval support (for streaming model responses)
- [ ] Web UI for browsing eval history
- [ ] OpenTelemetry integration for production monitoring
- [ ] More built-in suites: toxicity, bias, code quality
- [ ] Azure OpenAI adapter
- [ ] Weights & Biases / MLflow logging integration

Have an idea? [Open an issue](https://github.com/andydev/openeval/issues).

---

## License

MIT — free for personal and commercial use. See [LICENSE](LICENSE).

---

<div align="center">

Built by [Andy](https://github.com/andydev) · [Documentation](https://andydev.github.io/openeval) · [PyPI](https://pypi.org/project/openeval/)

**If OpenEval saves you time, a ⭐ on GitHub means a lot.**

</div>