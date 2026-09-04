# -*- coding: utf-8 -*-
"""RSNA 提交: 彻底绕代理(清空 HTTPS_PROXY + NO_PROXY=*),用 python kaggle 库。"""
import os

# 清掉代理相关环境变量, 让 requests 直连
for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from kaggle import KaggleApi

api = KaggleApi()
api.authenticate()
comp = "rsna-knee-abnormality-detection"
file_path = r"D:/桌面/Kaggle/submission.csv"
msg = "v3 baseline full-run: 3 planes ResNet34, pseudo+pretrained, 2 epochs"

print("开始提交...", flush=True)
api.competition_submit(file_path, msg, comp)
print("提交调用完成, 查询最新记录...", flush=True)
subs = api.competition_submissions(comp)
if subs:
    s = subs[0]
    print(f"最新提交: ref={s.ref} status={s.status} date={s.date}")
else:
    print("无提交记录")
