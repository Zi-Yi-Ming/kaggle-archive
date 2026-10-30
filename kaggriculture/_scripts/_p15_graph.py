# -*- coding: utf-8 -*-
"""P15 economic dependency graph (engine-derived, not R2 tape)."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")

EDGES = [
    # crop lifecycle
    ("SEED", "PLANT_TILE", "BUY_SEED+PLANT", "occupies tile"),
    ("PLANT_TILE", "WATER", "WATER daily or WEED at unwatered>=2", "labor"),
    ("PLANT_TILE", "HARVEST", "fy_day + yield_units", "to worker inv"),
    ("HARVEST", "INVENTORY", "DROP/PLACE", "must deposit"),
    ("INVENTORY", "SHED", "EOD DROP", "dawn wipes inv"),
    ("SHED", "CASH", "SELL", "market quote"),
    # wheat specifically feeds animals
    ("WHEAT_SHED", "FEED", "PICKUP WHEAT + FEED on animal tile", "feed coupling"),
    ("FEED", "ANIMAL_YIELD", "fed_today required; unfed>=2 escapes", "survival"),
    # animals
    ("BUY_ANIMAL", "SHED_ANIMAL", "market", "cash out"),
    ("SHED_ANIMAL", "STRUCTURE", "BUILD_COOP/PASTURE + PLACE", "tile+build"),
    ("ANIMAL_TILE", "MILK_WOOL_EGG", "fy+interval yield if fed", "product"),
    ("ANIMAL_TILE", "FERTILIZER", "sheep fertilizer_available + COLLECT", "secondary"),
    ("MILK_WOOL_EGG", "CASH", "SELL", "peak mid-late"),
    ("FERTILIZER", "CASH", "SELL or FERTILIZE crop", "dual use"),
    # cash enables more production
    ("CASH", "BUY_SEED", "", "expand crops"),
    ("CASH", "BUY_ANIMAL", "", "expand livestock"),
    ("CASH", "BUY_LAND", "1000/2000/4000", "more tiles"),
    ("CASH", "HIRE", "fib daily; hands reset dawn", "labor"),
    # hypothesized multi-stage paths
    ("MELON_CASH_D10", "BUY_ANIMAL", "early cash funds livestock", "H_MULTI_STAGE"),
    ("WHEAT_TILE", "FEED_CAPACITY", "more wheat tiles -> more feed heads", "H_MULTI_STAGE"),
    ("SHEEP", "FERTILIZER", "trickle", "H_MULTI_STAGE"),
    ("LAND", "TILES", "unlock quadrant", "capacity"),
]


def main():
    out = ROOT / "p15_dependency_graph.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["from_node", "to_node", "mechanism", "note"])
        for e in EDGES:
            w.writerow(list(e))
    print(f"nodes edges={len(EDGES)} wrote {out.name}")
    # key paths for H_MULTI_STAGE
    paths = [
        ("WHEAT->FEED->ANIMAL->PRODUCT->CASH", "classic feed coupling"),
        ("MELON->d10_CASH->BUY_ANIMAL->later_PRODUCT", "cash-timing bridge"),
        ("ANIMAL->FERT->CROP or FERT->CASH", "secondary output"),
        ("LAND->TILES->(CROP|STRUCT)->both portfolios", "capacity contest"),
    ]
    out2 = ROOT / "p15_key_paths.csv"
    with open(out2, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path", "note"])
        w.writerows(paths)
    print("wrote", out2.name)


if __name__ == "__main__":
    main()
