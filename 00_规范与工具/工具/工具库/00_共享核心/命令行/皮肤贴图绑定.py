# -*- coding: utf-8 -*-
r"""皮肤 → 贴图 绑定实测：遍历所有 skin_* 目录的 .mtg，提取贴图引用名，
算 fid，在全局索引里找它落在哪个容器/哪一行。

产出：每条引用四个状态之一
  resolved    —— 名字能定位到容器行（绑定成功）
  missing     —— 名字算出的 fid 在客户端里查不到（实体未下发）
  no_ref      —— mtg 里没有贴图引用
  error       —— mtg 读不了
"""
from __future__ import annotations

import collections
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
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/10_索引/皮肤贴图绑定_20261017.json")

TOK = re.compile(rb"[A-Za-z0-9_\-/\\][A-Za-z0-9_\-/\\.]{2,120}\.(?:tga|dds|png|jpg)", re.I)
PREFIXES = ["", "res\\", "weapon\\"]

con = sqlite3.connect(DB)
con.execute("PRAGMA temp_store=MEMORY")

fid_cache: dict[str, tuple | None] = {}


def locate(name: str):
    """名字 → (container, row)；带前缀尝试。"""
    base = name.replace("/", "\\").lstrip("\\")
    if base in fid_cache:
        return fid_cache[base]
    res = None
    for pre in PREFIXES:
        cand = pre + base
        try:
            f = N.fid_hex(cand)
        except Exception:
            continue
        row = con.execute("select container,row_index from entries where fid_hex=?", (f,)).fetchone()
        if row:
            res = {"fid": f, "container": row[0], "row": row[1], "path": cand}
            break
    fid_cache[base] = res
    return res


t0 = time.time()
skins = sorted([d for d in SKIN_ROOT.glob("skin_*") if d.is_dir()])
print("皮肤目录:", len(skins), flush=True)

result = {}
stat = collections.Counter()
for d in skins:
    mtgs = sorted(d.glob("*.mtg"))
    if not mtgs:
        stat["no_mtg"] += 1
        continue
    mtg = next((m for m in mtgs if "_preview" not in m.name), mtgs[0])
    try:
        b = mtg.read_bytes()
    except OSError:
        stat["error"] += 1
        continue
    names = sorted({t.decode("ascii", "replace") for t in TOK.findall(b)})
    if not names:
        stat["no_ref"] += 1
        result[d.name] = {"mtg": mtg.name, "textures": [], "status": "no_ref"}
        continue
    entries = []
    for nm in names:
        hit = locate(nm)
        entries.append({"ref": nm,
                        "status": "resolved" if hit else "missing",
                        "container": (hit or {}).get("container"),
                        "row": (hit or {}).get("row"),
                        "fid": (hit or {}).get("fid")})
        stat["resolved" if hit else "missing"] += 1
    ok = sum(1 for e in entries if e["status"] == "resolved")
    result[d.name] = {"mtg": mtg.name, "refs": len(entries), "resolved": ok,
                      "status": "full" if ok == len(entries) else ("partial" if ok else "none"),
                      "textures": entries}
    stat[result[d.name]["status"]] += 1

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")

print("完成 %.1fs" % (time.time() - t0))
print("引用条数：resolved %d ｜ missing %d ｜ 无引用 %d ｜ 无 mtg %d"
      % (stat["resolved"], stat["missing"], stat["no_ref"], stat["no_mtg"]))
print("皮肤级：full %d ｜ partial %d ｜ none %d"
      % (stat["full"], stat["partial"], stat["none"]))
print("\n=== 全绑定的皮肤（样例）===")
for k, v in list(result.items()):
    if v.get("status") == "full":
        print("  %-18s %d 张贴图全定位" % (k, v["refs"]))
print("\n=== 一张都定不住的 ===")
for k, v in result.items():
    if v.get("status") == "none":
        print("  %-18s %d 条引用全部 missing" % (k, v["refs"]))
print("\n写出:", OUT)
