from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from openeval.cli import app


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output


def test_cli_run_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "--model" in result.output
    assert "--async" in result.output


def test_cli_run_with_callable_model(tmp_path, monkeypatch) -> None:
    # Create a temporary importable module for callable:... usage.
    model_mod = tmp_path / "mymodels.py"
    model_mod.write_text(
        "def model(prompt: str) -> str:\n"
        "    return '4' if '2+2' in prompt else 'unknown'\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    dataset = tmp_path / "data.jsonl"
    dataset.write_text('{"input":"What is 2+2?","expected_output":"4"}\n', encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["run", "-d", str(dataset), "-m", "callable:mymodels:model", "-t", "0.7"],
    )
    assert result.exit_code == 0, result.output
    assert "OpenEval Run" in result.output


def test_cli_run_async_with_callable_model(tmp_path, monkeypatch) -> None:
    model_mod = tmp_path / "mymodels_async.py"
    model_mod.write_text(
        "def model(prompt: str) -> str:\n"
        "    return '4' if '2+2' in prompt else 'unknown'\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    dataset = tmp_path / "data.jsonl"
    dataset.write_text('{"input":"What is 2+2?","expected_output":"4"}\n', encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["run", "-d", str(dataset), "-m", "callable:mymodels_async:model", "--async", "--concurrency", "5"],
    )
    assert result.exit_code == 0, result.output


def test_cli_run_suite_with_callable_model(tmp_path: Path, monkeypatch) -> None:
    model_mod = tmp_path / "mymodels2.py"
    model_mod.write_text(
        "def model(prompt: str) -> str:\n"
        "    return \"I don't know.\" \n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    runner = CliRunner()
    result = runner.invoke(app, ["run", "-s", "hallucination", "-m", "callable:mymodels2:model"])
    assert result.exit_code == 0, result.output
