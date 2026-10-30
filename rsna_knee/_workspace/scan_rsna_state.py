from __future__ import annotations

import json
import zipfile
from pathlib import Path

ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
WORKSPACE = Path(r"D:/桌面/Kaggle/_workspace")


def safe_load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        return {"__error__": str(e)}


print("=== meta.json ===")
for p in sorted(ROOT.rglob("meta.json")):
    if "_dataset_stage" in str(p) or "__pycache__" in str(p):
        continue
    d = safe_load(p)
    if "__error__" in d:
        print(p, d)
        continue
    train = d.get("fold_train_time_sec")
    train_h = None if train is None else round(train / 3600.0, 2)
    print(
        f"{p.relative_to(ROOT)} | fold={d.get('fold')} plane={d.get('plane')} "
        f"status={d.get('completion_status')} train_h={train_h} pred={d.get('prediction_shape')}"
    )

print("\n=== config.json args ===")
for p in sorted(ROOT.rglob("config.json")):
    if "_dataset_stage" in str(p):
        continue
    d = safe_load(p)
    a = d.get("args", {})
    print(
        f"{p.relative_to(ROOT)} | exp={d.get('experiment_id')} planes={a.get('planes')} "
        f"only_fold={a.get('only_fold')} epochs={a.get('epochs')} no_report={a.get('no_report_labels')} "
        f"pretrained={a.get('pretrained')} resume={a.get('resume_dir')}"
    )

print("\n=== submissions sizes ===")
for p in sorted((ROOT / "submissions").glob("*.csv")):
    n = sum(1 for _ in p.open("rb"))
    print(f"{p.name}: rows={n}")

print("\n=== leaderboard zip ===")
zpath = Path(r"D:/桌面/Kaggle/rsna-knee-abnormality-detection.zip")
if zpath.exists():
    out = WORKSPACE / "_lb_tmp"
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zpath, "r") as zf:
        zf.extractall(out)
        print("extracted:", zf.namelist())
        for name in zf.namelist():
            fp = out / name
            if fp.suffix.lower() == ".csv":
                text = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
                print(f"--- {name} head ---")
                for line in text[:8]:
                    print(line)
                print(f"rows={len(text)-1}")
else:
    print("zip missing")

print("\n=== exp003 notebook text hits ===")
for p in [
    ROOT / "_push_exp003_fold1" / "rsna_exp003_fold1_run.ipynb",
    ROOT / "_push_exp003" / "rsna_exp003_sc_fold0_run.ipynb",
]:
    if not p.exists():
        print("missing", p)
        continue
    nb = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    print(f"--- {p.name} cells={len(nb.get('cells', []))} ---")
    for i, cell in enumerate(nb.get("cells", [])):
        src = "".join(cell.get("source", []))
        if cell.get("cell_type") != "code":
            continue
        if any(k in src for k in ["python ", "artifact", "only-fold", "planes", "submission", "resume", "experiment"]):
            print(f"[cell {i}]")
            print(src[:1200])
            print()
        outs = cell.get("outputs", [])
        for o in outs:
            text = ""
            if isinstance(o.get("text"), list):
                text = "".join(o["text"])
            elif isinstance(o.get("text"), str):
                text = o["text"]
            data = o.get("data", {})
            if isinstance(data, dict):
                t = data.get("text/plain")
                if isinstance(t, list):
                    text += "".join(t)
                elif isinstance(t, str):
                    text += t
            if text and any(k in text for k in ["fold", "artifact", "ensemble", "submission", "OOF", "score", "saved", "skip", "time"]):
                print(f"[out cell {i}] {text[:800]}")
                print()
