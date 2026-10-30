from pathlib import Path
import json

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p98_new")

def show(tag, rel, keys):
    nb = ROOT / rel
    data = json.loads(nb.read_text(encoding="utf-8"))
    for i, c in enumerate(data.get("cells", [])):
        src = c.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        hit = False
        for k in keys:
            if k in src:
                hit = True
        if not hit:
            continue
        print("====", tag, "cell", i, "len", len(src))
        for k in keys:
            pos = 0
            while True:
                j = src.find(k, pos)
                if j < 0:
                    break
                print(f"--- {k} @ {j} ---")
                print(src[max(0, j - 60): j + 220].replace("\n", " | "))
                pos = j + len(k)

show("v56", "v56/kaggriculture-v56-smarter-seeds-and-fertilizer.ipynb",
     ["MAIN", "base64", "zlib", "write_bytes", "b64decode", "decompress"])
show("v54leak", "v54leak/92-vs-the-best-public-farm-a-seed-leak-in-v54.ipynb",
     ["lzma", "base64", "write_bytes", "main =", "decompress", "b64decode"])
show("orderbook", "orderbook/your-market-list-is-an-order-book.ipynb",
     ["source =", "base64", "zlib", "write_bytes", "b64decode"])
