# 冲牌作战计划 — 2026-09-18 → 2026-09-23

**授权策略（用户已确认）**  
- 守成 + **最多 1 次路径孪生提交**  
- 首要目标：**奖牌 ≥2960（低概率）**；接受可能一无所获  
- alperen **policy 不改**；无门禁不提交其他候选  

**证据锚点**  
- alperen LB：public **2368.6** / team **2361.5** / rank **#1017**（`RESEARCH_P53`）  
- 奖牌区：**≥2960**（当时 15 队），#1 = 3197  
- Top10%：~2424（差 ~56 Elo）  
- 公开族诚实天花板：~2300–2400（`RESEARCH_P7` / `FINAL_CLOSE`）  
- 研究 P69 封版：无新 family 门禁不得重开旋钮实验  

---

## 0. last-2 算术（提交前必读）

规则：**只有最近 2 次提交计入终榜**（Bradley-Terry，截止后）。

文档记录的 last-2（P53 与 STATUS 略有出入，以你 **Kaggle Submissions 页实时列表**为准）：

| 来源 | slot | agent | Elo |
|---|---|---|---:|
| P53 (09-15) | 1 | alperen 56244291 | 2361.5 |
| P53 | 2 | R2 twin | 1901.5 |
| STATUS / FINAL_CLOSE (09-16) | 2 | V16 56268731 | ~978–1027 |

Submission ID 更大通常更新。若 **V16 (56268731) 比 alperen (56244291) 更新**：

```text
提交孪生前:  last-2 = [alperen, V16]     team ≈ max(2361, ~1000) = 2361
提交孪生后:  last-2 = [V16, twin]        ← alperen 原条目掉出
             但 twin ≡ alperen 同字节 policy → 策略仍在，只是换路径重开匹配
```

**含义：** 一次孪生提交 = 用同一策略换 path 重抽；弱 slot（V16）会暂时占着 last-2 另一格。  
**可选加赛（未授权，不要默认执行）：** 孪生稳定后若再交一次 alperen 原包，last-2 = [twin, alperen]，V16 掉出。这会消耗 **第 2 次** quota，需你单独点头。

**提交前动作（强制）：**  
打开 Competition → Submissions，抄下最近 2 条的 **ref / 日期 / publicScore**，填进本文件「现场记录」。

---

## 1. 路径孪生包（已就绪，未提交）

| 项 | 值 |
|---|---|
| 目录 | `kaggriculture/_push_alperen_twin/` |
| `main.py` | 与 `_push_alperen/main.py` **SHA256 相同** |
| SHA256 | `5B1102FA20EB0E60160502FFEF851B577B826038FD5CFF88427AB822DCDFD3C8` |
| kernel id | `ziyiming/kaggriculture-alperen-path-twin` |
| 标题 | `Kaggriculture Alperen Path Twin` |
| Internet | Off |
| 策略 | **不改任何逻辑**；仅独立 kernel 身份，使匹配路径重开 |

### 提交方式（二选一，需你本人操作或明确授权）

**A. Notebook（推荐）**  
1. 新建 private **Script**，competition = kaggriculture，Internet = Off  
2. 粘贴 `_push_alperen_twin/main.py` 全文  
3. Save & Run All（必须无报错）  
4. Submit — **只这一次**

**B. CLI**  
```powershell
cd D:\桌面\Kaggle\kaggriculture\_push_alperen_twin
kaggle kernels push
```
（低频使用；先确认 credentials。）

### 期望（诚实）

| 结果 | 含义 |
|---|---|
| twin ≈ 2300–2450 | path 方差内的正常收敛；**不是**奖牌信号 |
| twin 明显高于 alperen 历史（>2500 且对局样本够） | 保留观察；仍不能单靠这个推到 2960 |
| twin 崩盘（≪2000） | path 恶劣；**不要**立刻再交第三发去「救回来」 |

历史证据：path-twin 与主策略差距大约十几到数百 Elo；**单靠 path 到 +590 基本不现实**。

---

## 2. 每日扫描（守成主路径）

目标：只找 **可过门禁的新 public elite**，不是找「感觉更强的 notebook」。

**门禁（全部满足才允许讨论是否占用剩余 quota）：**

1. 可执行：有 `agent()` / `main.py` 入口，导入不炸  
2. **指纹非已知族**（非 R2 / alperen / guru / shop-router 同源；查 `_research` fingerprint / P66–P70）  
3. 本地 H2H：vs **alperen ≥5/8**，双 seat，finn 不 wrap  
4. 且 vs **≥2 个近期 elite** ≥5/8（R2 / tetsu / kaito / rayk / prvsiyan 等）  
5. 无 seat 撕裂（单 seat 崩溃 = FAIL）

**扫描源（按优先级）：**

- Competition → Discussions（新帖、高回复）  
- Notebooks：按 votes / 最近更新，看 title 含 adaptive / meta / RL / top  
- 你已有的 `_external/`、`tmp_candidates/`：优先扫还没跑完门禁的  
- 不要重新下载 21GB 全量 episode；只抽「最近小日」做指纹

**每日产出：** 写入 `_production/SCAN_LOG.md`  
- 日期 / 候选名 / 来源 URL / 是否可执行 / 指纹 / 门禁结果 / 结论  

**默认结论写法：** `NO_GATE_PASS — no submit`  
只有全过才写 `GATE_PASS — 等待用户授权 submit`。

---

## 3. 五日节奏

| 日期 | 动作 | 提交？ |
|---|---|---|
| **D0 09-18（今天）** | 计划落盘；孪生包哈希校验；Submissions 页抄 last-2；开 SCAN_LOG | 仅当你确认 last-2 顺序后授权孪生 **1** 次 |
| **D1 09-19** | 全量扫 discussion/notebook；过门禁候选本地 H2H；记录 twin 初盘（若有） | 无门禁 = 不交 |
| **D2 09-20** | 同上；若 twin 已跑数局，看是否稳定在 alperen 带 | 无门禁 = 不交 |
| **D3 09-21** | 再扫；评估是否出现新 family；**停止**任何 overlay 实验 | 默认不交 |
| **D4 09-22** | 最后扫描日；确认 last-2 是否为你要的两条；决定是否需要「补交 alperen 以挤掉 V16」（**单独授权**） | 最多再 1 次，且仅当挤掉弱 slot 对终榜 best-of-two 有必要 |
| **D5 09-23 截止日** | **停止提交**；核对 Submissions 页 last-2；备份 STATUS | 不交 |

配额：每日最多 5，**本计划实际用量目标 = 1（孪生）**；扫描不耗配额。  
第 2 次提交（补 alperen / 真门禁新 elite）**必须你现场点头**。

---

## 4. 硬停手条件

出现任一条 → 当天不再提交：

- 候选本地 <5/8 vs alperen，或 seat 撕裂  
- 指纹与已知 shop-router / alperen 族高度相似（sim 高）却无新 mechanism  
- twin 已交且仍在收敛，无新证据  
- 仅「作者宣称 2900+」而无本地 H2H  
- 想改 alperen 逻辑做 livestock 补丁却没跑完整门禁（默认禁止）

---

## 5. 不要做的事

- 不要交 `_push_medal_r*` / farm_v4 / 未门禁 notebook  
- 不要在赛末开 PPO / 从零 program search  
- 不要「连续 path 抽卡」——授权是 **1 次**孪生，不是 5 次  
- 不要删除或修改 `_push_alperen/main.py`  
- 不要相信 public notebook 的 bestScore 直接等于你能复现的 Elo  

---

## 6. 现场记录（CLI 实查 2026-09-18）

```text
Kaggle Submissions 最近两条（决定 last-2）:
  1) ref=56268731  date=2026-09-16 03:54  score=977.0    name=V16 claimed-2900
  2) ref=56251463  date=2026-09-15 09:48  score=1982.6   name=farm_v4
  已掉出 last-2: ref=56244291 alperen_meta score=2262.6

榜顶（09-18 CLI leaderboard）:
  #1 Majkel1337 3241.9 … 奖牌带约从 ~2978+（keiz）起

提交 twin 前 team ≈ max(977, 1982.6) = 1982.6
提交 twin 后 last-2 = [V16, twin]；farm_v4 掉出
twin SHA256 = alperen → 策略抢回 last-2，目标带 ~2260+（非保证）

孪生提交:
  授权人: 用户（2026-09-19「你直接交就行」）
  时间: 2026-09-19 02:52 UTC
  kernel id: ziyiming/kaggriculture-alperen-path-twin v1
  产物: submission.tar.gz
  ref: 56346424  status=COMPLETE  publicScore=600.0（初始 Elo）
  SHA256: 5B1102FA20EB0E60160502FFEF851B577B826038FD5CFF88427AB822DCDFD3C8
  提交后 last-2: V16(977) + twin(600爬分中)
  farm_v4(1981.7) 与 alperen 原条目(2262.6) 均掉出 last-2

观察:
  D+0 score: 600.0（expected start; R2 曾 600→882→1900+）
  D+1 score: ____
  结论: 策略已回 last-2；等待收敛；勿再 path 提交
```

---

## 7. 成功与失败的定义

| 档位 | 标准 | 动作 |
|---|---|---|
| **奖牌** | last-2 best ≥2960 | 停止；归档；勿再折腾 |
| **接近** | ≥2700 | 保持不动，等终榜；勿加码 |
| **top10%** | ≥2424 | 可接受的现实结果；归档方法论 |
| **守成** | ≈2360 | 预期内；path 没送你上牌 |
| **掉分** | ≪2300 | 检查 last-2 是否误踢 alperen；考虑补交原包（单独授权） |

---

## 8. 相关文件

```text
_push_alperen/main.py          生产主力（勿改）
_push_alperen_twin/            路径孪生包（已哈希一致）
_production/STATUS.md          生产状态
_production/SCAN_LOG.md        每日扫描日志
_production/MEDAL_PUSH_2026-09.md  本计划
_research/RESEARCH_P53_LEADERBOARD_CHECK.md
_research/RESEARCH_FINAL_CLOSE.md
```
