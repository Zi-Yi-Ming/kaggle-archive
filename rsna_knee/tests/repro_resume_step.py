"""诊断第二步:resume 之后手动跑一个 batch,看梯度到底有没有产生。

对同一份 ckpt 做两条路径:
  P1 全新初始化 → load_state_dict → 训练一步
  P2 全新初始化 → 训练一步(不 load)
比较两条路径的 grad 范数与参数变化。
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
from torch.utils.data import DataLoader, Dataset  # noqa: E402

import rsna_v3 as R3  # noqa: E402


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


def mkargs():
    a = A()
    a.epochs = 2
    a.batch = 8
    a.lr = 3e-4
    a.workers = 0
    a.n_clips = 6
    a.seed = 42
    a.experiment_id = "repro"
    a.max_batches = 0
    a.mem_interval = 30
    a.diag_json = ""
    a.verbose = True
    a.loader_order_probe = False
    return a


def sd_hash(sd):
    import hashlib
    h = hashlib.sha256()
    for name, p in sorted(sd.items()):
        h.update(name.encode())
        h.update(p.detach().float().cpu().contiguous().view(-1).tolist().__repr__().encode())
    return h.hexdigest()[:16]


def one_step(model, opt, crit, loader, dev, tag):
    model.train()
    opt.zero_grad()
    x, y, valid = next(iter(loader))
    x, y, valid = x.to(dev), y.to(dev), valid.to(dev)
    out = model(x)
    print(f"  [{tag}] out.requires_grad={out.requires_grad} "
          f"out.grad_fn={type(out.grad_fn).__name__ if out.grad_fn else None}")
    w = 2.0 * (y - 0.5).abs()
    denom = (valid * w).sum()
    loss = (crit(out, y) * valid * w).sum() / denom.clamp(min=1e-6)
    print(f"  [{tag}] loss={loss.item():.6f} requires_grad={loss.requires_grad}")
    loss.backward()
    n_with_grad = 0
    gnorm = 0.0
    for n, p in model.named_parameters():
        if p.grad is not None:
            n_with_grad += 1
            gnorm += float((p.grad.detach() ** 2).sum())
    print(f"  [{tag}] 有梯度的参数数={n_with_grad}/{sum(1 for _ in model.parameters())} "
          f"grad_L2={gnorm ** 0.5:.6e}")
    before = {n: p.detach().clone() for n, p in model.named_parameters()}
    opt.step()
    moved = [n for n, p in model.named_parameters()
             if not torch.equal(before[n], p.detach())]
    print(f"  [{tag}] opt.step 后发生变化的参数: {moved if moved else '（无）'}")
    return moved


def main():
    tmp = tempfile.mkdtemp(prefix="repro_step_")
    dev = torch.device("cpu")
    N, V = 64, 32
    ds = FakeDS(N, 0)
    crit = nn.BCEWithLogitsLoss(reduction="none")

    # --- 造一个 ckpt(等价 Kernel A) ---
    args = mkargs()
    args.epochs = 1
    torch.manual_seed(42)
    m0 = TinyNet().to(dev)
    R3._CKPT_OVERRIDE["root"] = os.path.join(tmp, "ck_a")
    art = os.path.join(tmp, "art_a")
    R3.run_fold(m0, FakeDS(N, 0), FakeDS(V, 1), dev, args,
                artifact_root=art, fold=0, plane="Axial")
    ck_path = os.path.join(R3._ckpt_dir(art, 0, "Axial"), "epoch1.ckpt")
    ck = R3._load_ckpt(ck_path)
    print("ckpt param_hash =", sd_hash(ck["model_state_dict"]))
    print()

    loader = DataLoader(ds, batch_size=8, shuffle=True, num_workers=0)

    print("=== P1: 初始化 → load_state_dict → 一步 ===")
    torch.manual_seed(42)
    m1 = TinyNet().to(dev)
    opt1 = torch.optim.AdamW(m1.parameters(), lr=3e-4, weight_decay=1e-4)
    m1.load_state_dict(ck["model_state_dict"])
    opt1.load_state_dict(ck["optimizer_state_dict"])
    print("  load 后 param_hash =", sd_hash(m1.state_dict()))
    one_step(m1, opt1, crit, loader, dev, "P1")
    print("  一步后 param_hash =", sd_hash(m1.state_dict()))
    print()

    print("=== P2: 初始化 → 直接一步(不 load) ===")
    torch.manual_seed(42)
    m2 = TinyNet().to(dev)
    opt2 = torch.optim.AdamW(m2.parameters(), lr=3e-4, weight_decay=1e-4)
    print("  初始 param_hash =", sd_hash(m2.state_dict()))
    one_step(m2, opt2, crit, loader, dev, "P2")
    print("  一步后 param_hash =", sd_hash(m2.state_dict()))


if __name__ == "__main__":
    main()
