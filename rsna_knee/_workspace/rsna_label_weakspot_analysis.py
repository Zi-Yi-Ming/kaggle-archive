from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(r"D:/桌面/Kaggle/rsna_knee")
sys.path.insert(0, str(ROOT))
import rsna_report_labels as RL  # noqa: E402

OUT = Path(r"D:/桌面/Kaggle/_workspace/rsna_label_weakspots")
OUT.mkdir(parents=True, exist_ok=True)

WEAK = ["Synovitis", "Medial OA", "Lateral OA", "PF OA", "Fracture", "Contusion"]
COMPARE = ["ACL", "Effusion", "Medial Meniscus"]

train = pd.read_csv(ROOT / "train.csv")
pseudo = RL.build_pseudo_table(train, verbose=False)
pseudo = pseudo.set_index("StudyInstanceUID")

LABELS = RL.TARGETS
lines = []


def log(s=""):
    print(s)
    lines.append(s)


log("# 标签弱项分析：报告抽取器 vs 官方 gold")
log("")
log(f"train n={len(train)}; gold 仅 58/4407")
log("")

# per-label: gold agreement with pseudo
log("## Gold 对齐诊断（仅 58 例官方标注）")
log("")
log("| label | gold_n | pseudo有效 | agree | pos漏抓 | neg误报 | silent_on_gold_pos |")
log("|---|---:|---:|---:|---:|---:|---:|")
diag = {}
for c in LABELS:
    g = train[["StudyInstanceUID", c]].dropna(subset=[c])
    p = pseudo["pseudo_" + c]
    merged = g.merge(p.rename("p"), left_on="StudyInstanceUID", right_index=True, how="left")
    gold_pos = merged[merged[c] > 0.5]
    gold_neg = merged[merged[c] <= 0.5]
    # agree if pseudo present and same side (allow soft)
    def side(x):
        if pd.isna(x):
            return "silent"
        return "pos" if x > 0.5 else "neg"

    agree = 0
    miss_pos = 0
    false_neg_on_pos = 0
    silent_on_pos = 0
    for _, r in gold_pos.iterrows():
        s = side(r["p"])
        if s == "pos":
            agree += 1
        elif s == "neg":
            false_neg_on_pos += 1
            miss_pos += 1
        else:
            silent_on_pos += 1
            miss_pos += 1
    false_pos_on_neg = 0
    silent_on_neg = 0
    agree_neg = 0
    for _, r in gold_neg.iterrows():
        s = side(r["p"])
        if s == "neg":
            agree_neg += 1
        elif s == "pos":
            false_pos_on_neg += 1
        else:
            silent_on_neg += 1
    n_pseudo_eff = int(merged["p"].notna().sum())
    n_gold = len(g)
    n_gold_pos = len(gold_pos)
    diag[c] = {
        "gold": n_gold,
        "gold_pos": n_gold_pos,
        "eff": n_pseudo_eff,
        "agree_pos": agree,
        "miss_pos": miss_pos,
        "neg_on_pos": false_neg_on_pos,
        "silent_on_pos": silent_on_pos,
        "pos_on_neg": false_pos_on_neg,
        "silent_on_neg": silent_on_neg,
        "agree_neg": agree_neg,
    }
    log(
        f"| {c} | {n_gold} | {n_pseudo_eff} | posOK={agree}/{n_gold_pos} | miss={miss_pos} | "
        f"neg_on_pos={false_neg_on_pos} | silent_on_gold_pos={silent_on_pos} |"
    )

log("")
log("## 全量覆盖与正负比")
log("")
log("| label | eff_cov | pos | neg | silent | pos/neg |")
log("|---|---:|---:|---:|---:|---:|")
for c in LABELS:
    p = pseudo["pseudo_" + c]
    n_pos = int((p > 0.5).sum())
    n_neg = int((p < 0.5).sum())
    n_sil = int(p.isna().sum())
    cov = (n_pos + n_neg) / len(p)
    ratio = f"{n_pos/max(n_neg,1):.2f}"
    log(f"| {c} | {cov:.1%} | {n_pos} | {n_neg} | {n_sil} | {ratio} |")

# Sample gold-positive misses for weak labels — what language is in the report?
log("")
log("## Gold 阳性但抽取器沉默/否定的报告片段（弱标签）")
log("")

# language / keyword probe on silent reports for weak labels
lang_hits = Counter()


def sniff_lang(text: str) -> str:
    t = text[:200]
    if re.search(r"[一-鿿]", t):
        return "zh"
    if re.search(r"[а-яА-Я]", t):
        return "ru"
    if re.search(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]", t):
        return "pl"
    if re.search(r"[çğıöşüÇĞİÖŞÜ]", t):
        return "tr"
    if re.search(r"[äöüßÄÖÜ]", t):
        return "de"
    if re.search(r"[àâçéèêëîïôùûüÿœ]", t, re.I):
        return "fr"
    if re.search(r"[áéíóúüñ¿¡]", t, re.I):
        return "es"
    if re.search(r"[ãõçáéíóúâêô]", t, re.I):
        return "pt"
    return "en/other"


weak_reports = {c: [] for c in WEAK}
for c in WEAK + COMPARE:
    g = train[["StudyInstanceUID", "Report", c]].dropna(subset=[c])
    p = pseudo["pseudo_" + c]
    for _, r in g.iterrows():
        pv = p.loc[r["StudyInstanceUID"]] if r["StudyInstanceUID"] in p.index else float("nan")
        gold_pos = r[c] > 0.5
        if not gold_pos:
            continue
        silent = pd.isna(pv)
        wrong_neg = (not pd.isna(pv)) and (pv <= 0.5)
        if silent or wrong_neg:
            rep = str(r["Report"])
            lang_hits[(c, sniff_lang(rep), "silent" if silent else "neg")] += 1
            if c in WEAK and len(weak_reports[c]) < 3:
                weak_reports[c].append(
                    {
                        "uid": r["StudyInstanceUID"],
                        "gold": r[c],
                        "pseudo": None if pd.isna(pv) else float(pv),
                        "kind": "silent" if silent else "neg_on_pos",
                        "report_head": rep[:400].replace("\n", " "),
                    }
                )

log("### 错误语言分布（gold 阳性 × 抽取失败）")
for k, v in sorted(lang_hits.items(), key=lambda x: -x[1]):
    log(f"- {k}: {v}")

log("")
log("### 弱标签失败样例（报告前 400 字）")
for c, items in weak_reports.items():
    log(f"\n#### {c}")
    if not items:
        log("(no gold-positive miss samples)")
        continue
    for it in items:
        log(f"- kind={it['kind']} gold={it['gold']} pseudo={it['pseudo']}")
        log(f"  {it['report_head']}")

# Keyword gap: do weak-label reports mention typical English terms when silent?
log("")
log("## 关键词探针：全量报告中弱标签相关词 vs 抽取覆盖")
probes = {
    "Synovitis": [
        r"synovit",
        r"sinovit",
        r"synovi",
        r"滑膜",
        r"синовит",
        r"synovitis",
        r"effusion",  # often co-mentioned
        r"joint fluid",
    ],
    "Medial OA": [
        r"osteoarthrit",
        r"osteoartr",
        r"gonarthros",
        r"degenerativ",
        r"medial compartment",
        r"关节炎",
        r"骨关节",
        r"мениск",  # sometimes OA described near meniscus
        r"chondromalacia",
        r"cartilage loss",
        r"joint space",
    ],
    "Fracture": [
        r"fractur",
        r"fraktur",
        r"перелом",
        r"骨折",
        r"bone bruise",
        r"bone marrow edema",
        r"contusion",
        r"trabecular",
    ],
}
for c, pats in probes.items():
    rep_col = train["Report"].astype(str)
    hit = rep_col.str.contains("|".join(pats), case=False, regex=True, na=False)
    p = pseudo["pseudo_" + c]
    both = hit & p.notna()
    hit_silent = hit & p.isna()
    log(
        f"- {c}: regex_hit_reports={int(hit.sum())} | extractor_eff={int(p.notna().sum())} | "
        f"hit_and_covered={int(both.sum())} | hit_but_silent={int(hit_silent.sum())}"
    )
    # among hit_but_silent, sample
    if int(hit_silent.sum()) > 0:
        sub = train.loc[hit_silent, ["StudyInstanceUID", "Report"]].head(2)
        for _, r in sub.iterrows():
            log(f"  silent-with-keyword: {str(r['Report'])[:220].replace(chr(10),' ')}")

# Overall extractor self-stats if available
log("")
log("## 抽取器自带统计（build_pseudo_table verbose 已在 coverage 跑过）")
log("结论候选写入 conclusions.md")

# save samples json
import json

(OUT / "gold_miss_samples.json").write_text(
    json.dumps(weak_reports, ensure_ascii=False, indent=2), encoding="utf-8"
)
(OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\nWROTE", OUT / "report.md")
