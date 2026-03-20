# Benchmarks (Days 16–18)

This folder contains a simple, reproducible comparison harness for:

- OpenEval (this repo)
- DeepEval (`deepeval` Python package)
- Promptfoo (Node.js CLI)

## Setup

### 1) OpenEval

Use the main project venv:

```bash
cd openeval
pip install -e ".[dev]"
```

### 2) DeepEval (separate venv)

```bash
cd openeval/benchmarks
python3 -m venv .venv
./.venv/bin/pip install deepeval
```

### 3) Promptfoo (Node)

The runner uses:

```bash
npx --yes promptfoo@latest eval -c benchmarks/task_a_promptfoo.yaml
```

## Run everything

```bash
cd openeval
./.venv/bin/python benchmarks/run_all.py
```

Outputs:

- `benchmarks/results.json`
- A Rich comparison table + Markdown table printed to stdout

