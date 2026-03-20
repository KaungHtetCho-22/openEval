from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table

ROOT = Path(__file__).resolve().parents[1]
BENCH = Path(__file__).resolve().parent


@dataclass(frozen=True)
class BenchResult:
    tool: str
    task: str
    loc: int
    setup_s: float | None
    run_s: float | None
    ok: bool
    notes: str = ""


def main() -> None:
    results: list[BenchResult] = []

    for task in ("a", "b", "c"):
        results.append(run_python(tool="openeval", task=task, path=BENCH / f"task_{task}_openeval.py"))
        results.append(run_deepeval(task=task, path=BENCH / f"task_{task}_deepeval.py"))
        results.append(run_promptfoo(task=task, path=BENCH / f"task_{task}_promptfoo.yaml"))

    console = Console()
    console.print(to_rich_table(results))

    out = {
        "generated_at": time.time(),
        "results": [r.__dict__ for r in results],
    }
    (BENCH / "results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\nMarkdown table:\n")
    print(to_markdown_table(results))


def run_python(*, tool: str, task: str, path: Path) -> BenchResult:
    loc = count_loc(path)
    t0 = time.perf_counter()
    mod = import_module_from_path(path)
    t1 = time.perf_counter()
    try:
        payload = mod.run_benchmark()
        run_s = float(payload.get("run_s", 0.0))
        setup_s = (time.perf_counter() - t0) - run_s
        return BenchResult(tool=tool, task=task.upper(), loc=loc, setup_s=setup_s, run_s=run_s, ok=True)
    except Exception as exc:
        return BenchResult(tool=tool, task=task.upper(), loc=loc, setup_s=t1 - t0, run_s=None, ok=False, notes=str(exc))


def run_deepeval(*, task: str, path: Path) -> BenchResult:
    loc = count_loc(path)
    py = BENCH / ".venv" / "bin" / "python"
    if not py.exists():
        return BenchResult(
            tool="deepeval",
            task=task.upper(),
            loc=loc,
            setup_s=None,
            run_s=None,
            ok=False,
            notes="benchmarks/.venv missing (see benchmarks/README.md)",
        )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    t0 = time.perf_counter()
    proc = subprocess.run([str(py), str(path)], capture_output=True, text=True, env=env)
    elapsed = time.perf_counter() - t0
    if proc.returncode != 0:
        return BenchResult("deepeval", task.upper(), loc, None, None, False, proc.stderr.strip()[:2000])

    # Script prints dict; parse best-effort.
    run_s = None
    try:
        payload = eval(proc.stdout.strip(), {"__builtins__": {}}, {})  # noqa: S307
        run_s = float(payload.get("run_s", 0.0))
    except Exception:
        run_s = None

    setup_s = elapsed - (run_s or 0.0) if run_s is not None else None
    return BenchResult("deepeval", task.upper(), loc, setup_s, run_s, True)


def run_promptfoo(*, task: str, path: Path) -> BenchResult:
    loc = count_loc(path)
    if os.environ.get("OPENEVAL_BENCH_PROMPTFOO") != "1":
        return BenchResult("promptfoo", task.upper(), loc, None, None, False, "set OPENEVAL_BENCH_PROMPTFOO=1 to run")
    cmd = ["npx", "--yes", "promptfoo@latest", "eval", "-c", str(path)]
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        return BenchResult("promptfoo", task.upper(), loc, None, None, False, "npx not found")
    except subprocess.TimeoutExpired:
        return BenchResult("promptfoo", task.upper(), loc, None, None, False, "timeout (120s)")

    elapsed = time.perf_counter() - t0
    if proc.returncode != 0:
        return BenchResult("promptfoo", task.upper(), loc, None, None, False, proc.stderr.strip()[:2000])
    return BenchResult("promptfoo", task.upper(), loc, None, elapsed, True)


def count_loc(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        count += 1
    return count


def import_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def to_rich_table(results: list[BenchResult]) -> Table:
    t = Table(title="Benchmark Comparison (Tasks A–C)")
    t.add_column("Tool", style="bold")
    t.add_column("Task")
    t.add_column("LOC", justify="right")
    t.add_column("Setup (s)", justify="right")
    t.add_column("Run (s)", justify="right")
    t.add_column("OK")
    t.add_column("Notes", overflow="fold")
    for r in results:
        ok = "✅" if r.ok else "❌"
        t.add_row(
            r.tool,
            r.task,
            str(r.loc),
            "-" if r.setup_s is None else f"{r.setup_s:.3f}",
            "-" if r.run_s is None else f"{r.run_s:.3f}",
            ok,
            r.notes,
        )
    return t


def to_markdown_table(results: list[BenchResult]) -> str:
    header = "| Tool | Task | LOC | Setup (s) | Run (s) | OK |\n|---|---:|---:|---:|---:|:---:|"
    rows = []
    for r in results:
        rows.append(
            "| "
            + " | ".join(
                [
                    r.tool,
                    r.task,
                    str(r.loc),
                    "-" if r.setup_s is None else f"{r.setup_s:.3f}",
                    "-" if r.run_s is None else f"{r.run_s:.3f}",
                    "✅" if r.ok else "❌",
                ]
            )
            + " |"
        )
    return "\n".join([header, *rows])


if __name__ == "__main__":
    main()
