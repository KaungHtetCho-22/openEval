# CLI Reference

```bash
openeval run --suite factuality --model callable:my_models:model
openeval run -d examples/data/basic_qa.jsonl -m ollama:llama3.2
```

## Async mode

```bash
openeval run -d data.jsonl -m openai:gpt-4o-mini --async --concurrency 20
```

## HTML report

```bash
openeval run -d data.jsonl -m callable:my_models:model -o report.html
```

