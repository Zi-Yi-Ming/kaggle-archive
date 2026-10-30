# -*- coding: utf-8 -*-
"""P76: extract thomas layer inventory for architecture note + ablation plan."""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(
    r"D:\桌面\Kaggle\kaggriculture\_external\scan_20260919\extracted\thomas_2945_clean.py"
)
OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_research\p76_thomas_layer_inventory.txt")

text = SRC.read_text(encoding="utf-8", errors="ignore")
lines = text.splitlines()

# section banners
banners = []
for i, line in enumerate(lines, 1):
    if re.match(r"^# -{10,}", line) or re.match(r"^# v\d", line) or re.match(r"^# EXP", line):
        if len(line) > 20:
            banners.append(f"{i:5d}| {line[:120]}")

# agent redefinitions
agents = []
for i, line in enumerate(lines, 1):
    if re.match(r"^def agent\s*\(", line) or re.match(r"^agent\s*=", line):
        agents.append(f"{i:5d}| {line[:100]}")

# v9 / R* functions
funcs = []
for m in re.finditer(r"(?m)^def\s+(_v9_[A-Za-z0-9_]+|_r\d+[A-Za-z0-9_]*|_v2\d+[A-Za-z0-9_]*)\s*\(", text):
    funcs.append(m.group(1))

# constants blocks
consts = re.findall(r"(?m)^(V9_[A-Z0-9_]+)\s*=\s*(.+)$", text)

body = [
    "P76 thomas_2945 layer inventory",
    f"source={SRC}",
    f"bytes={SRC.stat().st_size} lines={len(lines)}",
    "",
    "=== agent redefs / assignments (order = wrap order) ===",
    *agents,
    "",
    "=== named helper funcs ===",
    *funcs,
    "",
    "=== V9 constants ===",
]
for k, v in consts:
    body.append(f"  {k} = {v.strip()[:80]}")
body += ["", "=== comment banners (sample) ===", *banners[:80]]
OUT.write_text("\n".join(body) + "\n", encoding="utf-8")
print("\n".join(body[:120]))
print("...")
print("WROTE", OUT)
print("n_agent_lines", len(agents), "n_v9_funcs", len([f for f in funcs if f.startswith('_v9_')]))
