# OpenEval

## LLM evals that don't get in your way

OpenEval is a lightweight, code-first evaluation framework for LLM outputs.
You bring a model callable and a dataset; OpenEval runs an eval loop and returns a typed summary.

```python
from openeval import EvalCase, run
from openeval.scorers import exact_match

cases = [EvalCase(input="2+2", expected_output="4")]
summary = run(lambda _: "4", cases, {"exact": exact_match})
print(summary.pass_rate)  # 1.0
```

**Quick install**

```bash
pip install openeval
```

### Why OpenEval

- **Scorers are plain Python functions** (no YAML, no inheritance)
- **Model-agnostic**: OpenAI, Anthropic, Ollama, or your own callable
- **CI-first**: pytest plugin + GitHub Action to run evals on every PR

---

Badges (wire these up when you publish):

- PyPI version
- Python versions
- License
- GitHub stars

