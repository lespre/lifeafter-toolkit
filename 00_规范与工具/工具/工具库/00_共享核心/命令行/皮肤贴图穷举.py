# -*- coding: utf-8 -*-
r"""穷举写法：把全部皮肤的 mtg 贴图名 × 变体（前缀/后缀/大小写/分隔符）算出 fid 集合，
再与全库 entries 的 fid 求交集。交集为空 ⇒ 这些贴图真的不在客户端。
"""
from __future__ import annotations

import itertools
import json
import pathlib
import re
import sqlite3
import sys
import time

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import names as N   # noqa: E402

SKIN_ROOT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/res/weapon.gpk/weapon/skin")
DB = r"E:/la拆包项目/01_索引与产物/10_索引/indexes/lifeafter_files.sqlite3"
TOK = re.compile(rb"[A-Za-z0-9_\-/\\][A-Za-z0-9_\-/\\.]{2,120}\.(?:tga|dds|png|jpg)", re.I)

names = set()
for mtg in SKIN_ROOT.glob("*/*.mtg"):
    try:
        b = mtg.read_bytes()
    except OSError:
        continue
    for t in TOK.findall(b):
        names.add(t.decode("ascii", "replace").replace("/", "\\").lstrip("\\"))
print("唯一贴图名:", len(names))

prefixes = ["", "res\\", "weapon\\", "textures\\", "weapon\\textures\\"]
cands = set()
for nm in names:
    stem = nm.rsplit(".", 1)[0]
    for pre, ext in itertools.product(prefixes, [".tga", ".dds", "", ".png"]):
        cands.add((pre + stem + ext).lower())
print("变体总数:", len(cands))

fids = {}
for c in cands:
    try:
        fids[N.fid_hex(c)] = c
    except Exception:
        pass
print("算出 fid:", len(fids))

con = sqlite3.connect(DB)
found = []
keys = list(fids)
for i in range(0, len(keys), 5000):
    chunk = keys[i:i + 5000]
    q = "select fid_hex, container, row_index from entries where fid_hex in (%s)" % ",".join("?" * len(chunk))
    for f, cont, row in con.execute(q, chunk):
        found.append({"fid": f, "path": fids[f], "container": cont, "row": row})
print("\n★ 交集: %d" % len(found))
for x in found[:15]:
    print("   %-60s → %s row=%d" % (x["path"][:60], x["container"].split("\\")[-1], x["row"]))

out = pathlib.Path(r"E:/la拆包项目/01_索引与产物/10_索引/皮肤贴图_穷举命中_20261017.json")
out.write_text(json.dumps({"names": len(names), "variants": len(cands), "hits": found},
                          ensure_ascii=False, indent=1), encoding="utf-8")
print("写出:", out)
