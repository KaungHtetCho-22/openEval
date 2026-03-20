# Day 2 — 5 Built-in Scorers

## Goal for today
Build the 5 core scorers that ship with OpenEval. These are what people screenshot. They need to look clean, work correctly, and be dead simple to use.

---

## The 5 scorers to build

| Scorer | File | What it does |
|---|---|---|
| `exact_match` | scorers/basic.py | Returns 1.0 if output == expected (case-insensitive option) |
| `contains` | scorers/basic.py | Returns 1.0 if expected string appears anywhere in output |
| `regex` | scorers/basic.py | Returns 1.0 if output matches a regex pattern |
| `semantic_sim` | scorers/semantic.py | Cosine similarity between output and expected using embeddings |
| `llm_judge` | scorers/llm_judge.py | Asks an LLM to rate output quality 0.0–1.0 |

---

## Step 1 — Basic scorers

Ask Claude: **"Write openeval/scorers/basic.py with exact_match, contains, and regex scorers"**

Tell Claude:
- All scorers must follow the same signature: `def scorer(input: str, output: str, expected: str = "") -> float`
- `exact_match` should have a `case_sensitive=False` option (make it a factory function)
- `contains` should check if expected appears in output (case-insensitive)
- `regex` should be a factory: `regex(pattern)` returns a scorer function
- All should return float between 0.0 and 1.0

Example usage to show Claude:
```python
from openeval.scorers import exact_match, contains, regex

# Direct use
score = exact_match("What is 2+2?", "4", "4")  # 1.0

# Factory pattern
is_json = regex(r'^\{.*\}$')
score = is_json("...", '{"key": "val"}', "")  # 1.0
```

---

## Step 2 — Semantic similarity scorer

Ask Claude: **"Write openeval/scorers/semantic.py with a semantic_sim scorer using sentence-transformers"**

Tell Claude:
- Use `sentence-transformers` library, model: `all-MiniLM-L6-v2`
- Lazy-load the model (only load when first called, not on import)
- Use cosine similarity between output embedding and expected embedding
- Return float 0.0–1.0
- Add to pyproject.toml optional dependencies: `openeval[semantic]`

Add to pyproject.toml:
```toml
[project.optional-dependencies]
semantic = ["sentence-transformers>=2.2"]
```

Install with: `uv add sentence-transformers`

---

## Step 3 — LLM judge scorer

Ask Claude: **"Write openeval/scorers/llm_judge.py — a scorer that uses an LLM to judge output quality"**

Tell Claude:
- Factory function: `llm_judge(judge_fn, criteria="")` returns a scorer
- `judge_fn` is any callable that takes a prompt string and returns a string
- The scorer builds a prompt asking the judge to rate the output 0.0–1.0
- Parse the float from the judge's response (handle errors gracefully, return 0.5 on parse failure)
- Prompt template should include: the original input, the output to judge, the expected output (if provided), and the criteria

---

## Step 4 — Scorers `__init__.py`

Ask Claude: **"Write openeval/scorers/__init__.py that exports all scorers cleanly"**

Should export: `exact_match`, `contains`, `regex`, `semantic_sim`, `llm_judge`

---

## Step 5 — Tests for all scorers

Ask Claude: **"Write tests/test_scorers.py with unit tests for all 5 scorers"**

Tests should cover:
- `exact_match`: perfect match = 1.0, wrong answer = 0.0, case insensitive
- `contains`: output contains expected = 1.0, doesn't contain = 0.0
- `regex`: matching pattern = 1.0, non-matching = 0.0
- `llm_judge`: mock judge_fn that returns "0.8", verify score is 0.8
- Skip semantic_sim tests if sentence-transformers not installed (use `pytest.importorskip`)

Run: `uv run pytest tests/ -v`

---

## Done when:
- [ ] All 5 scorers importable: `from openeval.scorers import exact_match, contains, regex, semantic_sim, llm_judge`
- [ ] `uv run pytest tests/ -v` passes
- [ ] You can run a full eval using 2+ scorers together

Quick verification script to run:
```python
from openeval import run, EvalCase
from openeval.scorers import exact_match, contains

cases = [
    EvalCase(input="What is 2+2?", expected_output="4"),
    EvalCase(input="Name a color", expected_output="blue"),
]

def my_model(text):
    return "4" if "2+2" in text else "The color is blue"

summary = run(my_model, cases, {"exact": exact_match, "contains": contains})
print(f"Pass rate: {summary.pass_rate}")
```

---

## Notes for next session
At the start of Day 3, tell Claude:
> "I finished Days 1 and 2. The eval loop and all 5 scorers work. Now I need to build the model adapters: OpenAI, Anthropic, Ollama, and a generic callable adapter."
