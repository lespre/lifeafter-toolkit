# -*- coding: utf-8 -*-
"""奖池板缺口体检：名字解析率 / 图标在包内命中率。"""
import json
import pathlib
import sqlite3
import sys

sys.path.insert(0, r"E:\la拆包项目\00_规范与工具\工具\工具库\00_共享核心")
from toolkit_core.path_fid import fid_of

PROJ = pathlib.Path(r"E:\la拆包项目")
d = json.loads((PROJ / "02_wiki/web/data/boards/lottery_periods.json").read_text(encoding="utf-8"))
its = d["items"]
ids = sorted({i["item_id"] for i in its if i.get("item_id")})


def hx(p: str) -> str:
    v = fid_of(p)
    if isinstance(v, str):
        return v
    return "%016X" % (v & 0xFFFFFFFFFFFFFFFF)


con = sqlite3.connect(
    "file:%s?mode=ro" % str(PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3").replace("\\", "/"),
    uri=True, timeout=30)
have, miss = 0, []
for iid in ids:
    ok = False
    for suf in ("_b", "_s", ""):
        for ext in (".ktx", ".dds"):
            q = f"ui/item_icon/icon_{iid}{suf}{ext}"
            if con.execute("select 1 from rows where fid=? limit 1", (hx(q),)).fetchone():
                ok = True
                break
        if ok:
            break
    if ok:
        have += 1
    else:
        miss.append(iid)
con.close()

named = sum(1 for i in its if not str(i.get("name", "")).startswith(("未识别", "道具 ")))
withicon = sum(1 for i in its if i.get("icon"))
print("条目", len(its), "| 唯一 id", len(ids))
print("名字已解析", named, f"({named/len(its)*100:.1f}%)")
print("已挂图标条目", withicon, f"({withicon/len(its)*100:.1f}%)")
print("包内真有 icon_<id> 图的 id", have, f"({have/len(ids)*100:.1f}%)", "| 缺图 id", len(miss))
print("缺图样例", miss[:12])
