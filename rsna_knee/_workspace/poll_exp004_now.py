from __future__ import annotations

import os
import time

for k in list(os.environ):
    if "PROXY" in k.upper() or "proxy" in k:
        del os.environ[k]
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
slug = "ziyiming/rsna-exp-004-axial-fold0-gpu"
for i in range(6):
    try:
        api.authenticate()
        st = api.kernels_status(slug)
        print("STATUS", st.to_dict() if hasattr(st, "to_dict") else st)
        ks = api.kernels_list(user="ziyiming", search="exp-004", page_size=5)
        for k in ks or []:
            print("LIST", k.to_dict() if hasattr(k, "to_dict") else k)
        # try logs tail
        try:
            logs = api.kernels_logs(slug)
            if isinstance(logs, bytes):
                logs = logs.decode("utf-8", "replace")
            text = logs if isinstance(logs, str) else str(logs)
            print("LOG_LEN", len(text))
            print(text[-2500:])
        except Exception as e:
            print("LOG_ERR", type(e).__name__, str(e)[:200])
        break
    except Exception as e:
        print(f"try{i}", type(e).__name__, str(e)[:160])
        time.sleep(5)
