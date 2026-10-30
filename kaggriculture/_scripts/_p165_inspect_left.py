from pathlib import Path
import json

for tag in ["harvest_ledger", "ice_fire", "pop_robust"]:
    d = Path(rf"D:\桌面\Kaggle\kaggriculture\_external\scan_today\{tag}")
    nbs = list(d.glob("*.ipynb")) if d.exists() else []
    if not nbs:
        print(tag, "no nb")
        continue
    data = json.loads(nbs[0].read_text(encoding="utf-8"))
    src = ""
    for c in data["cells"]:
        s = c.get("source", "")
        if isinstance(s, list):
            s = "".join(s)
        if len(s) > len(src):
            src = s
    print("====", tag, "len", len(src))
    print(src[:300].replace("\n", " | "))
    for key in ["AGENT", "BLOB", "b64", "b85", "gzip", "join((", "writefile", "def agent", "decompress"]:
        print(f"  {key}: {src.find(key)}")
