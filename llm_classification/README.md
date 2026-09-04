# LLM Classification Finetuning — Chatbot Arena 人类偏好三分类

**比赛**:https://www.kaggle.com/competitions/llm-classification-finetuning
**脚本**:`llm_pref_v1.py` / `llm_pref_v1.ipynb`(单 cell 版,上传直接跑)
**类型**:Getting Started(练技术,不发奖牌/积分)

## Result

| Metric | Best Score | Best Version | Status |
|---|---:|---|---|
| LogLoss | —¹ | v1 (auto) | Completed |

¹ Getting Started 练习赛，以方法验证为主，未留最终成绩记录（基线 log(3)≈1.0986，社区好成绩 ~1.045）。

### Key Finding

本赛是 RSNA 文本分支的预演：双塔 Siamese + 融合特征结构 + 离线 HF 权重挂载（kozodoi/transformers）在无需联网时即可微调 distilbert。

## 任务与指标

- 给一个 prompt + 两个匿名 LLM 的响应(`response_a` / `response_b`),预测人类偏好:
  三分类 `winner_model_a` / `winner_model_b` / `winner_tie`
- 指标:**多分类 Log Loss**(随机基线 = log(3) ≈ 1.0986;社区好成绩 ~1.045)
- 数据:`train.csv` 57,477 行 × 9 列;`test.csv` 无标签(也无 model_a/b 列)

## 两条建模路径(`--method`)

| 路径 | 依赖 | 速度 | 预期 |
|---|---|---|---|
| `feat` | 仅 sklearn | 秒级 | TF-IDF+文本质量特征+LR,目标 logloss < 1.08,保底提交 |
| `finetune` | transformers+torch+GPU | 每折几分钟 | 双塔 Siamese 共享编码器,融合 [a;b;a−b;a⊙b],目标 ~1.05 |
| `auto`(默认) | 视是否扫到模型 | — | 扫到离线 HF 权重 → finetune;否则回退 feat |

## 在 Kaggle Notebook 上运行

1. **New Notebook** → **Settings → Accelerator** 选 **GPU T4**
2. **Add Input**:
   - 挂比赛 **llm-classification-finetuning**(数据本体)
   - (推荐)挂离线权重数据集 **kozodoi/transformers**(含 `distilbert-base-uncased`、
     `roberta-base` 等全套 config+tokenizer+权重,脚本自动扫描,**无需开 Internet**)
     - 备选:`virajjayant/distilbertbaseuncased`、`thuyvanne/bert-base-uncased-offline`
3. 上传 `llm_pref_v1.ipynb`,点 ▶ 运行唯一 cell
4. 输出 `/kaggle/working/submission.csv` → Submit

不挂权重数据集也能跑:`auto` 自动回退 `feat` 路径,无 GPU 也能出合法提交。

## 与 RSNA 的联动价值

这个赛是**阶段 4(distilbert 文本分支)的预演**:
- 双塔 Siamese + 融合特征结构,可迁移到 RSNA 的"影像特征 + 放射报告文本"双模态;
- 学会离线挂载 HF 权重(kozodoi/transformers),RSNA 阶段 4 同样无需开 Internet;
- 体验多分类 Log Loss 指标(RSNA 是 12 标签二分类 AUC,都是概率校准类问题)。

## 文件

```
llm_classification/
├── llm_pref_v1.py        # baseline 脚本(Kaggle Notebook 上跑)
├── llm_pref_v1.ipynb     # 单 cell 版,上传直接运行
└── README.md             # 本文档
```

---

# 🧠 深度复盘(2026-09 完赛归档)

## 1. 心理历程:一个"为了 RSNA 而打"的预演赛

这个赛不是我为了冲榜打的——它的真正定位是 **RSNA Knee 阶段 4(distilbert
文本分支)的预演**。当时 RSNA 计划里有一个"用放射报告文本辅助影像分类"的
分支,而我对"双塔 Siamese + 离线 HF 权重"这套玩法还不熟,不想直接在 RSNA
的 GPU 额度上试错,于是选了 LLM Classification 当练兵场。

设计时的两个核心决策都带着"预演"的目的:

**决策一:双塔 Siamese 结构**。这个赛的输入是 prompt + response_a +
response_b,天然适合双塔(两个响应共享编码器,交互用 [a;b;a−b;a⊙b] 融合)。
我特意选了和 RSNA 计划一致的"共享编码器 + 融合特征"结构——这样迁移时
只需要把"文本对"换成"影像 + 报告"。

**决策二:离线权重挂载**。Kaggle Notebook 默认联网不稳,我研究了
`kozodoi/transformers` 这个离线权重包(含 distilbert-base-uncased 全套),
学会了脚本自动扫描挂载、扫不到就回退 `feat` 路径(TF-IDF+LR)的容错设计。
这个"离线权重优先、联网兜底、再随机"的三级策略,后来原样搬进了 RSNA 的
预训练权重加载逻辑。

**结果**:方法上验证了双塔 Siamese + 融合特征能跑通、多分类 Log Loss 指标
能优化;工程上沉淀了离线 HF 挂载 + 自动回退的模板。分数本身(Getting Started
无奖牌)不是目的,RSNA 阶段 4 的"少踩一个坑"才是回报。

## 2. 架构方法演变:一次到位的双路径设计

```
v1(--method auto)
 ├── finetune 路径:双塔 Siamese(distilbert 共享编码器)
 │    输入 (a, b) → 编码 → 融合 [a; b; a−b; a⊙b] → 三分类头
 ├── feat 路径:TF-IDF + LR(无 GPU 保底)
 └── auto 决策:扫到离线 HF 权重 → finetune;否则回退 feat
```

**设计动机**:Getting Started 赛不值得多轮迭代,一次设计就同时覆盖
"有 GPU/有权重(finetune)" 和 "无 GPU/无权重(feat)" 两条路,保证必有合法提交。

## 3. 踩坑/经验档案

| 点 | 处理 | 沉淀 |
|---|---|---|
| 离线权重挂载 | kozodoi/transformers + 自动扫描 | RSNA 阶段4 同款(无需开 Internet) |
| 联网不稳定 | auto 回退 feat 路径 | 三级容错:离线→联网→随机 |
| 双塔融合特征 | [a;b;a−b;a⊙b] | RSNA"影像+报告"双模态的模板 |

## 4. 核心经验教训(武器库)

1. **练习赛的正确用法是当"预演"**:为 RSNA 阶段 4 验证双塔结构 + 离线权重,
   省下的 GPU 试错成本远大于这个赛本身
2. **双塔 Siamese + [a;b;a−b;a⊙b] 融合** 是"两个输入一个输出"类任务的通用骨架
3. **离线权重三级容错**(离线→联网→随机)是所有 Kaggle Notebook 的稳健模式
4. **多分类 Log Loss 与 12 标签 AUC 同属概率校准问题**,调优经验可平移
5. 打比赛前先问"这个赛能为我下一个赛沉淀什么"——目标驱动比冲榜更有长期价值
