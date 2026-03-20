from __future__ import annotations

"""
Example 08 — CI/CD integration

This file is intentionally "doc-like": it prints copy-paste snippets for:
- pytest plugin usage
- GitHub Action usage

Run:
  python examples/08_cicd_integration.py
"""


def main() -> None:
    print("=== pytest plugin example ===")
    print(
        r"""
# test_my_model.py
import pytest

@pytest.mark.eval
def test_factuality(eval_model):
    from openeval.suites import factuality
    summary = factuality.run(eval_model)
    assert summary.pass_rate >= 0.8
""".strip()
    )
    print()
    print("Run it:")
    print("  pytest --eval-model ollama:llama3.2")
    print()

    print("=== GitHub Action example ===")
    print(
        r"""
# .github/workflows/eval.yml
name: LLM Eval
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: your-username/openeval-action@v1
        with:
          suite: hallucination
          model: openai:gpt-4o-mini
          threshold: "0.8"
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
""".strip()
    )
    print()

    print("Tip: start with a conservative threshold (e.g. 0.7–0.8) and raise it gradually.")


if __name__ == "__main__":
    main()

