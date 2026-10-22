# -*- coding: utf-8 -*-
"""精校副标题三要素：来源 / 生成日 / 源包摘要。

规则（只做能证实的事）：
  · generated 缺失 → 用板块文件写入时间（构建时间），并标注 generated_source=file_mtime
  · package_sha 不是 64 位 hex → 清空并标 package_sha_status=未记录（不写零串、不编）
  · 统计每条板块的实际条目数，与 meta.count 对齐
"""
import datetime
import json
import pathlib
import re

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
B = WEB / "data" / "boards"

fixed = []
for p in sorted(B.glob("*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    m = d.get("meta")
    if not isinstance(m, dict):
        continue
    touched = []

    gen = str(m.get("generated") or "").strip()
    if not gen:
        mt = datetime.date.fromtimestamp(p.stat().st_mtime).isoformat()
        m["generated"] = mt
        m["generated_source"] = "file_mtime"
        touched.append("generated=%s(文件时间)" % mt)

    sha = str(m.get("package_sha") or "").strip()
    if not re.fullmatch(r"[0-9a-fA-F]{64}", sha):
        m.pop("package_sha", None)
        m["package_sha_status"] = "未记录"
        touched.append("sha→未记录")

    n = len(d.get("items") or [])
    if m.get("count") not in (None, n):
        touched.append("count %s→%s" % (m.get("count"), n))
    m["count"] = n

    if touched:
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        fixed.append((p.stem, "; ".join(touched)))

for bid, what in fixed:
    print("%-32s %s" % (bid, what))
print("修正板块", len(fixed))
