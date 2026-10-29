# -*- coding: utf-8 -*-
r"""用 building_icon 族补奖池无图成员（家具/建筑类图标在 ui/building_icon/icon_<id>）。

批量：先 SQL 解析 fid，按包分组，每包只扫一遍。
"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import sys
from collections import defaultdict


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
DET = PROJ / "01_索引与产物/10_索引/热更检测"
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

FAMILIES = ("ui/building_icon/icon_{id}", "ui/building_icon/icon_b_{id}",
            "ui/building_icon/icon_f_{id}")


def hx(p: str) -> str:
    v = fid_of(p)
    return v if isinstance(v, str) else "%016X" % (v & 0xFFFFFFFFFFFFFFFF)


def main() -> int:
    p = WEB / "data/boards/lottery_periods.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    miss = [i for i in d["items"] if not ((i.get("_media") or {}).get("images") or [{}])[0].get("png")]
    con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=30)

    plan = {}
    for it in miss:
        iid = it.get("item_id")
        if not iid:
            continue
        for tpl in FAMILIES:
            base = tpl.format(id=iid)
            for suf in ("_b", "_s"):
                b = base if base.endswith(suf) else base + suf
                for e in (".ktx", ".dds"):
                    r = con.execute("select pack,row from rows where fid=? limit 1", (hx(b + e),)).fetchone()
                    if r:
                        plan[str(it["id"])] = (b + e, r[0], r[1], b)
                        break
                if str(it["id"]) in plan:
                    break
            if str(it["id"]) in plan:
                break
    print("PE 命中", len(plan))

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
            pl = e.get("payload") or b""
            try:
                rgba = DEC.decode_compblks(pl) if pl.startswith(b"CompBlks") else None
                if rgba is None:
                    rec = dict(e)
                    rec["data"] = pl
                    if e.get("kind") == "ktx":
                        rec["info"] = AG.parse_ktx(pl)
                    rgba = AG.decode_image(rec)
                iid, base = need.pop(r)
                name = str(iid).replace(":", "_") + ".png"
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
    fixed = 0
    for it in d["items"]:
        if ((it.get("_media") or {}).get("images") or [{}])[0].get("png"):
            continue
        iid = it.get("item_id")
        if not iid:
            continue
        name = str(it["id"]).replace(":", "_") + ".png"
        for tpl in FAMILIES:
            base = tpl.format(id=iid)
            for suf in ("_b", "_s"):
                b = base if base.endswith(suf) else base + suf
                if pc_export.export_path(b + ".bc7", OUT / name, table):
                    it["_media"] = {"images": [{"png": "assets/lottery_icons/" + name,
                                                "base": base.rsplit("_", 1)[0] if base.endswith(suf) else base,
                                                "suffix": suf, "label": "图标"}], "total": 1}
                    it["icon_state"] = "有图"
                    fixed += 1
                    break
            if it.get("_media"):
                break
    print("PC 兜底", fixed)

    have = sum(1 for i in d["items"] if ((i.get("_media") or {}).get("images") or [{}])[0].get("png"))
    d["meta"]["state_summary"]["有图"] = have
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("有图", have, "/", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
