# Digit Recognizer (MNIST)

Kaggle 经典常驻赛(Getting Started,滚动榜):识别 28×28 灰度手写数字(0-9),
**10 分类**,评分指标为 **Accuracy**。

数据:训练集 42000 行 × 785 列(784 像素 + label),测试集 28000 行 × 784 列,
像素值 0-255,无缺失。

## 项目结构

```
digit_recognizer/
├── data/                          # train.csv / test.csv / sample_submission.csv
├── submissions/
│   ├── submission_baseline.csv    # 基线(RF,0.96378)
│   └── submission_cnn.csv         # CNN(最佳,0.98778)
├── digit_recognizer_baseline.py   # 基线:RF / PCA+LR / MLP 三模型 3 折对比
├── digit_recognizer_cnn.py        # CNN:双层卷积 + 验证集最佳权重
├── digit_recognizer_cnn_kaggle.py # Kaggle Notebook 版 CNN(自适应路径 + GPU)
└── README.md
```

## 提交记录(2026-08-18)

| 版本 | 文件 | 模型思路 | 本地验证 | 公开榜 |
|---|---|---|---|---|
| baseline | `submissions/submission_baseline.csv` | RF / PCA+LR / MLP 3 折对比,RF 最优 | 0.9602 (3折CV) | 0.96378 |
| **cnn** | `submissions/submission_cnn.csv` | **双层 CNN(Conv32→Conv64→FC128→10),Adam,10 epoch** | **0.9893 (验证集)** | **0.98778** |

**关键结论**:

- **CNN 比 RF 基线提升 +0.024**(0.96378 → 0.98778),验证集 0.9893 与公开榜
  0.98778 基本一致——CNN 的卷积平移不变性对手写数字是碾压级优势;
- **图像工作流入门**:CSV 像素 → reshape 为 `(N,1,28,28)` → 归一化 /255 →
  卷积+池化 → 全连接;MLP(0.954)证明了"全连接吃不下空间结构",CNN 才是图像的正解;
- **训练技巧**:验证集 10% 分层划分、保留最佳权重(不拿最后 epoch)、
  Dropout(0.5)防过拟合、Adam 1e-3、batch 256;10 epoch 在 CPU 上约 1-2 分钟。
- torch 安装注意:官方源 `download.pytorch.org` 在本机网络被拦(SSL 握手失败),
  需用 CPU 版镜像(本次通过官方源偶发成功,备用方案为阿里云
  `https://mirrors.aliyun.com/pytorch-wheels/cpu/`)。

## 使用方法

```bash
# 环境:conda activate kaggle(Python 3.11,含 torch 2.13 CPU 版)
python digit_recognizer/digit_recognizer_baseline.py   # 基线(RF)
python digit_recognizer/digit_recognizer_cnn.py        # CNN(当前最佳)
```

### 提交

```bash
# 需先 conda activate kaggle;NO_PROXY 绕过系统代理
NO_PROXY="*" no_proxy="*" HTTP_PROXY="" HTTPS_PROXY="" ALL_PROXY="" \
http_proxy="" https_proxy="" all_proxy="" \
kaggle competitions submit -c digit-recognizer \
  -f digit_recognizer/submissions/submission_cnn.csv -m "说明"
```

## 在 Kaggle Notebook 上跑 CNN(可选 GPU)

`digit_recognizer_cnn_kaggle.py` 与本地 CNN 完全同构(结果可对比),适配 Notebook:

1. 打开 https://www.kaggle.com/code → **New Notebook**
2. 右侧 **Settings → Accelerator** 可选 **GPU**(选了快几十倍;选不了也无所谓,CPU 也就 1-2 分钟)
3. **Add Input** → 搜索 **digit-recognizer** 挂载比赛数据(忘记挂也没关系,脚本会用内置 `kagglehub` 自动下载)
4. 把 `digit_recognizer_cnn_kaggle.py` 内容粘贴进单元格运行
   (或上传文件后 `!python digit_recognizer_cnn_kaggle.py`)
5. 跑完打印"提交文件已生成: /kaggle/working/submission_cnn.csv" → 右侧 **Submit to Competition**

脚本自动适配:优先扫描 `/kaggle/input/` 挂载的数据 → kagglehub 兜底 → 本地 `data/`;
GPU 可用则自动启用。预期:验证精度 ~0.989,公开榜 ~0.988(与本地一致)。

## 进阶方向(无截止日期)

1. **数据增强**(随机平移/旋转/缩放)——手写数字赛最大的提升来源,公开榜可到 0.995+
2. **更深的 CNN**(VGG 风格堆叠层、BatchNorm)——0.997+
3. **换 Kaggle Notebook + GPU 跑**(torch 官方源在本机网络不稳,Notebook 里
   自带 GPU 版 torch,训练快几十倍,且 Kaggle 平台可直接提交)
4. 之后可以把这个 CNN 模板迁移到 torchvision 数据集流程,接真实图像比赛
