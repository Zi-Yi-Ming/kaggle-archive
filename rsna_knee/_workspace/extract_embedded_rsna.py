from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

nb_path = Path(r"D:/桌面/Kaggle/rsna_knee/_push_exp003/rsna_exp003_sc_fold0_run.ipynb")
local_v3 = Path(r"D:/桌面/Kaggle/rsna_knee/rsna_v3.py")
local_lab = Path(r"D:/桌面/Kaggle/rsna_knee/rsna_report_labels.py")
out_dir = Path(r"D:/桌面/Kaggle/_workspace/rsna_exp004_prep")
out_dir.mkdir(parents=True, exist_ok=True)

nb = json.loads(nb_path.read_text(encoding="utf-8"))
embedded = {}
for cell in nb["cells"]:
    src = cell.get("source", [])
    if isinstance(src, list):
        text = "".join(src)
    else:
        text = src
    if "base64.b64decode" in text and "parts.append" in text:
        # extract first long base64 string
        import re

        m = re.search(r'parts\.append\("([A-Za-z0-9+/=]{200,})"\)', text)
        if not m:
            # try without escape - the json already unescaped
            m = re.search(r'parts\.append\("([^"]{200,})"\)', text)
        if m:
            raw = base64.b64decode(m.group(1))
            name = "rsna_v3.py" if "rsna_v3" in text else "rsna_report_labels.py"
            if "report_labels" in text:
                name = "rsna_report_labels.py"
            elif "rsna_v3" in text:
                name = "rsna_v3.py"
            embedded[name] = raw
            p = out_dir / f"embedded_{name}"
            p.write_bytes(raw)
            print(name, "embedded sha", hashlib.sha256(raw).hexdigest(), "size", len(raw))

print("local v3", hashlib.sha256(local_v3.read_bytes()).hexdigest(), local_v3.stat().st_size)
print("local lab", hashlib.sha256(local_lab.read_bytes()).hexdigest(), local_lab.stat().st_size)

# fallback: pull from fold1 notebook which also embeds
nb2 = Path(r"D:/桌面/Kaggle/rsna_knee/_push_exp003_fold1/rsna_exp003_fold1_run.ipynb")
if nb2.exists():
    nb = json.loads(nb2.read_text(encoding="utf-8"))
    for cell in nb["cells"]:
        src = cell.get("source", [])
        text = "".join(src) if isinstance(src, list) else src
        if "parts.append" not in text:
            continue
        import re

        ms = re.findall(r'parts\.append\("([^"]+)"\)', text)
        for blob in ms:
            if len(blob) < 200:
                continue
            raw = base64.b64decode(blob)
            h = hashlib.sha256(raw).hexdigest()
            print("fold1 embed candidate", h, len(raw), raw[:40])
            if h.startswith("1612f21") or b"rsna_v3" in raw[:80] or b"Knee" in raw[:80]:
                (out_dir / "embedded_from_fold1_rsna_v3.py").write_bytes(raw)
            if h.startswith("bc356e71") or b"report_labels" in raw[:80]:
                (out_dir / "embedded_from_fold1_labels.py").write_bytes(raw)

print("files", list(out_dir.iterdir()))
