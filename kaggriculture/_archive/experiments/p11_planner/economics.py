# -*- coding: utf-8 -*-
"""Economic constants and elite prior (mined from R2 structure, not tape copy)."""
from __future__ import annotations

ANIMALS = ("GOOSE", "COW", "SHEEP")
CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
PRODUCTS = CROPS + ("EGG", "MILK", "WOOL", "FERTILIZER")

ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
ANIMAL_PRODUCT = {"GOOSE": "EGG", "COW": "MILK", "SHEEP": "WOOL"}
ANIMAL_STRUCTURE = {"GOOSE": "COOP", "COW": "PASTURE", "SHEEP": "PASTURE"}
ANIMAL_MAX_HELD = {"GOOSE": 4, "COW": 6, "SHEEP": 6}

SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
CROP_BASE_PRICE = {
    "WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250,
    "EGG": 50, "MILK": 80, "WOOL": 100, "FERTILIZER": 40,
}
LAND_ORDER = ("NE", "SW", "SE")
LAND_PRICES = (1000, 2000, 4000)
SHED_CAP = 100
MAX_ORDERS = 10
MAX_DAYS = 30
TURNS_PER_DAY = 24
LAST_STEP = 718

# Elite production prior (Ashok top-10 + R2 structure). Not a schedule tape.
ELITE_ANIMALS = {"COW": 8, "SHEEP": 6, "GOOSE": 3}
ELITE_LAND = 3  # quadrants

# Land unlock cost by quadrant index (0 already owned)
def land_cost(unlocked_n: int) -> int | None:
    n = unlocked_n - 1
    if n < 0 or n >= len(LAND_PRICES):
        return None
    return LAND_PRICES[n]


def fib(n: int) -> int:
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


def hire_batch_cost(hires_today: int, count: int) -> int:
    return sum(fib(hires_today + i) for i in range(count))


def cash_reserve(day: int, money: float) -> float:
    """Adaptive reserve: keep enough to rehire + feed animals tomorrow."""
    if money < 400:
        return 80
    if money < 1500:
        return 150
    return 250 + 20 * min(day, 20)


def crop_priority(day: int, shops: list[str]) -> list[str]:
    """Cash-crop preference. Shop-aware; falls back to elite mix."""
    shop_set = set(shops or [])
    if day < 8:
        return ["WHEAT"]  # feed bootstrap
    prefs = []
    # High value first; tweak by shops when known
    if "YARN_STORE" in shop_set:
        prefs += ["STRAWBERRY", "MELON"]
    if "ICE_CREAM_SHOP" in shop_set or "SMOOTHIE_SHOP" in shop_set:
        prefs += ["MELON", "STRAWBERRY"]
    if "BAKERY" in shop_set or "BRUNCH_SPOT" in shop_set:
        prefs += ["CARROT", "WHEAT"]
    if "FARMERS_MARKET" in shop_set or "PET_CAFE" in shop_set:
        prefs += ["STRAWBERRY", "CARROT"]
    if "PIZZA_SHOP" in shop_set:
        prefs += ["CARROT", "TOMATO"]
    # stable elite backbone
    for c in ("STRAWBERRY", "MELON", "CARROT", "WHEAT"):
        if c not in prefs:
            prefs.append(c)
    return prefs


def empty_tiles(tiles):
    out = []
    for y, row in enumerate(tiles or []):
        for x, t in enumerate(row):
            if t is None:
                out.append((x, y))
    return out


def count_kind(tiles, pred):
    n = 0
    for row in tiles or []:
        for t in row:
            if isinstance(t, dict) and pred(t):
                n += 1
    return n


def animal_counts(tiles):
    counts = {a: 0 for a in ANIMALS}
    for row in tiles or []:
        for t in row:
            if isinstance(t, dict):
                a = t.get("animal")
                if a in counts:
                    counts[a] += 1
    return counts


def structure_gaps(tiles, shed, inventories):
    """How many more structures / placements needed for elite animals."""
    live = animal_counts(tiles)
    in_shed = {a: int(shed.get(a) or 0) for a in ANIMALS}
    in_inv = {a: 0 for a in ANIMALS}
    for inv in inventories or []:
        for a in ANIMALS:
            in_inv[a] += int((inv or {}).get(a) or 0)
    # empty structures waiting for animals
    empty_coop = count_kind(tiles, lambda t: t.get("kind") == "COOP" and not t.get("animal"))
    empty_past = count_kind(tiles, lambda t: t.get("kind") == "PASTURE" and not t.get("animal"))
    occupied_past = count_kind(tiles, lambda t: t.get("kind") == "PASTURE" and t.get("animal"))
    occupied_coop = count_kind(tiles, lambda t: t.get("kind") == "COOP" and t.get("animal"))
    need_buy = {}
    need_build = {}
    need_place = {}
    for a, target in ELITE_ANIMALS.items():
        have = live[a] + in_shed[a] + in_inv[a]
        gap = max(0, target - have)
        need_buy[a] = gap
        struct = ANIMAL_STRUCTURE[a]
        empty = empty_coop if struct == "COOP" else empty_past
        occ = occupied_coop if struct == "COOP" else occupied_past
        live_n = live[a]
        # need structures for live + pending purchase not yet built
        need_struct = max(0, target - occ - empty)
        need_build[a] = need_struct
        # place: animals in shed/inv onto empty structures
        empty_for_a = empty_coop if struct == "COOP" else empty_past
        need_place[a] = min(in_shed[a] + in_inv[a], empty_for_a)
    return need_buy, need_build, need_place


def hungry_animals(tiles):
    n = 0
    for row in tiles or []:
        for t in row:
            if isinstance(t, dict) and t.get("animal") and not t.get("fed_today"):
                n += 1
    return n


def uncared_animals(tiles):
    n = 0
    for row in tiles or []:
        for t in row:
            if isinstance(t, dict) and t.get("animal") and t.get("fed_today") and not t.get("cared_today"):
                n += 1
    return n


def ready_yields(tiles):
    """Tiles with harvestable yield (crops or animals)."""
    out = []
    for y, row in enumerate(tiles or []):
        for x, t in enumerate(row):
            if isinstance(t, dict) and int(t.get("yield_units") or 0) > 0:
                out.append((x, y))
    return out


def dry_plants(tiles, day):
    out = []
    for y, row in enumerate(tiles or []):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today"):
                if day < 29:
                    out.append((x, y))
    return out


def fert_ready(tiles):
    out = []
    for y, row in enumerate(tiles or []):
        for x, t in enumerate(row):
            if isinstance(t, dict) and t.get("fertilizer_available"):
                out.append((x, y))
    return out
