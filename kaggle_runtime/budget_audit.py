"""Static audit of the evaluation budget: official runtime default vs sample vs our fallback.

This reads the ACTUAL installed package sources (unpacked wheels / dist-info under
_workspace/gemma_rt/extract) rather than inferring defaults from documentation or from
community notebooks. Run it before any A/B so the budget in play is explicit.

    python kaggle_runtime/budget_audit.py

Exit code 0 = the three groups resolved and the fallback is consistent with the runtime.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXTRACT = REPO_ROOT / "_workspace" / "gemma_rt" / "extract"
SAMPLE_EVAL_CONFIG = REPO_ROOT / "gemma4_agent" / "data" / "sample_submission" / "eval_config.yaml"
SMOKE_MODULE = REPO_ROOT / "gemma4_agent" / "experiments" / "runtime_smoke.py"

FIELDS = (
    "time_minutes",
    "tool_calls",
    "turns",
    "command_timeout_seconds",
)

# The runtime dataclass names vs. the keys the participant-facing yaml uses.
# Getting this mapping wrong is exactly how a fallback silently becomes the demo
# budget instead of the real default, so it is declared explicitly here.
YAML_KEY = {
    "time_minutes": "max_time_minutes",
    "tool_calls": "max_tool_calls",
    "turns": "max_turns",
    "command_timeout_seconds": "timeout_seconds",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _dataclass_defaults(source: str, class_name: str) -> dict[str, object]:
    """Extract `name: type = default` assignments from a dataclass body via AST."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            out: dict[str, object] = {}
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    if stmt.value is None:
                        out[stmt.target.id] = None
                        continue
                    try:
                        out[stmt.target.id] = ast.literal_eval(stmt.value)
                    except Exception:
                        out[stmt.target.id] = ast.unparse(stmt.value)
            return out
    raise LookupError(f"class {class_name} not found")


def runtime_defaults() -> dict[str, dict[str, object]]:
    budget_py = EXTRACT / "swegemma" / "swegemma" / "budget.py"
    if not budget_py.is_file():
        raise FileNotFoundError(f"missing {budget_py}")
    src = _read(budget_py)
    return {
        "EvaluationBudget": _dataclass_defaults(src, "EvaluationBudget"),
        "HarnessLimits": _dataclass_defaults(src, "HarnessLimits"),
    }


def turns_effective_default() -> int:
    """`turns: None` is resolved to 500 inside agent_runner, not in the dataclass."""
    runner = EXTRACT / "swegemma" / "swegemma" / "harness" / "agent_runner.py"
    src = _read(runner)
    m = re.search(
        r"max_llm_calls\s*=\s*\(\s*config\.budget\.turns\s+if\s+config\.budget\.turns\s+is\s+not\s+None\s+else\s+(\d+)",
        src,
    )
    if not m:
        raise LookupError("could not find turns None->N fallback in agent_runner.py")
    return int(m.group(1))


def sample_config() -> dict[str, object]:
    """Parse the `evaluation:` block of the official sample eval_config.yaml."""
    if not SAMPLE_EVAL_CONFIG.is_file():
        raise FileNotFoundError(f"missing {SAMPLE_EVAL_CONFIG}")

    block: dict[str, object] | None = None
    indent_of_block: int | None = None

    for line in _read(SAMPLE_EVAL_CONFIG).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())

        if block is None:
            if stripped == "evaluation:":
                block = {}
                indent_of_block = indent
            continue

        # Leave the block once indentation drops back to (or below) its header.
        if indent <= (indent_of_block or 0):
            break
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*):\s*(\S+)\s*$", stripped)
        if not m:
            continue
        key, raw = m.group(1), m.group(2)
        try:
            block[key] = int(raw)
        except ValueError:
            try:
                block[key] = float(raw)
            except ValueError:
                block[key] = raw

    if not block:
        raise LookupError("no `evaluation:` block in sample eval_config.yaml")
    return block


def our_fallback() -> dict[str, object]:
    """Read the mirrored default straight out of runtime_smoke.py via AST.

    Importing it would pull in the whole smoke stack; the values live in a plain
    dict literal, so parsing is both cheaper and dependency-free. It is keyed by
    yaml names, so translate through YAML_KEY.
    """
    if not SMOKE_MODULE.is_file():
        raise FileNotFoundError(f"missing {SMOKE_MODULE}")
    tree = ast.parse(_read(SMOKE_MODULE))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "OFFICIAL_SAMPLE_EVAL_CONFIG":
                    raw = dict(ast.literal_eval(node.value))
                    if set(raw) & set(FIELDS):
                        return raw  # already in runtime names
                    return {f: raw.get(YAML_KEY[f]) for f in FIELDS}
    raise LookupError("OFFICIAL_SAMPLE_EVAL_CONFIG not found in runtime_smoke.py")


def _translate_sample(block: dict[str, object]) -> dict[str, object]:
    return {f: block.get(YAML_KEY[f]) for f in FIELDS}


def main() -> int:
    rt = runtime_defaults()
    eb = rt["EvaluationBudget"]
    hl = rt["HarnessLimits"]
    turns_eff = turns_effective_default()
    sample = _translate_sample(sample_config())
    ours = our_fallback()

    official = {
        "time_minutes": eb["time_minutes"],
        # None means unbounded; nothing in EvalConfig raises it.
        "tool_calls": eb["tool_calls"],
        "turns": turns_eff,
        "command_timeout_seconds": hl["command_timeout_seconds"],
    }

    print("=== OFFICIAL RUNTIME DEFAULT (swegemma/budget.py + agent_runner.py) ===")
    for k in FIELDS:
        print(f"  {k}: {official[k]}")
    print(f"  (dataclass time_minutes={eb['time_minutes']!r}, tool_calls={eb['tool_calls']!r}, "
          f"turns={eb['turns']!r} -> resolved {turns_eff} in agent_runner.py)")

    print()
    print("=== SAMPLE eval_config.yaml (participant-facing demo) ===")
    for k in FIELDS:
        print(f"  {k}: {sample.get(k)}")

    print()
    print("=== OUR CURRENT FALLBACK (DEFAULT_EVAL_SETTINGS) ===")
    for k in FIELDS:
        print(f"  {k}: {ours.get(k)}")
    print(f"  source: {SAMPLE_EVAL_CONFIG.relative_to(REPO_ROOT)} (mirrored)")

    print()
    print("=== VERDICT ===")
    same_as_sample = all(ours.get(k) == sample.get(k) for k in FIELDS)
    same_as_official = all(ours.get(k) == official.get(k) for k in FIELDS)

    print(f"  fallback == sample  : {same_as_sample}")
    print(f"  fallback == official: {same_as_official}")
    if same_as_sample and not same_as_official:
        print("  => fallback is the DEMO budget, NOT the official capability ceiling.")
        print("     Any run using it is BUDGET-LIMITED and cannot measure true repair ability.")
        for k in FIELDS:
            a, b = official.get(k), ours.get(k)
            if a == b:
                continue
            if a is None:
                print(f"     {k}: official unbounded vs ours {b}")
            else:
                print(f"     {k}: official {a} vs ours {b}")

    print()
    print("=== EFFECTIVE OFFICIAL-EQUIVALENT CONFIG ===")
    print("  (use this to make a run explicit and reproducible)")
    print("  evaluation:")
    print(f"    timeout_seconds: {official['command_timeout_seconds']}")
    print(f"    max_tool_calls: <unset / omit>   # runtime default is None = unbounded")
    print(f"    max_time_minutes: {int(official['time_minutes'])}")
    print(f"    max_turns: {official['turns']}")

    return 0 if same_as_official or same_as_sample else 1


if __name__ == "__main__":
    raise SystemExit(main())
