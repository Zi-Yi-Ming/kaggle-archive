"""EXP-018 优先级 1 最小训练 smoke。

跑同一份 EXP-018 配置(physical Axial, n_clips=6, batch=8),但用真 DICOM
只跑很少的 batch。目的仅限验证 instrumentation 在真实训练环境里工作:

  1. memory logger 有输出(进程树 RSS / 系统内存 / CUDA / nvidia-smi)
  2. checkpoint 能写到磁盘,且 metadata 正确
  3. DataLoader worker 的 RSS 能被采集到
  4. GPU peak 能被采集到

不产出任何 validation 结论,不写 submission,不提交。

用真 DICOM 而不是假张量,因为要验证的正是「真实数据加载路径下的内存行为」:
worker 是否存在、DICOM 解码是否吃内存,假张量测不出来。
"""
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

OUT = "/kaggle/working/_out/smoke1"
N_TRAIN = 48        # 只取 48 个 study,batch=8 → 每 epoch 6 个 batch
N_VAL = 16
N_CLIPS = 6
SAMPLING_MODE = "physical"
# 真实条件 = EXP-018 正式跑的那条命令:rsna_v3.py 未传 --workers → argparse 默认 0。
# smoke 的主证据必须复现这个值,否则测出来的内存结构不代表被验证对象。
WORKERS_MAIN = 0
# H1(CPU RAM)敏感性探测:多 worker 时 worker RSS 是否被计入。
# 这是**辅助**证据,标签独立,不参与「是否复现真实条件」的结论。
WORKERS_PROBE = 2
BATCH = 8
EPOCHS = 1
SEED = 42
MEM_INTERVAL = 5.0  # 采样密一点,保证 smoke 里也能采到多个点


def log(m):
    print(f"[smoke] {m}", flush=True)


def _torch_version_in_subprocess():
    """在独立子进程里探测 torch 版本。

    绝不能在主进程里 import torch 来探测版本:主进程一旦加载过镜像预装的
    2.10.0,pip 换成 2.2.0 之后当前进程仍持有旧模块(文件已删、模块在内存),
    后续代码会继续用旧版;若强行 del sys.modules 再 import,旧 C 扩展已在
    进程内初始化,重新执行 torch/__init__.py 会撞
    RuntimeError: function '_has_torch_function' already has a docstring。
    所以版本探测一律走子进程,主进程等装完再首次 import。
    """
    try:
        r = subprocess.run([sys.executable, "-c",
                            "import torch;print(torch.__version__)"],
                           capture_output=True, text=True, timeout=600)
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if r.returncode != 0:
        tail = (r.stderr or "").strip().splitlines()
        return None, (tail[-1] if tail else "import failed")
    return r.stdout.strip().splitlines()[-1], None


def ensure_torch():
    """装 torch 2.2.0+cu118,并在**子进程**里校验装完的版本。

    真实训练环境是 torch 2.2.0+cu118;镜像预装的是 2.10.0+cu128,用它测出来的
    内存/兼容性行为与真实训练不可比,必须强制替换。返回后主进程才首次 import
    torch,拿到的必然是刚装好的版本。
    """
    pre, _ = _torch_version_in_subprocess()
    log(f"preinstalled torch = {pre}; 强制替换为离线包")

    wh = sorted(glob.glob("/kaggle/input/**/*.whl", recursive=True))
    log(f"mounted wheels = {len(wh)}")
    if len(wh) < 13:
        log("BLOCKED: fewer than 13 offline wheels mounted")
        sys.exit(1)
    fixed = []
    for w in wh:
        base = os.path.basename(w)
        dst = os.path.join("/kaggle/working",
                           base.replace("cu118", "+cu118", 1) if "cu118" in base else base)
        shutil.copy(w, dst)
        fixed.append(dst)
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "-q",
                           "torch", "torchvision", "torchaudio"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                           "--no-deps", "--no-index"] + fixed)
    for f in fixed:
        os.remove(f)

    post, err = _torch_version_in_subprocess()
    log(f"offline torch install done -> torch={post} err={err}")
    if not (post or "").startswith("2.2.0"):
        log(f"BLOCKED: 期望 torch 2.2.0+cu118,实际 {post} {err or ''}")
        sys.exit(1)


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

    import numpy as np
    import pandas as pd
    import torch
    import psutil
    import rsna_v3 as R3

    sha = hashlib.sha256(open(os.path.join(code_dir, "rsna_v3.py"), "rb").read()).hexdigest()
    log(f"rsna_v3.py sha256 = {sha}")
    log(f"python={sys.version.split()[0]} torch={torch.__version__} "
        f"numpy={np.__version__} cuda={torch.cuda.is_available()} "
        f"psutil={'yes' if R3.HAS_PSUTIL else 'no'}")

    root = find_root()
    if root is None:
        log("BLOCKED: competition root not found")
        sys.exit(1)
    log(f"data root = {root}")

    os.environ["EXP013_MULTISOURCE"] = "1"
    labels_df = R3.load_labels(root, pseudo_conf=0.0, use_report_labels=False)
    series_df = pd.read_csv(os.path.join(root, "train_series.csv"))
    train_csv = pd.read_csv(os.path.join(root, "train.csv"))
    dcm_train = os.path.join(root, "train_series")

    ax = series_df[series_df["Anatomical_Plane"].astype(str).str.lower() == "axial"]
    uids = list(dict.fromkeys(ax["StudyInstanceUID"].tolist()))
    log(f"axial studies available = {len(uids)}")
    tr_uids = uids[:N_TRAIN]
    va_uids = uids[N_TRAIN:N_TRAIN + N_VAL]

    class A:
        pass

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log(f"device={device}")

    tr_ds = R3.KneeDataset(tr_uids, labels_df, dcm_train, series_df, "Axial",
                           n_clips=N_CLIPS, sampling_mode=SAMPLING_MODE)
    va_ds = R3.KneeDataset(va_uids, labels_df, dcm_train, series_df, "Axial",
                           n_clips=N_CLIPS, sampling_mode=SAMPLING_MODE)

    # 单变量口径:除 workers 外,两段其它一切相同。段标签独立,结论不混。
    segments = [("main_workers0", WORKERS_MAIN), ("probe_workers2", WORKERS_PROBE)]
    all_checks = {}

    for seg_name, nworkers in segments:
        seg_out = os.path.join(OUT, seg_name)
        os.makedirs(seg_out, exist_ok=True)

        args = A()
        args.epochs = EPOCHS
        args.batch = BATCH
        args.lr = 3e-4
        args.workers = nworkers
        args.n_clips = N_CLIPS
        args.sampling_mode = SAMPLING_MODE
        args.seed = SEED
        args.experiment_id = "exp018_smoke_" + seg_name
        args.max_batches = 6          # 只跑 6 个 batch —— 这是 smoke,不是实验
        args.mem_interval = MEM_INTERVAL
        args.diag_json = os.path.join(seg_out, "mem_smoke.jsonl")
        args.verbose = True

        torch.manual_seed(SEED)
        model = R3.KneeModel(pretrained=False, channels=N_CLIPS * R3.CLIP).to(device)
        R3._CKPT_OVERRIDE["root"] = os.path.join(seg_out, "ckpt")
        art = os.path.join(seg_out, "art", "exp018_smoke")

        log(f"=== [{seg_name}] {len(tr_ds)} train / {len(va_ds)} val, "
            f"workers={nworkers}, max_batches={args.max_batches} ===")
        R3.run_fold(model, tr_ds, va_ds, device, args,
                    artifact_root=art, fold=0, plane="Axial")

        ck_dir = R3._ckpt_dir(art, 0, "Axial")
        ck1 = os.path.join(ck_dir, "epoch1.ckpt")
        diag_path = args.diag_json
        summary_path = diag_path + ".summary.json"

        c = {}
        c["workers_requested"] = nworkers
        c["ckpt_epoch1_exists"] = os.path.isfile(ck1)
        c["ckpt_latest_exists"] = os.path.isfile(os.path.join(ck_dir, "latest.ckpt"))
        c["diag_jsonl_exists"] = os.path.isfile(diag_path)
        c["diag_summary_exists"] = os.path.isfile(summary_path)

        if os.path.isfile(ck1):
            ck = R3._load_ckpt(ck1)
            c["ckpt_epoch_done"] = int(ck["epoch_done"]) == 1
            c["ckpt_has_model"] = "model_state_dict" in ck
            c["ckpt_has_optimizer"] = "optimizer_state_dict" in ck
            c["ckpt_has_scheduler"] = ck.get("scheduler_state_dict") is not None
            c["ckpt_rng_keys"] = sorted(list(ck.get("rng", {}).keys()))
            c["ckpt_runtime"] = ck.get("runtime")
            c["ckpt_config_sampling_mode"] = ck.get("config", {}).get("sampling_mode")
            c["ckpt_config_n_clips"] = ck.get("config", {}).get("n_clips")
            c["ckpt_config_workers"] = ck.get("config", {}).get("workers")
            c["ckpt_has_memory_snapshot"] = ck.get("memory_snapshot") is not None
            c["ckpt_memory_snapshot"] = ck.get("memory_snapshot")
            c["ckpt_steps_per_epoch"] = ck.get("steps_per_epoch")

        if os.path.isfile(diag_path):
            rows = [json.loads(x) for x in
                    open(diag_path, encoding="utf-8").read().strip().splitlines() if x.strip()]
            c["telemetry_n_samples"] = len(rows)
            c["telemetry_has_main_rss"] = any(r.get("main_process_rss_gb", 0) > 0 for r in rows)
            c["telemetry_has_child_rss"] = any(r.get("child_process_rss_gb", 0) > 0 for r in rows)
            c["telemetry_max_n_children"] = max((r.get("n_children", 0) for r in rows), default=0)
            c["telemetry_has_system"] = any(r.get("system_used_pct", 0) > 0 for r in rows)
            c["telemetry_has_cuda_peak"] = any(
                r.get("torch_cuda_max_allocated_gb", 0) > 0 for r in rows)
            c["telemetry_has_nvidia_smi"] = any(
                r.get("gpu_mem_used_mib", 0) > 0 for r in rows)
            c["telemetry_worker_count_recorded"] = rows[0].get("worker_count")
            c["telemetry_peak_process_tree_rss_gb"] = max(
                (r.get("process_tree_rss_gb", 0) for r in rows), default=0)
            c["telemetry_peak_child_rss_gb"] = max(
                (r.get("child_process_rss_gb", 0) for r in rows), default=0)
            c["telemetry_min_system_available_gb"] = min(
                (r.get("system_available_gb", 0) for r in rows), default=0)

        if os.path.isfile(summary_path):
            c["summary"] = json.loads(open(summary_path, encoding="utf-8").read())

        all_checks[seg_name] = c
        log(f"[{seg_name}] SMOKE_CHECKS " + json.dumps(c, ensure_ascii=False, indent=2, default=str))

    # 这台机器上真 DICOM 的 x.shape 断言(EXP-018 定义:18 通道)
    try:
        x, y, v = tr_ds[0]
        log(f"x.shape = {tuple(x.shape)} (期望 [18,224,224])")
        all_checks["x_shape"] = list(x.shape)
    except Exception as exc:
        log(f"x_shape probe failed: {exc}")

    with open(os.path.join(OUT, "smoke_checks.json"), "w") as fh:
        json.dump(all_checks, fh, ensure_ascii=False, indent=2, default=str)

    log(f"DONE wall={time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
