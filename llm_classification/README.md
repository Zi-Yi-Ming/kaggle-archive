# LLM Classification Finetuning — Chatbot Arena 人类偏好三分类

**比赛**:https://www.kaggle.com/competitions/llm-classification-finetuning
**脚本**:`llm_pref_v1.py` / `llm_pref_v1.ipynb`(单 cell 版,上传直接跑)
**类型**:Getting Started(练技术,不发奖牌/积分)

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
