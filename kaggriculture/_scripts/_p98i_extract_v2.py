from pathlib import Path
import json
import re
import base64
import gzip
import zlib
import lzma
import hashlib

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_p98_new")
OUT = ROOT / "extracted"
OUT.mkdir(parents=True, exist_ok=True)


def cells_of(rel):
    nb = ROOT / rel
    data = json.loads(nb.read_text(encoding="utf-8"))
    out = []
    for c in data.get("cells", []):
        src = c.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        out.append((c.get("cell_type"), src))
    return out


def write_main(tag: str, src: bytes) -> Path | None:
    if not src:
        return None
    if isinstance(src, str):
        src = src.encode("utf-8")
    if len(src) < 5000:
        print("reject small", tag, len(src))
        return None
    if b"def " not in src:
        print("reject no def", tag, len(src))
        return None
    p = OUT / f"{tag}_main.py"
    p.write_bytes(src)
    print("WROTE", p.name, len(src), hashlib.sha256(src).hexdigest()[:16])
    return p


def region_after_assign(text: str, name: str, span=2000000) -> str | None:
    m = re.search(rf"{re.escape(name)}\s*=\s*", text)
    if not m:
        return None
    start = m.end()
    # end at decode of this name
    end_m = re.search(
        rf"{re.escape(name)}\)",
        text[start:start + span],
    )
    end = start + (end_m.start() if end_m else min(span, len(text) - start))
    return text[start:end]


def quoted_chunks(region: str) -> str:
    # pull '...' and "..." contents; b85 has no quotes inside
    chunks = re.findall(r"['\"]([^'\"]*)['\"]", region)
    return "".join(chunks)


def decode_blob(packed: str):
    if not packed:
        return None
    packed = re.sub(r"\s+", "", packed)
    raws = []
    for fn in (
        lambda s: base64.b85decode(s),
        lambda s: base64.b64decode(s + "=" * (-len(s) % 4)),
    ):
        try:
            raws.append(fn(packed))
        except Exception:
            continue
    decoders = [
        lambda b: zlib.decompress(b),
        lambda b: gzip.decompress(b),
        lambda b: lzma.decompress(b),
        lambda b: b,
    ]
    for raw in raws:
        for dec in decoders:
            try:
                out = dec(raw)
            except Exception:
                continue
            if b"def " in out and len(out) > 5000:
                return out
    return None


def extract(tag: str, rel: str):
    chunks = cells_of(rel)
    full = "\n".join(s for _, s in chunks)
    names = [
        "SOURCE_BLOB", "PAYLOAD", "AGENT_B64", "V54_B85", "SOURCE_B85",
        "AGENT_B85", "CODE_B85", "BLOB", "SOURCE",
    ]
    # discover NAME = ''.join((  or NAME = "..."
    for name in names:
        if name not in full:
            continue
        region = region_after_assign(full, name)
        if not region:
            continue
        packed = quoted_chunks(region)
        print(f"try {tag} {name} packed_len={len(packed)}")
        src = decode_blob(packed)
        if src:
            p = write_main(tag, src)
            if p:
                return p
        else:
            print("  decode fail")
    # discover any  X = ''.join((
    for m in re.finditer(r"(\w+)\s*=\s*['\"]['\"]\.join\(\(", full):
        name = m.group(1)
        region = region_after_assign(full, name)
        packed = quoted_chunks(region) if region else None
        print(f"join-try {tag} {name} packed_len={len(packed or '')}")
        src = decode_blob(packed) if packed else None
        if src:
            p = write_main(tag, src)
            if p:
                return p
    print("FAIL", tag)
    return None


def main():
    pairs = [
        ("v55", "v55/kaggriculture-v55-one-turn-market-race-edge.ipynb"),
        ("v56", "v56/kaggriculture-v56-smarter-seeds-and-fertilizer.ipynb"),
        ("v54leak", "v54leak/92-vs-the-best-public-farm-a-seed-leak-in-v54.ipynb"),
        ("orderbook", "orderbook/your-market-list-is-an-order-book.ipynb"),
    ]
    found = {}
    for tag, rel in pairs:
        print("====", tag)
        p = extract(tag, rel)
        if p:
            found[tag] = str(p)
    idx = OUT / "extract_index.json"
    prev = json.loads(idx.read_text(encoding="utf-8")) if idx.exists() else {}
    prev.update(found)
    idx.write_text(json.dumps(prev, indent=2), encoding="utf-8")
    print("ALL", prev)


if __name__ == "__main__":
    main()
