"""EXP-018 优先级 2 的本地等价性验证(CPU,不依赖 Kaggle)。

验证三件事,全部以「行为」为准,不以「文件存在」为准:
  A. checkpoint 写后读回:model / optimizer / scheduler / epoch / global_step
     逐项一致(数值级,不是键存在级)。
  B. RNG 快照/恢复:恢复后产生的随机数与快照前严格一致。
  C. resume 轨迹等价:连续跑 2 epoch 的结果 vs 「跑 1 epoch→存→新进程读回→跑
     第 2 epoch」的结果,比较 loss / 参数 hash / optimizer 状态。

C 是本测试的核心。它用的是真 Loss + 真 AdamW + 真 DataLoader(shuffle=True)
+ 真 Dropout,不简化,否则测不出 RNG 消费顺序这类问题。

跑法:
    python tests/test_ckpt_resume_equivalence.py
退出码 0 = 全部通过,1 = 有失败。
"""
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import rsna_v3 as R3  # noqa: E402


class ToyDS(Dataset):
    """确定性假数据集:n_clips=6 × 3 通道 = 18ch,224×224,12 标签。"""

    def __init__(self, n=32, seed=0):
        g = torch.Generator().manual_seed(seed)
        self.x = torch.randn(n, 18, 224, 224, generator=g)
        self.y = torch.rand(n, 12, generator=g)
        self.valid = torch.ones(n, 12)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, i):
        return self.x[i], self.y[i], self.valid[i]


class ToyNet(nn.Module):
    """带 Dropout 的极小网络:没有 Dropout 就测不出 RNG 消费顺序。"""

    def __init__(self):
        super().__init__()
        self.c = nn.Conv2d(18, 8, 3, stride=8)
        self.drop = nn.Dropout(0.3)
        self.head = nn.Linear(8, 12)

    def forward(self, x):
        x = torch.relu(self.c(x)).mean(dim=(2, 3))
        return self.head(self.drop(x))


class Args:
    def __init__(self, epochs=2, batch=8, lr=3e-4, workers=0, n_clips=6,
                 experiment_id="resume_test", max_batches=0, mem_interval=999,
                 seed=42):
        self.epochs = epochs
        self.batch = batch
        self.lr = lr
        self.workers = workers
        self.n_clips = n_clips
        self.experiment_id = experiment_id
        self.max_batches = max_batches
        self.mem_interval = mem_interval
        self.diag_json = ""
        self.verbose = True
        self.seed = seed


def _one_epoch(model, ds, args, opt, crit, device, epoch, start_step,
               order_out=None):
    """复刻 rsna_v3.train_epoch 的核心路径,loader 走 rsna_v3._epoch_loader。"""
    model.train()
    if order_out is not None:
        order_out[epoch] = R3.probe_loader_order(ds, args, epoch)
    loader = R3._epoch_loader(ds, args, epoch, shuffle=True)
    tot, cnt, gstep = 0.0, 0, int(start_step)
    for x, y, valid in loader:
        x, y, valid = x.to(device), y.to(device), valid.to(device)
        opt.zero_grad()
        out = model(x)
        w = 2.0 * (y - 0.5).abs()
        loss = (crit(out, y) * valid * w).sum() / (valid * w).sum().clamp(min=1e-6)
        loss.backward()
        opt.step()
        tot += loss.item() * len(x)
        cnt += len(x)
        gstep += 1
    del loader
    return tot / max(cnt, 1), gstep


def _build(seed, args, ds_seed=0):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    model = ToyNet()
    opt = AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    sched = CosineAnnealingLR(opt, T_max=args.epochs)
    ds = ToyDS(n=32, seed=ds_seed)
    crit = nn.BCEWithLogitsLoss(reduction="none")
    return model, opt, sched, ds, crit


def run_continuous(args, device, ckpt_path=None):
    """连续跑 args.epochs 个 epoch;可选在第 1 个 epoch 后存 ckpt。"""
    model, opt, sched, ds, crit = _build(args.seed, args)
    gstep = 0
    losses = []
    order = {}
    for ep in range(args.epochs):
        loss, gstep = _one_epoch(model, ds, args, opt, crit, device, ep, gstep,
                                 order_out=order)
        sched.step()
        losses.append(loss)
        if ckpt_path is not None and ep == 0:
            R3._save_ckpt_verified(ckpt_path, model, opt, sched, ep + 1, gstep,
                                   args, None, 0, "toy",
                                   extra={"steps_per_epoch": {"0": gstep}})
    return model, opt, losses, gstep, order


def run_resumed(args, device, ckpt_path):
    """只读 ckpt → 恢复全部状态 → 从 epoch_done 继续跑到 args.epochs。

    顺序严格对齐 run_fold:
      建 model/opt/sched/ds → load_state_dict → 恢复 epoch/step → 恢复 RNG
      → 循环内建 loader(走 global RNG)
    禁止「先恢复 RNG 再初始化 model」—— model init 会消费 RNG。
    """
    ck = R3._load_ckpt(ckpt_path)

    model = ToyNet()
    model.load_state_dict(ck["model_state_dict"])
    opt = AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    opt.load_state_dict(ck["optimizer_state_dict"])
    sched = CosineAnnealingLR(opt, T_max=args.epochs)
    sched.load_state_dict(ck["scheduler_state_dict"])
    ds = ToyDS(n=32, seed=0)
    crit = nn.BCEWithLogitsLoss(reduction="none")

    gstep = int(ck["global_step"])
    start_ep = int(ck["epoch_done"])

    torch.manual_seed(0)  # 故意打乱,验证 _restore_rng 真的覆盖了它
    ok = R3._restore_rng(ck["rng"])
    assert ok, "RNG 恢复失败"

    losses = []
    order = {}
    for ep in range(start_ep, args.epochs):
        loss, gstep = _one_epoch(model, ds, args, opt, crit, device, ep, gstep,
                                 order_out=order)
        sched.step()
        losses.append(loss)
    return model, opt, losses, gstep, order


def _opt_flat(opt):
    vals = []
    for st in opt.state.values():
        for k, v in st.items():
            if torch.is_tensor(v):
                vals.append(v.detach().float().cpu().reshape(-1))
    return torch.cat(vals) if vals else torch.zeros(1)


def main():
    torch.manual_seed(0)
    device = torch.device("cpu")
    args = Args()
    tmp = Path(tempfile.mkdtemp(prefix="ckptresume_"))
    ck = tmp / "epoch1.ckpt"
    results = {}

    # ---- A + B:写后读回一致性 ----
    model, opt, sched, ds, crit = _build(args.seed, args)
    gstep = 0
    loss1, gstep = _one_epoch(model, ds, args, opt, crit, device, 0, gstep)
    sched.step()
    R3._save_ckpt_verified(ck, model, opt, sched, 1, gstep, args, None, 0, "toy",
                           extra={"steps_per_epoch": {"0": gstep}})
    back = R3._load_ckpt(ck)
    for k in ("model_state_dict", "optimizer_state_dict", "scheduler_state_dict",
              "rng", "runtime", "config"):
        results[f"ckpt_has_{k}"] = k in back
    results["ckpt_epoch_done"] = int(back["epoch_done"]) == 1
    results["ckpt_global_step"] = int(back["global_step"]) == gstep
    sd = model.state_dict()
    results["ckpt_weights_bitwise_equal"] = all(
        torch.equal(sd[k].float(), back["model_state_dict"][k].float()) for k in sd)

    # optimizer 状态逐张量比对(AdamW 的 exp_avg / exp_avg_sq / step)
    ost_a = opt.state_dict()["state"]
    ost_b = back["optimizer_state_dict"]["state"]
    results["ckpt_optimizer_roundtrip"] = (
        set(ost_a.keys()) == set(ost_b.keys())
        and all(
            torch.equal(ost_a[k][t].float(), ost_b[k][t].float())
            for k in ost_a for t in ost_a[k] if torch.is_tensor(ost_a[k][t])
        )
        and all(
            ost_a[k][t] == ost_b[k][t]
            for k in ost_a for t in ost_a[k] if not torch.is_tensor(ost_a[k][t])
        )
    )
    results["ckpt_scheduler_roundtrip"] = (
        json.dumps({k: str(v) for k, v in sched.state_dict().items()})
        == json.dumps({k: str(v) for k, v in back["scheduler_state_dict"].items()}))

    # RNG 快照/恢复
    random.seed(11)
    np.random.seed(11)
    torch.manual_seed(11)
    snap = R3._rng_state()
    expect = (random.random(), float(np.random.rand()), float(torch.rand(1)))
    R3._restore_rng(snap)
    got = (random.random(), float(np.random.rand()), float(torch.rand(1)))
    results["rng_snapshot_restore"] = all(
        abs(a - b) < 1e-12 for a, b in zip(expect, got))

    # ---- shuffle 语义:必须与 EXP-016 原版一致(无自定义 generator) ----
    from torch.utils.data import RandomSampler, SequentialSampler
    loader = R3._epoch_loader(ds, args, 0, shuffle=True)
    results["loader_uses_no_custom_generator"] = (loader.generator is None)
    results["loader_uses_random_sampler"] = isinstance(loader.sampler, RandomSampler)
    loader_seq = R3._epoch_loader(ds, args, 0, shuffle=False)
    results["loader_val_uses_sequential_sampler"] = isinstance(
        loader_seq.sampler, SequentialSampler)
    del loader, loader_seq

    # ---- C:resume 轨迹等价(核心闸门)----
    ck2 = tmp / "traj_epoch1.ckpt"
    cmodel, copt, closses, cstep, corder = run_continuous(args, device, ckpt_path=None)
    _, _, cont_losses, cont_step, _ = run_continuous(args, device, ckpt_path=ck2)
    rmodel, ropt, res_losses, res_step, rorder = run_resumed(args, device, ck2)

    # run_continuous 跑两次必须自身一致 —— 否则测的是不可复现的训练,不是 resume
    results["baseline_self_consistent"] = (
        R3._model_param_hash(cmodel) == R3._model_param_hash(
            run_continuous(args, device, ckpt_path=None)[0])
        and abs(closses[1] - cont_losses[1]) < 1e-9)

    # loader order hash:continuous 与 resumed 的 epoch 1 必须逐位一致。
    # 不接受「都是随机 shuffle 所以等价」这种论证。
    results["loader_order_hash_continuous_ep1"] = corder.get(1, ("", 0))[0][:16]
    results["loader_order_hash_resumed_ep1"] = rorder.get(1, ("", 0))[0][:16]
    results["loader_order_equal"] = (
        corder.get(1, ("", 0))[0] == rorder.get(1, ("", 0))[0]
        and corder.get(1, ("", 0))[1] > 0)

    results["trajectory_epoch2_loss_equal"] = (
        abs(res_losses[0] - closses[1]) < 1e-9)
    results["trajectory_global_step_equal"] = (res_step == cstep)
    results["trajectory_param_hash_equal"] = (
        R3._model_param_hash(rmodel) == R3._model_param_hash(cmodel))
    results["trajectory_optimizer_equal"] = all(
        torch.equal(a[1][t].float(), b[1][t].float())
        for a, b in zip(sorted(copt.state_dict()["state"].items()),
                        sorted(ropt.state_dict()["state"].items()))
        for t in a[1] if torch.is_tensor(a[1][t]))

    results["loss_continuous_ep1"] = round(closses[0], 9)
    results["loss_continuous_ep2"] = round(closses[1], 9)
    results["loss_resumed_ep2"] = round(res_losses[0], 9)
    results["loss_delta"] = abs(res_losses[0] - closses[1])

    print(json.dumps(results, indent=2, ensure_ascii=False))

    gate = all([
        results["ckpt_epoch_done"],
        results["ckpt_global_step"],
        results["ckpt_weights_bitwise_equal"],
        results["ckpt_optimizer_roundtrip"],
        results["ckpt_scheduler_roundtrip"],
        results["rng_snapshot_restore"],
        results["loader_uses_no_custom_generator"],
        results["loader_uses_random_sampler"],
        results["loader_val_uses_sequential_sampler"],
        results["baseline_self_consistent"],
        results["loader_order_equal"],
        results["trajectory_epoch2_loss_equal"],
        results["trajectory_global_step_equal"],
        results["trajectory_param_hash_equal"],
        results["trajectory_optimizer_equal"],
    ])
    print("RESUME_GATE =", "PASS" if gate else "FAIL")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
