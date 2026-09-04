# NLP Getting Started - Disaster Tweets

Kaggle 常驻赛(Natural Language Processing with Disaster Tweets,滚动榜):
判断推特文本是否在报道**真实灾难**(而非比喻/广告/电影台词),二分类,
评分指标为 **F1**。

数据:训练集 7613 行 × 5 列,测试集 3263 行;文本平均 101 字符;
`keyword`(61 个缺失)与 `location`(2533 个缺失)是弱特征,主体信号在 `text`。

## 项目结构

```
nlp_getting_started/
├── data/                          # train.csv / test.csv / sample_submission.csv
├── submissions/
│   ├── submission_v1.csv          # v1 基线(TF-IDF + LR,0.79895)
│   ├── submission_v2.csv          # v2 特征增强(0.80784)
│   └── submission_v3.csv          # v3 distilbert 微调(当前最佳,0.83174)
├── nlp_v1.py                      # v1: TF-IDF(词1-2gram) + LR/MNB 5 折对比
├── nlp_v2.py                      # v2: TF-IDF(word+char) + keyword + W2V 句向量
├── nlp_v3_kaggle.py               # v3: distilbert 微调(Kaggle Notebook + GPU 版)
├── nlp_v4_kaggle.py               # v4: distilbert + TF-IDF 概率集成(留待 Notebook 跑)
└── README.md
```

## 提交记录(2026-08-19)

| 版本 | 文件 | 模型思路 | 本地 5 折 CV / 验证 | 公开榜 |
|---|---|---|---|---|
| v1 | `submissions/submission_v1.csv` | TF-IDF(词 1-2 gram,min_df=3,sublinear) + LogisticRegression | F1 0.7459 | 0.79895 |
| v2 | `submissions/submission_v2.csv` | TF-IDF(word 1-2 + char 2-4) + keyword 拼入 text + LR | F1 0.7668 | 0.80784 |
| **v3** | `submissions/submission_v3.csv` | **distilbert-base-uncased 微调(GPU,早停,最佳权重回滚)** | **验证 F1 0.8232** | **0.83174** |
| v4 | `submissions/submission_nlp_v4.csv` | distilbert + TF-IDF LR 概率混合(权重+阈值网格搜索) | 待跑 | 待提交 |

**关键结论**:

- **v3 公开榜 0.83174 创最佳**(v1 0.79895 → v2 0.80784 → v3 0.83174),
  预训练 Transformer 终于突破了词袋特征的天花板——v2 之后本地自训练
  W2V 只有 0.687, 而**预训练** distilbert 验证 F1 0.8232, 差在"语料"不在"方法":
  BERT 的语义知识来自 8 亿网页预训练, 7613 条推文只负责微调。
- **v3 训练细节**: 分层 10% 验证(762 条), 4 epoch + 早停(patience=2,
  实际 epoch 2 就到 0.8232 平台), 最佳权重回滚; loss 0.445→0.284
  收敛正常; 分类头 MISSING 参数随机初始化是预期行为。
- **脚本兼容性坑(已修)**: transformers 5.x 移除了顶层 `AdamW` 导出,
  改用 `torch.optim.AdamW`(Kaggle 的 4.x 与本地 5.x 都兼容);
  数据自动定位用 kagglehub 兜底(用户未挂载时自动下载成功)。
- **本赛天花板参考**: 头部 ~0.85(常用 ensemble 或 roberta/deberta),
  v3 的 0.83174 已属"单模型认真做"水平。

## 使用方法

```bash
# 环境:conda activate kaggle
python nlp_getting_started/nlp_v1.py   # v1 基线(当前最佳)
```

### 提交

```bash
# 需先 conda activate kaggle;NO_PROXY 绕过系统代理
NO_PROXY="*" no_proxy="*" HTTP_PROXY="" HTTPS_PROXY="" ALL_PROXY="" \
http_proxy="" https_proxy="" all_proxy="" \
kaggle competitions submit -c nlp-getting-started \
  -f nlp_getting_started/submissions/submission_v1.csv -m "说明"
```

## 进阶方向(无截止日期,可慢慢磨)

1. **词嵌入**(本赛最大提升来源):Word2Vec/GloVe 句子向量 + LR/SVM,
   或直接上预训练 Transformer(distilbert-base),公开榜可到 0.85+;
   Kaggle Notebook 有 GPU 时 BERT 类模型微调 3-5 epoch 即可
2. **keyword 特征**:keyword 缺失本身就是信号;把 keyword 拼进 text 或
   单独 one-hot/嵌入,通常 +0.005~0.01
3. **集成**:TF-IDF LR + 词嵌入模型 + BERT 概率平均
4. **清洗**:URL/#mention 处理策略对比、拼写纠正(灾难推文俚语多)
