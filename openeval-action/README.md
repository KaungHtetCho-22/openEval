# OpenEval — GitHub Action

Run OpenEval evals on every pull request and post results as a PR comment.

## Quick start

```yaml
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
```

## Inputs

- `suite` (optional): `hallucination`, `factuality`, `instruction_following`
- `dataset` (optional): path to `.jsonl` or `.csv` (required if `suite` is not provided)
- `model` (required): `openai:...`, `anthropic:...`, `ollama:...`, or `callable:module:fn`
- `threshold` (default `"0.7"`): pass threshold
- `fail_on_threshold` (default `"true"`): fail CI on low pass rate
- `openai_api_key` / `anthropic_api_key` (optional): you can provide keys via `with:` or via env vars

## OpenAI / Anthropic secrets

Prefer environment variables:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Ollama

Ollama requires a runner that can reach your Ollama server. Use a self-hosted runner and set `model: ollama:...`.

## Outputs

- `pass_rate`: float 0.0–1.0
- `passed`: `"true"` / `"false"`
- `report_path`: path to the generated HTML report

