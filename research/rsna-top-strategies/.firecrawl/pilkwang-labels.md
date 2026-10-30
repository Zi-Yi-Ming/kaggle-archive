[Pilkwang Kim's profile](https://www.kaggle.com/pilkwang) Pilkwang Kim  · Updated 2 months ago

arrow\_drop\_up26

codeCode

file\_downloadDownload

![](https://www.kaggle.com/static/images/medals/datasets/silverl@2x.png)

more\_vert

# RSNA Knee LLM-read report labels

Twelve findings per study, read from the report by a language model

![](https://storage.googleapis.com/kaggle-datasets-images/11529209/18673450/c7004212f5acd212002f80f55b893c83/dataset-cover.png?t=2026-08-06-10-38-31)

## RSNA Knee LLM-read report labels

[Data Card](https://www.kaggle.com/datasets/pilkwang/rsna-knee-llm-labels/data) [Code (345)](https://www.kaggle.com/datasets/pilkwang/rsna-knee-llm-labels/code) [Discussion (0)](https://www.kaggle.com/datasets/pilkwang/rsna-knee-llm-labels/discussion) [Suggestions (0)](https://www.kaggle.com/datasets/pilkwang/rsna-knee-llm-labels/suggestions)

## About Dataset

Twelve per-study scores with per-target confidences and the underlying verdicts, obtained by having a language model read each radiology report in its original language.

Why this exists: a rule extractor matches morphology, and its failure mode is silence rather than error. Silence is measurable without ground truth - for each (report, finding) pair, did anything match? - and that measurement shows the misses concentrate in particular languages, on findings a knee report almost always comments on. Enumerating morphology for nine languages is the wrong instrument for that; reading the sentence is the right one.

Each report is answered as twelve (verdict, severity) pairs under a constrained response schema, so a reply that does not fit the twelve-finding shape cannot be returned. Verdicts are YES / NO / UNK, where NO means the report denies the finding or calls the structure normal and UNK means the report does not mention it. Severity grades how emphatic an assertion is, which matters because the reports are unthresholded while the annotations are not. Scores are rank-usable, not calibrated probabilities.

Columns: StudyInstanceUID, then per finding

## Usability

info

5.88

## License

[CC0: Public Domain](https://creativecommons.org/publicdomain/zero/1.0/)

## Expected update frequency

Not specified

## Tags

## api\_labeler.py(12.98 kB)

get\_app

fullscreen

chevron\_right

"""
Read knee MRI reports with a hosted model, as a second reader where the rules go silent.

Relationship to the other two extractors
\-\-\--------------------------------------
\`report\_labeler\` is a lexicon: fast, free, and strong on the vocabulary it knows. Its
failure mode is silence, and silence is measurable without labels - for each (report,
finding) pair, did any rule match? That measurement says the gaps are concentrated in a
few languages rather than spread evenly, which is what makes a second reader worth
buying: it is only asked to read the pairs the rules left blank.

\`llm\_labeler\` runs local weights and answers the same question at roughly eighteen
seconds a report. That is affordable while a prompt is being tuned and unaffordable
across the corpus several times over.

This module is the same prompt against a hosted model. Three things change:

\\* \*\*The output shape is enforced, not parsed.\*\* The local path asks for twelve numbered
lines and reads them with a tolerant regex, because a quantised model asked for JSON
will sometimes emit prose. Here the response is constrained to a schema, so a reply
that does not fit the twelve-finding shape cannot be returned at all. There is no
parser to be lenient with, and therefore no silent mis-parse.

\\* \*\*The instructions are hoisted out of the per-report text.\*\* Caching matches on a
prefix, so the half of the prompt that never changes - the task and the twelve
definitions - is sent as a system block and marked cacheable, and the report is the
only thing that varies. Across thousands of reports the fixed half is charged once
per cache lifetime instead of once per report.

\\* \*\*Requests are submitted in bulk.\*\* Nothing here is latency-sensitive; this runs
offline and its output is a CSV. Bulk submission halves the price for the same work.

The result is a per-study record with the same fields the local path writes, so the two
are interchangeable downstream and can be compared against the annotated studies on
equal terms before either is trusted.
"""

from \_\_future\_\_ import annotations

import json
import os
import threading
import time
from pathlib import Path

from llm\_labeler import FINDING\_SPEC, TARGETS, to\_scores

\# Order is load-bearing: these keys index the same twelve findings as TARGETS, and the
\# scoring code reads them positionally.
KEYS = \[\
"acl", "mcl", "medial\_meniscus", "lateral\_meniscus",\
"medial\_oa", "lateral\_oa", "pf\_oa", "effusion",\
"synovitis", "bakers", "contusion", "fracture",\
\]

SYSTEM = """You are an expert musculoskeletal radiologist reading a knee MRI report.
Reports may be written in any language, including Greek, Bulgarian, Turkish, Croatian,
Dutch, German, Spanish, French or English. Read each one in its original language.

For each of the twelve findings below, state what THE REPORT IN FRONT OF YOU says.

{spec}
verdict:
YES the report asserts the finding is present
NO the report denies it, or describes that structure as normal, intact or preserved
UNK the report does not mention it at all, or is explicitly uncertain

severity (0 whenever the verdict is not YES):
1 minimal, trace, small, mild, slight, grade 1
2 stated without qualification, moderate
3 marked, large, severe, extensive, complete, full-thickness, grade 3-4

Rules you must follow:
\- Judge only what the report states. Do not infer a finding from a related one.
\- A structure described as normal or intact is NO, not UNK.
\- A finding the report never names is UNK, not NO.
\- Medial and lateral are distinct. If the report names one, the other is not thereby
answered.
""".format(spec=FINDING\_SPEC)

\# A schema, not a format request. The response is constrained to this shape, so the
\# twelve keys are always present and the verdict is always one of three strings; there
\# is no reply that parses into a partial answer.
\_FINDING = {
"type": "object",
"properties": {
"verdict": {"type": "string", "enum": \["YES", "NO", "UNK"\]},
"severity": {"type": "integer", "enum": \[0, 1, 2, 3\]},
},
"required": \["verdict", "severity"\],
"additionalProperties": False,
}
SCHEMA = {
"type": "object",
"properties": {k: {"$ref": "#/$defs/finding"} for k in KEYS},
"required": KEYS,
"additionalProperties": False,
"$defs": {"finding": \_FINDING},
}

def \_key(explicit=None):
"""Resolve the credential without ever putting it on a command line."""
if explicit:
return explicit
if os.environ.get("ANTHROPIC\_API\_KEY"):
return os.environ\["ANTHROPIC\_API\_KEY"\]
p = Path.home() / ".config" / "rsna\_llm\_key"
if p.is\_file():
return p.read\_text().strip()
raise RuntimeError(
"No API key. Put it in ~/.config/rsna\_llm\_key (chmod 600) or set ANTHROPIC\_API\_KEY."
)

def \_verdicts(obj):
"""Schema-validated object -> the (verdict, severity) pairs the scorer expects."""
out = \[\]
for k in KEYS:
f = obj\[k\]
v = f\["verdict"\]
out.append((v, f\["severity"\] if v == "YES" else 0))
return out

def \_record(uid, obj, secs, usage=None):
verdicts = \_verdicts(obj)
score, conf = to\_scores(verdicts)
rec = {
"uid": uid,
"verdict": \[v for v, \_ in verdicts\],
"severity": \[s for \_, s in verdicts\],
"score": score,
"conf": conf,
"secs": round(secs, 2),
"raw": json.dumps(obj, ensure\_ascii=False),
}
if usage:
rec\["usage"\] = usage
return rec

class ApiLabeler:
"""One report at a time. Use this to tune the prompt; use \`submit\_batch\` to run it.

\`effort\` is the cost lever. Twelve bounded judgements over a page of text is a short,
scoped task, so the low setting is the starting point rather than a compromise; raise
it only if the annotated studies say the reading is shallow.
"""

def \_\_init\_\_(self, model="claude-opus-5", effort="low", api\_key=None,
cache\_path=None, max\_tokens=2000):
import anthropic
self.client = anthropic.Anthropic(api\_key=\_key(api\_key))
self.model = model
self.effort = effort
self.max\_tokens = max\_tokens
self.cache\_path = Path(cache\_path) if cache\_path else None
self.cache = {}
if self.cache\_path and self.cache\_path.is\_file():
for line in self.cache\_path.read\_text().splitlines():
if line.strip():
d = json.loads(line)
self.cache\[d\["uid"\]\] = d
self.n\_new = 0
# Reports are independent, so the obvious way to run a few hundred is a thread
# pool. Only the shared cache needs guarding; the client is already safe.
self.\_lock = threading.Lock()

def \_store(self, rec):
with self.\_lock:
self.cache\[rec\["uid"\]\] = rec
self.n\_new += 1
if self.cache\_path:
with self.cache\_path.open("a") as fh:
fh.write(json.dumps(rec, ensure\_ascii=False) + "\\n")

def \_params(self, report):
"""The request body, shared by the single-call and bulk paths.

The system block carries everything that does not vary and is marked cacheable;
the user turn carries only the report. Any content placed above a changing byte
stops being reusable, so the ordering here is the whole point.
"""
return dict(
model=self.model,
max\_tokens=self.max\_tokens,
system=\[{"type": "text", "text": SYSTEM,\
"cache\_control": {"type": "ephemeral"}}\],
messages=\[{"role": "user", "content": report.strip()\[:12000\]}\],
output\_config={
"effort": self.effort,
"format": {"type": "json\_schema", "schema": SCHEMA},
},
)

def label(self, uid, report):
if uid in self.cache:
return self.cache\[uid\]
t = time.time()
resp = self.client.messages.create(\*\*self.\_params(report))
obj = json.loads(next(b.text for b in resp.content if b.type == "text"))
u = resp.usage
rec = \_record(uid, obj, time.time() - t, {
"in": u.input\_tokens, "out": u.output\_tokens,
"cache\_read": getattr(u, "cache\_read\_input\_tokens", 0),
"cache\_write": getattr(u, "cache\_creation\_input\_tokens", 0),
})
self.\_store(rec)
return rec

def label\_many(self, items, workers=8, progress=None):
"""items: \[(uid, report), ...\] -> records, in the order given."""
from concurrent.futures import ThreadPoolExecutor
done = \[0\]

def one(it):
r = self.label(\*it)
done\[0\] += 1
if progress and done\[0\] % progress == 0:
print(f" {done\[0\]}/{len(items)}", flush=True)
return r

with ThreadPoolExecutor(workers) as ex:
return list(ex.map(one, items))

def \_map\_path(self, batch\_id):
base = self.cache\_path or Path("batch")
return base.with\_suffix(f".{batch\_id}.map.json")

def submit\_batch(self, items):
"""items: \[(uid, report), ...\] -> batch id. Skips anything already cached.

A study UID contains dots and can reach 64 characters, and \`custom\_id\` accepts
only \[A-Za-z0-9\_-\] within 64. So requests are keyed by position and the mapping
back to UIDs is written beside the cache - results can then be collected by a
later process, which matters because a batch may take an hour.
"""
todo = \[(u, r) for u, r in items if u not in self.cache\]
if not todo:
return None
ids = {f"r{i:06d}": u for i, (u, \_) in enumerate(todo)}
batch = self.client.messages.batches.create(
requests=\[{"custom\_id": f"r{i:06d}", "params": self.\_params(r)}\
for i, (\_, r) in enumerate(todo)\]
)
self.\_map\_path(batch.id).write\_text(json.dumps(ids))
return batch.id

def collect\_batch(self, batch\_id, poll\_s=60, timeout\_s=7200):
"""Block until the batch ends, then fold its results into the cache."""
t0 = time.time()
while True:
b = self.client.messages.batches.retrieve(batch\_id)
if b.processing\_status == "ended":
break
if time.time() - t0 > timeout\_s:
raise TimeoutError(f"{batch\_id} still {b.processing\_status}")
print(f" {b.processing\_status} {b.request\_counts}", flush=True)
time.sleep(poll\_s)

ids = json.loads(self.\_map\_path(batch\_id).read\_text())
ok = err = 0
# Results come back in arbitrary order; custom\_id is the only safe key.
for res in self.client.messages.batches.results(batch\_id):
if res.result.type != "succeeded":
err += 1
continue
msg = res.result.message
obj = json.loads(next(x.text for x in msg.content if x.type == "text"))
u = msg.usage
rec = \_record(ids\[res.custom\_id\], obj, 0.0, {
"in": u.input\_tokens, "out": u.output\_tokens,
"cache\_read": getattr(u, "cache\_read\_input\_tokens", 0),
"cache\_write": getattr(u, "cache\_creation\_input\_tokens", 0),
})
self.\_store(rec)
ok += 1
return ok, err

def cost(self, rate\_in=5.0, rate\_out=25.0):
"""Dollars spent so far, from the usage the API reported.

Cache reads are charged at a tenth of the input rate and writes at 1.25x, so the
fixed half of the prompt is only expensive the first time it is sent.
"""
ti = to = tr = tw = 0
for r in self.cache.values():
u = r.get("usage") or {}
ti += u.get("in", 0); to += u.get("out", 0)
tr += u.get("cache\_read", 0); tw += u.get("cache\_write", 0)
d = (ti + tw \* 1.25 + tr \* 0.1) / 1e6 \* rate\_in + to / 1e6 \* rate\_out
return {"input": ti, "output": to, "cache\_read": tr, "cache\_write": tw,
"usd\_full\_rate": round(d, 4), "usd\_batch\_rate": round(d / 2, 4)}

def count\_prefix\_tokens(model="claude-opus-5", api\_key=None):
"""How large is the cacheable half? Below the model's minimum it silently won't cache."""
import anthropic
c = anthropic.Anthropic(api\_key=\_key(api\_key))
r = c.messages.count\_tokens(
model=model,
system=\[{"type": "text", "text": SYSTEM}\],
messages=\[{"role": "user", "content": "x"}\],
)
return r.input\_tokens

def frame(records):
"""Same column layout the other two extractors emit."""
import pandas as pd
rows = \[\]
for r in records:
row = {"StudyInstanceUID": r\["uid"\]}
for j, t in enumerate(TARGETS):
row\[t\] = r\["score"\]\[j\]
row\[t + "\_\_conf"\] = r\["conf"\]\[j\]
row\[t + "\_\_verdict"\] = r\["verdict"\]\[j\]
rows.append(row)
return pd.DataFrame(rows)

## Data Explorer

Version 1 (1.02 MB)

- code






api\_labeler.py

- calendar\_view\_week






report\_labels\_v2.csv


## Summary

arrow\_right

folder

2 files

arrow\_right

calendar\_view\_week

37 columns

lightbulb

## See what others are saying about this dataset

### What have you used this dataset for?

Learning 0Research 0Application 0LLM Fine-Tuning 0

### How would you describe this dataset?

Well-documented 0Well-maintained 0Clean data 0Original 0High-quality notebooks 0Other

text\_snippet

## Metadata

unfold\_moreExpand All

### Collaborators

keyboard\_arrow\_down

### Authors

keyboard\_arrow\_down

### Coverage

keyboard\_arrow\_down

### DOI Citation

keyboard\_arrow\_down

### Provenance

keyboard\_arrow\_down

### License

keyboard\_arrow\_down

### Expected Update Frequency

keyboard\_arrow\_down

insights

## Activity Overview

visibility

### Views

2654

| date | Views |
| --- | --- |
| Aug 30, 2026 | 37 |
| Aug 31, 2026 | 31 |
| Sep 1, 2026 | 37 |
| Sep 2, 2026 | 49 |
| Sep 3, 2026 | 39 |
| Sep 4, 2026 | 42 |
| Sep 5, 2026 | 41 |
| Sep 6, 2026 | 48 |
| Sep 7, 2026 | 50 |
| Sep 8, 2026 | 28 |
| Sep 9, 2026 | 48 |
| Sep 10, 2026 | 56 |
| Sep 11, 2026 | 47 |
| Sep 12, 2026 | 39 |
| Sep 13, 2026 | 29 |
| Sep 14, 2026 | 62 |
| Sep 15, 2026 | 67 |
| Sep 16, 2026 | 54 |
| Sep 17, 2026 | 43 |
| Sep 18, 2026 | 42 |
| Sep 19, 2026 | 45 |
| Sep 20, 2026 | 43 |
| Sep 21, 2026 | 35 |
| Sep 22, 2026 | 25 |
| Sep 23, 2026 | 38 |
| Sep 24, 2026 | 33 |
| Sep 25, 2026 | 32 |
| Sep 26, 2026 | 48 |
| Sep 27, 2026 | 40 |

| date | Views |
| --- | --- |
| Aug 30, 2026 | 37 |
| Aug 31, 2026 | 31 |
| Sep 1, 2026 | 37 |
| Sep 2, 2026 | 49 |
| Sep 3, 2026 | 39 |
| Sep 4, 2026 | 42 |
| Sep 5, 2026 | 41 |
| Sep 6, 2026 | 48 |
| Sep 7, 2026 | 50 |
| Sep 8, 2026 | 28 |
| Sep 9, 2026 | 48 |
| Sep 10, 2026 | 56 |
| Sep 11, 2026 | 47 |
| Sep 12, 2026 | 39 |
| Sep 13, 2026 | 29 |
| Sep 14, 2026 | 62 |
| Sep 15, 2026 | 67 |
| Sep 16, 2026 | 54 |
| Sep 17, 2026 | 43 |
| Sep 18, 2026 | 42 |
| Sep 19, 2026 | 45 |
| Sep 20, 2026 | 43 |
| Sep 21, 2026 | 35 |
| Sep 22, 2026 | 25 |
| Sep 23, 2026 | 38 |
| Sep 24, 2026 | 33 |
| Sep 25, 2026 | 32 |
| Sep 26, 2026 | 48 |
| Sep 27, 2026 | 40 |

trending\_up1228in the last 30 days

download

### Downloads

4886

| date | Downloads |
| --- | --- |
| Aug 30, 2026 | 63 |
| Aug 31, 2026 | 61 |
| Sep 1, 2026 | 97 |
| Sep 2, 2026 | 89 |
| Sep 3, 2026 | 64 |
| Sep 4, 2026 | 96 |
| Sep 5, 2026 | 72 |
| Sep 6, 2026 | 74 |
| Sep 7, 2026 | 80 |
| Sep 8, 2026 | 75 |
| Sep 9, 2026 | 67 |
| Sep 10, 2026 | 76 |
| Sep 11, 2026 | 66 |
| Sep 12, 2026 | 65 |
| Sep 13, 2026 | 84 |
| Sep 14, 2026 | 72 |
| Sep 15, 2026 | 92 |
| Sep 16, 2026 | 87 |
| Sep 17, 2026 | 74 |
| Sep 18, 2026 | 97 |
| Sep 19, 2026 | 102 |
| Sep 20, 2026 | 119 |
| Sep 21, 2026 | 75 |
| Sep 22, 2026 | 86 |
| Sep 23, 2026 | 93 |
| Sep 24, 2026 | 103 |
| Sep 25, 2026 | 95 |
| Sep 26, 2026 | 98 |
| Sep 27, 2026 | 110 |

| date | Downloads |
| --- | --- |
| Aug 30, 2026 | 63 |
| Aug 31, 2026 | 61 |
| Sep 1, 2026 | 97 |
| Sep 2, 2026 | 89 |
| Sep 3, 2026 | 64 |
| Sep 4, 2026 | 96 |
| Sep 5, 2026 | 72 |
| Sep 6, 2026 | 74 |
| Sep 7, 2026 | 80 |
| Sep 8, 2026 | 75 |
| Sep 9, 2026 | 67 |
| Sep 10, 2026 | 76 |
| Sep 11, 2026 | 66 |
| Sep 12, 2026 | 65 |
| Sep 13, 2026 | 84 |
| Sep 14, 2026 | 72 |
| Sep 15, 2026 | 92 |
| Sep 16, 2026 | 87 |
| Sep 17, 2026 | 74 |
| Sep 18, 2026 | 97 |
| Sep 19, 2026 | 102 |
| Sep 20, 2026 | 119 |
| Sep 21, 2026 | 75 |
| Sep 22, 2026 | 86 |
| Sep 23, 2026 | 93 |
| Sep 24, 2026 | 103 |
| Sep 25, 2026 | 95 |
| Sep 26, 2026 | 98 |
| Sep 27, 2026 | 110 |

trending\_up2432in the last 30 days

downloading

### Engagement

1.84099

downloads per view

forum

### Comments

0

posted

person

### Top Contributors

[Mattia Angeli's profile](https://www.kaggle.com/mattiaangeli)[Pilkwang Kim's profile](https://www.kaggle.com/pilkwang)[prvsiyan's profile](https://www.kaggle.com/prvsiyan)

### Detail View

keyboard\_arrow\_up

#### Views

Last month

08/3109/0709/1409/210255075

| date | Views |
| --- | --- |
| Aug 30, 2026 | 37 |
| Aug 31, 2026 | 31 |
| Sep 1, 2026 | 37 |
| Sep 2, 2026 | 49 |
| Sep 3, 2026 | 39 |
| Sep 4, 2026 | 42 |
| Sep 5, 2026 | 41 |
| Sep 6, 2026 | 48 |
| Sep 7, 2026 | 50 |
| Sep 8, 2026 | 28 |
| Sep 9, 2026 | 48 |
| Sep 10, 2026 | 56 |
| Sep 11, 2026 | 47 |
| Sep 12, 2026 | 39 |
| Sep 13, 2026 | 29 |
| Sep 14, 2026 | 62 |
| Sep 15, 2026 | 67 |
| Sep 16, 2026 | 54 |
| Sep 17, 2026 | 43 |
| Sep 18, 2026 | 42 |
| Sep 19, 2026 | 45 |
| Sep 20, 2026 | 43 |
| Sep 21, 2026 | 35 |
| Sep 22, 2026 | 25 |
| Sep 23, 2026 | 38 |
| Sep 24, 2026 | 33 |
| Sep 25, 2026 | 32 |
| Sep 26, 2026 | 48 |
| Sep 27, 2026 | 40 |

| date | Views |
| --- | --- |
| Aug 30, 2026 | 37 |
| Aug 31, 2026 | 31 |
| Sep 1, 2026 | 37 |
| Sep 2, 2026 | 49 |
| Sep 3, 2026 | 39 |
| Sep 4, 2026 | 42 |
| Sep 5, 2026 | 41 |
| Sep 6, 2026 | 48 |
| Sep 7, 2026 | 50 |
| Sep 8, 2026 | 28 |
| Sep 9, 2026 | 48 |
| Sep 10, 2026 | 56 |
| Sep 11, 2026 | 47 |
| Sep 12, 2026 | 39 |
| Sep 13, 2026 | 29 |
| Sep 14, 2026 | 62 |
| Sep 15, 2026 | 67 |
| Sep 16, 2026 | 54 |
| Sep 17, 2026 | 43 |
| Sep 18, 2026 | 42 |
| Sep 19, 2026 | 45 |
| Sep 20, 2026 | 43 |
| Sep 21, 2026 | 35 |
| Sep 22, 2026 | 25 |
| Sep 23, 2026 | 38 |
| Sep 24, 2026 | 33 |
| Sep 25, 2026 | 32 |
| Sep 26, 2026 | 48 |
| Sep 27, 2026 | 40 |

75

#### Downloads

Last month

08/3109/0709/1409/216080100120

| date | Downloads |
| --- | --- |
| Aug 30, 2026 | 63 |
| Aug 31, 2026 | 61 |
| Sep 1, 2026 | 97 |
| Sep 2, 2026 | 89 |
| Sep 3, 2026 | 64 |
| Sep 4, 2026 | 96 |
| Sep 5, 2026 | 72 |
| Sep 6, 2026 | 74 |
| Sep 7, 2026 | 80 |
| Sep 8, 2026 | 75 |
| Sep 9, 2026 | 67 |
| Sep 10, 2026 | 76 |
| Sep 11, 2026 | 66 |
| Sep 12, 2026 | 65 |
| Sep 13, 2026 | 84 |
| Sep 14, 2026 | 72 |
| Sep 15, 2026 | 92 |
| Sep 16, 2026 | 87 |
| Sep 17, 2026 | 74 |
| Sep 18, 2026 | 97 |
| Sep 19, 2026 | 102 |
| Sep 20, 2026 | 119 |
| Sep 21, 2026 | 75 |
| Sep 22, 2026 | 86 |
| Sep 23, 2026 | 93 |
| Sep 24, 2026 | 103 |
| Sep 25, 2026 | 95 |
| Sep 26, 2026 | 98 |
| Sep 27, 2026 | 110 |

| date | Downloads |
| --- | --- |
| Aug 30, 2026 | 63 |
| Aug 31, 2026 | 61 |
| Sep 1, 2026 | 97 |
| Sep 2, 2026 | 89 |
| Sep 3, 2026 | 64 |
| Sep 4, 2026 | 96 |
| Sep 5, 2026 | 72 |
| Sep 6, 2026 | 74 |
| Sep 7, 2026 | 80 |
| Sep 8, 2026 | 75 |
| Sep 9, 2026 | 67 |
| Sep 10, 2026 | 76 |
| Sep 11, 2026 | 66 |
| Sep 12, 2026 | 65 |
| Sep 13, 2026 | 84 |
| Sep 14, 2026 | 72 |
| Sep 15, 2026 | 92 |
| Sep 16, 2026 | 87 |
| Sep 17, 2026 | 74 |
| Sep 18, 2026 | 97 |
| Sep 19, 2026 | 102 |
| Sep 20, 2026 | 119 |
| Sep 21, 2026 | 75 |
| Sep 22, 2026 | 86 |
| Sep 23, 2026 | 93 |
| Sep 24, 2026 | 103 |
| Sep 25, 2026 | 95 |
| Sep 26, 2026 | 98 |
| Sep 27, 2026 | 110 |

120

code

## Related Notebooks

See all

[![](https://www.kaggleusercontent.com/kf/340906482/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..rxKxeRKcawKasPSlbOg9Fw.JSjoPKVM8eSxsrrVHzU6twM4kkxMKgd-9I8_Ga6Zda9NzSknHWhRjlGA2w0_g511o3fuvMHITKJHNVbF26pvrJ9315kMg4o7AnDSGdgmhD5XVxTb3tkvK_3TPeLM9afOeGQYiFfrQfCgPS96oocZ3I1ArgQssUAEdfx-3Vi5XZhDsrCZRiC9AGTFlff3--FhK8bPsDbhEOvjTLzO46Ui6ktY-ThX__VK4b52N_iQ08UpKT5FXRFbHtMGS3lnHFw6S67ldfTF3ffhYyBcjGpEHh36Iw1-2uOT0-bY43naz44xtwDnruY_vyj8C4SR14Qep1De9YZtTAYA00OzBOJiHzDGR8hbDU4Bh0Il9nO--jSPPJlQpcejQ2PR0f0JJqTTlbI9XGPhsBLs65q5LeP6PHZ3fKzWCRm_UAzGnqvWvXgteSVOanUZ8vCyoTpnXbvYb-FDxm7BVjsjgl3u6fBGmAECf6UjLRKlRCW2GA8eETAJxiOPZeNdQkRVOsvlnfNMIdM8o6eFyaUwN0tvbbou3rWf_RnDiDjApGUFbeW3XpXTi5kHgtazkkWcujK2eIgiKk6o8MMd9KuOsdeeuf6lwcfgughny2e0AoYq3-JQbBE.kEw_h6G_aTn8DX60WOQXzg/__results___files/__results___0_0.png)\\
\\
RSNA Knee baseline v1\\
\\
more\_vert\\
\\
Updated 2 months ago\\
\\
RSNA Knee LLM-read report labels+4](https://www.kaggle.com/code/pilkwang/rsna-knee-baseline-v1)

arrow\_drop\_up642

![](https://www.kaggle.com/static/images/medals/competitions/goldl@2x.png)[Pilkwang Kim's profile (opens in a new tab)](https://www.kaggle.com/pilkwang)

[![](https://storage.googleapis.com/kaggle-datasets-images/new-version-temp-images/default-backgrounds-82.png-18800101/dataset-thumbnail.png)\\
\\
Bend the Knee to the Dinosaurs\\
\\
more\_vert\\
\\
Updated 15 days ago\\
\\
resnet-50-RadImageNet-Marwan+15](https://www.kaggle.com/code/mattiaangeli/bend-the-knee-to-the-dinosaurs)

arrow\_drop\_up285

![](https://www.kaggle.com/static/images/medals/competitions/goldl@2x.png)[Mattia Angeli's profile (opens in a new tab)](https://www.kaggle.com/mattiaangeli)

[![](https://www.kaggleusercontent.com/kf/341789600/eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..1hCmcXL6aq6tTZPzC-47Uw.qwqJbcS3Y6xRcRQzR2a0F6vTn6V4H8QzD0UnBgsSU_n8TiC3TFL598fpo_9_nPeSJ7jfzg0snuEMCL1YR9GtAzqu2hneNXCwyaZ1egPUFErWeVNsQtg-EgdYKXBxYsaxJXcAnL4F13_K3pfJunE07Tz5lszDZ4-j_oR2Y8OA49l498Lb8OMh1GXSv0QASmvZIGsZ5Uqns9NirFvEZra-2X-EWwb1ZSJuGxpBL8TWJv6TBGvh5aLl2JkLW6sDs6Lz7rhPrKk7vHsVXCEMGTgURz6UIVV6bPPjT59T9WsHJVKMhw53ue1oLhsh4fNpbVXJgub_BlXiIFmhdTr0BER89IDafESQy1tYTu8gIx1LrL3J5O5TPRmZYMRM0P7vmFpF1CG0j1PY9Xt3jQWY2r8i29TAXwEyFCVvz2Rjvldtblyyt02ufj7fqhKsA7kSNpPy6RUPvjKLVqXFBtUJwaaKU0yA-KnOrLnKl6X0wq24zd0ZHaIoJmqJeCMKsKvzxAvHX0xNc1f0J0Iq_l-lQRVXHgttcwVASE7p9Oo7JrI-1zEFh57ZNe_M5DLMqWX_mE3r8HopjKw7h9efJbFpcZOldzq79VVup4fwDC7gMPFdIBgC0kX22Rjkq-J7PJbKY307unANP4pVtBVbxd1GB-8oWA.suiPyvWt_Cxt2ZdRCuD-1w/__results___files/__results___10_1.png)\\
\\
RSNA Knee: read the report, then the knee\\
\\
more\_vert\\
\\
Updated 2 months ago\\
\\
rsna-medicalnet-resnet50-weights+18](https://www.kaggle.com/code/prvsiyan/rsna-knee-read-the-report-then-the-knee)

arrow\_drop\_up262

![](https://www.kaggle.com/static/images/medals/competitions/goldl@2x.png)[prvsiyan's profile (opens in a new tab)](https://www.kaggle.com/prvsiyan)

table\_chart

## You May Also Like

[![](https://storage.googleapis.com/kaggle-datasets-images/new-version-temp-images/default-backgrounds-40.png-13484631/dataset-thumbnail.png)](https://www.kaggle.com/datasets/yunusgmsoy/rsna-knee-llm-report-labels)

[RSNA Knee LLM Report Labels\\
\\
more\_vert](https://www.kaggle.com/datasets/yunusgmsoy/rsna-knee-llm-report-labels)

[Yunus Gümüşsoy](https://www.kaggle.com/yunusgmsoy)

Usability 4.7 · Updated a month ago

1 File (CSV) · 128 kB · 488 downloads

arrow\_drop\_up2

[Yunus Gümüşsoy's profile (opens in a new tab)](https://www.kaggle.com/yunusgmsoy)

[![](https://storage.googleapis.com/kaggle-datasets-images/new-version-temp-images/default-backgrounds-49.png-5954600/dataset-thumbnail.png)](https://www.kaggle.com/datasets/tasmeemreza/rsna-knee-refined-llm-labels)

[RSNA Knee Refined LLM Labels\\
\\
more\_vert](https://www.kaggle.com/datasets/tasmeemreza/rsna-knee-refined-llm-labels)

[tasmeem reza](https://www.kaggle.com/tasmeemreza)

Usability 4.7 · Updated a month ago

1 File (CSV) · 129 kB · 413 downloads

arrow\_drop\_up0

[tasmeem reza's profile (opens in a new tab)](https://www.kaggle.com/tasmeemreza)

[![](https://storage.googleapis.com/kaggle-datasets-images/11742423/19125270/cc223f1e84453683e79c7eadc05020ff/dataset-thumbnail.png?t=2026-08-23-17-27-34)](https://www.kaggle.com/datasets/dreaddevelopment/raptor-knee-widedense)

[Knee MRI model weights: twelve findings\\
\\
more\_vert](https://www.kaggle.com/datasets/dreaddevelopment/raptor-knee-widedense)

[Dread Development](https://www.kaggle.com/dreaddevelopment)

Usability 9.4 · Updated a month ago

2 Files (other) · 543 MB · 1,462 downloads

arrow\_drop\_up81

![](https://www.kaggle.com/static/images/medals/datasets/silverl@2x.png)[Dread Development's profile (opens in a new tab)](https://www.kaggle.com/dreaddevelopment)

[![](https://storage.googleapis.com/kaggle-datasets-images/new-version-temp-images/default-backgrounds-9.png-22562637/dataset-thumbnail.png)](https://www.kaggle.com/datasets/flight0234/rsna-knee-hybrid-report-labels)

[RSNA Knee hybrid report labels\\
\\
more\_vert](https://www.kaggle.com/datasets/flight0234/rsna-knee-hybrid-report-labels)

[Stephen Gardner](https://www.kaggle.com/flight0234)

Usability 5.3 · Updated 2 months ago

1 File (CSV) · 206 kB · 783 downloads

arrow\_drop\_up0

[Stephen Gardner's profile (opens in a new tab)](https://www.kaggle.com/flight0234)