# GitHub Action

The official action lives in the `openeval-action/` folder in this repo.

Minimal workflow:

```yaml
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

Notes:

- Ollama requires a self-hosted runner.
- The action writes an HTML report and posts a PR comment.

