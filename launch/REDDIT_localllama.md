# r/LocalLLaMA post (draft)

Title options:
- OpenEval: local-first LLM evals with Ollama + a pytest-like API
- OpenEval (Python): run eval suites against Ollama or any callable

Post:

I made **OpenEval**, a Python eval harness where scorers are just functions — no YAML, no SaaS, no lock-in.

It supports local evals via **Ollama**:

`openeval run --suite factuality --model ollama:llama3.2`

…and can run async/parallel eval calls + generate an HTML report.

Repo: <REPO_URL>
PyPI: https://pypi.org/project/openeval-ai/

If you’re doing local model iteration, what eval suites do you find most useful (factuality, instruction following, hallucination/uncertainty, RAG relevance, etc.)?
