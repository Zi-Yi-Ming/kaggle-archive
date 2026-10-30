# -*- coding: utf-8 -*-
"""Find and download kaggriculture daily top-episodes datasets."""
from __future__ import annotations

from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

OUT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\p51_episodes")
OUT.mkdir(parents=True, exist_ok=True)


def main():
    api = KaggleApi()
    api.authenticate()

    # search datasets
    queries = [
        "kaggriculture episodes",
        "kaggriculture top episodes",
        "kaggriculture daily",
    ]
    found = []
    for q in queries:
        try:
            ds = api.dataset_list(search=q, sort_by="updated")
            # ds may be list-like
            items = ds if isinstance(ds, list) else getattr(ds, "datasets", ds)
            if not isinstance(items, list):
                items = list(items)
        except Exception as e:
            print(f"search fail {q}: {e}")
            continue
        print(f"\n=== search '{q}' n={len(items)} ===")
        for d in items[:15]:
            ref = getattr(d, "ref", None) or (d.get("ref") if isinstance(d, dict) else None)
            title = getattr(d, "title", None) or (d.get("title") if isinstance(d, dict) else None)
            size = getattr(d, "totalBytes", None) or (d.get("totalBytes") if isinstance(d, dict) else None)
            upd = getattr(d, "lastUpdated", None) or (d.get("lastUpdated") if isinstance(d, dict) else None)
            print(f"  {ref} | {title} | {size} | {upd}")
            if ref and "kaggriculture" in str(ref).lower() + str(title).lower():
                found.append(ref)

    # unique preserve order
    seen = set()
    uniq = []
    for r in found:
        if r not in seen:
            seen.add(r)
            uniq.append(r)
    print(f"\nfound {len(uniq)} kaggriculture-related datasets")

    # download a few most relevant (prefer small-ish recent)
    for ref in uniq[:6]:
        dest = OUT / ref.replace("/", "_")
        dest.mkdir(parents=True, exist_ok=True)
        print(f"\nDOWNLOAD {ref} -> {dest}")
        try:
            api.dataset_download_files(ref, path=str(dest), unzip=True)
            files = list(dest.rglob("*"))
            print(f"  files={len(files)}")
            for f in files[:8]:
                if f.is_file():
                    print(f"    {f.name} {f.stat().st_size}")
        except Exception as e:
            print(f"  FAIL: {e}")

    print("\nOUT:", OUT)


if __name__ == "__main__":
    main()
