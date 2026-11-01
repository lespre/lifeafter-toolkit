# -*- coding: utf-8 -*-
r"""一次性审计：核对 fashion_wardrobe 卡片字段与源表（只读，不写盘）。"""
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


def load(stem: str):
    raw = (CD / f"{stem}.py").read_bytes()
    at = raw.find(b"x{")
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + ln]
    pool = BT.parse_legacy_chs_pool((CD / f"{stem}_chs.py").read_bytes())
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    return rows, blob, pool


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def jl(blob, row, field, pool):
    got = row["values"].get(field)
    if not got:
        return []
    tag, val = got
    if tag != "0x0b":
        return [val]
    try:
        off = int(str(val).split(":")[1])
    except (IndexError, ValueError):
        return []
    out: list = []

    def walk(g):
        kind, els = g
        for e in els:
            if kind == 0x0B:
                g2 = BT.read_27_group(blob, e)
                if g2:
                    walk(g2)
            elif kind == 0x05:
                out.append(pool[e] if 0 <= e < len(pool) else f"<oob:{e}>")
            else:
                out.append(e)

    g0 = BT.read_27_group(blob, off)
    if g0:
        walk(g0)
    return out


def main():
    f_rows, f_blob, f_pool = load("fashion_data")
    fmap = {r["key"]: r for r in f_rows}
    a_rows, a_blob, a_pool = load("player_appear_data")
    amap = {r["key"]: r for r in a_rows}
    c_rows, c_blob, c_pool = load("appear_change_color_data")
    cmap = {r["key"]: r for r in c_rows}
    hb_rows, hb_blob, hb_pool = load("fashion_obtain_handbook_data")
    r_rows, r_blob, r_pool = load("fashion_obtain_res_data")
    b_rows, b_blob, b_pool = load("fashion_bg_data")

    # 0) 原始字段结构样本
    sample = 361310
    if sample in cmap:
        r = cmap[sample]
        print("== appear_change_color_data 样本", sample)
        for k, v in r["values"].items():
            if k in ("colors", "color_values", "change_color_switch", "pbr_default_mode", "hsv_switch", "channel_crystal"):
                print("  ", k, v, "-> jl:", jl(c_blob, r, k, c_pool)[:6])

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    ids = [it.get("id") for it in items]
    print("== cards", len(items), "unique ids", len(set(ids)))
    dup = [k for k, v in collections.Counter(ids).items() if v > 1]
    if dup:
        print("  duplicate ids:", dup[:10])

    def rk(it):
        out = []
        for k in it.get("row_keys") or []:
            try:
                out.append(int(k))
            except (TypeError, ValueError):
                pass
        return out

    # 1) dye 内部一致性
    has_dye = [it for it in items if it.get("dye")]
    no_scm = [it for it in has_dye if not it["dye"].get("scheme_count") and not it["dye"].get("hair")]
    empty_colors = [it for it in has_dye if it["dye"].get("schemes") and not it["dye"].get("colors")]
    cnt_gt = [it for it in has_dye if (it["dye"].get("scheme_count") or 0) > len(it["dye"].get("schemes") or [])]
    print("== dye cards", len(has_dye))
    print("  scheme_count==0 && no hair:", len(no_scm), [ (x["id"], x.get("name")) for x in no_scm[:6]])
    print("  schemes present but colors empty:", len(empty_colors))
    print("  scheme_count > len(schemes):", len(cnt_gt), [(x["id"], x["dye"].get("scheme_count"), len(x["dye"].get("schemes") or [])) for x in cnt_gt[:8]])

    # 2) theme / obtain_res 来源核对（只按 row_keys 是否命中源数据）
    tid = set()
    for r in hb_rows:
        for x in jl(hb_blob, r, "fashion_ids", hb_pool):
            if isinstance(x, int):
                tid.add(x)
    theme_ok = theme_fb = 0
    theme_fb_list = []
    res_ok = res_fb = 0
    res_fb_list = []
    for it in items:
        keys = rk(it)
        if it.get("theme"):
            direct = any(k in tid for k in keys)
            if direct:
                theme_ok += 1
            else:
                theme_fb += 1
                theme_fb_list.append((it["id"], it.get("name"), keys, it["theme"].get("name")))
        if it.get("obtain_res"):
            hit = False
            for r in r_rows:
                if r["key"] in keys:
                    if jl(r_blob, r, "obtain_res", r_pool):
                        hit = True
                        break
            if hit:
                res_ok += 1
            else:
                res_fb += 1
                res_fb_list.append((it["id"], it.get("name"), keys, it["obtain_res"]))
    print("== theme: direct", theme_ok, "fallback/name", theme_fb)
    for x in theme_fb_list[:10]:
        print("   ", x)
    print("== obtain_res: direct", res_ok, "fallback/name", res_fb)
    for x in res_fb_list[:10]:
        print("   ", x)

    # 3) display_bg / anim_graph / show_start / glowstick / hide_idle 直证
    for field, expect in (("display_bg", 36), ("show_start", 10), ("anim_graph", 47),
                          ("glowstick_switchable", 128), ("hide_idle_anim", 62),
                          ("gift_package", 23)):
        cards = [it for it in items if it.get(field)]
        direct = 0
        orphan = []
        for it in cards:
            keys = rk(it)
            src = fmap
            ok = False
            for k in keys:
                r = src.get(k)
                if r and jl(f_blob, r, {"display_bg": "bg_ids", "show_start": "start_show_ts",
                                        "anim_graph": "anim_graph_id", "gift_package": "gift_package_id",
                                        "glowstick_switchable": "is_available_glowstick",
                                        "hide_idle_anim": "can_hide_special_idle_anim"}.get(field, field), f_pool):
                    ok = True
                    break
            if ok:
                direct += 1
            else:
                orphan.append((it["id"], it.get("name"), keys))
        print(f"== {field}: cards {len(cards)} / direct-row {direct} / not-in-row {len(orphan)}")
        for x in orphan[:6]:
            print("   ", x)

    # 4) model_change_color_id
    cards = [it for it in items if it.get("model_change_color_id")]
    direct = sum(1 for it in cards if any(k in fmap and jl(f_blob, fmap[k], "model_change_color_id", f_pool) for k in rk(it)))
    print("== model_change_color_id cards", len(cards), "direct", direct)

    # 5) theme poster vs img
    th = [it for it in items if it.get("theme")]
    n_img = sum(1 for it in th if it["theme"].get("img"))
    n_poster = sum(1 for it in th if it["theme"].get("poster"))
    n_time = sum(1 for it in th if it["theme"].get("open_time"))
    print("== theme fields: name", len(th), "img", n_img, "poster", n_poster, "open_time", n_time)

    # 6) 字段命名扫描（顶层键）
    keycnt = collections.Counter()
    for it in items:
        for k in it:
            keycnt[k] += 1
    print("== top-level keys (fashion-ish)")
    for k in sorted(keycnt):
        if k in ("dye", "theme", "obtain_res", "display_bg", "anim_graph", "value_words",
                 "rebirth_tex", "other_get_methods", "uncap_appear_gender", "bone_info",
                 "green_model", "preview_group", "cohabit_friendliness", "cohabit_level",
                 "model_paths", "npc_hidden", "tech_flags", "misc_flags", "show_schedule",
                 "show_name", "man_show_name", "part_code", "part_code_cn",
                 "model_change_color_id", "gift_package", "show_start"):
            print(f"   {k:24s}{keycnt[k]}")


if __name__ == "__main__":
    raise SystemExit(main())
