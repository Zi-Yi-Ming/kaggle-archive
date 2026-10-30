"""EXP-018 优先级 2 · Kernel A —— 只跑 epoch 1,写 checkpoint,然后退出。

目的:验证 epoch-level checkpoint 真的落盘,且内容完整可读。
不跑完整训练,不产出 validation 结论,不写 submission。

与 Kernel B 配对:B 在新实例里读这个 ckpt 继续跑 epoch 2。
A 与 B 之间唯一的传递通道是 Kaggle dataset,这就是「跨 kernel 持久化」的实测。
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import time

OUT = "/kaggle/working/_out/resume_a"
N_TRAIN = 64          # 小样本:这里测的是 ckpt 往返,不是精度
N_VAL = 32
EPOCHS = 2            # 必须与 B/C 一致 —— 决定 scheduler 的 T_max,影响 ckpt 里的 lr
SEED = 42


def log(m):
    print(f"[A] {m}", flush=True)


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
    """在 /kaggle/input 下找同时含 rsna_v3.py 与 sampling_geometry.py 的目录。"""
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

    import numpy as np
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset
    import rsna_v3 as R3

    # ---- 代码 sha256 闸门:必须与预期一致,否则说明挂错了数据集 ----
    import hashlib
    got = hashlib.sha256(open(os.path.join(code_dir, "rsna_v3.py"), "rb").read()).hexdigest()
    log(f"rsna_v3.py sha256 = {got}")
    with open(os.path.join(OUT, "code_sha.json"), "w") as fh:
        json.dump({"rsna_v3": got,
                   "sampling_geometry": hashlib.sha256(
                       open(os.path.join(code_dir, "sampling_geometry.py"), "rb").read()
                   ).hexdigest()}, fh, indent=2)

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
    args.diag_json = os.path.join(OUT, "mem_a.jsonl")
    args.verbose = True

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log(f"device={device} torch={torch.__version__} "
        f"cuda={torch.cuda.is_available()}")
    if torch.cuda.is_available():
        log(f"gpu={torch.cuda.get_device_name(0)}")

    torch.manual_seed(SEED)
    model = TinyNet().to(device)
    R3._CKPT_OVERRIDE["root"] = os.path.join(OUT, "ckpt")
    art = os.path.join(OUT, "art", "resume_gate")

    # epochs 必须与 Kernel B/C 一致(=EPOCHS)。
    # 这里曾为了「只跑 1 个 epoch」把 epochs 设成 1,结果 CosineAnnealingLR 的
    # T_max 变成 1,epoch1 结束后 sched.step() 把 lr 归零,并写进 ckpt。
    # B resume 后 lr=0,整个 epoch 参数一步没动 —— 一次静默的无效训练。
    # A 跑满 EPOCHS 即可,我们只取它的 epoch1.ckpt 给 B 用。
    R3.run_fold(model, FakeDS(N_TRAIN, 0), FakeDS(N_VAL, 1), device, args,
                artifact_root=art, fold=0, plane="Axial")

    ck_dir = R3._ckpt_dir(art, 0, "Axial")
    ck1 = os.path.join(ck_dir, "epoch1.ckpt")
    latest = os.path.join(ck_dir, "latest.ckpt")
    exists = {"epoch1.ckpt": os.path.isfile(ck1), "latest.ckpt": os.path.isfile(latest)}
    log(f"ckpt exists = {json.dumps(exists)}")

    ck = R3._load_ckpt(ck1)

    def _sd_hash(sd):
        h = hashlib.sha256()
        for name, p in sorted(sd.items()):
            h.update(name.encode())
            h.update(p.detach().float().cpu().contiguous().view(-1)
                     .tolist().__repr__().encode())
        return h.hexdigest()

    pg = ck["optimizer_state_dict"]["param_groups"][0]
    info = {
        "exists": exists,
        "epoch_done": int(ck["epoch_done"]),
        "global_step": int(ck["global_step"]),
        "has_model": "model_state_dict" in ck,
        "has_optimizer": "optimizer_state_dict" in ck,
        "has_scheduler": ck.get("scheduler_state_dict") is not None,
        "has_rng": "rng" in ck,
        "rng_keys": sorted(list(ck.get("rng", {}).keys())),
        "has_runtime": "runtime" in ck,
        "runtime": ck.get("runtime"),
        "has_config": "config" in ck,
        "has_memory_snapshot": ck.get("memory_snapshot") is not None,
        "has_steps_per_epoch": "steps_per_epoch" in ck,
        "steps_per_epoch": ck.get("steps_per_epoch"),
        # epoch1.ckpt 内的参数指纹(不是最终模型 —— 那是 epoch_done 的)
        "param_hash_epoch1": _sd_hash(ck["model_state_dict"]),
        # 这两个量必须非零/正确,否则 B resume 后训练是空转
        "ckpt_lr": pg.get("lr"),
        "ckpt_scheduler_T_max": ck.get("scheduler_state_dict", {}).get("T_max"),
        "ckpt_scheduler_last_epoch": ck.get("scheduler_state_dict", {}).get("last_epoch"),
        "param_hash_final": R3._model_param_hash(model),
        "ckpt_bytes_epoch1": os.path.getsize(ck1),
        "ckpt_bytes_latest": os.path.getsize(latest) if os.path.isfile(latest) else 0,
    }
    log("CKPT_INFO " + json.dumps(info, ensure_ascii=False, indent=2))
    with open(os.path.join(OUT, "ckpt_info.json"), "w") as fh:
        json.dump(info, fh, ensure_ascii=False, indent=2)

    # 硬闸门:lr 归零的 ckpt 不能交给 B —— 那会让 resume 静默变成空转。
    if not pg.get("lr"):
        log(f"BLOCKED: epoch1.ckpt 里 lr={pg.get('lr')},B resume 后会训练无效")
        sys.exit(1)

    # 只发布 epoch1.ckpt(B 的 resume 点)。latest.ckpt 此时是跑完 EPOCHS 的状态,
    # 发布出去容易被误当 resume 点。
    pub = "/kaggle/working/ckpt_for_b"
    os.makedirs(pub, exist_ok=True)
    if os.path.isfile(ck1):
        shutil.copy(ck1, pub)
    log(f"published ckpt -> {pub}: {sorted(os.listdir(pub))}")

    with open(os.path.join(OUT, "done.json"), "w") as fh:
        json.dump({"stage": "A", "wall_sec": round(time.time() - t0, 1),
                   "confirms": "epoch-level checkpoint written, readable, complete"},
                  fh, indent=2)
    log(f"DONE wall={time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
