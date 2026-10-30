"""诊断:resume 之后模型参数到底有没有被更新。

B(跨 kernel resume)在 Kaggle 上跑完,optimizer 状态变了(step 计数动过),
但模型参数与 resume 起点逐位相同 —— 说明梯度没流到被保存的那组参数。
本脚本在本地复现同一路径,逐步打印参数指纹,定位是「训练没生效」还是
「优化器指向了另一组张量」。

只跑 CPU、假数据,不写 submission,不碰真 DICOM。
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
from torch.utils.data import Dataset  # noqa: E402

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


def make_args(out):
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


def main():
    tmp = tempfile.mkdtemp(prefix="repro_resume_")
    dev = torch.device("cpu")
    N, V = 64, 32

    # ---- 第一步:等价于 Kernel A,跑 1 epoch 写 ckpt ----
    # 关键:A 必须与 B 用同一个 epochs(→ 同一个 scheduler T_max),
    # 否则 sched.step() 会把 lr 归零并写进 ckpt,resume 后 lr=0 训练无效。
    args = make_args(tmp)
    args.epochs = 2
    torch.manual_seed(42)
    m0 = TinyNet().to(dev)
    R3._CKPT_OVERRIDE["root"] = os.path.join(tmp, "ckpt_a")
    art = os.path.join(tmp, "art_a")
    print("[A] 训练前 param_hash =", sd_hash(m0.state_dict()))
    R3.run_fold(m0, FakeDS(N, 0), FakeDS(V, 1), dev, args,
                artifact_root=art, fold=0, plane="Axial")
    h_a1 = sd_hash(m0.state_dict())
    print("[A] 连续跑完 2 epoch 的最终 param_hash =", h_a1)

    ck_dir = R3._ckpt_dir(art, 0, "Axial")
    ck_path = os.path.join(ck_dir, "epoch1.ckpt")
    ck = R3._load_ckpt(ck_path)
    print("[A] ckpt 内 param_hash =", sd_hash(ck["model_state_dict"]))
    print("[A] ckpt 内 optimizer 有 state =", len(ck["optimizer_state_dict"]["state"]))
    print("[A] ckpt 内 lr =", ck["optimizer_state_dict"]["param_groups"][0]["lr"],
          "| scheduler T_max =", ck["scheduler_state_dict"]["T_max"])

    # ---- 第二步:等价于 Kernel B,新对象 + resume ----
    args2 = make_args(tmp)
    args2.epochs = 2
    torch.manual_seed(42)
    m1 = TinyNet().to(dev)
    R3._CKPT_OVERRIDE["root"] = os.path.join(tmp, "ckpt_b")
    art2 = os.path.join(tmp, "art_b")

    print()
    print("[B] resume 前(随机初始化)param_hash =", sd_hash(m1.state_dict()))

    # 手动复刻 run_fold 的 resume 前置步骤,以便逐步观察
    opt = torch.optim.AdamW(m1.parameters(), lr=args2.lr, weight_decay=1e-4)
    opt_ids_before = [id(p) for p in m1.parameters()]
    ck2 = R3._load_ckpt(ck_path, map_location="cpu")
    m1.load_state_dict(ck2["model_state_dict"])
    print("[B] load_state_dict 后 param_hash =", sd_hash(m1.state_dict()))
    opt.load_state_dict(ck2["optimizer_state_dict"])
    opt_ids_after = [id(p) for g in opt.param_groups for p in g["params"]]
    model_ids = [id(p) for p in m1.parameters()]
    print("[B] optimizer 引用的 param id == model 的 param id ?",
          opt_ids_after == model_ids)
    print("[B] 参数 requires_grad 全为 True ?",
          all(p.requires_grad for p in m1.parameters()))

    # 跑一个 epoch,看参数变不变
    R3.run_fold(m1, FakeDS(N, 0), FakeDS(V, 1), dev, args2,
                artifact_root=art2, fold=0, plane="Axial",
                resume_ckpt=ck_path)
    h_b2 = sd_hash(m1.state_dict())
    print("[B] resume 训练后 param_hash =", h_b2)
    print()
    print("A 连续跑完的最终 param_hash :", h_a1)
    print("B resume 后的最终 param_hash:", h_b2)
    print("等价(B == A 连续)           :", h_b2 == h_a1)
    print("B 相对 resume 起点有变化    :", h_b2 != sd_hash(ck["model_state_dict"]))

    ck_b = R3._load_ckpt(os.path.join(R3._ckpt_dir(art2, 0, "Axial"), "epoch2.ckpt"))
    print("B 的 ckpt 内 param_hash:", sd_hash(ck_b["model_state_dict"]))
    print("B ckpt 内 loss         :", ck_b.get("epoch_losses"))


if __name__ == "__main__":
    main()
