from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .models import EvalCase


def from_csv(path: str | Path, input_col: str = "input", output_col: str = "expected_output") -> list[EvalCase]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file has no header row: {csv_path}")

        fieldnames = set(reader.fieldnames)
        if input_col not in fieldnames:
            raise KeyError(f"Missing required column '{input_col}' in CSV: {csv_path}")

        cases: list[EvalCase] = []
        for row in reader:
            raw_input = row.get(input_col, "")
            if raw_input is None or str(raw_input).strip() == "":
                continue

            expected_raw = row.get(output_col) if output_col in fieldnames else None
            expected = _none_if_blank(expected_raw)

            metadata = {k: v for k, v in row.items() if k not in {input_col, output_col}}
            cases.append(EvalCase(input=str(raw_input), expected_output=expected, metadata=metadata))

    return cases


def from_jsonl(path: str | Path) -> list[EvalCase]:
    jsonl_path = Path(path)
    if not jsonl_path.exists():
        raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")

    cases: list[EvalCase] = []
    with jsonl_path.open(encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {idx} in {jsonl_path}") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"Expected a JSON object on line {idx} in {jsonl_path}")

            if "input" not in obj:
                raise KeyError(f"Missing required key 'input' on line {idx} in {jsonl_path}")

            expected = _none_if_blank(obj.get("expected_output"))
            metadata = {k: v for k, v in obj.items() if k not in {"input", "expected_output"}}
            cases.append(EvalCase(input=str(obj["input"]), expected_output=expected, metadata=metadata))

    return cases


def from_list(data: list[dict[str, Any]]) -> list[EvalCase]:
    cases: list[EvalCase] = []
    for idx, obj in enumerate(data, start=1):
        if "input" not in obj:
            raise KeyError(f"Missing required key 'input' at index {idx}")
        expected = _none_if_blank(obj.get("expected_output"))
        metadata = {k: v for k, v in obj.items() if k not in {"input", "expected_output"}}
        cases.append(EvalCase(input=str(obj["input"]), expected_output=expected, metadata=metadata))
    return cases


def _none_if_blank(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return None if text.strip() == "" else text

