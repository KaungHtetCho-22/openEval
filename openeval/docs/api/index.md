# API Reference

## Core

- `openeval.run(model_fn, dataset, scorers, pass_threshold=0.7) -> EvalSummary`
- `openeval.arun(model_fn, dataset, scorers, pass_threshold=0.7, concurrency=10) -> EvalSummary`

## Batch

- `openeval.batch.batch_run(model_configs, dataset, scorers) -> dict[str, EvalSummary]`
- `openeval.batch.compare(summaries) -> ComparisonTable`

## Dataset loaders

- `openeval.dataset.from_csv(path, input_col="input", output_col="expected_output") -> list[EvalCase]`
- `openeval.dataset.from_jsonl(path) -> list[EvalCase]`
- `openeval.dataset.from_list(data) -> list[EvalCase]`

## Scorers

- `exact_match`, `contains`, `regex(...)`, `semantic_sim`, `llm_judge(...)`

## Adapters

- `openai_adapter(...)`, `anthropic_adapter(...)`, `ollama_adapter(...)`, `callable_adapter(...)`
- Async variants: `openai_async_adapter(...)`, `anthropic_async_adapter(...)`, `ollama_async_adapter(...)`

## Reporting

- `openeval.generate_report(summary, output_path, title="OpenEval Report")`

