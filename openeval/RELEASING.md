# Releasing OpenEval

This folder is the Python package.

If you keep a monorepo, ensure your GitHub Actions workflows live at the repository root under `.github/workflows/`.

## One-time setup

- Ensure `pyproject.toml` has correct `[project.urls]` (GitHub + docs URLs).
- Ensure `README.md` action snippet uses the correct action repo owner (search for `OWNER/openeval-action`).
- Add a `PYPI_TOKEN` repository secret (PyPI API token).

## Local release (manual)

From `openeval/`:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

Test install in a clean venv:

```bash
python -m venv /tmp/openeval-test
source /tmp/openeval-test/bin/activate
pip install dist/*.whl
openeval --help
```

## GitHub Action publish (recommended)

- Create and push a tag (example):

```bash
git tag v0.1.0
git push origin v0.1.0
```

- `openeval/.github/workflows/publish.yml` builds and publishes to PyPI on tag pushes.
