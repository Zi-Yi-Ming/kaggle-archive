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
    # accept agents without literal "def agent" (last-callable entry)
    looks = (b"def " in src and (b"action" in src or b"bid" in src or b"agent" in src.lower()))
    if not looks and b"def agent" not in src:
        print("reject", tag, "len", len(src))
        return None
    if len(src) < 5000:
        print("reject small", tag, len(src))
        return None
    p = OUT / f"{tag}_main.py"
    p.write_bytes(src)
    print("WROTE", p.name, len(src), hashlib.sha256(src).hexdigest()[:16])
    return p


def join_quoted_chunks(blob_region: str) -> str:
    # capture both '...' and "..." chunks (b85 has mixed punct)
    chunks = re.findall(r"[\"']([^\"']+)[\"']", blob_region)
    return "".join(chunks)


def extract_assign_blob(text: str, name: str) -> str | None:
    # NAME = ''.join(( 'a', 'b', ... ))
    m = re.search(
        rf"{re.escape(name)}\s*=\s*['\"]['\"]\.join\(\(([\s\S]*?)\)\)",
        text,
    )
    if m:
        return join_quoted_chunks(m.group(1))
    # NAME = ( 'a'\n 'b'\n )
    m = re.search(rf"{re.escape(name)}\s*=\s*\(([\s\S]*?)\)\s*\n\s*[A-Z_]", text)
    if m:
        return join_quoted_chunks(m.group(1))
    # NAME = "...." single
    m = re.search(rf"{re.escape(name)}\s*=\s*[\"']([A-Za-z0-9+/=]{{200,}})[\"']", text)
    if m:
        return re.sub(r"\s+", "", m.group(1))
    return None


def decode_blob(packed: str):
    if not packed:
        return None
    packed = re.sub(r"\s+", "", packed)
    candidates = []
    # b85
    try:
        raw = base64.b85decode(packed)
        candidates.append(raw)
    except Exception:
        pass
    try:
        raw = base64.b64decode(packed + "=" * (-len(packed) % 4))
        candidates.append(raw)
    except Exception:
        pass
    decoders = [
        lambda b: zlib.decompress(b),
        lambda b: gzip.decompress(b),
        lambda b: lzma.decompress(b),
        lambda b: b,
    ]
    for raw in candidates:
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
    names = (
        "SOURCE_BLOB", "PAYLOAD", "AGENT_B64", "V54_B85", "SOURCE_B85",
        "AGENT_B85", "CODE_B85", "BLOB", "ARCHIVE_BYTES", "SOURCE",
    )
    for name in names:
        packed = extract_assign_blob(full, name)
        if not packed:
            continue
        src = decode_blob(packed)
        if src:
            p = write_main(tag, src)
            if p:
                return p
        else:
            print("decode fail", tag, name, "packed_len", len(packed))
    # any NAME = ''.join(( ... )) that decodes
    for m in re.finditer(r"(\w+)\s*=\s*['\"]['\"]\.join\(\(", full):
        name = m.group(1)
        packed = extract_assign_blob(full, name)
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
        ("v54fork", "v54fork/v54-fork-wins-72-5-head-to-head-against-v54.ipynb"),
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
