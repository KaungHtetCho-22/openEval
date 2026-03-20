# OpenEval — Master Project Context
> Paste this file at the start of every new chat session to restore full context.

---

## Who I Am
- Name: Andy
- Building: OpenEval — an open-source, model-agnostic LLM evaluation framework
- Goal: Go viral on GitHub (target: 5k+ stars), become known as an AI engineer
- Stack preference: Python, FastAPI, React, uv for package management
- Style: I prefer honest tradeoff analysis, no hype, production-grade thinking

---

## What OpenEval Is

**One-line pitch:** The missing standard for LLM evaluation — zero config, any model, feels like pytest.

**The problem it solves:**
Every team building with LLMs writes their own messy eval boilerplate from scratch. Existing tools (DeepEval, Promptfoo, RAGAS) are either locked to one framework, require heavy YAML config, or push you to paid cloud platforms. No open standard exists that just works.

**The killer insight:**
Scorers are just Python functions. A scorer takes `(input, output)` and returns a float. That's the entire API surface. No YAML. No classes to inherit. No config files.

**The three killer features:**
1. Scorers are plain Python functions — composable, testable, versionable
2. Model-agnostic — works with OpenAI, Anthropic, Ollama, any callable
3. Official GitHub Action — runs evals on every PR, posts results as PR comment

---

## Project Structure (final target)

```
openeval/
├── openeval/
│   ├── __init__.py
│   ├── runner.py          # Core eval loop
│   ├── scorers/
│   │   ├── __init__.py
│   │   ├── basic.py       # exact_match, contains, regex
│   │   ├── semantic.py    # semantic_sim (sentence-transformers)
│   │   └── llm_judge.py   # llm_judge scorer
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── openai.py
│   │   ├── anthropic.py
│   │   ├── ollama.py
│   │   └── callable.py
│   ├── dataset.py         # CSV/JSONL loaders
│   ├── report.py          # HTML report generator
│   ├── cli.py             # typer CLI
│   └── suites/
│       ├── hallucination.py
│       ├── factuality.py
│       └── instruction_following.py
├── pytest_openeval/
│   └── plugin.py          # pytest plugin
├── openeval-action/
│   └── action.yml         # GitHub Action
├── docs/                  # MkDocs Material site
├── examples/              # 8 copy-paste examples
├── tests/
├── pyproject.toml
├── README.md
└── CONTRIBUTING.md
```

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.11+ | Universal for ML devs |
| Package manager | uv | Fast, modern |
| CLI | typer + rich | Beautiful terminal output |
| Semantic scoring | sentence-transformers | Local, no API needed |
| Async | asyncio + aiohttp | Parallel eval calls |
| Docs | MkDocs Material | Beautiful, free on GitHub Pages |
| Testing | pytest | Standard |
| Packaging | pyproject.toml + PyPI | `pip install openeval` |
| CI/CD | GitHub Actions | Auto-publish on tag |

---

## Viral Strategy

1. **Hacker News** — "Show HN: OpenEval, a model-agnostic LLM eval framework" (Tuesday/Wednesday morning US time)
2. **LinkedIn** — origin story post with 45-second terminal demo recording
3. **r/MachineLearning + r/LocalLLaMA** — post the comparison benchmark table (OpenEval vs DeepEval vs Promptfoo)
4. **Cold outreach** — 10 LLM tutorial creators on Medium/Substack
5. **GitHub Action as growth loop** — every repo using it puts `openeval` in their public workflow files

---

## Competitors & Positioning

| Tool | Stars | Weakness | Our advantage |
|---|---|---|---|
| DeepEval | ~8k | Pushes to paid cloud, complex custom scorers | Pure open, scorers as functions |
| Promptfoo | ~5k | YAML-heavy, prompt-focused only | Code-first, any pipeline |
| RAGAS | ~3k | RAG-only | General purpose |
| LangSmith | SaaS | Expensive, not open source | Self-hostable, free forever |

---

## 21-Day Build Timeline Summary

| Days | Focus |
|---|---|
| 1–2 | Core eval loop + 5 built-in scorers |
| 3 | Model adapters (OpenAI, Anthropic, Ollama, callable) |
| 4–5 | Dataset loaders + 3 built-in eval suites |
| 6–7 | CLI (typer) + pytest plugin |
| 8–9 | GitHub Action + HTML report generator |
| 10–12 | Async runner + batch evaluation |
| 13–15 | MkDocs docs site + 8 examples |
| 16–18 | Comparison benchmarks (vs DeepEval, Promptfoo) |
| 19–21 | Polish, PyPI publish, launch prep |

---

## Current Progress
> Update this section as you complete each day.

- [x] Day 1 — Core eval loop + scorer protocol
- [x] Day 2 — 5 built-in scorers
- [x] Day 3 — Model adapters
- [x] Day 4 — Dataset loaders
- [x] Day 5 — 3 built-in eval suites
- [x] Day 6 — CLI (typer + rich)
- [x] Day 7 — pytest plugin
- [x] Day 8 — GitHub Action
- [x] Day 9 — HTML report generator
- [x] Day 10 — Async runner
- [x] Day 11 — Batch evaluation
- [x] Day 12 — Async testing + polish
- [x] Day 13 — MkDocs setup + structure
- [x] Day 14 — Write 4 example scripts
- [x] Day 15 — Write 4 more example scripts
- [x] Day 16 — Benchmark setup
- [x] Day 17 — Run + record benchmarks
- [x] Day 18 — README comparison table
- [x] Day 19 — Production README + architecture diagram
- [x] Day 20 — PyPI publish + GitHub release
- [x] Day 21 — Demo GIF + launch content

Notes:
- PyPI publish is set up via `openeval/.github/workflows/publish.yml` + `openeval/RELEASING.md` (tag push publishes). Actual publication depends on your `PYPI_TOKEN` secret.

---

## How to Use This File

1. At the start of a new chat, paste the contents of this file
2. Tell Claude which day you are on and what you completed last session
3. Ask Claude to continue with today's instruction file
4. Update the "Current Progress" checklist as you go
