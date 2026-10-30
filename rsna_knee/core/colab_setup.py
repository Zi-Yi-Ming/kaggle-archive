# -*- coding: utf-8 -*-
"""Colab 一键配置 kaggle + 下载 RSNA 数据。上传到 Colab 后运行即可。"""
import os
import shutil
import subprocess

# === 1. 配置 kaggle.json ===
if not os.path.exists(os.path.expanduser("~/.kaggle/kaggle.json")):
    print("请上传 kaggle.json 文件...")
    from google.colab import files
    uploaded = files.upload()
    if "kaggle.json" not in uploaded:
        print("错误: 没有上传 kaggle.json!")
        raise SystemExit(1)
    os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)
    shutil.move("kaggle.json", os.path.expanduser("~/.kaggle/kaggle.json"))
    os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)
    print("kaggle.json 配置完成!")
else:
    print("kaggle.json 已存在")

# === 2. 验证 API ===
r = subprocess.run(["kaggle", "competitions", "list", "--competition",
                    "rsna-knee-abnormality-detection"],
                   capture_output=True, text=True)
if r.returncode != 0:
    print(f"kaggle API 错误: {r.stderr}")
    raise SystemExit(1)
print(f"kaggle API 正常: {r.stdout[:100]}")

# === 3. 下载比赛数据 ===
WORK_DIR = "/content/rsna_knee"
COMP_DIR = os.path.join(WORK_DIR, "rsna-knee-abnormality-detection")
os.makedirs(COMP_DIR, exist_ok=True)

if not os.path.exists(os.path.join(COMP_DIR, "train_series")):
    print("下载比赛数据 (约30GB, 需15-30分钟)...")
    r = subprocess.run(["kaggle", "competitions", "download", "-c",
                        "rsna-knee-abnormality-detection", "-p", COMP_DIR],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"下载失败: {r.stderr}")
        raise SystemExit(1)
    print("解压 CSV...")
    for zf in ["train.csv.zip", "test.csv.zip", "sample_submission.csv.zip",
               "train_series.csv.zip", "test_series.csv.zip"]:
        zp = os.path.join(COMP_DIR, zf)
        if os.path.exists(zp):
            subprocess.run(["unzip", "-o", zp, "-d", COMP_DIR], check=True)
    print("解压 DICOM (约30GB, 需10-20分钟)...")
    dicom_zip = os.path.join(COMP_DIR, "train_series.zip")
    if os.path.exists(dicom_zip):
        subprocess.run(["unzip", "-o", dicom_zip, "-d", COMP_DIR], check=True)
    test_zip = os.path.join(COMP_DIR, "test_series.zip")
    if os.path.exists(test_zip):
        subprocess.run(["unzip", "-o", test_zip, "-d", COMP_DIR], check=True)
    print("比赛数据下载完成!")
else:
    print("比赛数据已存在")

# === 4. 下载软标签 + 预训练权重 ===
SOFT_DIR = os.path.join(WORK_DIR, "rsna-knee-stratified-folds-and-llm-soft-labels")
if not os.path.exists(SOFT_DIR):
    print("下载软标签...")
    subprocess.run(["kaggle", "datasets", "download", "-d",
                    "barun2104/rsna-knee-stratified-folds-and-llm-soft-labels",
                    "-p", SOFT_DIR, "--unzip"], check=True)
    print("软标签下载完成!")

WEIGHT_DIR = os.path.join(WORK_DIR, "resnet34-imagenet-pth")
if not os.path.exists(WEIGHT_DIR):
    print("下载预训练权重...")
    subprocess.run(["kaggle", "datasets", "download", "-d",
                    "matteonaccarato/resnet34-imagenet-pth",
                    "-p", WEIGHT_DIR, "--unzip"], check=True)
    print("预训练权重下载完成!")

# === 5. 创建符号链接 ===
TARGET = os.path.join(WORK_DIR, "rsna_knee")
os.makedirs(TARGET, exist_ok=True)

for f in ["train.csv", "test.csv", "sample_submission.csv",
          "train_series.csv", "test_series.csv"]:
    src = os.path.join(COMP_DIR, f)
    dst = os.path.join(TARGET, f)
    if os.path.exists(src) and not os.path.exists(dst):
        os.symlink(src, dst)

for d in ["train_series", "test_series"]:
    src = os.path.join(COMP_DIR, d)
    dst = os.path.join(TARGET, d)
    if os.path.isdir(src) and not os.path.exists(dst):
        os.symlink(src, dst)

for f in os.listdir(SOFT_DIR):
    src = os.path.join(SOFT_DIR, f)
    dst = os.path.join(TARGET, f)
    if os.path.isfile(src) and not os.path.exists(dst):
        os.symlink(src, dst)

for f in os.listdir(WEIGHT_DIR):
    src = os.path.join(WEIGHT_DIR, f)
    dst = os.path.join(TARGET, f)
    if os.path.isfile(src) and not os.path.exists(dst):
        os.symlink(src, dst)

print(f"\n配置完成! rsna_knee/ 内容:")
for f in sorted(os.listdir(TARGET)):
    print(f"  {f}")

print(f"\nGPU 信息:")
import torch
if torch.cuda.is_available():
    print(f"  {torch.cuda.get_device_name(0)}")
else:
    print("  没有 GPU! 请设置 Runtime -> T4 GPU")

print("\n下一步: 上传 rsna_v3.py 到 rsna_knee/ 目录, 然后运行训练")
print(f"训练命令: !cd {TARGET} && python rsna_v3.py --planes sagittal --epochs 5 --batch 16 --pretrained")
