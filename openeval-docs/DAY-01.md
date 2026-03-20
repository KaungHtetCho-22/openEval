# Day 1 — Core Eval Loop + Scorer Protocol

## Goal for today
By end of Day 1 you will have a working Python package skeleton that can run a basic evaluation loop. You can `pip install -e .` it locally and import it in a Python script.

---

## Step 1 — Project scaffold

Run these commands:

```bash
mkdir openeval && cd openeval
uv init
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

Then create this folder structure manually:

```
openeval/
├── openeval/
│   ├── __init__.py
│   ├── runner.py
│   └── scorers/
│       └── __init__.py
├── tests/
│   └── test_runner.py
└── pyproject.toml
```

---

## Step 2 — pyproject.toml

Ask Claude: **"Write the pyproject.toml for OpenEval"**

Tell Claude:
- Package name: `openeval`
- Python 3.11+
- Use `uv` / `hatchling` build backend
- Dependencies for today: `pydantic>=2.0`
- Optional dev dependencies: `pytest`, `pytest-asyncio`

---

## Step 3 — Core data models

Ask Claude: **"Write openeval/models.py with Pydantic models for EvalCase, EvalResult, and EvalSummary"**

Tell Claude the models need:
- `EvalCase`: fields for `input` (str), `expected_output` (str, optional), `metadata` (dict, optional)
- `EvalResult`: fields for `case` (EvalCase), `actual_output` (str), `scores` (dict[str, float]), `passed` (bool)
- `EvalSummary`: fields for `results` (list[EvalResult]), `mean_score` (float), `pass_rate` (float), `total` (int)

---

## Step 4 — Runner

Ask Claude: **"Write openeval/runner.py — the core eval loop"**

Tell Claude:
- Function signature: `run(model_fn, dataset, scorers, pass_threshold=0.7) -> EvalSummary`
- `model_fn` is a callable: takes a string, returns a string
- `dataset` is a list of `EvalCase`
- `scorers` is a dict of `{name: scorer_fn}` where scorer_fn takes `(input, output, expected)` and returns a float 0.0–1.0
- Loop through dataset, call model_fn, call each scorer, build EvalResult for each case
- Calculate and return EvalSummary at the end

---

## Step 5 — `__init__.py`

Ask Claude: **"Write openeval/__init__.py that exports the public API"**

Should export: `run`, `EvalCase`, `EvalResult`, `EvalSummary`

---

## Step 6 — Smoke test

Ask Claude: **"Write tests/test_runner.py with a basic smoke test for the eval loop"**

The test should:
- Create 3 EvalCases with known inputs and expected outputs
- Use a dummy model_fn that always returns the expected output (perfect model)
- Use a simple scorer that returns 1.0 if output matches expected, else 0.0
- Assert pass_rate == 1.0

Run with: `uv run pytest tests/ -v`

---

## Done when:
- [ ] `uv run pytest tests/ -v` passes with no errors
- [ ] You can open a Python shell and run `from openeval import run, EvalCase` without errors
- [ ] The eval loop runs end-to-end with a dummy model and dummy scorer

---

## Notes for next session
At the start of Day 2, tell Claude:
> "I finished Day 1. The core eval loop works. Now I need to build the 5 built-in scorers: exact_match, contains, regex, llm_judge, and semantic_sim."
