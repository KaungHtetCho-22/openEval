# Contributing to OpenEval

Thanks for contributing — OpenEval aims to stay simple, fast, and pleasant to use.

## Dev setup

```bash
cd openeval
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run tests

```bash
pytest tests/ -q
```

## Lint + type check

```bash
ruff check openeval/ pytest_openeval/ benchmarks/ tests/
mypy openeval/
```

## Add a new scorer

1. Implement the scorer in `openeval/openeval/scorers/` (usually `basic.py` or a new module).
2. Follow the scorer protocol:
   - Signature: `scorer(input: str, output: str, expected: str = "") -> float`
   - Return a float in `[0.0, 1.0]`
3. Export it from `openeval/openeval/scorers/__init__.py`.
4. Add unit tests in `tests/test_scorers.py`.

## Add a new adapter

1. Add a new file under `openeval/openeval/adapters/` (sync + optional async).
2. Return a callable `prompt: str -> str`.
3. Raise a helpful error if the optional SDK dependency is missing.
4. Export it from `openeval/openeval/adapters/__init__.py`.
5. Add tests using mocks in `tests/test_adapters.py`.

## Pre-commit (recommended)

```bash
pre-commit install
pre-commit run --all-files
```

## PR checklist

- Tests pass: `pytest tests/ -q`
- Lint passes: `ruff check ...`
- Types pass: `mypy openeval/`
- Public API changes are reflected in docs (`docs/`) and examples (`examples/`)
- New features include tests

## Code style

- `ruff` for linting/format rules
- Type hints required for new code
- Keep modules small and dependency-light

