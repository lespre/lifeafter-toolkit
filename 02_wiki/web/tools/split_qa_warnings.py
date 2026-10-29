# -*- coding: utf-8 -*-
"""把 QA 输出里的告警分成「中间帧转储 _fN」与真 APNG 两类，并列出真 APNG 的问题。"""
from __future__ import annotations

import re
import pathlib

LOG = pathlib.Path("/tmp/qa_out.txt")
PAT = re.compile(r"\[(静止|贴边|全透明|帧数少|乱码)\]\s+(\S+)")


def main() -> int:
    txt = LOG.read_text(encoding="utf-8", errors="ignore")
    hits = PAT.findall(txt)
    real, dump = [], []
    for tag, name in hits:
        (dump if re.search(r"_f\d+(\.png)?$", name) else real).append((tag, name))
    print("告警总计 %d ｜ 中间帧转储 %d ｜ 真 APNG %d" % (len(hits), len(dump), len(real)))
    from collections import Counter
    print("真 APNG 告警分布", Counter(t for t, _ in real).most_common())
    for tag, name in real[:15]:
        print("  ", tag, name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
