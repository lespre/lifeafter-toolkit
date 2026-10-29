# -*- coding: utf-8 -*-
"""异变核芯板：升星段位改从「经典服 base 表」取全 5/9/12 星。

背景（2026-10-29 用户报）：板内 star_entries 只有 5 星一段 —— 旧工具
fill_core_star_entries.py 读的是简单生存服变体（nucleus_build_data kj1），
简单生存只开到 5 星，rank_to_desc 自然只有一段。

经典服正源 = com/cdata/nucleus_build_data.py（base，无服型后缀），
rank_to_desc 实测分布：30 行 (5,9,12) / 32 行 (5,9) / 11 行 (5,) / 4 行空。
（中低品核芯经典服只开 5/9 星，是配置本身如此，不是缺数据。）

简单生存独有核芯（家园守卫限定 4 行 + 淬焰燃锋）base 表无此名，保留原 kj1 段，
并在卡上标 star_source 区分。

用法：
    python tools/fill_core_star_entries_classic.py --dry
    python tools/fill_core_star_entries_classic.py
"""
from __future__ import annotations

import json
import pathlib
import shutil
import struct
import sys
import time

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = WEB / "data/boards/mutation_core_full.json"
BOARD_JS = WEB / "data/boards/mutation_core_full.js"
SRC_TABLE = "com/cdata/nucleus_build_data.py（经典服 base，无服型后缀）"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402


def clean(t: str) -> str:
    return (t or "").replace("#f", "").replace("#n", "").replace("#r", "\n").strip()


def load_base():
    raw = (CD / "nucleus_build_data.py").read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((CD / "nucleus_build_data_chs.py").read_bytes())
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    return rows, blob, pool


def stars_of(rec, blob, pool):
    v = rec["values"].get("rank_to_desc")
    v = v[1] if isinstance(v, tuple) else v
    if not isinstance(v, str) or not v.startswith("jump:"):
        return []
    pos = int(v.split(":")[1])
    if pos >= len(blob) or blob[pos] != 0x36:
        return []
    n = blob[pos + 3]
    pos += 4
    out = []
    for _ in range(n):
        rk, pos = BT.uleb(blob, pos, len(blob))
        idx, pos = BT.uleb(blob, pos, len(blob))
        txt = pool[idx] if idx < len(pool) else ""
        txt = clean(txt)
        if txt:
            out.append({"star": rk, "text": txt})
    return out


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    rows, blob, pool = load_base()
    by_name = {}
    for r in rows:
        v = r["values"].get("nucleus_effect_name")
        nm = v[1] if isinstance(v, tuple) else v
        if nm:
            by_name[str(nm).strip()] = r

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    st = {"卡": 0, "经典覆盖": 0, "保留kj1": 0, "星段变化": 0,
          "5912": 0, "59": 0, "仅5": 0, "空": 0}
    for it in board["items"]:
        st["卡"] += 1
        nm = (it.get("name") or "").strip()
        rec = by_name.get(nm)
        if rec is None:
            # 简单生存独有：保留 kj1 段
            if it.get("star_entries"):
                it["star_source"] = "com/cdata/oversea nucleus_build_data kj1（简单生存独有核芯，经典服无此行）"
                st["保留kj1"] += 1
            continue
        seg = stars_of(rec, blob, pool)
        key = tuple(sorted(x["star"] for x in seg))
        if key == (5, 9, 12):
            st["5912"] += 1
        elif key == (5, 9):
            st["59"] += 1
        elif key == (5,):
            st["仅5"] += 1
        else:
            st["空"] += 1
        old = it.get("star_entries") or []
        if [x.get("star") for x in old] != [x["star"] for x in seg]:
            st["星段变化"] += 1
        st["经典覆盖"] += 1
        if not a.dry:
            it["star_entries"] = seg
            it["rank_star_segments"] = {str(x["star"]): x["text"] for x in seg}
            it["max_star"] = max((x["star"] for x in seg), default=it.get("max_star") or 12)
            it["build_id"] = rec["key"]
            it["star_source"] = SRC_TABLE
    if not a.dry:
        board["meta"]["star_source_note"] = (
            "升星段位正源=经典服 nucleus_build_data（base）：%d 卡取 5/9/12 完整段位；"
            "%d 卡经典服配置本身只有 5/9 星（中低品如此）；"
            "简单生存独有核芯（家园守卫限定×4、淬焰燃锋）保留简单生存段位。"
            % (st["经典覆盖"], st["59"] + st["仅5"]))
        ts = time.strftime("%Y%m%d_%H%M%S")
        shutil.copy2(BOARD, BOARD.with_name(BOARD.name + ".bak_%s_starcls" % ts))
        shutil.copy2(BOARD_JS, BOARD_JS.with_name(BOARD_JS.name + ".bak_%s_starcls" % ts))
        BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
        BOARD_JS.write_text(
            "window.WIKI_BOARD_mutation_core_full = "
            + json.dumps(board, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(st)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
