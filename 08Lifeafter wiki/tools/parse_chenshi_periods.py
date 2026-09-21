# -*- coding: utf-8 -*-
"""把公告宸世段（announce_chenshi.json）按首日期对齐 optional_version_data 期次，更新 rebuild 脚本的期次内容层。"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"E:\la拆包项目\08Lifeafter wiki")
ann = json.load(open(ROOT / "data/external_refs/announce_chenshi.json", encoding="utf-8"))

# 公告段：按（公告日期→段文本）收集；经典/简单服并存时合并标注
by_date = {}   # 公告发布日期(YYYY-MM-DD) -> {"classic": [seg...], "simple": [seg...]}
for a in ann["announcements"]:
    d = a["date"]
    is_classic = "经典服" in a["title"]
    is_simple = "简单" in a["title"]
    bucket = by_date.setdefault(d, {"classic": [], "simple": [], "other": []})
    for s in a["segments"]:
        s = s.strip().strip('"').strip()
        if not s or "返利小队" in s:
            continue
        if is_classic:
            bucket["classic"].append(s)
        elif is_simple:
            bucket["simple"].append(s)
        else:
            bucket["other"].append(s)

# 每期内容：公告段内提取起始日期（X月X日）与正文
def first_date_of(seg, year):
    m = re.search(r"(\d{1,2})月(\d{1,2})日", seg)
    if not m:
        return None
    return f"{year}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"

content_by_period = {}  # period_start_date -> {classic/simple: 正文}
for d, bucket in by_date.items():
    year = d[:4]
    for s in bucket["classic"] + bucket["simple"]:
        fd = first_date_of(s, year)
        if not fd:
            continue
        cb = content_by_period.setdefault(fd, {})
        # 正文=「宸世臻藏：」之后
        body = re.sub(r"^[\d、\s]*", "", s)
        body = re.sub(r"^(?:宸世臻藏|臻藏上新|宸世臻藏焕新|宸世臻藏全面更新|本期宸世臻藏)[：:，,]?\s*", "", body)
        src = "classic" if s in bucket["classic"] else "simple"
        cb.setdefault(src, []).append(body)

out = {k: v for k, v in sorted(content_by_period.items())}
json.dump(out, open(ROOT / "data/external_refs/chenshi_period_content.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
for k, v in out.items():
    c = " | ".join(v.get("classic", []))[:70]
    s = " | ".join(v.get("simple", []))[:70]
    print(f"{k}:\n  经典: {c}\n  简单: {s}")
