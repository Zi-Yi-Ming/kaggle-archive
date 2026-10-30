"""端到端验证:直接调用 rsna_v3.run_fold,验证 checkpoint 落盘 + resume 真跑通。

与 test_ckpt_resume_equivalence.py 的区别:那份测的是 RNG/optimizer 等价性,
这份测的是「不 mock,真走 run_fold 这个函数」。用假 Dataset 替换 KneeDataset
(不需要 DICOM),其余全真:真 AdamW、真 CosineAnnealingLR、真 BCE、
真 DataLoader、真 checkpoint、真 MemLogger。
"""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import rsna_v3 as R3  # noqa: E402


class FakeDS(Dataset):
    """冒充 KneeDataset:只需 __len__ / __getitem__ / studies / stats()。"""

    def __init__(self, n, seed=0):
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
        return len(self), 0, float(self.n_clips)


class TinyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.c = nn.Conv2d(18, 8, 3, stride=16)
        self.drop = nn.Dropout(0.2)
        self.head = nn.Linear(8, 12)

    def forward(self, x):
        return self.head(self.drop(torch.relu(self.c(x)).mean(dim=(2, 3))))


class A:
    def __init__(self):
        self.epochs = 2
        self.batch = 8
        self.lr = 3e-4
        self.workers = 0
        self.n_clips = 6
        self.seed = 42
        self.experiment_id = "e2e"
        self.max_batches = 0
        self.mem_interval = 0.2   # 快速采样,验证线程真在工作
        self.diag_json = ""
        self.verbose = True


def main():
    device = torch.device("cpu")
    tmp = Path(tempfile.mkdtemp(prefix="runfold_e2e_"))
    res = {}

    # ---- 连续跑:run_fold 内会自动写 ckpt ----
    args = A()
    torch.manual_seed(args.seed)
    train_ds, val_ds = FakeDS(32, 0), FakeDS(16, 1)
    model = TinyNet()
    diag1 = str(tmp / "diag_cont.jsonl")
    args.diag_json = diag1
    R3._CKPT_OVERRIDE["root"] = str(tmp / "ckptroot")
    _, _ = R3.run_fold(model, train_ds, val_ds, device, args,
                       artifact_root=tmp / "art" / "e2e", fold=0, plane="Axial")
    ck_dir = R3._ckpt_dir(tmp / "art" / "e2e", 0, "Axial")
    res["ckpt_epoch1_exists"] = (ck_dir / "epoch1.ckpt").exists()
    res["ckpt_epoch2_exists"] = (ck_dir / "epoch2.ckpt").exists()
    res["ckpt_latest_exists"] = (ck_dir / "latest.ckpt").exists()
    res["diag_written"] = Path(diag1).exists()
    n_lines = len(Path(diag1).read_text(encoding="utf-8").strip().splitlines())
    res["telemetry_samples"] = n_lines
    res["telemetry_multi_sample"] = n_lines >= 3   # start + periodic + stop
    peak = json.loads(Path(diag1 + ".summary.json").read_text(encoding="utf-8"))
    res["peak_process_tree_rss_gb"] = peak["peak"]["process_tree_rss_gb"]
    res["peak_has_system_used_pct"] = peak["peak"]["system_used_pct"] >= 0
    res["psutil_available_locally"] = R3.HAS_PSUTIL
    res["ckpt_has_extra"] = "steps_per_epoch" in R3._load_ckpt(ck_dir / "latest.ckpt")

    # ---- 连续基线(第 2 次独立跑,同一 seed) ----
    torch.manual_seed(args.seed)
    args2 = A()
    args2.diag_json = ""
    model2 = TinyNet()
    R3._CKPT_OVERRIDE["root"] = str(tmp / "ckptroot2")
    R3.run_fold(model2, FakeDS(32, 0), FakeDS(16, 1), device, args2,
                artifact_root=tmp / "art" / "e2e2", fold=0, plane="Axial")

    # ---- resume:epoch1 的 ckpt → 跑完 epoch2 ----
    args3 = A()
    args3.diag_json = ""
    model3 = TinyNet()
    R3._CKPT_OVERRIDE["root"] = str(tmp / "ckptroot3")
    R3.run_fold(model3, FakeDS(32, 0), FakeDS(16, 1), device, args3,
                artifact_root=tmp / "art" / "e2e3", fold=0, plane="Axial",
                resume_ckpt=str(ck_dir / "epoch1.ckpt"))

    res["resume_param_hash_equal_continuous"] = (
        R3._model_param_hash(model3) == R3._model_param_hash(model2))
    res["continuous_self_consistent"] = (
        R3._model_param_hash(model) == R3._model_param_hash(model2))
    res["hash_cont"] = R3._model_param_hash(model2)[:16]
    res["hash_resumed"] = R3._model_param_hash(model3)[:16]

    print(json.dumps(res, indent=2, ensure_ascii=False))
    gate = all([
        res["ckpt_epoch1_exists"], res["ckpt_epoch2_exists"],
        res["ckpt_latest_exists"], res["diag_written"],
        res["telemetry_multi_sample"], res["psutil_available_locally"],
        res["ckpt_has_extra"], res["continuous_self_consistent"],
        res["resume_param_hash_equal_continuous"],
    ])
    print("E2E_GATE =", "PASS" if gate else "FAIL")
    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
