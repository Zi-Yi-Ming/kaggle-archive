# C1 Live-Agent Reproduction Audit（EXP-9A）

日期：2026-09-07 ｜ 引擎 kaggle_environments 1.32.7 ｜ production v11E 冻结（md5 `224a1c47...`，Elo 942.2，未提交 Kaggle）

```
HARD GATE A = FAIL
C1 LIVE REPRODUCTION = NOT REPRODUCIBLE
```

## 1. Submission Identity

| 项 | 值 |
| --- | --- |
| submission | **55425101**（team カワシギ，ladder rank-1 @ 2026-08-15 快照，ladder score 3282.6） |
| episode | 91889284（seed 1579917451，seat 1，bank 133,672） |
| 已知公开 artifact | 仅动作流（destbreso top-10 streams + Kaggle replay endpoint）——EXP-9 已用作 exact tape |
| **可执行 policy code** | **未发现** |

## 2. Source / Entrypoint

**NOT FOUND**（三条检索通道全部核验）：
- Kaggle 比赛公开 kernels 全表（60+，按 dateCreated）：无カワシギ/55425101 对应 kernel（近期公开者均为其他作者：yamakawanin、thomastschinkel、tokenjunkielabs、y3uanm 等，其中 yamakawanin 的 "kawa" 匹配为不同作者，无证据关联）
- web 检索「カワシギ kaggriculture」「kaggriculture submission 55425101」：无 kaggriculture agent 匹配（仅日本农业企业等无关结果）
- 检索到的其他 agent 仓库/notebook（deepeshumrao/kaggriculture-agent、avikdas567 策略引擎、raykkretzschmar reference agents）：**均无证据与 55425101 对应**——按 HARD GATE A 不拿"看起来像"的 repo 冒充

## 3. Live Policy Classification

**UNKNOWN / NOT CLASSIFIABLE**：
- 无 policy code → 无法判定 55425101 的提交本体是 live policy / replay / hybrid / router / adaptive
- 其公开动作流表现为 open-loop 特征（EXP-9 复现 81.2% SELL 失败 = 状态依赖性强），但**不能**从动作流反推提交本体类型

## 4. Environment Compatibility

N/A——无可执行 policy 可测（无 code → 无 entrypoint → 无环境兼容性可验证）

## 5. Determinism

N/A——无 policy（随机源可控性无从核验）

## 6. 16-game Smoke Results

**NOT EXECUTED**——Phase 1 smoke gated on Phase 0 PASS；HARD GATE A = FAIL（身份无法建立），依协议不进入 smoke，未跑任何 L1 局

## 7. Comparison

| Agent | Games | Mean Bank | Win Rate | Mean Margin |
| --- | -: | ---: | ---: | ---: |
| v11E | — | （EXP-9 基准可用，无需重跑） | — | — |
| C1 live | **0**（未执行） | N/A | N/A | N/A |

## 8. Tape vs Live Interpretation

- **C1 tape ≪ v11E**（EXP-9 已证：0/370 胜、Δ −47.8k~−71.5k/局、SELL 失败 81.2%）——此为 exact action tape 的 transferability 判定，结论维持
- **C1 live 无法测**（无 source）——Case A/B/C 均不可判定；不推断"live 一定弱"（无证据），也不推断"live 一定强"（同样无证据）

## 9. Reproduction Confidence

```
NOT REPRODUCIBLE
```

- 提交本体 code 不可合法取得（未公开/不可发现），身份-源码对应链（submission → episode → source → entrypoint → executable policy）在可及范围内断裂

## 10. Decision

```
IDENTITY UNVERIFIED
```

- EXP-9A 未能建立 55425101 的 live agent 可复现链路；不进行任何 live benchmark、不 reverse-engineer、不 repair

## 处置（STOP）

- **不进入** EXP-10 / compatibility repair / C1 reverse engineering / 大规模 benchmark / production modification / Kaggle submission
- Production v11E 继续冻结（md5 `224a1c47...`、Elo 942.2、recovery submission 56047543）
- EXP-9 结论（tape 不可迁移、NOT TRANSFERABLE）**不受影响、不修改**——本审计与 EXP-9 测的是不同对象（live policy 不可得 vs exact tape 已测）

## 调查留档

检索记录：kaggle kernels list（60+ 全表）、web_search ×4（队名/提交号/agent 源）、dataset 核验（destbreso/dariushafshar）。若未来 55425101 的 source 公开，可重新评估。

---

## FINAL CLOSURE（EXP-9A → STOP / CLOSED）

```
EXP-9A → STOP / CLOSED
Phase 0 → COMPLETED（HARD GATE A = FAIL）
Phase 1 → NOT EXECUTED / NOT REQUIRED（blocked by HARD GATE A）
DECISION = IDENTITY UNVERIFIED
```

### 总实验记录解释（明确区分，勿混淆）

| 实验 | 对象 | 结论 |
| --- | --- | --- |
| **EXP-9** | C1 **public episode action tape**（720 步 exact replay） | exact tape 在 fresh seeds 上 **NOT TRANSFERABLE**（0/370 胜，SELL 失败 81.2%）——测的是 **action tape 的 replay transferability** |
| **EXP-9A** | C1 **live executable agent** | source/submission identity **无法核验**（无合法可取得的 policy code）→ live agent 的 transferable strength **不可判定** |

**重要**：EXP-9A 的 NOT REPRODUCIBLE **不是**"C1 agent 弱"的证据——它只说明 C1 的 live policy 无法被本审计链路获取与验证。EXP-9 的 tape 结论也不外推为 live 结论。

### 关闭确认

- 不追踪 55425101 source、不执行 Phase 1 smoke、不使用无身份证据的 repo/notebook 代替 C1
- 不进入 EXP-10 / compatibility repair / reverse engineering / 大规模 benchmark / production modification / Kaggle submission
- Production v11E 冻结：Elo 942.2、recovery 56047543、engine 1.32.7、md5 `224a1c47...`
- 本报告（EXP9A_LIVE_AUDIT_REPORT.md）为最终证据
