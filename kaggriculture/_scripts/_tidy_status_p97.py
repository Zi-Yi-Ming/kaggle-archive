from pathlib import Path

p = Path(r"D:\桌面\Kaggle\kaggriculture\_production\STATUS.md")
text = p.read_text(encoding="utf-8")

CLEAN = """
---

## P97 原创终局杂交（2026-09-27 · 首次过双门 · H3 已授权提交）

- autopsy：胜负手 **day26–29**；**H3** day27+ 余量现金品抢先卖 / **H4** cap+lead+greedy
- **H3_term_greedy** 扩大 dual PASS：vs Metav4 **8/10 80% +369** · shop **8/8 100%** · thomas/alperen/pipe16 全胜
- **H4_combo**：87.5% +570 · shop 66–75% → 次优备胎
- 包：`_push_h3_term_greedy/submission.tar.gz`、`_push_h4_term_combo/`
- **用户已授权 → 已提交 1 发 H3**（ref **56453212** COMPLETE **600.0** 爬分中）
- last-2 = **[H3 56453212, Fieldcraft 56434477]**；**Metav4 56390446 暂挤出 last-2**（team=max ≈ Fieldcraft 1975.7 直至 H3 爬升）
- 口径：终榜 BT 打真局；public 爬分 ≠ 终榜。勿 re-roll；无新过门不再交
- 详见 `_research/RESEARCH_P97B_TERM_HYBRID.md`

"""

# Remove every duplicate P97/P97b block, keep one clean version.
# Strategy: find the first P97-related block start, cut from there until a stable
# section that is NOT another P97 duplicate (e.g. "## " heading that's not P97).
starts = []
for m in ("**P97b 原创终局杂交", "**P97 原创终局杂交", "### P97", "**P97 原创"):
    start = 0
    while True:
        i = text.find(m, start)
        if i < 0:
            break
        starts.append(i)
        start = i + 1

if not starts:
    # append clean block at end of first third
    text = text.rstrip() + "\n" + CLEAN
    p.write_text(text, encoding="utf-8")
    print("no dups found; appended clean block")
else:
    first = min(starts)
    # Find end: next top-level section after first that is not P97
    # Look at content after first, skip all P97-flavored blocks
    rest = text[first:]
    # Cut a generous window of repeated P97 blocks
    # End at first line matching a non-P97 major heading after the dups
    lines = rest.splitlines(keepends=True)
    kept_tail = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        is_p97_heading = (
            "P97" in line
            and (
                line.startswith("**P97")
                or line.startswith("### P97")
                or line.startswith("## P97")
                or line.strip().startswith("- **H3")
                or line.strip().startswith("- **H4")
                or line.strip().startswith("- autopsy")
                or line.strip().startswith("- smoke")
                or line.strip().startswith("- 包")
                or line.strip().startswith("- **未授权")
                or line.strip().startswith("- **用户")
                or line.strip().startswith("- Fieldcraft 日账")
                or "详见 `_research/RESEARCH_P97B" in line
                or "day26" in line
                or "term_greedy" in line
                or "H4_combo" in line
            )
        )
        # Simpler approach below instead of line filter
        i += 1
    # Use block-based cut: from first P97 start to the first subsequent heading
    # that looks like a different topic (## or ### without P97).
    import re
    # Find all P97 block-ish regions as from each start to just before next
    # non-P97 ##/### heading
    heading_re = re.compile(r"^#{2,3} .+$", re.M)
    positions = [m.start() for m in heading_re.finditer(text)]
    # also bold-section headers like **P97
    cut_start = first
    # walk headings after cut_start; skip while heading contains P97 or H3/H4/终局/term
    cut_end = len(text)
    for pos in positions:
        if pos <= cut_start:
            continue
        # get heading line
        m = heading_re.match(text, pos)
        if not m:
            continue
        h = m.group(0)
        if any(k in h for k in ("P97", "H3", "H4", "终局杂交", "term_")):
            continue
        # non-P97 major heading — stop here
        cut_end = pos
        break
    # Also handle case where P97 blocks are inline with **bold** not ###
    # Expand cut_end if next content is more **P97
    # Already handled if headings catch it; for ** bold blocks, scan
    tail = text[cut_end:]
    # If tail still starts with P97 dups, strip those too
    while True:
        stripped = tail.lstrip()
        if stripped.startswith("**P97"):
            # skip this paragraph block (until blank line + non-related)
            nxt = stripped.find("\n\n")
            if nxt < 0:
                tail = ""
                break
            # actually find end of this repeated unit — next **P97 or real heading
            # use find of next double newline followed by non-bullet? just skip 20 lines
            block_lines = stripped.splitlines(keepends=True)
            skip = 0
            for j, ln in enumerate(block_lines):
                if j > 0 and (ln.startswith("##") or ln.startswith("###") or ln.startswith("**P9") is False and ln.startswith("**") and "P97" not in ln):
                    if "P97" not in ln and "H3" not in ln and "H4" not in ln:
                        skip = j
                        break
            else:
                skip = len(block_lines)
            tail = "".join(block_lines[skip:])
        else:
            break

    new_text = text[:cut_start] + CLEAN.lstrip("\n") + "\n" + tail
    # collapse 3+ blank lines
    new_text = re.sub(r"\n{3,}", "\n\n", new_text)
    p.write_text(new_text, encoding="utf-8")
    print("cleaned", "old_bytes", len(text), "new_bytes", len(new_text))
    print("remaining P97 mentions:", new_text.count("P97"))
    print("remaining H3_term:", new_text.count("H3_term"))
