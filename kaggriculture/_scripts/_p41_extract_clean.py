# -*- coding: utf-8 -*-
"""Cleaner notebook→agent extraction."""
from __future__ import annotations

import json
import re
from pathlib import Path

NB_DIR = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p41_candidates")
OUT_DIR = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p41_extracted")
OUT_DIR.mkdir(exist_ok=True)

DROP_PATTERNS = [
    r"^\s*!",
    r"^\s*%",
    r"get_ipython",
    r"^\s*from IPython",
    r"^\s*import IPython",
    r"^\s*from ipywidgets",
    r"^\s*display\(",
    r"^\s*from IPython\.display",
]


def clean_code(code: str) -> str:
    lines = []
    for line in code.splitlines():
        s = line.strip()
        if any(re.search(p, line) for p in DROP_PATTERNS):
            # keep display() as no-op stub line if it's a real call mid-cell
            if s.startswith("display(") or s.startswith("from IPython"):
                continue
            if s.startswith("!") or s.startswith("%") or "get_ipython" in s:
                continue
            if "IPython" in s or "ipywidgets" in s:
                continue
        lines.append(line)
    text = "\n".join(lines)
    # stub display
    preamble = "def display(*a, **k):\n    pass\n\n"
    # move __future__ to top if present
    futures = re.findall(r"^from __future__ import .+$", text, flags=re.M)
    text = re.sub(r"^from __future__ import .+\n?", "", text, flags=re.M)
    head = "\n".join(futures) + "\n" if futures else ""
    return head + preamble + text


def extract(nb_path: Path) -> str | None:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    parts = []
    for c in nb.get("cells", []):
        if c.get("cell_type") == "code":
            parts.append("".join(c.get("source") or []))
    code = clean_code("\n\n".join(parts))
    if "def agent" not in code and "def build_agent" not in code:
        return None
    return code


def main():
    for nb in sorted(NB_DIR.glob("*.ipynb")):
        code = extract(nb)
        if not code:
            print("skip", nb.name)
            continue
        out = OUT_DIR / (re.sub(r"[^a-zA-Z0-9]+", "_", nb.stem)[:48] + ".py")
        out.write_text(code, encoding="utf-8")
        print("wrote", out.name, "chars", len(code))


if __name__ == "__main__":
    main()
