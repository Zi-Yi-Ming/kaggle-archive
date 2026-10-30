"""EXP-017 — fold0 validation A/B (single-fold validation comparison)

CONTROL  : EXP-013 legacy Axial fold0
TREATMENT: EXP-016 physical Axial fold0
ONLY VARIABLE: sampling_mode (legacy -> physical)

This is NOT a full OOF. Only fold0 checkpoints exist; validation set is the
882 studies held out by fold0. Nothing is trained, nothing is submitted.

Hard rules enforced in code:
  - no training call is ever made (weights are loaded, optimizer never built)
  - no Kaggle submission is produced
  - both models are evaluated on the identical fold0 validation UID list
  - all variables other than sampling_mode stay frozen
"""

import csv
import hashlib
import json
import os
import sys
import time
import traceback

csv.field_size_limit(10 ** 9)

import numpy as np

WORK = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORK)

OUT_DIR = "/kaggle/working/_out/exp017_oof_ab"
SMOKE_N = 8          # studies used for the smoke gate
TARGET_ORDER = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "PF OA", "Medial OA", "Lateral OA",
    "Effusion", "Synovitis", "Baker's", "Contusion", "Fracture",
]

# CANONICAL_LABELS order as recorded in both experiments' config.json
CANONICAL_LABELS = [
    "ACL", "MCL", "Medial Meniscus", "Lateral Meniscus",
    "Medial OA", "Lateral OA", "PF OA",
    "Effusion", "Synovitis", "Baker's", "Contusion", "Fracture",
]


def log(msg):
    print(f"[exp017] {msg}", flush=True)


# ---------------------------------------------------------------- environment

def find_input_dir():
    """Locate competition data root (contains train.csv + train_series/)."""
    base = "/kaggle/input"
    if not os.path.isdir(base):
        return None
    for sub in sorted(os.listdir(base)):
        for cand in (os.path.join(base, sub), os.path.join(base, sub, sub)):
            if os.path.exists(os.path.join(cand, "train.csv")):
                return cand
        d = os.path.join(base, sub)
        if os.path.isdir(d):
            for sub2 in sorted(os.listdir(d)):
                cand = os.path.join(d, sub2)
                if os.path.exists(os.path.join(cand, "train.csv")):
                    return cand
    return None


def find_weights_dir():
    """Locate uploaded checkpoints. Returns {exp_tag: path}."""
    found = {}
    for sub in sorted(os.listdir("/kaggle/input")):
        d = os.path.join("/kaggle/input", sub)
        if not os.path.isdir(d):
            continue
        for root, _dirs, files in os.walk(d):
            for f in files:
                if not f.endswith(".pt"):
                    continue
                low = root.lower().replace("\\", "/")
                if "exp013" in low or "exp_013" in low:
                    found.setdefault("exp013", os.path.join(root, f))
                elif "exp016" in low or "exp_016" in low:
                    found.setdefault("exp016", os.path.join(root, f))
    return found


def locate_frozen_code():
    """Find the directory holding the frozen rsna_v3.py / sampling_geometry.py.

    Kaggle script kernels only ship `code_file` into /kaggle/src/, so sibling
    modules must arrive via a mounted dataset. Returns the directory or None.
    """
    for sub in sorted(os.listdir("/kaggle/input")):
        d = os.path.join("/kaggle/input", sub)
        if not os.path.isdir(d):
            continue
        for root, _dirs, files in os.walk(d):
            if "rsna_v3.py" in files and "sampling_geometry.py" in files:
                return root
    return None


def locate_fold_assignment(root):
    """Find fold_assignment.csv wherever it was mounted (dataset / working dir).

    It may sit next to the competition data, inside the checkpoints dataset,
    or beside this script — search all of them rather than assuming one path.
    """
    candidates = [os.path.join(root, "fold_assignment.csv"),
                  os.path.join(WORK, "fold_assignment.csv")]
    for sub in sorted(os.listdir("/kaggle/input")):
        d = os.path.join("/kaggle/input", sub)
        if not os.path.isdir(d):
            continue
        for r, _dirs, files in os.walk(d):
            if "fold_assignment.csv" in files:
                candidates.append(os.path.join(r, "fold_assignment.csv"))
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)


def blocked(stage, reason, extra=None):
    payload = {
        "STATUS": "BLOCKED",
        "stage": stage,
        "reason": reason,
    }
    if extra:
        payload.update(extra)
    write_json(os.path.join(OUT_DIR, "STATUS_BLOCKED.json"), payload)
    log(f"STATUS: BLOCKED ({stage}) — {reason}")
    print("\nEXP017_STATUS_BLOCKED")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(0)


# ---------------------------------------------------------------- gate checks

def hard_gate(root, n_expected_total=4407):
    """Re-verify the pre-flight conditions inside the kernel itself."""
    import ast
    import pandas as pd

    train = pd.read_csv(os.path.join(root, "train.csv"))
    n_total = len(train)
    if n_total != n_expected_total:
        blocked("gate:total", f"train.csv has {n_total} studies, expected {n_expected_total}")

    fa_path = locate_fold_assignment(root)
    if fa_path is None:
        blocked("gate:fold_assignment", "fold_assignment.csv not found in any mounted input")
    log(f"gate: fold_assignment = {fa_path}")
    rows = list(csv.DictReader(open(fa_path, encoding="utf-8")))
    if len(rows) != 5:
        blocked("gate:fold_assignment", f"expected 5 folds, found {len(rows)}")

    train_by_fold = {}
    for r in rows:
        train_by_fold[int(r["fold"])] = ast.literal_eval(r["train_uids"])

    n_tr = len(train_by_fold[0])
    n_va = n_total - n_tr
    if n_tr != 3525 or n_va != 882:
        blocked("gate:sizes",
                f"fold0 train={n_tr} val={n_va}, expected 3525/882")

    all_uids = set(train["StudyInstanceUID"].tolist())
    val_uids = [u for u in train["StudyInstanceUID"].tolist()
                if u not in set(train_by_fold[0])]
    if len(val_uids) != n_va:
        blocked("gate:val_uids", f"derived val list {len(val_uids)} != {n_va}")
    if not set(val_uids).issubset(all_uids):
        blocked("gate:val_subset", "val uids not a subset of train.csv")

    uid_hash = hashlib.sha256(
        "\n".join(sorted(val_uids)).encode("utf-8")).hexdigest()

    # checkpoint sampling_mode attribution, read from the uploaded configs
    attrib = {}
    for sub in sorted(os.listdir("/kaggle/input")):
        d = os.path.join("/kaggle/input", sub)
        if not os.path.isdir(d):
            continue
        for root2, _dirs, files in os.walk(d):
            if "config.json" in files:
                try:
                    cfg = json.load(open(os.path.join(root2, "config.json"), encoding="utf-8"))
                except Exception:
                    continue
                eid = str(cfg.get("experiment_id", "")).lower()
                if "013" in eid:
                    attrib["exp013"] = cfg.get("args", {}).get("sampling_mode")
                elif "016" in eid:
                    attrib["exp016"] = cfg.get("args", {}).get("sampling_mode")

    log(f"gate: total={n_total} fold0_train={n_tr} fold0_val={n_va}")
    log(f"gate: val uid_hash={uid_hash[:16]}...")
    log(f"gate: checkpoint sampling attribution={attrib}")
    return train, val_uids, uid_hash, attrib


# ---------------------------------------------------------------- inference

def run_inference(model_path, sampling_mode, val_uids, root, train_csv):
    """Load a checkpoint and predict on the given validation UID list."""
    import torch
    import pandas as pd
    from torch.utils.data import DataLoader
    import rsna_v3 as R3

    # CRITICAL: physical mode silently degrades to legacy index sampling when
    # sampling_geometry failed to import. That would make both arms of the A/B
    # identical and fake a "no difference" result. Refuse to run instead.
    if sampling_mode == "physical" and not getattr(R3, "HAS_SG", False):
        blocked("guard:has_sg",
                "sampling_mode='physical' but rsna_v3.HAS_SG is False — physical "
                "would silently fall back to legacy sampling, invalidating the A/B")
    if not getattr(R3, "HAS_PYDICOM", False):
        blocked("guard:pydicom", "pydicom not importable inside rsna_v3")

    series_df = pd.read_csv(os.path.join(root, "train_series.csv"))
    dcm_root = os.path.join(root, "train_series")

    net = R3.KneeModel(channels=4 * 3, num_labels=len(CANONICAL_LABELS),
                       pretrained=False, offline_paths=None)
    state = torch.load(model_path, map_location="cpu")
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    net.load_state_dict(state)
    net.eval()

    ds = R3.KneeDataset(val_uids, None, dcm_root, series_df, "Axial",
                        has_targets=False, n_clips=4, sampling_mode=sampling_mode)
    # num_workers MUST stay 0: worker processes own their own copy of the
    # dataset, so ds.stats() in this process would silently read zeros.
    # EXP-016 trained with workers=0 as well.
    loader = DataLoader(ds, batch_size=16, shuffle=False, num_workers=0)
    pred = R3.predict(net, loader, torch.device("cpu"))
    hit, empty, avg = ds.stats()
    log(f"  [{sampling_mode}] hit={hit}/{len(val_uids)} empty={empty} avg_clips={avg:.2f} "
        f"shape={pred.shape}")
    return pred, {"hit": hit, "empty": empty, "avg_clips": round(float(avg), 3)}


def probe_dicom(root, uids, sampling_mode, n=2):
    """Directly read DICOM in THIS process and report real pixel content.

    Bypasses DataLoader workers entirely so the measurement cannot be a
    multiprocessing artifact. Returns per-study evidence.
    """
    import pandas as pd
    import rsna_v3 as R3

    series_df = pd.read_csv(os.path.join(root, "train_series.csv"))
    dcm_root = os.path.join(root, "train_series")
    ds = R3.KneeDataset(uids[:n], None, dcm_root, series_df, "Axial",
                        has_targets=False, n_clips=4, sampling_mode=sampling_mode)
    out = []
    for i, uid in enumerate(uids[:n]):
        clips = ds._load_study(uid)
        x, _y, _v = ds[i]
        xa = x.numpy()
        out.append({
            "uid_tail": uid[-12:],
            "n_clips": len(clips),
            "clip_shape": list(clips[0].shape) if clips else None,
            "nonzero_frac": float((xa != 0).mean()),
            "pixel_mean": float(xa.mean()),
            "pixel_max": float(xa.max()),
        })
        log(f"  probe[{sampling_mode}] {uid[-12:]} clips={len(clips)} "
            f"nonzero={out[-1]['nonzero_frac']:.3f} mean={out[-1]['pixel_mean']:.4f} "
            f"max={out[-1]['pixel_max']:.4f}")
    return out


def macro_auc(pred, labels, val_uids):
    """Per-target AUC on gold labels only; macro = mean of computable targets."""
    from sklearn.metrics import roc_auc_score
    import pandas as pd

    labels = labels.set_index("StudyInstanceUID")
    per_target = {}
    for j, name in enumerate(CANONICAL_LABELS):
        y = labels.reindex(val_uids)[name].values.astype(float)
        mask = ~np.isnan(y)
        n_pos = int((y[mask] == 1).sum())
        n_neg = int((y[mask] == 0).sum())
        if n_pos == 0 or n_neg == 0:
            per_target[name] = {"auc": None, "n_pos": n_pos, "n_neg": n_neg,
                                "note": "single-class, AUC undefined"}
            continue
        auc = float(roc_auc_score(y[mask], pred[mask, j]))
        per_target[name] = {"auc": auc, "n_pos": n_pos, "n_neg": n_neg}
    vals = [v["auc"] for v in per_target.values() if v["auc"] is not None]
    macro = float(np.mean(vals)) if vals else None
    return macro, per_target


# ---------------------------------------------------------------- main

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t_start = time.time()

    root = find_input_dir()
    if root is None:
        blocked("env:data", "competition data (train.csv) not found under /kaggle/input")
    log(f"data root = {root}")

    if not os.path.exists(os.path.join(root, "train_series.csv")):
        blocked("env:data", "train_series.csv missing at data root")
    if not os.path.isdir(os.path.join(root, "train_series")):
        blocked("env:data", "train_series/ DICOM directory missing at data root")

    # Record the real on-disk layout so a DICOM failure is diagnosable from the log.
    dcm_probe_root = os.path.join(root, "train_series")
    try:
        lvl1 = sorted(os.listdir(dcm_probe_root))[:3]
        log(f"train_series/ first entries = {lvl1}")
        if lvl1:
            p1 = os.path.join(dcm_probe_root, lvl1[0])
            if os.path.isdir(p1):
                lvl2 = sorted(os.listdir(p1))[:3]
                log(f"train_series/{lvl1[0]}/ first entries = {lvl2}")
                if lvl2:
                    p2 = os.path.join(p1, lvl2[0])
                    if os.path.isdir(p2):
                        lvl3 = sorted(os.listdir(p2))[:3]
                        log(f"train_series/{lvl1[0]}/{lvl2[0]}/ first entries = {lvl3}")
                        log(f"  -> .dcm count at this level = "
                            f"{sum(1 for f in os.listdir(p2) if f.lower().endswith('.dcm'))}")
    except OSError as exc:
        log(f"train_series listing failed: {exc}")

    weights = find_weights_dir()
    log(f"weights found = {weights}")
    for tag in ("exp013", "exp016"):
        if tag not in weights:
            blocked("env:weights", f"{tag} checkpoint not found under /kaggle/input")

    # ---- frozen code must be importable before any inference ----
    code_dir = locate_frozen_code()
    if code_dir is None:
        blocked("env:code",
                "frozen code (rsna_v3.py + sampling_geometry.py) not found under "
                "/kaggle/input — script kernels do not ship sibling modules")
    sys.path.insert(0, code_dir)
    log(f"frozen code dir = {code_dir}")

    import rsna_v3 as _R3
    code_sha = {}
    for fname in ("rsna_v3.py", "sampling_geometry.py"):
        p = os.path.join(code_dir, fname)
        code_sha[fname] = hashlib.sha256(open(p, "rb").read()).hexdigest()
        log(f"  {fname} sha256={code_sha[fname][:16]}...")
    log(f"  HAS_SG={getattr(_R3, 'HAS_SG', None)} "
        f"HAS_PYDICOM={getattr(_R3, 'HAS_PYDICOM', None)} "
        f"HAS_TORCH={getattr(_R3, 'HAS_TORCH', None)}")

    # Expected shas recorded by EXP-016 at training time (see exp016_config.json)
    EXPECTED_SHA = {
        "rsna_v3.py": "cf878311dbeaa75b4ded03d9b70f97866ff6a4d66be8f618d4c7505ac83a7111",
        "sampling_geometry.py": "eb7fd2cd27efc905f46095338aefd989953b4cac697e1958e1190cfa783842d0",
    }
    for fname, exp in EXPECTED_SHA.items():
        if code_sha[fname] != exp:
            blocked("gate:code_sha",
                    f"{fname} sha256={code_sha[fname]} != training-time {exp} — "
                    "preprocessing would not match the checkpoints")
    log("gate: frozen code sha256 matches EXP-016 training-time code")

    for tag, path in weights.items():
        h = hashlib.sha256(open(path, "rb").read()).hexdigest()
        sz = os.path.getsize(path)
        log(f"  {tag}: {path} size={sz} sha256={h[:16]}...")
        weights[tag] = {"path": path, "size": sz, "sha256": h}

    # ---- HARD GATE ----
    train_csv, val_uids, uid_hash, attrib = hard_gate(root)

    if attrib.get("exp016") != "physical":
        blocked("gate:attribution",
                f"EXP-016 config sampling_mode={attrib.get('exp016')!r}, expected 'physical'")
    if attrib.get("exp013") not in (None, "legacy"):
        blocked("gate:attribution",
                f"EXP-013 config sampling_mode={attrib.get('exp013')!r}, expected None/'legacy'")

    # ---- SMOKE GATE ----
    log(f"=== SMOKE TEST on {SMOKE_N} validation studies ===")
    smoke_uids = val_uids[:SMOKE_N]
    smoke = {}
    try:
        # 1) direct main-process DICOM probe — real pixels, no worker indirection
        for mode in ("legacy", "physical"):
            probe = probe_dicom(root, val_uids, mode, n=2)
            smoke[f"probe_{mode}"] = probe
            if any(p["n_clips"] == 0 for p in probe):
                blocked("smoke:dicom_probe",
                        f"{mode}: 0 clips read in main process — genuine DICOM failure")
            if any(p["nonzero_frac"] == 0.0 for p in probe):
                blocked("smoke:dicom_probe",
                        f"{mode}: clips read but tensor is all zeros — decode failure")

        # 2) end-to-end smoke through the model
        for tag, mode in (("exp013", "legacy"), ("exp016", "physical")):
            pred, ds_stat = run_inference(weights[tag]["path"], mode,
                                          smoke_uids, root, train_csv)
            if pred.shape != (SMOKE_N, 12):
                blocked("smoke:shape", f"{tag} smoke output {pred.shape}, expected ({SMOKE_N}, 12)")
            if not np.isfinite(pred).all():
                blocked("smoke:nan", f"{tag} smoke output contains NaN/Inf")
            smoke[tag] = {"shape": list(pred.shape), "ds": ds_stat,
                          "pred_head": np.round(pred[0], 4).tolist()}
            if ds_stat["hit"] != SMOKE_N:
                blocked("smoke:dicom",
                        f"{tag} read {ds_stat['hit']}/{SMOKE_N} studies — DICOM read failure")
    except SystemExit:
        raise
    except Exception as exc:
        traceback.print_exc()
        blocked("smoke:exception", f"{type(exc).__name__}: {exc}")

    write_json(os.path.join(OUT_DIR, "smoke.json"), smoke)
    log("smoke gate PASS")

    # ---- FULL RUN ----
    log(f"=== FULL RUN on {len(val_uids)} validation studies ===")
    results = {}
    for tag, mode, key in (("exp013", "legacy", "legacy"), ("exp016", "physical", "physical")):
        log(f"--- {key} ({tag}) ---")
        t0 = time.time()
        try:
            pred, ds_stat = run_inference(weights[tag]["path"], mode, val_uids, root, train_csv)
        except Exception as exc:
            traceback.print_exc()
            blocked(f"full:{key}", f"{type(exc).__name__}: {exc}")
        if pred.shape != (len(val_uids), 12):
            blocked(f"full:{key}", f"output {pred.shape}, expected ({len(val_uids)}, 12)")
        if not np.isfinite(pred).all():
            blocked(f"full:{key}", "output contains NaN/Inf")
        macro, per_target = macro_auc(pred, train_csv, val_uids)
        runtime = time.time() - t0
        results[key] = {"pred": pred, "macro": macro, "per_target": per_target,
                        "runtime": runtime, "ds": ds_stat}
        log(f"  {key} macro AUC = {macro}  ({runtime:.0f}s)")

        os.makedirs(os.path.join(OUT_DIR, key), exist_ok=True)
        np.save(os.path.join(OUT_DIR, key, "val_pred.npy"), pred)
        write_json(os.path.join(OUT_DIR, key, "target_auc.json"), {
            "sampling_mode": mode,
            "checkpoint": weights[tag],
            "macro_auc": macro,
            "per_target": per_target,
            "runtime_sec": runtime,
            "dataset_stats": ds_stat,
        })

    # ---- COMPARISON ----
    a, b = results["legacy"]["pred"], results["physical"]["pred"]
    corr = float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
    per_target_cmp = {}
    for name in CANONICAL_LABELS:
        la = results["legacy"]["per_target"][name]
        pb = results["physical"]["per_target"][name]
        delta = (None if (la["auc"] is None or pb["auc"] is None)
                 else float(pb["auc"] - la["auc"]))
        j = CANONICAL_LABELS.index(name)
        per_target_cmp[name] = {
            "legacy_auc": la["auc"], "physical_auc": pb["auc"], "delta": delta,
            "n_pos": la["n_pos"], "n_neg": la["n_neg"],
            "legacy_pred_mean": float(a[:, j].mean()),
            "legacy_pred_std": float(a[:, j].std()),
            "physical_pred_mean": float(b[:, j].mean()),
            "physical_pred_std": float(b[:, j].std()),
            "pred_mean_delta": float(b[:, j].mean() - a[:, j].mean()),
        }

    deltas = [v["delta"] for v in per_target_cmp.values() if v["delta"] is not None]
    macro_delta = None
    if results["legacy"]["macro"] is not None and results["physical"]["macro"] is not None:
        macro_delta = float(results["physical"]["macro"] - results["legacy"]["macro"])

    comparison = {
        "experiment": "EXP-017",
        "name": "fold0 validation A/B",
        "type": "single-fold validation comparison",
        "not_a_full_oof": True,
        "note": ("Only fold0 checkpoints exist. This is a single-fold validation "
                 "comparison on 882 held-out studies, NOT a complete OOF."),
        "validation_fold": 0,
        "validation_studies": len(val_uids),
        "fold0_train_studies": 3525,
        "total_studies": 4407,
        "only_changed_variable": "sampling_mode",
        "legacy_macro_auc": results["legacy"]["macro"],
        "physical_macro_auc": results["physical"]["macro"],
        "delta": macro_delta,
        "per_target_auc": {
            k: {"legacy": v["legacy_auc"], "physical": v["physical_auc"]}
            for k, v in per_target_cmp.items()
        },
        "per_target_delta": {k: v["delta"] for k, v in per_target_cmp.items()},
        "per_target_detail": per_target_cmp,
        "per_target_prediction_delta": {
            k: v["pred_mean_delta"] for k, v in per_target_cmp.items()
        },
        "prediction_correlation": corr,
        "prediction_mean": float(b.mean()),
        "prediction_std": float(b.std()),
        "legacy_prediction_mean": float(a.mean()),
        "legacy_prediction_std": float(a.std()),
        "per_target_prediction_mean_std": {
            k: {"legacy_mean": v["legacy_pred_mean"], "legacy_std": v["legacy_pred_std"],
                "physical_mean": v["physical_pred_mean"], "physical_std": v["physical_pred_std"]}
            for k, v in per_target_cmp.items()
        },
        "uid_hash": uid_hash,
        "target_order": CANONICAL_LABELS,
        "reported_target_order": TARGET_ORDER,
        "delta_summary": {
            "n_targets_compared": len(deltas),
            "n_improved": sum(1 for d in deltas if d > 0),
            "n_degraded": sum(1 for d in deltas if d < 0),
            "min_delta": min(deltas) if deltas else None,
            "max_delta": max(deltas) if deltas else None,
            "mean_delta": float(np.mean(deltas)) if deltas else None,
        },
        "checkpoints": {k: weights[k] for k in ("exp013", "exp016")},
        "frozen_code_sha256": code_sha,
        "frozen_code_dir": code_dir,
        "dataset_stats": {k: results[k]["ds"] for k in results},
        "runtime_sec": {k: results[k]["runtime"] for k in results},
        "total_runtime_sec": time.time() - t_start,
        "gpu_used": False,
        "trained": False,
        "submitted": False,
    }
    write_json(os.path.join(OUT_DIR, "comparison.json"), comparison)

    log("=== DONE ===")
    print("\nEXP017_STATUS")
    print(json.dumps({
        "status": "COMPLETE",
        "validation_studies": len(val_uids),
        "legacy_macro_auc": comparison["legacy_macro_auc"],
        "physical_macro_auc": comparison["physical_macro_auc"],
        "delta": comparison["delta"],
        "prediction_correlation": corr,
        "delta_summary": comparison["delta_summary"],
        "total_runtime_sec": comparison["total_runtime_sec"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
