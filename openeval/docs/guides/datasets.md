# Loading Datasets

OpenEval can load datasets from CSV and JSONL.

```python
from openeval.dataset import from_csv, from_jsonl

cases = from_jsonl("data.jsonl")
cases = from_csv("data.csv", input_col="input", output_col="expected_output")
```

## JSONL format

```jsonl
{"input": "What is 2+2?", "expected_output": "4"}
```

