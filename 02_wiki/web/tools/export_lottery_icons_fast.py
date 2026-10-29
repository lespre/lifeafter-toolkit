# -*- coding: utf-8 -*-
r"""奖池图标批量导出（快版）：先 SQL 解析全部 fid，再按包一次性扫行解码。

相比逐条 pe_fetch.export（每张图重开包 + 全表扫行，~1.1s/张），本版把同包的图
合并成一次遍历，实测 400 张量级可在十几秒内完成。
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
sys.path.insert(0, str(DET))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(DET / "pe_icon_bind"))
from toolkit_core.path_fid import fid_of  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402
import pc_fetch  # noqa: E402
import pc_export  # noqa: E402
from PIL import Image  # noqa: E402

PACKS = DET / "pe_packs"


def hx(p: str) -> str:
    v = fid_of(p)
    return v if isinstance(v, str) else "%016X" % (v & 0xFFFFFFFFFFFFFFFF)


def candidates(it: dict) -> list[str]:
    out = []
    icon = it.get("icon") or ""
    if icon:
        out.append(icon[:-4] if icon.lower().endswith((".png", ".ktx", ".dds")) else icon)
    iid = it.get("item_id")
    if iid:
        out.append("ui/item_icon/icon_%s" % iid)
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    p = WEB / "data/boards/lottery_periods.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=30)

    plan = {}          # item_id(str) → (path, pack, row)
    for it in d["items"]:
        if ((it.get("_media") or {}).get("images") or [{}])[0].get("png"):
            continue
        for base in candidates(it):
            found = None
            for suf in ("_b", "_s", ""):
                b = base if (suf and base.endswith(suf)) else base + suf
                for e in (".ktx", ".dds"):
                    q = b + e
                    r = con.execute("select pack,row from rows where fid=? limit 1", (hx(q),)).fetchone()
                    if r:
                        found = (q, r[0], r[1])
                        break
                if found:
                    break
            if found:
                plan[str(it["id"])] = found
                break
    print("PE 计划导出", len(plan))

    bypack = defaultdict(dict)   # pack → {row: (item_id, path)}
    for iid, (q, pk, rw) in plan.items():
        bypack[pk][rw] = (iid, q)

    done = 0
    for pk, rows in bypack.items():
        need = dict(rows)
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
                iid, q = need.pop(r)
                name = str(iid).replace(":", "_") + ".png"
                Image.fromarray(rgba, "RGBA").save(OUT / name)
                q0 = q
                stem = q0.rsplit(".", 1)[0]
                suf = "_b" if stem.endswith("_b") else ("_s" if stem.endswith("_s") else "")
                base = stem[:-2] if suf else stem
                for it in d["items"]:
                    if str(it["id"]) == iid:
                        it["_media"] = {"images": [{"png": "assets/lottery_icons/" + name,
                                                    "base": base, "suffix": suf, "label": "图标"}],
                                        "total": 1}
                        it["icon_state"] = "有图"
                done += 1
            except Exception:
                continue
            if not need:
                break
    print("PE 实导", done)

    # PC 兜底（无 icon 字段且未被 PE 命中的，仍走 PC 同名路径）
    table = pc_export.load_table()
    fixed = 0
    for it in d["items"]:
        if ((it.get("_media") or {}).get("images") or [{}])[0].get("png"):
            continue
        name = str(it["id"]).replace(":", "_") + ".png"
        for base in candidates(it):
            for suf in ("_b", "_s"):
                b = base if base.endswith(suf) else base + suf
                for e in (".bc7", ".png"):
                    if pc_export.export_path(b + e, OUT / name, table):
                        it["_media"] = {"images": [{"png": "assets/lottery_icons/" + name,
                                                    "base": b, "suffix": suf, "label": "图标"}],
                                        "total": 1}
                        it["icon_state"] = "有图"
                        fixed += 1
                        break
                if it.get("_media"):
                    break
            if it.get("_media"):
                break
    print("PC 兜底", fixed)

    have = sum(1 for i in d["items"] if ((i.get("_media") or {}).get("images") or [{}])[0].get("png"))
    d["meta"]["state_summary"]["有图"] = have
    d["meta"]["card_mode"] = "period"
    d["meta"]["card_summary"] = []
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("有图", have, "/", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
