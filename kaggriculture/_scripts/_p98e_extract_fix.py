from pathlib import Path
import json
import re
import base64
import gzip
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
    if b"def agent" not in src or len(src) < 5000:
        return None
    p = OUT / f"{tag}_main.py"
    p.write_bytes(src)
    print("WROTE", p.name, len(src), hashlib.sha256(src).hexdigest()[:16])
    return p


def extract_concat_b64(text: str) -> bytes | None:
    """AGENT_B64 = (\\n    \"chunk\"\\n    \"chunk\"\\n)"""
    m = re.search(r"AGENT_B64\s*=\s*\(([\s\S]*?)\)", text)
    if not m:
        # maybe single string
        m = re.search(r"AGENT_B64\s*=\s*[\"']([A-Za-z0-9+/=]{200,})[\"']", text)
        if not m:
            return None
        packed = re.sub(r"\s+", "", m.group(1))
    else:
        chunks = re.findall(r"[\"']([A-Za-z0-9+/=]+)[\"']", m.group(1))
        packed = "".join(chunks)
    try:
        raw = base64.b64decode(packed)
    except Exception as e:
        print("b64 fail", e)
        return None
    if raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except Exception as e:
            print("gz fail", e)
            return None
    return raw


def extract_pipe(tag: str, rel: str):
    for i, (ct, src) in enumerate(cells_of(rel)):
        if "AGENT_B64" in src:
            raw = extract_concat_b64(src)
            if raw:
                return write_main(tag, raw)
    return None


def extract_path_write(tag: str, rel: str):
    """v55/v56: MAIN = Path(...) and source written via %%writefile or Path.write_*."""
    full = []
    for i, (ct, src) in enumerate(cells_of(rel)):
        full.append(src)
        if "%%writefile" in src and "main.py" in src and "def agent" in src:
            text = re.sub(r"(?m)^%%writefile[^\n]*\n", "", src)
            p = write_main(tag, text.encode("utf-8"))
            if p:
                return p
        # MAIN.write_text / Path('main.py').write_text(<big string>)
        if "def agent" in src and len(src) > 8000 and ct == "code":
            # maybe the cell itself is the agent source
            if src.strip().startswith(("import ", "from ", "#", "\"\"\"", "'''", "from __future__")):
                # heuristic: agent cells usually define agent and don't only pack
                if "tarfile" not in src[:500] and "AGENT_B64" not in src:
                    p = write_main(tag, src.encode("utf-8"))
                    if p:
                        return p
    text = "\n".join(full)
    # Path('xxx/main.py').write_text / write_bytes of a variable
    m = re.search(
        r"(?:MAIN|main_py|agent_path|OUT_MAIN)\s*=\s*([^\n]+)",
        text,
    )
    # look for write_text of triple quote near end
    for m in re.finditer(r"[r]?[\"']{3}([\s\S]{8000,}?)[\"']{3}", text):
        if "def agent" in m.group(1):
            p = write_main(tag, m.group(1).encode("utf-8"))
            if p:
                return p
    # literal assignment main = '''...'''
    for name in ("main", "MAIN", "source", "SOURCE", "agent", "AGENT", "code", "CODE", "data"):
        m = re.search(rf"(?m)^{name}\s*=\s*[r]?[\"']{{3}}([\s\S]+?)[\"']{{3}}", text)
        if m and "def agent" in m.group(1):
            p = write_main(tag, m.group(1).encode("utf-8"))
            if p:
                return p
        m = re.search(rf"{name}\s*=\s*[r]?[\"']{{3}}([\s\S]+?)[\"']{{3}}", text)
        if m and "def agent" in m.group(1) and len(m.group(1)) > 5000:
            p = write_main(tag, m.group(1).encode("utf-8"))
            if p:
                return p
    return None


def inspect():
    for tag, rel in [
        ("pipe18", "pipe18/kaggriculture-pipe18-six-layers.ipynb"),
        ("pipe19", "pipe19/kaggriculture-pipe19-sale-advance-overflow.ipynb"),
        ("v55", "v55/kaggriculture-v55-one-turn-market-race-edge.ipynb"),
        ("v56", "v56/kaggriculture-v56-smarter-seeds-and-fertilizer.ipynb"),
        ("v54leak", "v54leak/92-vs-the-best-public-farm-a-seed-leak-in-v54.ipynb"),
        ("v54fork", "v54fork/v54-fork-wins-72-5-head-to-head-against-v54.ipynb"),
        ("orderbook", "orderbook/your-market-list-is-an-order-book.ipynb"),
    ]:
        print("========", tag)
        for i, (ct, src) in enumerate(cells_of(rel)):
            marks = [k for k in (
                "AGENT_B64", "MAIN", "def agent", "write_text", "write_bytes",
                "%%writefile", "source =", "main =", "Path(", "gzip.decompress",
            ) if k in src]
            head = src[:100].replace("\n", " ")
            print(f"  [{i}] {ct} len={len(src)} marks={marks} :: {head}")


def main():
    inspect()
    found = {}
    for tag, rel, kind in [
        ("pipe18", "pipe18/kaggriculture-pipe18-six-layers.ipynb", "pipe"),
        ("pipe19", "pipe19/kaggriculture-pipe19-sale-advance-overflow.ipynb", "pipe"),
        ("v55", "v55/kaggriculture-v55-one-turn-market-race-edge.ipynb", "path"),
        ("v56", "v56/kaggriculture-v56-smarter-seeds-and-fertilizer.ipynb", "path"),
        ("v54leak", "v54leak/92-vs-the-best-public-farm-a-seed-leak-in-v54.ipynb", "path"),
        ("v54fork", "v54fork/v54-fork-wins-72-5-head-to-head-against-v54.ipynb", "path"),
    ]:
        print("==== EXTRACT", tag, kind)
        p = extract_pipe(tag, rel) if kind == "pipe" else extract_path_write(tag, rel)
        if p:
            found[tag] = str(p)
        else:
            print("FAIL", tag)
    (OUT / "extract_index.json").write_text(json.dumps(found, indent=2), encoding="utf-8")
    print("FOUND", found)


if __name__ == "__main__":
    main()
