# -*- coding: utf-8 -*-
"""Extract executable agent sources from scan notebooks (P74)."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_20260919")
OUT = ROOT / "extracted"
OUT.mkdir(exist_ok=True)

# prefer folders that look like the 2945 / master-engine line
TARGETS = {
    "thomastschinkel__the-2945-farm-96-vs-the-top-10-public-bots": "thomas_2945",
    "sunil123kumar__kaggriculture-top-10-public-bots": "sunil_top10",
    "guruprasaathas111__kaggriculture-master-engine-v3": "guru_master_v3",
    "guruprasaathas111__game-theoretic-master-discrete-optimization": "guru_gametheory",
    "goodpjw2008__kaggriculture-melon-threshold-squeeze-2749": "goodpjw_melon2749",
    "ahmedberatozer__kaggriculture-v50-early-yarn-commit": "ahmed_v50",
}


def cell_sources(nb_path: Path) -> list[str]:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    out = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", [])
        out.append("".join(src) if isinstance(src, list) else str(src))
    return out


def decode_escapes(text: str) -> str:
    if text.count("\\n") > 20 and "\n" not in text[:200]:
        try:
            return text.encode("utf-8").decode("unicode_escape")
        except Exception:
            return text
    return text


def extract_agent_block(text: str) -> str | None:
    text = decode_escapes(text)
    # 1) full cell already defines agent()
    if re.search(r"def\s+agent\s*\(", text):
        return text
    # 2) string assignment holding full main.py
    m = re.search(
        r"""(?is)(?:main_py|MAIN_PY|AGENT_SRC|agent_src|SOURCE)\s*=\s*(?:r?\"\"\"|r?''')(.*?)(?:\"\"\"|''')""",
        text,
    )
    if m:
        body = m.group(1)
        body = decode_escapes(body)
        if re.search(r"def\s+agent\s*\(", body):
            return body
    return None


def syntax_ok(src: str) -> bool:
    try:
        ast.parse(src)
        return True
    except SyntaxError:
        return False


def main() -> None:
    report = []
    for folder, tag in TARGETS.items():
        d = ROOT / folder
        nbs = list(d.glob("*.ipynb"))
        if not nbs:
            report.append(f"{tag}: NO_NB")
            continue
        best = None
        best_score = -1
        for src in cell_sources(nbs[0]):
            block = extract_agent_block(src)
            if not block:
                continue
            score = block.count("def ") + (50 if re.search(r"def\s+agent\s*\(", block) else 0)
            if "agent(" in block:
                score += 20
            if score > best_score:
                best_score = score
                best = block
        if not best:
            # fallback: concatenate all code cells that mention agent
            joined = []
            for src in cell_sources(nbs[0]):
                if "agent" in src.lower() or "ACTIONS" in src or "SHOP" in src:
                    joined.append(decode_escapes(src))
            best = "\n\n".join(joined) if joined else None
        if not best:
            report.append(f"{tag}: NO_AGENT_BLOCK")
            continue
        out_py = OUT / f"{tag}.py"
        out_py.write_text(best, encoding="utf-8")
        ok = syntax_ok(best)
        has_agent = bool(re.search(r"def\s+agent\s*\(", best))
        report.append(
            f"{tag}: wrote {out_py.name} bytes={out_py.stat().st_size} "
            f"agent_fn={has_agent} syntax_ok={ok}"
        )
    report_path = OUT / "extract_report.txt"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    print("WROTE", report_path)


if __name__ == "__main__":
    main()
