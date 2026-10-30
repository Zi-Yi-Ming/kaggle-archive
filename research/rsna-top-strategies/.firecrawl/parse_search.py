import json, os, sys

base = r"D:\桌面\Kaggle\research\rsna-top-strategies\.firecrawl"
names = sys.argv[1:] or ["search1-llm-labels", "search2-multiplane", "search3-labels-vs-scale"]

for name in names:
    path = os.path.join(base, name + ".json")
    if not os.path.exists(path):
        print("MISSING", path)
        continue
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    print("===", name, "===")
    print("id:", d.get("id"))
    data = d.get("data") or []
    items = []
    if isinstance(data, dict):
        items = data.get("web") or data.get("results") or []
    else:
        for x in data:
            if isinstance(x, dict) and x.get("web"):
                items.extend(x["web"])
            elif isinstance(x, dict) and x.get("url"):
                items.append(x)
    for i, it in enumerate(items[:12]):
        title = (it.get("title") or "")[:140]
        url = it.get("url") or ""
        desc = it.get("description") or it.get("snippet") or it.get("highlights") or ""
        if isinstance(desc, list):
            desc = " | ".join(str(x) for x in desc[:4])
        desc = str(desc)[:300].replace("\n", " ")
        print(f"[{i}] {title}")
        print("    ", url)
        print("    ", desc)
        print()
