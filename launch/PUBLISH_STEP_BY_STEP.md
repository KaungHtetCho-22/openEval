# Publish OpenEval to GitHub + (Test)PyPI — Step by step

This guide assumes this repo lives at:

- `/home/koala/portfolio/openEval`

## Security first (do this once)

- **Never paste API tokens** into chat, issues, or commits.
- If you pasted a token anywhere, **revoke it immediately** and create a new one.

Token pages:

- PyPI: `https://pypi.org/manage/account/token/`
- TestPyPI: `https://test.pypi.org/manage/account/token/`

---

## Part A — Publish the repo to GitHub (monorepo)

### 1) Create a GitHub repository

1. GitHub → **New repository**
2. Name: `openEval` (or `openeval`)
3. Visibility: Public
4. Don’t add README / .gitignore (already in this repo)

Copy the repo URL (SSH recommended):

- `git@github.com:YOUR_USER/YOUR_REPO.git`

### 2) Initialize git locally and push

From the repo root:

```bash
cd /home/koala/portfolio/openEval

git init
git branch -m main

git add .
git commit -m "Initial release"

git remote add origin git@github.com:YOUR_USER/YOUR_REPO.git
git push -u origin main
```

### 3) Fix docs deploy permissions (GH Pages)

Your docs deploy workflow pushes to `gh-pages`.

1. GitHub repo → **Settings → Actions → General**
2. Under **Workflow permissions**:
   - Select **Read and write permissions**
   - Save

### 4) Enable GitHub Pages

1. GitHub repo → **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `gh-pages` / `(root)`
4. Save

Push any commit to `main` (or re-run the workflow) to deploy docs.

Workflows live at:

- `.github/workflows/docs.yml`

---

## Part B — Publish the Python package to TestPyPI and PyPI

The Python package folder is:

- `openeval/`

### 1) Choose a unique package name

`openeval` is already taken on PyPI.

Pick a unique name, e.g.:

- `openeval-ai`
- `openeval-llm`
- `openeval-kit`

Then update:

- `openeval/pyproject.toml` → `[project].name = "YOUR_NEW_NAME"`
- `openeval/README.md` → replace `pip install openeval` with `pip install YOUR_NEW_NAME`

### 2) Build locally

```bash
cd /home/koala/portfolio/openEval/openeval
uv build
```

Your artifacts will be in:

- `openeval/dist/`

### 3) Publish to TestPyPI

1. Create a **TestPyPI** token at `https://test.pypi.org/manage/account/token/`
2. Export it locally (don’t print it):

```bash
export TEST_PYPI_TOKEN='pypi-...'
```

3. Publish:

```bash
cd /home/koala/portfolio/openEval/openeval
uv publish \
  --publish-url https://test.pypi.org/legacy/ \
  --check-url https://test.pypi.org/simple/ \
  -u __token__ \
  -p "$TEST_PYPI_TOKEN" \
  dist/*
```

### 4) Test install from TestPyPI

TestPyPI is incomplete, so keep real PyPI as a fallback index:

```bash
python -m venv /tmp/openeval-test
source /tmp/openeval-test/bin/activate
pip install -U pip

pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  openeval-ai

openeval --help
```

### 5) Publish to real PyPI

1. Create a **PyPI** token at `https://pypi.org/manage/account/token/`
2. Export it locally:

```bash
export PYPI_TOKEN='pypi-...'
```

3. Publish (default endpoint is PyPI):

```bash
cd /home/koala/portfolio/openEval/openeval
uv publish -u __token__ -p "$PYPI_TOKEN" dist/*
```

---

## Part C — Automate publishing via GitHub Actions (optional)

Workflow:

- `.github/workflows/publish.yml`
- Trigger: push tags like `v0.1.0`
- Secret required: `PYPI_TOKEN`

### 1) Add the secret

GitHub repo → **Settings → Secrets and variables → Actions** → **New repository secret**

- Name: `PYPI_TOKEN`
- Value: your PyPI token (from pypi.org)

### 2) Tag and push

```bash
git tag v0.1.0
git push origin v0.1.0
```

---

## Part D — GitHub releases (recommended)

1. GitHub repo → **Releases** → **Draft a new release**
2. Tag: `v0.1.0`
3. Title: `OpenEval v0.1.0`
4. Paste highlights from `openeval/README.md`

---

## Troubleshooting

### Docs deploy: 403 pushing to `gh-pages`

- Ensure **Actions workflow permissions** are **Read and write**.
- Ensure `gh-pages` is not blocked by branch protection rules.

### TestPyPI publish: “Invalid or non-existent authentication information”

- You used a **PyPI** token on **TestPyPI** (wrong site).
- The token has trailing whitespace/newline (re-export it carefully).

### PyPI publish: “isn't allowed to upload to project”

- Project name is taken by someone else → rename `[project].name`.

