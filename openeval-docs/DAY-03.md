# Day 3 — Model Adapters

## Goal for today
Build 4 model adapters so OpenEval works with any LLM — OpenAI, Anthropic, Ollama, or any plain Python function. The eval framework never touches the model directly. You always pass in a callable.

---

## The adapter concept

An adapter wraps an LLM API and returns a simple callable:

```python
model_fn = openai_adapter(model="gpt-4o")
# model_fn is now: def model_fn(prompt: str) -> str

summary = run(model_fn, dataset, scorers)
```

This is the feature that gets tweeted about. The scorer never knows which model it's talking to.

---

## Step 1 — Adapters folder

Create this structure:
```
openeval/adapters/
├── __init__.py
├── openai.py
├── anthropic.py
├── ollama.py
└── callable.py
```

---

## Step 2 — OpenAI adapter

Ask Claude: **"Write openeval/adapters/openai.py — an adapter that wraps the OpenAI API"**

Tell Claude:
- Function: `openai_adapter(model="gpt-4o", system_prompt="", **kwargs) -> Callable`
- Returns a function that takes a string prompt, returns a string response
- Use `openai` Python SDK
- Add `openai>=1.0` to optional dependencies: `openeval[openai]`
- Raise a helpful error if `openai` not installed: `pip install openeval[openai]`
- Support passing extra kwargs to the API call (temperature, max_tokens, etc.)

---

## Step 3 — Anthropic adapter

Ask Claude: **"Write openeval/adapters/anthropic.py — an adapter that wraps the Anthropic API"**

Tell Claude:
- Function: `anthropic_adapter(model="claude-sonnet-4-20250514", system_prompt="", **kwargs) -> Callable`
- Use `anthropic` Python SDK
- Add `anthropic>=0.20` to optional dependencies: `openeval[anthropic]`
- Same pattern as OpenAI adapter

---

## Step 4 — Ollama adapter

Ask Claude: **"Write openeval/adapters/ollama.py — an adapter for local Ollama models"**

Tell Claude:
- Function: `ollama_adapter(model="llama3.2", host="http://localhost:11434", **kwargs) -> Callable`
- Use `httpx` to call the Ollama REST API (no special SDK needed)
- Endpoint: `POST {host}/api/generate` with `{"model": model, "prompt": prompt, "stream": false}`
- Add `httpx>=0.24` to base dependencies (needed anyway)
- Raise a clear error if Ollama is not running (connection refused)

---

## Step 5 — Generic callable adapter

Ask Claude: **"Write openeval/adapters/callable.py — a pass-through adapter for any Python function"**

Tell Claude:
- Function: `callable_adapter(fn) -> Callable`
- Just validates that fn is callable and returns it
- Useful for testing with mock models or wrapping custom inference code
- Should type-check: fn must accept a single string argument

---

## Step 6 — Adapters `__init__.py`

Ask Claude: **"Write openeval/adapters/__init__.py"**

Export: `openai_adapter`, `anthropic_adapter`, `ollama_adapter`, `callable_adapter`

---

## Step 7 — Update main `__init__.py`

Ask Claude: **"Update openeval/__init__.py to also export adapters"**

---

## Step 8 — Tests

Ask Claude: **"Write tests/test_adapters.py — unit tests for all adapters using mocks"**

Tell Claude:
- Mock the OpenAI and Anthropic SDK calls (don't make real API calls in tests)
- Mock the httpx call for Ollama
- Test that each adapter returns a callable
- Test that the callable returns a string when called with a string
- Use `unittest.mock.patch` or `pytest-mock`

Run: `uv run pytest tests/ -v`

---

## Done when:
- [ ] All 4 adapters importable: `from openeval.adapters import openai_adapter, anthropic_adapter, ollama_adapter, callable_adapter`
- [ ] Tests pass with mocked API calls
- [ ] You can do a real test with Ollama if you have it installed locally

Quick verification (no API keys needed):
```python
from openeval import run, EvalCase
from openeval.adapters import callable_adapter
from openeval.scorers import exact_match

my_fn = callable_adapter(lambda prompt: "Paris" if "France" in prompt else "I don't know")
cases = [EvalCase(input="What is the capital of France?", expected_output="Paris")]
summary = run(my_fn, cases, {"exact": exact_match})
print(summary.pass_rate)  # Should print 1.0
```

---

## Notes for next session
At the start of Day 4, tell Claude:
> "I finished Days 1–3. Eval loop, scorers, and model adapters all work. Now I need to build dataset loaders — CSV and JSONL — and the EvalCase batch loading utilities."
