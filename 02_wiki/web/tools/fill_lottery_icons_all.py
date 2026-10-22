# -*- coding: utf-8 -*-
r"""给合并后的奖池板批量补图：icon 字段族 + item_icon + building_icon，按包一次扫完。"""
from __future__ import annotations

import json
import re
import pathlib
import sqlite3
import sys
from collections import defaultdict

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
DET = PROJ / "01_索引与产物/30_分析/热更检测"
OUT = WEB / "assets/lottery_icons"
IDX = DET / "pe_index.sqlite3"
PACKS = DET / "pe_packs"
sys.path.insert(0, str(DET))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(DET / "pe_icon_bind"))
from toolkit_core.path_fid import fid_of  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402
import pc_export  # noqa: E402
from PIL import Image  # noqa: E402

TEMPLATES = ("ui/item_icon/icon_{id}", "ui/building_icon/icon_{id}",
             "ui/item_icon_new/icon_{id}", "ui/other_icon/icon_{id}")


def safe_name(s: str) -> str:
    return re.sub(r"[^0-9A-Za-z_.-]+", "_", str(s)) + ".png"


def hx(p: str) -> str:
    v = fid_of(p)
    return v if isinstance(v, str) else "%016X" % (v & 0xFFFFFFFFFFFFFFFF)


def base_of(icon: str) -> str:
    icon = icon or ""
    return icon[:-4] if icon.lower().endswith((".png", ".ktx", ".dds")) else icon


def main() -> int:
    p = WEB / "data/boards/lottery_periods.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    miss = [i for i in d["items"]
            if not (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png")]
    print("无图", len(miss))
    con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=30)

    plan = {}
    for it in miss:
        cands = []
        if it.get("icon"):
            cands.append(base_of(it["icon"]))
        if it.get("item_id"):
            cands += [t.format(id=it["item_id"]) for t in TEMPLATES]
        for base in cands:
            got = None
            for suf in ("_b", "_s", ""):
                b = base if (suf and base.endswith(suf)) else base + suf
                for e in (".ktx", ".dds"):
                    r = con.execute("select pack,row from rows where fid=? limit 1", (hx(b + e),)).fetchone()
                    if r:
                        got = (b + e, r[0], r[1], b)
                        break
                if got:
                    break
            if got:
                plan[str(it["id"])] = got
                break
    print("PE 计划", len(plan))

    bypack = defaultdict(dict)
    for iid, (q, pk, rw, base) in plan.items():
        bypack[pk][rw] = (iid, base)

    done = 0
    for pk, need in bypack.items():
        need = dict(need)
        for e in AG.iter_entries(str(PACKS / pk)):
            r = e["row"]
            if r not in need:
                continue
            try:
                pl = e.get("payload") or b""
                rgba = DEC.decode_compblks(pl) if pl.startswith(b"CompBlks") else None
                if rgba is None:
                    rec = dict(e)
                    rec["data"] = pl
                    if e.get("kind") == "ktx":
                        rec["info"] = AG.parse_ktx(pl)
                    rgba = AG.decode_image(rec)
                iid, base = need.pop(r)
                name = safe_name(iid)
                Image.fromarray(rgba, "RGBA").save(OUT / name)
                suf = "_b" if base.endswith("_b") else ("_s" if base.endswith("_s") else "")
                stem = base[:-2] if suf else base
                for it in d["items"]:
                    if str(it["id"]) == iid:
                        it["_media"] = {"images": [{"png": "assets/lottery_icons/" + name,
                                                    "base": stem, "suffix": suf, "label": "图标"}],
                                        "total": 1}
                        it["icon_state"] = "有图"
                done += 1
            except Exception:
                continue
            if not need:
                break
    print("PE 实导", done)

    table = pc_export.load_table()
    pc_done = 0
    for it in d["items"]:
        if (((it.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"):
            continue
        iid = it.get("item_id")
        if not iid:
            continue
        name = safe_name(it["id"])
        for base in [base_of(it.get("icon"))] + [t.format(id=iid) for t in TEMPLATES]:
            if not base:
                continue
            for suf in ("_b", "_s"):
                b = base if base.endswith(suf) else base + suf
                if pc_export.export_path(b + ".bc7", OUT / name, table):
                    it["_media"] = {"images": [{"png": "assets/lottery_icons/" + name,
                                                "base": b[:-2] if b.endswith(suf) else b,
                                                "suffix": suf, "label": "图标"}], "total": 1}
                    it["icon_state"] = "有图"
                    pc_done += 1
                    break
            if it.get("icon_state") == "有图":
                break
    print("PC 兜底", pc_done)

    have = sum(1 for i in d["items"]
               if (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"))
    d["meta"]["state_summary"]["有图"] = have
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("有图", have, "/", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
