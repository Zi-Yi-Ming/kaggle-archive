# EXP-9A Phase 0B Report：Submission Provenance Recovery

日期：2026-09-07 ｜ 对象：submission 55425101（カワシギ）→ source identity 反查 ｜ production v11E 冻结（未动）

## 分类结论

```
P3 CLASSIFICATION = D（IDENTITY STILL UNVERIFIED）
PHASE 1 DECISION  = NOT ENTERED（仅 A 允许进入 live-agent reproduction）
```

**阻塞类型：identity 尚未闭环（access limitation，非"source 不存在"）**——Kaggle 官方面不暴露他人提交的 source linkage，无法区分"私有未发布"与"不存在"。

## Evidence Table（P2）

| claim | evidence | confidence |
| --- | --- | --- |
| submission identity：55425101 ↔ カワシギ，ladder rank-1 @ 08-15（3282.6） | destbreso episodes.csv（rank_at_snapshot=1） | **HIGH** |
| episode identity：91889284 ↔ seed 1579917451 ↔ seat 1 ↔ bank 133672 ↔ 720 turns | 官方 replay（info：TeamNames=[Jonathan Ashenaf1, カワシギ]，seed）+ episodes.csv 交叉一致 | **HIGH** |
| engine provenance：episode 录制于 **module_version 1.32.6**（≠ 基准 1.32.7） | replay 顶层 module_version | HIGH（documented caveat） |
| source notebook / kernel | 公开 kernels 60+ 无カワシギ/55425101；API 不暴露他人提交的 source 链接；页面 JS 不可读 | **NONE（不可得）** |
| executable policy | 无 source → 不可合法取得 | **NONE（不可得）** |
| owner 账号级身份 | 仅队名"カワシギ"；无进一步公开元数据 | LOW/NONE |

## 调查记录（P0/P1，全部完成）

1. **Kaggle API 通道验证**：`kaggle competitions submissions -c kaggriculture` **可用**（返回我们的记录）→ 通道未坏；但 submissions API **只暴露本账号自己的提交**，55425101 属他人，不可经官方 API 访问（**access limitation**）
2. 直接 API 探测：`submissions/55425101`、`replays/91889284` → 404（在通道可用前提下，为作用域/路径限制，非"不存在"证据）
3. **replay 元数据全量检查**：info（Agents/TeamNames/EpisodeId/seed）+ 顶层（module_version 1.32.6、specification、configuration）——全文件关键词扫描：**无 submission/notebook/kernel/55425101 引用**
4. **episodes.csv 全 schema**（11 字段：submission/episode_id/rank/team/ladder/seat/opponent/bank/opponent_bank/seed/turns）——**无 source/url/notebook 字段**
5. 公开 kernels 列表（60+，按 dateCreated）：无カワシギ对应 kernel
6. Kaggle 页面（submissions/leaderboard/discussions/datasets）：JS 渲染，无正文（access limitation）
7. web_search ×4（队名/提交号/agent 源）：无 kaggriculture 匹配；其他 agent 仓库（deepeshumrao 等）无身份证据、按禁止事项排除

## 六问回答（用户必答项）

1. **55425101 能否映射到 Kaggle Notebook/Kernel？** → **不能**（无可访问映射；无公开 kernel；API 不暴露他人 source 链接）
2. **若能，Notebook/Kernel ID？** → N/A
3. **owner？** → 队名 カワシギ（已知）；账号级身份不可进一步核验
4. **能否拿到 source/version？** → **不能**（access limitation，非"source 不存在"）
5. **能否证明它产生了 episode 91889284？** → episode→submission 链**已验证**（队名+episodes.csv+seed+bank 全对上，HIGH），但**"哪段代码产生它"不可证**（无 source）
6. **阻塞类型？** → **identity 尚未闭环**（Kaggle 官方面不暴露他人提交的 source linkage；无法区分"私有未发布"与"不存在"）；附加：episode 引擎 1.32.6 ≠ 基准 1.32.7（不影响 EXP-9 结论，记录在案）

## 与 EXP-9A Phase 0 的关系

- Phase 0（公开搜索）→ NOT REPRODUCIBLE（IDENTITY UNVERIFIED）
- Phase 0B（Kaggle 内部 provenance）→ **同样无法闭环**，但阻塞性质明确为 **access limitation**（API 作用域限制 + 无公开 source 面），非"source 不存在"
- 两轮调查相互独立、证据一致：无身份证据的 repo 一律排除（禁止事项 1）

## 处置（STOP）

- **不进入 Phase 1**（仅 A 允许）；不追踪替代 repo；不 reverse-engineer；不 repair；不 EXP-10；不修改 production；不提交 Kaggle
- Production v11E 冻结：Elo 942.2、recovery 56047543、engine 1.32.7（基准）、md5 `224a1c47...`
- 若 Kaggle 未来开放他人提交的 source 链接（或 カワシギ 发布 notebook），可重新评估（届时重跑 Phase 0B）
