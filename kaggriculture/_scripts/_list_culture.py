from pathlib import Path
base = Path(r"D:\桌面\Kaggle")
for p in base.iterdir():
    if "ulture" in p.name and p.is_dir():
        ok = (p / "reference_agents" / "fallow_finn.py").exists()
        codes = " ".join(f"{ord(c):x}" for c in p.name)
        print(ok, len(p.name), codes)
