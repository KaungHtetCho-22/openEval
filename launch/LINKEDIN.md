# LinkedIn launch post (draft)

I kept running into the same problem building with LLMs: everyone ends up writing their own eval harness, and it turns into a pile of ad-hoc scripts.

So I built **OpenEval** — a tiny Python library for *model-agnostic* LLM evaluation that feels like pytest.

- Scorers are plain Python functions (no YAML, no framework lock-in)
- Works with OpenAI, Anthropic, Ollama, or any callable
- CLI + pytest plugin + GitHub Action

I measured a simple offline benchmark on 2026-03-20 and OpenEval’s setup is intentionally lightweight compared to heavier eval frameworks.

Demo + repo in the comments:
- <REPO_URL>
- `pip install openeval`

What eval problems are you running into most often: correctness, hallucinations, formatting, or regressions over time?

