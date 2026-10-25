# -*- coding: utf-8 -*-
"""给时装卡补三个「详情」字段：花苞可见、副武器可见、可隐藏部位（挂件等）。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
PART_CN = {"pendant": "挂件", "bag": "背包", "light": "荧光棒", "cloth": "衣服",
           "hat": "头饰", "suit": "整套", "face": "面饰", "proj": "投影"}
v = lambda x: x[1] if isinstance(x, tuple) else x

P = CD / "fashion_data.py"
raw = P.read_bytes()
at = raw.find(b"x{")
L = int.from_bytes(raw[at + 2:at + 6], "little")
body = raw[at + 6:at + 6 + L]
cnt = struct.unpack_from("<I", body, 0)[0]
blob = body[8 + 4 * cnt:]
pool = BT.parse_legacy_chs_pool((CD / "fashion_data_chs.py").read_bytes())
rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]

info = {}
for r in rows:
    val = r["values"]
    d = {}
    if val.get("reborn_vis") is not None:
        d["reborn_vis"] = bool(v(val.get("reborn_vis")))

    if val.get("back_weapon_vis") is not None:
        d["back_weapon_vis"] = bool(v(val.get("back_weapon_vis")))
    # 背包：按用户口径，翅膀/翼类背包会遮住半感染者花苞（rebirth_tex 不足以判定，别用）
    if (str(v(val.get("part_type"))) == "bag"
            and any(t in str(v(val.get("name")) or "") for t in ("翅膀", "翼"))):
        d["reborn_vis"] = True
        d["reborn_src"] = "wings"
    h = val.get("hide_other_part")
    if isinstance(h, tuple):
        try:
            off = int(str(h[1]).split(":")[1])
            g = BT.read_27_group(blob, off)
            if g:
                parts = [pool[i] for i in g[1] if i < len(pool)]
                if parts:
                    d["hide_parts"] = [PART_CN.get(x, x) for x in parts]
        except Exception:
            pass
    if d:
        info[str(r["key"])] = d

board = json.loads(BOARD.read_text(encoding="utf-8"))
hit = 0
for it in board["items"]:
    merged = {}
    for k in (it.get("row_keys") or []):
        for kk, vv in info.get(str(k), {}).items():
            if kk == "hide_parts":
                merged.setdefault(kk, [])
                for p in vv:
                    if p not in merged[kk]:
                        merged[kk].append(p)
            else:
                merged[kk] = merged.get(kk, False) or vv
    if merged:
        it.update(merged)
        hit += 1
BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
print("带详情字段的卡", hit, "/", len(board["items"]))
print("样例", {k: board["items"][0].get(k) for k in ("reborn_vis", "back_weapon_vis", "hide_parts")})
