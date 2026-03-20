from __future__ import annotations

import pytest

from openeval.dataset import from_csv, from_jsonl


def test_from_csv_loads_cases(tmp_path) -> None:
    p = tmp_path / "data.csv"
    p.write_text('input,expected_output,tag\n"What is 2+2?","4","math"\n', encoding="utf-8")
    cases = from_csv(p)
    assert len(cases) == 1
    assert cases[0].input == "What is 2+2?"
    assert cases[0].expected_output == "4"
    assert cases[0].metadata["tag"] == "math"


def test_from_csv_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        from_csv(tmp_path / "missing.csv")


def test_from_csv_missing_expected_output_column_is_allowed(tmp_path) -> None:
    p = tmp_path / "data.csv"
    p.write_text("input,tag\nhello,world\n", encoding="utf-8")
    cases = from_csv(p)
    assert len(cases) == 1
    assert cases[0].expected_output is None


def test_from_csv_missing_input_column_errors(tmp_path) -> None:
    p = tmp_path / "data.csv"
    p.write_text("x,expected_output\nhi,there\n", encoding="utf-8")
    with pytest.raises(KeyError):
        from_csv(p)


def test_from_jsonl_loads_cases(tmp_path) -> None:
    p = tmp_path / "data.jsonl"
    p.write_text(
        '{"input":"What is 2+2?","expected_output":"4","tag":"math"}\n{"input":"hi"}\n',
        encoding="utf-8",
    )
    cases = from_jsonl(p)
    assert len(cases) == 2
    assert cases[0].expected_output == "4"
    assert cases[0].metadata["tag"] == "math"
    assert cases[1].expected_output is None


def test_from_jsonl_missing_file(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        from_jsonl(tmp_path / "missing.jsonl")

