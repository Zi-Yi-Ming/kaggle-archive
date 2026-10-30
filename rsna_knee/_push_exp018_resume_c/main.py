"""EXP-018 优先级 2 · Kernel C —— 连续训练基线(Run C)。

同一份假数据、同一 seed,一口气跑完 epoch 1 → epoch 2,不重启。
用来给 Kernel B 提供对照:B 从 A 的 ckpt 续训,若最终参数 hash 与 C 不一致
就说明 resume 不等价,RESUME_GATE = FAIL。

与 Kernel B 必须使用完全相同的模型定义、数据、超参。任何一处不同都会让
比对失去意义。
"""
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

OUT = "/kaggle/working/_out/resume_c"
N_TRAIN = 64
N_VAL = 32
EPOCHS = 2
SEED = 42


def log(m):
    print(f"[C] {m}", flush=True)


def ensure_torch():
    try:
        import torch  # noqa: F401
        log("torch already importable")
        return
    except ImportError:
        pass
    wh = sorted(glob.glob("/kaggle/input/**/*.whl", recursive=True))
    log(f"mounted wheels = {len(wh)}")
    if len(wh) < 13:
        log("BLOCKED: fewer than 13 offline wheels")
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
    log("offline torch install done")


def locate_code():
    for sub in sorted(os.listdir("/kaggle/input")):
        d = os.path.join("/kaggle/input", sub)
        if not os.path.isdir(d):
            continue
        for root, _dirs, files in os.walk(d):
            if "rsna_v3.py" in files and "sampling_geometry.py" in files:
                return root
    return None


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

    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset
    import rsna_v3 as R3

    got = hashlib.sha256(open(os.path.join(code_dir, "rsna_v3.py"), "rb").read()).hexdigest()
    log(f"rsna_v3.py sha256 = {got}")

    class FakeDS(Dataset):
        def __init__(self, n, seed):
            g = torch.Generator().manual_seed(seed)
            self.x = torch.randn(n, 18, 224, 224, generator=g)
            self.y = torch.rand(n, 12, generator=g)
            self.valid = torch.ones(n, 12)
            self.studies = [f"s{i}" for i in range(n)]
            self.n_clips = 6

        def __len__(self):
            return len(self.x)

        def __getitem__(self, i):
            return self.x[i], self.y[i], self.valid[i]

        def stats(self):
            return len(self), 0, 6.0

    class TinyNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.c = nn.Conv2d(18, 8, 3, stride=16)
            self.drop = nn.Dropout(0.2)
            self.head = nn.Linear(8, 12)

        def forward(self, x):
            return self.head(self.drop(torch.relu(self.c(x)).mean(dim=(2, 3))))

    class A:
        pass

    args = A()
    args.epochs = EPOCHS
    args.batch = 8
    args.lr = 3e-4
    args.workers = 0
    args.n_clips = 6
    args.seed = SEED
    args.experiment_id = "resume_gate"
    args.max_batches = 0
    args.mem_interval = 30
    args.diag_json = os.path.join(OUT, "mem_c.jsonl")
    args.verbose = True
    args.loader_order_probe = True

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log(f"device={device} torch={torch.__version__}")
    torch.manual_seed(SEED)
    model = TinyNet().to(device)
    R3._CKPT_OVERRIDE["root"] = os.path.join(OUT, "ckpt")
    art = os.path.join(OUT, "art", "resume_gate")

    R3.run_fold(model, FakeDS(N_TRAIN, 0), FakeDS(N_VAL, 1), device, args,
                artifact_root=art, fold=0, plane="Axial")

    ck_dir = R3._ckpt_dir(art, 0, "Axial")
    latest = R3._load_ckpt(os.path.join(ck_dir, "latest.ckpt"))

    opt_sd = latest["optimizer_state_dict"]
    oh = hashlib.sha256()
    for k in sorted(opt_sd["state"].keys()):
        st = opt_sd["state"][k]
        for f in sorted(st.keys()):
            v = st[f]
            if hasattr(v, "detach"):
                oh.update(v.detach().float().cpu().contiguous().view(-1).numpy().tobytes())
            else:
                oh.update(str(v).encode())
    opt_hash = oh.hexdigest()

    summ_path = args.diag_json + ".summary.json"
    loader_orders = None
    if os.path.isfile(summ_path):
        try:
            with open(summ_path) as fh:
                loader_orders = json.load(fh).get("loader_order_hashes")
        except Exception as exc:
            log(f"read summary failed: {exc}")

    info = {
        "role": "continuous_baseline",
        "epoch_done": int(latest["epoch_done"]),
        "global_step": int(latest["global_step"]),
        "param_hash_final": R3._model_param_hash(model),
        "optimizer_state_hash": opt_hash,
        "rng_keys": sorted(list(latest.get("rng", {}).keys())),
        "epoch_losses": [round(float(x), 9) for x in latest.get("epoch_losses", [])],
        "steps_per_epoch": latest.get("steps_per_epoch"),
        "loader_order_hashes": loader_orders,
        "code_sha_rsna_v3": got,
        "seed": SEED,
        "n_train": N_TRAIN,
        "batch": args.batch,
        "epochs": EPOCHS,
        "runtime": R3._runtime_info(),
    }
    log("C_RESULT " + json.dumps(info, ensure_ascii=False, indent=2))
    with open(os.path.join(OUT, "c_result.json"), "w") as fh:
        json.dump(info, fh, ensure_ascii=False, indent=2)
    log(f"DONE wall={time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
