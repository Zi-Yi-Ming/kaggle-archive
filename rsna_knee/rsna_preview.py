# -*- coding: utf-8 -*-
"""
RSNA Knee 数据预览:下载后运行,查看 train/test CSV 结构与 DICOM 组织方式。
用法:先 kaggle competitions download -c rsna-knee-abnormality-detection
     然后运行本脚本(自动在 rsna_knee/ 下找解压出的 CSV)。
"""
import os
import glob

BASE = os.path.dirname(os.path.abspath(__file__))


def find(pattern):
    hits = glob.glob(os.path.join(BASE, pattern)) + glob.glob(os.path.join(BASE, "**", pattern), recursive=True)
    return hits


def main():
    import pandas as pd

    for f in ["train.csv", "test.csv", "sample_submission.csv", "train_series.csv", "test_series.csv"]:
        hits = find(f)
        if not hits:
            print(f"[缺失] {f} —— 先运行 kaggle competitions download")
            continue
        p = hits[0]
        df = pd.read_csv(p)
        print(f"\n===== {f} ({p}) =====")
        print(f"shape: {df.shape}")
        print(f"columns: {list(df.columns)}")
        print(df.head(3).to_string())
        if "StudyInstanceUID" in df.columns:
            print(f"唯一 study 数: {df['StudyInstanceUID'].nunique()}")

    # DICOM 目录结构抽样
    dcm = find("*.dcm")
    print(f"\n===== DICOM 文件 =====")
    if dcm:
        print(f"共找到 {len(dcm)} 个 .dcm(样本)")
        for d in dcm[:5]:
            print(" ", d)
        # 一个 study 的序列组织
        import numpy as np
        try:
            import pydicom
            d = pydicom.dcmread(dcm[0], stop_before_pixels=True)
            print(f"\nDICOM 元数据示例({os.path.basename(dcm[0])}):")
            for tag in ["PatientID", "StudyInstanceUID", "SeriesInstanceUID",
                        "Modality", "SeriesDescription", "Rows", "Columns",
                        "SliceThickness", "SpacingBetweenSlices", "MagneticFieldStrength"]:
                print(f"  {tag}: {d.get(tag, 'N/A')}")
        except ImportError:
            print("未安装 pydicom,跳过元数据读取(pip install pydicom)")
    else:
        print("未找到 .dcm(数据还没解压)")


if __name__ == "__main__":
    main()
