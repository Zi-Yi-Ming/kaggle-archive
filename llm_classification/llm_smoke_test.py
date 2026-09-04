# -*- coding: utf-8 -*-
"""llm_pref_v1 双塔管线 CPU 冒烟验证:100 行样本,1 折,1 epoch。

用途:不上 Kaggle 也能验证 PairDataset → SiameseModel → train/predict 全链路无 bug。
运行: python llm_smoke_test.py
"""
import os
import sys
import time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import llm_pref_v1 as m

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MODEL = "distilbert-base-uncased"  # 走 ~/.cache/huggingface 本地缓存

def main():
    train = pd.read_csv(os.path.join(DATA, "train.csv"), nrows=100)
    test = pd.read_csv(os.path.join(DATA, "test.csv"))
    print(f"[冒烟] train {len(train)} 行(截断) / test {len(test)} 行")
    print(f"[冒烟] 类别分布: {train[m.TARGETS].sum().to_dict()}")
    print(f"[冒烟] 文本列样例 prompt: {str(train['prompt'].iloc[0])[:80]}...")

    t0 = time.time()
    oof, test_pred = m.run_finetune(
        train, test, MODEL,
        argparse_args(epochs=1, folds=2, batch=4, lr=2e-5, seed=42))
    dt = time.time() - t0

    print(f"\n[冒烟] OOF shape={oof.shape} test_pred shape={test_pred.shape}")
    print(f"[冒烟] OOF 概率范围: [{oof.min():.4f}, {oof.max():.4f}], 每行和 ≈ {oof.sum(axis=1).mean():.3f}")
    y = train[m.TARGETS].values
    try:
        from sklearn.metrics import log_loss
        print(f"[冒烟] 1 折 OOF LogLoss(1 epoch, 仅冒烟): {log_loss(y, oof):.4f}")
    except Exception as e:
        print(f"[冒烟] log_loss 跳过: {e}")
    print(f"[冒烟] 总耗时 {dt:.1f}s —— 管线跑通 ✓")


def argparse_args(epochs=1, folds=1, batch=4, lr=2e-5, seed=42):
    """构造与 llm_pref_v1 main 一致的简易 args 对象。"""
    class A: pass
    a = A()
    a.epochs, a.folds, a.batch, a.lr, a.seed = epochs, folds, batch, lr, seed
    return a


if __name__ == "__main__":
    main()
