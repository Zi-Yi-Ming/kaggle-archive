# -*- coding: utf-8 -*-
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()
mr = api.competition_list_topic_messages(competition="kaggriculture", topic_id=730708)
print("resp attrs", [a for a in dir(mr) if not a.startswith("_")])
msgs = getattr(mr, "messages", None) or getattr(mr, "result", None) or []
print("n", len(msgs) if hasattr(msgs, "__len__") else msgs)
if msgs:
    m0 = msgs[0]
    print(type(m0))
    print([a for a in dir(m0) if not a.startswith("_")])
    import pprint
    if hasattr(m0, "to_dict"):
        pprint.pp(m0.to_dict())
    else:
        pprint.pp({k: getattr(m0, k, None) for k in dir(m0) if not k.startswith("_")})
