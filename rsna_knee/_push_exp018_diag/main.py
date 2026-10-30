"""EXP-018 MEMORY DIAGNOSTIC (CPU + GPU)

Answers, with measurements rather than inference:
  - how much system RAM does the clip cache actually consume?
  - does the cache hold clips that __getitem__ never uses?
  - does CPU RSS grow linearly with the number of studies touched?
  - what is the GPU memory high-water mark?
  - what is the host's real total RAM (never measured before)?

Does NOT train. Reads at most N_STUDIES studies. Nothing is written to the
competition. No submission is produced.
"""

import gc
import json
import os
import sys
import time

N_STUDIES = 300
SNAP_EVERY = 100
N_CLIPS = 6
SAMPLING_MODE = "physical"
OUT = "/kaggle/working/_out/exp018_diag"


def log(msg):
    print(f"[diag] {msg}", flush=True)


def locate_code():
    for sub in sorted(os.listdir("/kaggle/input")):
        d = os.path.join("/kaggle/input", sub)
        if not os.path.isdir(d):
            continue
        for root, _dirs, files in os.walk(d):
            if "rsna_v3.py" in files and "sampling_geometry.py" in files:
                return root
    return None


def find_root():
    def rec(b, depth=0, maxd=4):
        if depth > maxd or not os.path.isdir(b):
            return None
        try:
            ents = sorted(os.listdir(b))
        except OSError:
            return None
        if "train.csv" in ents and os.path.isdir(os.path.join(b, "train_series")):
            return b
        for e in ents:
            r = rec(os.path.join(b, e), depth + 1, maxd)
            if r:
                return r
        return None
    return rec("/kaggle/input")


def ensure_torch():
    """Install torch 2.2.0+cu118 from the offline wheel dataset.

    Replicated from the EXP-016/018 training notebook so the diagnostic runs
    in the identical environment. Without torch, rsna_v3.KneeDataset is not
    even defined (it lives inside `if HAS_TORCH:`).
    """
    import glob
    import shutil
    import subprocess
    try:
        import torch  # noqa: F401
        log("torch already importable; skipping offline install")
        return
    except ImportError:
        pass
    wh = sorted(glob.glob("/kaggle/input/**/*.whl", recursive=True))
    log(f"mounted wheels = {len(wh)}")
    if len(wh) < 13:
        log("BLOCKED: fewer than 13 offline wheels mounted")
        sys.exit(1)
    fixed = []
    for w in wh:
        base = os.path.basename(w)
        dst = os.path.join(
            "/kaggle/working",
            base.replace("cu118", "+cu118", 1) if "cu118" in base else base)
        shutil.copy(w, dst)
        fixed.append(dst)
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "-q",
                           "torch", "torchvision", "torchaudio"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                           "--no-deps", "--no-index"] + fixed)
    for f in fixed:
        os.remove(f)
    log("offline torch install done")


def main():
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    ensure_torch()

    code_dir = locate_code()
    if code_dir is None:
        log("BLOCKED: frozen code not found")
        sys.exit(1)
    sys.path.insert(0, code_dir)
    log(f"code dir = {code_dir}")

    import psutil
    import numpy as np
    import pandas as pd
    import torch
    import rsna_v3 as R3

    proc = psutil.Process()
    has_cuda = torch.cuda.is_available()

    log(f"python={sys.version.split()[0]} torch={torch.__version__} "
        f"numpy={np.__version__} cuda={has_cuda}")
    if has_cuda:
        log(f"gpu={torch.cuda.get_device_name(0)} "
            f"vram_gb={torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f}")

    def snap(tag):
        vm = psutil.virtual_memory()
        d = {
            "tag": tag,
            "t_sec": round(time.time() - t0, 1),
            "cpu_rss_gb": round(proc.memory_info().rss / 1024**3, 3),
            "sys_total_gb": round(vm.total / 1024**3, 2),
            "sys_available_gb": round(vm.available / 1024**3, 2),
            "sys_used_pct": vm.percent,
        }
        if has_cuda:
            d.update({
                "gpu_alloc_gb": round(torch.cuda.memory_allocated() / 1024**3, 3),
                "gpu_reserved_gb": round(torch.cuda.memory_reserved() / 1024**3, 3),
                "gpu_max_alloc_gb": round(torch.cuda.max_memory_allocated() / 1024**3, 3),
                "gpu_max_reserved_gb": round(torch.cuda.max_memory_reserved() / 1024**3, 3),
            })
        log("SNAP " + json.dumps(d))
        return d

    root = find_root()
    if root is None:
        log("BLOCKED: competition root not found")
        sys.exit(1)
    log(f"data root = {root}")

    snaps = [snap("baseline")]

    series_df = pd.read_csv(os.path.join(root, "train_series.csv"))
    dcm_root = os.path.join(root, "train_series")

    ax = series_df[series_df["Anatomical_Plane"].astype(str).str.lower() == "axial"]
    uids = list(dict.fromkeys(ax["StudyInstanceUID"].tolist()))
    log(f"axial studies available = {len(uids)}")
    uids = uids[:N_STUDIES]

    ds = R3.KneeDataset(uids, None, dcm_root, series_df, "Axial",
                        has_targets=False, n_clips=N_CLIPS,
                        sampling_mode=SAMPLING_MODE)
    snaps.append(snap("dataset_init"))

    clip_shape = None
    for i, uid in enumerate(uids, 1):
        x, _y, _v = ds[i - 1]
        if clip_shape is None:
            clip_shape = list(x.shape)
        if i % SNAP_EVERY == 0:
            snaps.append(snap(f"studies_{i}"))
            log(f"  processed {i} studies, x_shape={clip_shape}")

    snaps.append(snap("after_300_studies"))

    # ---- cache semantics ----
    cache = ds.cache
    n_entries = len(cache)
    per_study_clips = [len(v) for v in cache.values()]
    total_clips = int(sum(per_study_clips))
    total_bytes = int(sum(c.nbytes for v in cache.values() for c in v))
    used_clips = int(sum(min(len(v), N_CLIPS) for v in cache.values()))
    clip_nbytes = None
    for v in cache.values():
        if v:
            clip_nbytes = v[0].nbytes
            break
    used_bytes = int(used_clips * clip_nbytes) if clip_nbytes else 0

    def pct(a, p):
        return float(np.percentile(a, p)) if a else None

    cache_stats = {
        "n_cache_entries": n_entries,
        "clips_per_study_P50": pct(per_study_clips, 50),
        "clips_per_study_P90": pct(per_study_clips, 90),
        "clips_per_study_P95": pct(per_study_clips, 95),
        "clips_per_study_max": int(max(per_study_clips)) if per_study_clips else 0,
        "total_clips_cached": total_clips,
        "clip_nbytes": clip_nbytes,
        "total_cache_bytes": total_bytes,
        "total_cache_gb": round(total_bytes / 1024**3, 3),
        "clips_actually_used": used_clips,
        "used_bytes": used_bytes,
        "used_gb": round(used_bytes / 1024**3, 3),
        "wasted_bytes": total_bytes - used_bytes,
        "wasted_gb": round((total_bytes - used_bytes) / 1024**3, 3),
        "cache_holds_more_than_used": total_clips > used_clips,
        "n_clips": N_CLIPS,
    }
    log("CACHE_STATS " + json.dumps(cache_stats, indent=2))

    # ---- extrapolation to the full fold ----
    per_study_bytes = (total_bytes / n_entries) if n_entries else 0
    extrap = {
        "measured_studies": n_entries,
        "bytes_per_study": int(per_study_bytes),
        "projected_gb_fold0_train_3525": round(per_study_bytes * 3525 / 1024**3, 2),
        "projected_gb_fold0_train_plus_val_4407": round(per_study_bytes * 4407 / 1024**3, 2),
        "projected_gb_used_only_4407": round(
            (used_bytes / n_entries if n_entries else 0) * 4407 / 1024**3, 2),
        "host_total_ram_gb": round(psutil.virtual_memory().total / 1024**3, 2),
    }
    log("EXTRAPOLATION " + json.dumps(extrap, indent=2))

    # ---- GPU memory under the real training shapes ----
    gpu_probe = None
    if has_cuda:
        try:
            torch.cuda.reset_peak_memory_stats()
            net = R3.KneeModel(channels=N_CLIPS * 3, num_labels=12,
                               pretrained=False, offline_paths=None).cuda()
            net.train()
            opt = torch.optim.AdamW(net.parameters(), lr=3e-4)
            crit = torch.nn.BCEWithLogitsLoss(reduction="none")
            xb = torch.randn(8, N_CLIPS * 3, 224, 224, device="cuda")
            yb = torch.zeros(8, 12, device="cuda")
            out = net(xb)
            loss = crit(out, yb).mean()
            loss.backward()
            opt.step()
            gpu_probe = {
                "batch": 8,
                "channels": N_CLIPS * 3,
                "alloc_gb": round(torch.cuda.memory_allocated() / 1024**3, 3),
                "reserved_gb": round(torch.cuda.memory_reserved() / 1024**3, 3),
                "max_alloc_gb": round(torch.cuda.max_memory_allocated() / 1024**3, 3),
                "max_reserved_gb": round(torch.cuda.max_memory_reserved() / 1024**3, 3),
                "vram_total_gb": round(
                    torch.cuda.get_device_properties(0).total_memory / 1024**3, 2),
            }
            log("GPU_PROBE " + json.dumps(gpu_probe, indent=2))
            del net, opt, xb, yb, out, loss
            gc.collect()
            torch.cuda.empty_cache()
        except Exception as exc:
            gpu_probe = {"error": f"{type(exc).__name__}: {exc}"}
            log("GPU_PROBE FAILED " + json.dumps(gpu_probe))

    snaps.append(snap("end"))

    report = {
        "experiment": "EXP-018 memory diagnostic",
        "n_clips": N_CLIPS,
        "sampling_mode": SAMPLING_MODE,
        "studies_processed": n_entries,
        "clip_tensor_shape": clip_shape,
        "snapshots": snaps,
        "cache_stats": cache_stats,
        "extrapolation": extrap,
        "gpu_probe": gpu_probe,
        "total_sec": round(time.time() - t0, 1),
    }
    with open(os.path.join(OUT, "memory_diag.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    log("DONE -> " + os.path.join(OUT, "memory_diag.json"))


if __name__ == "__main__":
    main()
