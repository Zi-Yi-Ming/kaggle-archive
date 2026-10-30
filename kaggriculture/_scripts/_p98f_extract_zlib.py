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
    if b"def agent" not in src or len(src) < 5000:
        print("reject", tag, "len", len(src), "has_agent", b"def agent" in src)
        return None
    p = OUT / f"{tag}_main.py"
    p.write_bytes(src)
    print("WROTE", p.name, len(src), hashlib.sha256(src).hexdigest()[:16])
    return p


def concat_string_after(text: str, name: str) -> str | None:
    """NAME = (\\n  \"a\"\\n  \"b\"\\n) or NAME = \"...\" or NAME = r'''...'''"""
    m = re.search(rf"{re.escape(name)}\s*=\s*\(([\s\S]*?)\)\s*\n", text)
    if m:
        chunks = re.findall(r"[\"']([A-Za-z0-9+/=\s]+)[\"']", m.group(1))
        if chunks:
            return "".join(re.sub(r"\s+", "", c) for c in chunks)
    m = re.search(rf"{re.escape(name)}\s*=\s*[\"']([A-Za-z0-9+/=]{{200,}})[\"']", text)
    if m:
        return re.sub(r"\s+", "", m.group(1))
    m = re.search(rf"{re.escape(name)}\s*=\s*[r]?[\"']{{3}}([\s\S]+?)[\"']{{3}}", text)
    if m:
        body = m.group(1)
        if "def agent" in body and len(body) > 5000:
            return body  # plain source
        if re.fullmatch(r"[A-Za-z0-9+/=\s]+", body[:200] + body[-50:] if body else ""):
            return re.sub(r"\s+", "", body)
        # concatenated quoted chunks inside
        chunks = re.findall(r"[\"']([A-Za-z0-9+/=]{20,})[\"']", body)
        if chunks:
            return "".join(chunks)
    return None


def decode_payload(packed_or_src):
    if packed_or_src is None:
        return None
    if "def agent" in packed_or_src and len(packed_or_src) > 5000:
        return packed_or_src.encode("utf-8")
    packed = re.sub(r"\s+", "", packed_or_src)
    try:
        raw = base64.b64decode(packed)
    except Exception:
        return None
    for dec in (
        lambda b: gzip.decompress(b),
        lambda b: zlib.decompress(b),
        lambda b: lzma.decompress(b),
        lambda b: b,
    ):
        try:
            out = dec(raw)
        except Exception:
            continue
        if b"def agent" in out and len(out) > 5000:
            return out
    return None


def extract_named_b64(text: str, tag: str, names):
    for name in names:
        packed = concat_string_after(text, name)
        src = decode_payload(packed) if packed else None
        if src:
            return write_main(tag, src)
    return None


def extract(tag: str, rel: str):
    chunks = cells_of(rel)
    full = "\n".join(s for _, s in chunks)
    # 1) AGENT_B64 / MAIN payload
    p = extract_named_b64(full, tag, ("AGENT_B64", "SOURCE_B64", "PAYLOAD", "SOURCE_BLOB", "ARCHIVE_B64", "CODE_B64", "MAIN_B64", "B64", "blob"))
    if p:
        return p
    # 2) any b64decode('...') long string
    for m in re.finditer(r"b64decode\(\s*[\"']([A-Za-z0-9+/=]{200,})[\"']", full):
        src = decode_payload(m.group(1))
        if src:
            return write_main(tag, src)
    # 3) concat assignment to something then b64decode
    for m in re.finditer(r"(\w+)\s*=\s*\(\s*\n(\s*[\"'][A-Za-z0-9+/=]{20,}[\"']\s*\n)+", full):
        name = m.group(1)
        packed = concat_string_after(full, name)
        src = decode_payload(packed) if packed else None
        if src:
            return write_main(tag, src)
    # 4) triple-quoted source with def agent
    for m in re.finditer(r"[r]?[\"']{3}([\s\S]{8000,}?)[\"']{3}", full):
        if "def agent" in m.group(1):
            return write_main(tag, m.group(1).encode("utf-8"))
    # 5) %%writefile main.py
    for _, src in chunks:
        if "%%writefile" in src and "main.py" in src and "def agent" in src:
            text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", src)
            return write_main(tag, text.encode("utf-8"))
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
    # keep pipe18/19 if already there
    idx = OUT / "extract_index.json"
    prev = {}
    if idx.exists():
        import json as _j
        prev = _j.loads(idx.read_text(encoding="utf-8"))
    prev.update(found)
    idx.write_text(json.dumps(prev, indent=2), encoding="utf-8")
    print("ALL", prev)


if __name__ == "__main__":
    main()
