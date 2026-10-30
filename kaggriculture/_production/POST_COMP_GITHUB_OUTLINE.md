# 农场赛（kaggriculture）赛后 GitHub 复盘大纲

> 状态：**骨架 · 赛期不公开**（本目录被 `.gitignore` 排除）  
> 截止：2026-09-30 提交锁；BT 终榜约 10-01→10-15  
> 详细正文等 **封榜 + 终榜出来后再写**；本文件只定结构与素材清单。

---

## 0. 发布原则

- 公开时再拷贝精选内容到公开仓；**不要**整包上传 5GB `_external`
- 成绩写 CLI/UI 实查值，不写未验证文案分
- 失败与否决与成功同等重要（farm_v4、goodpjw ERROR、P77 否决）
- License / 上游归属（Apache-2.0 衍生链）必须保留

---

## 1. 建议公开结构（封榜后）

```text
kaggriculture/
├── README.md                 # 赛后长复盘（见 §2 提纲）
├── COMPETITION.md            # 赛制：last-2 / Elo / Validation / BT
├── timeline.md               # 关键节点
├── packages/                 # 精选提交包（代码可公开时）
│   ├── thomas_2945/          # 生产主力（来自 public + 本地门禁）
│   └── alperen_path_twin/    # path 策略对照
├── research/                 # 里程碑报告（非全部 P1–P77）
│   ├── P74_thomas_gate.md
│   ├── P76_thomas_architecture.md
│   └── P77_search.md
└── lessons.md                # 方法论（可与主 README 合并）
```

---

## 2. README 复盘提纲（详细正文）

1. **Result**  
   - 最终 public / private（BT）分、名次、奖牌（以官方为准）  

### 2.0 校准点素材（P88–P92b · 必写）

公开 Best 标签 vs 本地异构面板（Metav4 + shop_router v7）exact 复核：

| 候选 | 公开 Best | Exact SHA | vs Metav4 | vs shop_v7 |
|---|---:|---|---:|---:|
| Pipe-16 谱系（2965/2950/guru v4） | ~2965 | 克隆同 bank | +50～78 / 高胜率 | **0% −16k** |
| Kaito v43 | 2882 | =manifest | 0% −23.6k | 0% −22.4k |
| Kaito v48 Fast Routes | 3009 | =manifest | 0% −23.6k | 0% −22.4k |
| Andrey V12 | 2883 | **UNRESOLVED**（版本 API 403） | — | — |
| Andrey V21-R1 bootstrap | — | =notebook | 0% −35.8k | 0% −33.6k |
| Metav4 生产 | — | 生产包 | 镜像 | **100% +数千** |

**论点:** local heterogeneous gate ≠ public Best；提交资格 = exact + 双门 + Validation + 授权。  
方法论句：`3009 → 0/6 vs Metav4`、`2965 → 0% vs shop` 是 game-agent benchmark 上的 **calibration points**。

Also document:
- Official second-slot = hedge (team score = max) — Slot-B 门禁设计
- 自研 P87–P91 全灭（中盘劳力 −17k、F7 holdout 假阳性、tape 感知仍伤）
- Metav4 探针：seeds.WHEAT=0、tile(2,4)=PASTURE、day1 money~11、step0 market 毒点
- **RL meta 解释（P46–P69 闭环）:** 有限 replay 无法恢复 full conditional policy（LOSO 1.0→0.163）；榜前或有 RL 在线 π(s)；naive PPO 社区证据易 plateau → 赛后路线 = **Metav4 skeleton + state abstraction + hierarchical RL refine + population**，而非端到端 PPO 或再写 deterministic counter
- **Gold Shot v0（赛中 moonshot）:** Metav4 day6 route 覆盖 + tabular bandit 30 局 → eval vs Metav4 0.125/mean0、shop 1.0 未崩 → **STOP_NO_SIGNAL**。写复盘时必须区分：*minimal single-node probe no signal* ≠ *RL failed*；接口与鲁棒性已验证，缺的是样本量与多决策窗
- **Gold Shot v1:** 多窗口 d6–d21 + 现金 reward + 90 局联赛；吞吐 **~94 SPS**（社区 ~10k）→ `FAIL_COMMUNITY_SCALE`；eval 时 Q 几乎未触发→default≈Metav4；shop 仍 100%。判定：**INFRASTRUCTURE_PASS / LEARNING_SIGNAL_UNTESTED**。真正 kill = **赛前算力无法达到可证明 RL 的样本规模**。赛后 v2 继承 chassis/接口，先建 fast simulator




   - last-2 构成与队分规则回顾  
2. **赛制理解**  
   - 每日 5 提交、仅最新 2 tracked、Validation ERROR 不进池  
   - 只计 W/L；封榜后 BT ~2 周；live Elo ≠ 终榜  
3. **策略演进时间线**  
   - v11E / Cleo 系 → R2 / alperen → path twin → **thomas 2945**  
   - 何时冻结、为何不交、门禁标准如何收紧  
4. **关键战役**  
   - 公开扫描发现 thomas（P74 门禁 8/8×3 elite）  
   - P76 架构：V39 底座 + COURIER/HERD/RACE；主 alpha 在底座+非 v9  
   - P77：guru 等 0/8 vs thomas → 不交  
   - goodpjw 本地过门禁但 Kaggle Validation ERROR  
   - farm_v4：本地 8-0 ≠ LB  
5. **失败档案**  
   - 盲交 / path re-roll 期望、弱包占 last-2、本地 margin 迷信  
6. **数据与证据**  
   - 榜样本 thomas：修正后 ~86.8% WR（33-4-1），败局很薄  
   - 作者宣称 2944.7 vs 己方 ~2645：path/池/峰值差  
7. **方法论**  
   - 底座优先、每层一个引擎事实、telemetry、胜率门禁、Validation 一等公民  
   - 本地 H2H 只能否决，不能单独保证 LB  
8. **资产索引**  
   - 指向本仓 `research/` 与私有归档路径（不公开大文件）

---

## 3. 本地里程碑素材（写作时引用）

| 主题 | 路径 |
|---|---|
| 生产真相 / 截止 / last-2 | `_production/STATUS.md` |
| 冲牌计划与门禁 | `_production/MEDAL_PUSH_2026-09.md` |
| 扫描日志 | `_production/SCAN_LOG.md` |
| thomas 门禁 | `_research/RESEARCH_P74_THOMAS_GATE.md` |
| thomas 架构消融 | `_research/RESEARCH_P76_THOMAS_ARCHITECTURE.md` |
| P77 否决 | `_research/` P77 相关 + `p77d_guru_dynamic_gate.json` |
| 生产包 | `_push_thomas_2945/`、`_push_alperen_twin/` |
| ERROR 对照 | `_push_goodpjw_melon2749/` |
| 根目录泄漏归档 | `_archive/submissions/root_leaks_20260926/` |
| 目录整理日志 | `_workspace/organize_log.jsonl`、`cleanup_log_20260926.jsonl` |

---

## 4. 封榜后 checklist

- [ ] CLI/UI 记录最终 public 分与奖牌  
- [ ] 等待 BT 终榜，记录 private/最终名次  
- [ ] 确认 last-2 未在截止前被误挤  
- [ ] 从上表精选报告，改写成公开 README  
- [ ] 决定公开哪些 `main.py`（license 检查）  
- [ ] 更新公开仓根 README 的 Archive 表（去掉「赛期不公开」占位）  
- [ ] 不提交任何仍含密钥/本机绝对路径的材料  

---

## 5. 明确不做

- 赛期内把 `kaggriculture/` 整包推公开仓  
- 用未验证「作者 LB 文案」当最终成绩  
- 为 GitHub 美化而改写实验结论  
