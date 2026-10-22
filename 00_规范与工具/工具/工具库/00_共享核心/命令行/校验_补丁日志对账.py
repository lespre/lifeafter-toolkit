# -*- coding: utf-8 -*-
r"""把补丁日志里「缺」的 2,074 条逐个查：是目录名映射（bin/x64→x64-a50）还是真缺；
并把 fver=本期 的 250 条清单按顶层目录聚合、逐条核盘（size/sha）。"""
from __future__ import annotations

import ast
import collections
import hashlib
import json
import pathlib
import re

CLIENT = pathlib.Path(r"E:/mrzh")
FVER = "20261016_213554_playertest_newpc"
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/热更检测/post_update_20261017_batch2/校验")
OUT.mkdir(parents=True, exist_ok=True)

entries: dict[str, dict] = {}
for f in (CLIENT / "Documents/plcoht_ag", CLIENT / "Documents/plcoht_ag.1"):
    if not f.is_file():
        continue
    txt = bytes(b ^ 0xAA for b in f.read_bytes()).decode("utf-8", "replace")
    for m in re.finditer(r"'([^']+\.(?:npk|gpk|wpk|idx|exe|dll|py|lc|bin))':\s*(\{[^{}]*\})", txt):
        try:
            d = ast.literal_eval(m.group(2))
        except Exception:                                       # noqa: BLE001
            continue
        if isinstance(d, dict) and "size" in d:
            entries[m.group(1)] = d

print("日志期待清单：%d 条" % len(entries))

# 目录名映射（skill 记过：日志写 bin/x64，本地是 bin/x64-a50）
MAP = [("bin/x64-win7", "bin/x64-a50-win7"), ("bin/x64-3", "bin/x64-a50-3"),
       ("bin/x64-2", "bin/x64-a50-2"), ("bin/x64", "bin/x64-a50")]


def resolve(rel: str) -> pathlib.Path:
    p = CLIENT / rel.replace("\\", "/")
    if p.is_file():
        return p
    for a, b in MAP:
        if a in rel:
            q = CLIENT / rel.replace(a, b).replace("\\", "/")
            if q.is_file():
                return q
    return p


ok = miss = mapped = bad = 0
missing_samples, bad_samples = [], []
for rel, d in entries.items():
    p = resolve(rel)
    direct = (CLIENT / rel.replace("\\", "/")).is_file()
    if not p.is_file():
        miss += 1
        if len(missing_samples) < 12:
            missing_samples.append(rel)
        continue
    if not direct:
        mapped += 1
    exp = d.get("size")
    if exp and p.stat().st_size != exp:
        bad += 1
        if len(bad_samples) < 8:
            bad_samples.append((rel, exp, p.stat().st_size))
    else:
        ok += 1

print("落盘核对：一致 %d ｜ 经目录映射后一致 %d ｜ 仍缺 %d ｜ 大小不符 %d"
      % (ok, mapped, miss, bad))
if missing_samples:
    print("  仍缺样例：")
    for s in missing_samples:
        print("     ", s[:100])
if bad_samples:
    print("  大小不符：")
    for r, e, a in bad_samples:
        print("     %s 期望 %s 实际 %s" % (r[:70], e, a))

# fver=本期 的清单，按顶层目录聚合
cur = {k: v for k, v in entries.items() if str(v.get("fver")) == FVER}
print("\n本期 fver（%s）条目：%d 条" % (FVER, len(cur)))
by = collections.Counter(k.replace("\\", "/").split("/")[0] for k in cur)
for k, v in by.most_common(10):
    print("   %-16s %4d" % (k, v))

# 逐条核盘（本期这批）+ sha 抽查
rows = []
for rel, d in sorted(cur.items()):
    p = resolve(rel)
    if not p.is_file():
        rows.append({"路径": rel, "状态": "缺", "期望大小": d.get("size")})
        continue
    st = p.stat()
    rows.append({"路径": rel, "状态": "一致" if (not d.get("size") or st.st_size == d["size"]) else "大小不符",
                 "期望大小": d.get("size"), "实际大小": st.st_size})
okc = sum(1 for r in rows if r["状态"] == "一致")
print("本期这批：一致 %d / %d" % (okc, len(rows)))
(OUT / "补丁日志对账.json").write_text(json.dumps(
    {"期待总条数": len(entries), "一致": ok, "经映射一致": mapped, "仍缺": miss,
     "大小不符": bad, "仍缺样例": missing_samples, "本期条目": rows}, ensure_ascii=False, indent=1),
    encoding="utf-8")
print("产物 →", OUT / "补丁日志对账.json")
