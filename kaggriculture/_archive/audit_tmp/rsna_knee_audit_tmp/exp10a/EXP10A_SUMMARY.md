# EXP-10A SUMMARY — v11E Tape Structure Audit

日期：2026-09-07 ｜ 只读审计，production 冻结（md5 224a1c47... 未动）

**核心结论（详见 EXP10A_FINAL_REPORT.md）：**

```
v11E = 固定确定性主干（backbone 93.6%）+ 稀疏商店驱动 SELL 自适应点（6%）
TYPE: B（Tape + Sparse Adaptation）
```

- Gates A-D 全 PASS（20/20 确定性、40 games 720/720、recon 0、fingerprint 不变）
- movement/buy/hire/land 100% 固定；全部可变性集中在 **SELL 族**
- 380/380 首分歧归因 **SHOP**（H|shop 降熵 1.036→0.020）；divergence episodes median 1/longest 3 = **稀疏局部、快速重收敛、非级联**
- 序列相似性高：lev_norm 3.75%、LCP 362（前半局逐位一致）
- 稳定性与 bank 无相关（r = −0.016）
- 决策规则结论：可研究"固定 backbone + sparse adaptation"（**提出，不执行**）；H1/H2 hypothesis 仅记录

**边界确认**：不实现 adaptive branch、不 EXP-10、不 tape 移植、不优化、不提交 Kaggle。
