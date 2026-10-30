from pathlib import Path
import io
import tarfile

p = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\extracted\pilk_econ.py")
raw = p.read_bytes()
print("raw", len(raw), raw[:20], flush=True)

# try tar
for mode in ("r:*", "r:", "r:gz"):
    try:
        tf = tarfile.open(fileobj=io.BytesIO(raw), mode=mode)
        names = tf.getnames()
        print("tar", mode, names[:20], flush=True)
        for n in names:
            if n.endswith("main.py") or n.endswith(".py"):
                data = tf.extractfile(n).read()
                out = Path(r"D:\桌面\Kaggle\kaggriculture\_external\scan_burst\extracted") / ("pilk_" + Path(n).name)
                out.write_bytes(data)
                print("extracted", out, len(data), flush=True)
        break
    except Exception as e:
        print("tar", mode, type(e).__name__, e, flush=True)
