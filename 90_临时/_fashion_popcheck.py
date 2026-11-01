# -*- coding: utf-8 -*-
r"""只读：评估 add_fashion_style_fields 若重跑，会对无源行卡清理掉哪些已有字段。"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import struct
import sys

PROJ = pathlib.Path(r"e:\la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from toolkit_core import bindict_table as BT  # noqa

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"

POP = ["dye", "obtain_res", "theme", "show_start", "gift_package", "display_bg", "anim_graph",
       "model_change_color_id", "glowstick_switchable", "hide_idle_anim", "value_words",
       "rebirth_tex", "other_get_methods", "uncap_appear_gender", "bone_info", "green_model",
       "preview_group", "cohabit_friendliness", "cohabit_level", "tech_flags",
       "part_code", "part_code_cn", "show_name", "man_show_name", "show_schedule", "misc_flags",
       "model_paths", "npc_hidden"]


def load(stem):
    raw = (CD / f"{stem}.py").read_bytes()
    at = raw.find(b"x{")
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + ln]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((CD / f"{stem}_chs.py").read_bytes())
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    return rows, blob, pool


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def base_name(s):
    return re.sub(r"-\d+天$", "", str(s or ""))


def main():
    f_rows, _, _ = load("fashion_data")
    fmap = {r["key"]: r for r in f_rows}
    by_base = collections.defaultdict(list)
    for r in f_rows:
        by_base[base_name(sv(r["values"].get("name")))] .append(r["key"])

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    no_src = []
    for it in board["items"]:
        rk = [int(k) for k in (it.get("row_keys") or []) if str(k).lstrip("-").isdigit()]
        frecs = [k for k in rk if k in fmap]
        if frecs:
            continue
        if it.get("face_kind"):
            no_src.append(it)
            continue
        cand = by_base.get(base_name(it.get("name"))) or []
        picked = [k for k in cand if sv(fmap[k]["values"].get("part")) is not None]
        if not picked:
            no_src.append(it)
    print("无源行卡（会被清理）:", len(no_src))
    fc = collections.Counter()
    for it in no_src:
        for k in POP:
            if k in it:
                fc[k] += 1
    print("这些卡上将被 pop 的现有字段:", dict(fc))
    ex = [it for it in no_src if "model_paths" in it or "dye" in it or "part_code" in it][:12]
    for it in ex:
        print("  ", it["id"], it.get("name"), "part=", it.get("part"), "fields=",
              [k for k in POP if k in it])


if __name__ == "__main__":
    raise SystemExit(main())
