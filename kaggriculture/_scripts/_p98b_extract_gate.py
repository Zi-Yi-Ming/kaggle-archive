"""P98b: extract agents from new notebooks and dual-gate vs Metav4 + shop."""
from __future__ import annotations

import base64
import gzip
import json
import re
import sys
import tarfile
import zlib
from pathlib import Path

ROOT = Path(r"D:\桌面\Kaggle\kaggriculture")
SCAN = ROOT / "_external" / "scan_p98_new"
OUT = ROOT / "_external" / "scan_p98_new" / "extracted"
OUT.mkdir(parents=True, exist_ok=True)

# Pull extra high-label kernels into SCAN first if missing
EXTRA = [
    ("haideptry/the-2965-master-hybrid-engine", "hy2965"),
    ("haideptry/the-2950-peak-farm", "peak2950"),
    ("evgendvorkin/kaggriculture", "evgen"),
    ("dmitriigluzdov/kaggriculture-more-wheat-smarter-sales", "dmitrii_wheat"),
    ("leoprovorov/a-song-of-ice-and-fire-fixed-flexible", "icefire"),
    ("xuanzhang001/kaggriculture-auto-top1", "autotop1"),
]


def pull_extras():
    import subprocess

    for slug, name in EXTRA:
        dest = SCAN / name
        if dest.exists() and any(dest.glob("*.ipynb")):
            print("skip", name)
            continue
        dest.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(
            ["kaggle", "kernels", "pull", slug, "-p", str(dest), "-m"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        print("pull", name, "ok" if r.returncode == 0 else r.stderr[-200:])


def cell_sources(nb_path: Path) -> list[str]:
    data = json.loads(nb_path.read_text(encoding="utf-8"))
    out = []
    for cell in data.get("cells", []):
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        out.append(src)
    return out


def try_unpack_b64_payload(text: str, out_dir: Path, tag: str) -> Path | None:
    """Find base64 tar.gz / gzip of main.py or submission.tar.gz."""
    # submission.tar.gz write patterns
    m = re.search(
        r'(?:submission|raw|blob|payload|archive|tgz|code)\s*=\s*(?:base64\.b64decode|bytes\.fromhex)\(\s*["\']([A-Za-z0-9+/=\s]{200,})["\']',
        text,
    )
    if m:
        raw = re.sub(r"\s+", "", m.group(1))
        try:
            blob = base64.b64decode(raw)
        except Exception:
            return None
        return _save_blob(blob, out_dir, tag)

    # gzip.decompress(b64)
    m = re.search(
        r"gzip\.decompress\(\s*(?:base64\.b64decode|zlib\.decompress)?\(\s*[\"']([A-Za-z0-9+/=\s]{200,})[\"']",
        text,
    )
    if m:
        raw = re.sub(r"\s+", "", m.group(1))
        try:
            blob = base64.b64decode(raw)
            if blob[:2] == b"\x1f\x8b":
                blob = gzip.decompress(blob)
        except Exception:
            return None
        return _save_blob(blob, out_dir, tag)

    # direct triple-quoted main.py
    m = re.search(
        r'(?:MAIN|AGENT|SOURCE|main_py|agent_src|code)\s*=\s*r?["\']{3}([\s\S]{500,}?)["\']{3}',
        text,
    )
    if m and ("def agent" in m.group(1) or "class " in m.group(1) or "def bid" in m.group(1)):
        p = out_dir / f"{tag}_inline_main.py"
        p.write_text(m.group(1), encoding="utf-8")
        print("inline", p.name, len(m.group(1)))
        return p

    # tarfile write of main.py as text near end — capture SOURCE if assigned
    m = re.search(
        r"Path\([\"']main\.py[\"']\)\.write_text\(([\s\S]{20,80}?)\)",
        text,
    )
    return None


def _save_blob(blob: bytes, out_dir: Path, tag: str) -> Path | None:
    # is tar.gz?
    if blob[:2] == b"\x1f\x8b":
        try:
            tar_bytes = gzip.decompress(blob)
        except Exception:
            tar_bytes = blob
    else:
        tar_bytes = blob
    # try tar
    try:
        import io

        with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:*") as tf:
            names = tf.getnames()
            print(tag, "tar names", names[:12])
            for n in names:
                if n.endswith("main.py") or n.endswith("agent.py") or n == "main.py":
                    member = tf.getmember(n)
                    f = tf.extractfile(member)
                    if f:
                        data = f.read()
                        p = out_dir / f"{tag}_main.py"
                        p.write_bytes(data)
                        print("wrote", p, len(data))
                        return p
            # extract all py
            for n in names:
                if n.endswith(".py"):
                    f = tf.extractfile(tf.getmember(n))
                    if f:
                        p = out_dir / f"{tag}_{Path(n).name}"
                        p.write_bytes(f.read())
            return out_dir / f"{tag}_main.py" if (out_dir / f"{tag}_main.py").exists() else None
    except Exception:
        pass
    # plain python source
    if b"def " in tar_bytes[:5000] or b"class " in tar_bytes[:5000]:
        p = out_dir / f"{tag}_raw.py"
        p.write_bytes(tar_bytes)
        print("raw py", p, len(tar_bytes))
        return p
    return None


def extract_nb(nb_path: Path, tag: str) -> Path | None:
    texts = cell_sources(nb_path)
    full = "\n\n".join(texts)
    p = try_unpack_b64_payload(full, OUT, tag)
    if p:
        return p
    # write all cells for manual / secondary extract
    dump = OUT / f"{tag}_all_cells.txt"
    dump.write_text(full, encoding="utf-8")
    print("dump only", dump.name, "chars", len(full))
    return None


def main():
    pull_extras()
    found = {}
    for nb in sorted(SCAN.rglob("*.ipynb")):
        tag = nb.parent.name
        if tag == "extracted":
            continue
        print("====", tag, nb.name)
        try:
            p = extract_nb(nb, tag)
        except Exception as e:
            print("ERR", tag, e)
            p = None
        if p:
            found[tag] = str(p)
    print("FOUND", found)
    (OUT / "extract_index.json").write_text(json.dumps(found, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
