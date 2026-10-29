# -*- coding: utf-8 -*-
"""料理板块补图 + 制作食谱 + 效果数值。

用户报（2026-10-29）：料理没图、没制作食谱、没效果具体数值。

做法（数据源全部实解，不猜）：
  1) 图标：pe_fetch 按 ui/item_icon/icon_<item_id> 三档解析导出
     → assets/edible_icons/ed_<item_id>_b.png / _s.png。
  2) 食谱：join 同目录 recipe_book.json（cook_recipe_data 571 条已建板），
     dish_item_id == item_id 或 item_id ∈ item_ids 命中；
     材料 = food_materials 正值项 [type_id, count]。
  3) 效果数值：food_material_data（375 行食材属性表）按 type 聚合成员的
     hp_recover / satiety_recover / infection_recover / star 区间；
     成品效果数值由食材品质决定（表内无固定的"成品数值"列，
     dish_star_data / cook_recipe_data_key_data 为未解码格式，如实留缺）。

幂等：已有同源字段先清再写；--dry 只统计。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys
import time

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = WEB / "data/boards/edible_catalog.json"
BOARD_JS = WEB / "data/boards/edible_catalog.js"
RECIPES = WEB / "data/boards/recipe_book.json"
ICON_DIR = WEB / "assets/edible_icons"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core import bindict_table as BT  # noqa: E402


def gs(blob, pool, off, d=0):
    if d > 6:
        return []
    g = BT.read_27_group(blob, off)
    if not g:
        return []
    k, els = g
    o = []
    if k == 0x0B:
        for e in els:
            o += gs(blob, pool, e, d + 1)
    elif k == 0x05:
        for e in els:
            if 0 <= e < len(pool):
                o.append(pool[e])
    return o


def val(v, blob, pool):
    if isinstance(v, tuple) and len(v) == 2:
        if str(v[1]).startswith("jump:"):
            try:
                return gs(blob, pool, int(str(v[1]).split(":")[1]))
            except Exception:
                return []
        return [v[1]]
    return [v]


def load_table(stem):
    raw = (CD / (stem + ".py")).read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None, []
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    cnt = struct_cnt(body)
    if cnt is None:
        return None, []
    blob = body[8 + 4 * cnt:]
    cp = CD / (stem + "_chs.py")
    pool = []
    if cp.exists():
        try:
            pool = BT.parse_legacy_chs_pool(cp.read_bytes())
        except Exception:
            pool = []
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    return (blob, pool), rows


def struct_cnt(body):
    import struct
    if len(body) < 8:
        return None
    cnt = struct.unpack_from("<I", body, 0)[0]
    if cnt <= 0 or cnt > 900000:
        return None
    return cnt


def build_food_material_info():
    """type → {names, attr_minmax}（food_material_data 375 行）。"""
    (blob, pool), rows = load_table("food_material_data")
    if not rows:
        return {}
    by_type = {}
    for r in rows:
        f = r["values"]
        t = val(f.get("type"), blob, pool)
        t = int(t[0]) if t and isinstance(t[0], (int, float)) else None
        if t is None:
            continue
        d = by_type.setdefault(t, {"keys": [], "attrs": {}})
        d["keys"].append(int(r["key"]))
        for k in ("hp_recover", "satiety_recover", "infection_recover", "star"):
            v = val(f.get(k), blob, pool)
            if v and isinstance(v[0], (int, float)):
                d["attrs"].setdefault(k, []).append(float(v[0]))
    out = {}
    for t, d in by_type.items():
        mm = {}
        for k, vs in d["attrs"].items():
            if vs:
                lo, hi = min(vs), max(vs)
                mm[k] = [lo, hi] if lo != hi else [lo]
        out[t] = {"keys": d["keys"], "attrs": mm}
    return out


def name_members(ids):
    """食材 member item id → 名字（common_item_names 跨表查）。"""
    from toolkit_core import common_item_names as CIN
    try:
        m = CIN.lookup(sorted({int(i) for i in ids}))
    except Exception:
        m = {}
    return {int(k): v for k, v in m.items() if v}


def build_pe_cook_index():
    """PE cook_recipe_data 行键 → {desc, simple_desc, proficiency, dish_buff_duration}。"""
    (blob, pool), rows = load_table("cook_recipe_data")
    out = {}
    for r in rows or []:
        f = r["values"]

        def s(k):
            v = val(f.get(k), blob, pool)
            return v[0] if v and isinstance(v[0], str) else None

        def num(k):
            v = val(f.get(k), blob, pool)
            return v[0] if v and isinstance(v[0], (int, float)) else None
        try:
            key = int(r["key"])
        except (TypeError, ValueError):
            continue
        out[key] = {"key": key, "name": s("name"), "desc": s("desc"),
                    "simple_desc": s("simple_desc"),
                    "proficiency": num("proficiency"),
                    "dish_buff_duration": num("dish_buff_duration")}
    return out


def build_pe_edible_index():
    """PE edible_item_data：名字 → [{row_key, icon, 数值字段}]（同名多品质行全收）。"""
    (blob, pool), rows = load_table("edible_item_data")
    out = {}
    for r in rows or []:
        f = r["values"]
        nm = val(f.get("name"), blob, pool)
        if not nm or not isinstance(nm[0], str):
            continue
        ic = val(f.get("icon"), blob, pool)
        nums = {}
        for k in ("satiety_recover", "duration", "talent_hp_recover", "hp_recover",
                  "infection_recover", "talent_sfx_duration"):
            v = val(f.get(k), blob, pool)
            if v and isinstance(v[0], (int, float)):
                nums[k] = float(v[0])
        bd = val(f.get("buff_durations"), blob, pool)
        if bd:
            nums["buff_durations"] = [x for x in bd if isinstance(x, (int, float))]
        out.setdefault(nm[0].strip(), []).append({
            "row_key": int(r["key"]),
            "icon": ic[0] if ic and isinstance(ic[0], str) else None,
            "level": (val(f.get("level"), blob, pool) or [None])[0],
            "nums": nums,
        })
    return out


def pe_fetch_resolve(base, suf):
    import pe_fetch
    c = pe_fetch.con()
    return pe_fetch.resolve(base, suf, c)


def pe_fetch_export(base, suf, out: pathlib.Path):
    import pe_fetch
    c = pe_fetch.con()
    for sfx in (suf, ""):
        r = pe_fetch.resolve(base, sfx, c)
        if r:
            if pe_fetch.export(r[0], out):
                return True
    return False


ATTR_CN = {"hp_recover": "血量", "satiety_recover": "饱食度",
           "infection_recover": "感染", "star": "品质加成"}


def attr_text(mm):
    parts = []
    for k in ("hp_recover", "satiety_recover", "infection_recover", "star"):
        v = mm.get(k)
        if not v:
            continue
        if len(v) == 1:
            parts.append("%s%g" % (ATTR_CN[k], v[0]))
        else:
            parts.append("%s%g~%g" % (ATTR_CN[k], v[0], v[1]))
    return "、".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    recipes = json.loads(RECIPES.read_text(encoding="utf-8"))["items"]
    fm = build_food_material_info()
    pe_cook = build_pe_cook_index()
    pe_edible = build_pe_edible_index()

    # recipe 索引（recipe_book 板，简单生存快照 id 空间 77xxx）
    r_by_item = {}
    r_by_name = {}
    for rc in recipes:
        did = rc.get("dish_item_id")
        if did is not None:
            r_by_item.setdefault(int(did), rc)
        nm = (rc.get("dish_name") or rc.get("name") or "").strip()
        if nm:
            r_by_name.setdefault(nm, []).append(rc)

    st = {"料理卡": 0, "有图": 0, "缺图": 0, "有食谱": 0, "无食谱": 0,
          "有效果数值": 0, "图新导": 0, "同名多食谱": 0}
    fam_cache = {}
    for it in board["items"]:
        if (it.get("kind") or it.get("cookable")) != "料理":
            continue
        st["料理卡"] += 1
        try:
            iid = int(it.get("item_id"))
        except (TypeError, ValueError):
            continue
        nm_card = (it.get("name") or "").strip()

        # ── 1) 图标 ──
        # 先按名 join PE edible_item_data（成品行自带 icon 路径，如 icon_77001），
        # 命中不到再退回 icon_<item_id> 探测
        if not a.dry:
            pe_rows = pe_edible.get(nm_card) or []
            icon_paths = []
            for pr in pe_rows:
                if pr.get("icon") and pr["icon"] not in icon_paths:
                    icon_paths.append(pr["icon"])
            if not icon_paths:
                icon_paths = ["ui/item_icon/icon_%d" % iid]
            media = {"total": 0, "images": [], "missing": []}
            exported = set()
            for ip in icon_paths:
                base = ip.rsplit(".", 1)[0]
                for suf in ("_b", "_s"):
                    out = ICON_DIR / ("ed_%d%s.png" % (iid, suf)) if len(icon_paths) == 1 else \
                        ICON_DIR / ("ed_%d_%s%s.png" % (iid, base.rsplit("/", 1)[-1], suf))
                    rel = "assets/edible_icons/" + out.name
                    got = None
                    for sfx in (suf, ""):
                        got = pe_fetch_resolve(base, sfx)
                        if got:
                            break
                    if got:
                        if not out.exists() or a.force:
                            pe_fetch_export(base, suf, out)
                            st["图新导"] += 1
                        if out.exists() and rel not in exported:
                            media["images"].append({
                                "png": rel, "base": base, "suffix": suf, "via": "pe"})
                            exported.add(rel)
                    else:
                        media["missing"].append({"base": base, "suffix": suf})
                if exported:
                    break
            media["total"] = len(media["images"])
            it["_media"] = media
            it["icon_state"] = "有图" if media["images"] else "缺图"
            if media["images"]:
                st["有图"] += 1
            else:
                st["缺图"] += 1

        # ── 2) 食谱 ──
        # 优先同源：PE cook_recipe_data 行键 == 料理 item_id（101201=烤肉）
        pc = pe_cook.get(iid)
        rc = None
        join_kind = None
        cands = r_by_name.get(nm_card) or []
        if len(cands) == 1:
            rc = cands[0]
            join_kind = "name-unique"
        elif len(cands) > 1:
            rc = cands[0]
            join_kind = "name-ambiguous"
            st["同名多食谱"] += 1
        if rc or pc:
            st["有食谱"] += 1
            pos = (rc.get("materials_positive") or []) if rc else []
            mats = []
            for tid, cnt in pos:
                info = fm.get(int(tid)) or {}
                if int(tid) not in fam_cache:
                    fam_cache[int(tid)] = name_members(info.get("keys") or [])
                nm = next(iter(fam_cache[int(tid)].values()), "食材类%s" % tid)
                mats.append({"type_id": int(tid), "count": cnt, "name": nm})
            if not a.dry:
                if pc:
                    it["recipe_id"] = pc["key"]
                    it["recipe_source"] = ("com/cdata/cook_recipe_data.py#%d（同源："
                                           "行键=料理条目ID）" % pc["key"])
                    if pc.get("desc"):
                        it["desc"] = pc["desc"]
                    if pc.get("simple_desc"):
                        it["simple_desc"] = pc["simple_desc"]
                    it["proficiency"] = pc.get("proficiency")
                    dur = pc.get("dish_buff_duration")
                    it["buff_duration_text"] = ("%g 分钟" % (dur / 60.0)) if dur else None
                if rc:
                    it["recipe_materials"] = mats
                    it["recipe_text"] = "、".join(
                        "%s×%g" % (m["name"], m["count"]) for m in mats) or "—"
                    it.setdefault("recipe_id", rc.get("recipe_id"))
                    it["recipe_materials_source"] = (
                        "recipe_book 板（cook_recipe_data 简单生存快照）按名 join=%s" % join_kind)
                else:
                    it["recipe_materials_source"] = "recipe_book 板按名未命中（该配方不在快照）"
        else:
            st["无食谱"] += 1

        # ── 3) 效果数值 ──
        # 3a) PE 成品行数值（satiety_recover / duration / talent_hp_recover …），
        #     同名多行=品质档，取区间
        pe_rows = pe_edible.get(nm_card) or []
        pe_nums = {}
        for pr in pe_rows:
            for k, v in (pr.get("nums") or {}).items():
                if isinstance(v, list):
                    pe_nums.setdefault(k, []).extend(v)
                else:
                    pe_nums.setdefault(k, []).append(v)
        if pe_rows and not a.dry:
            it["pe_edible_rows"] = [pr["row_key"] for pr in pe_rows]
            parts = []
            CN2 = {"satiety_recover": "饱食度", "duration": "持续(秒)",
                   "talent_hp_recover": "血量", "hp_recover": "血量",
                   "infection_recover": "感染", "talent_sfx_duration": "特效(秒)"}
            for k in ("satiety_recover", "hp_recover", "talent_hp_recover",
                      "infection_recover", "duration", "talent_sfx_duration"):
                vs = pe_nums.get(k)
                if not vs:
                    continue
                lo, hi = min(vs), max(vs)
                parts.append("%s%g" % (CN2.get(k, k), lo) if lo == hi
                             else "%s%g~%g" % (CN2.get(k, k), lo, hi))
            if parts:
                it["pe_effect_text"] = "、".join(parts)
                it["pe_effect_source"] = ("com/cdata/edible_item_data.py 行 %s"
                                          % (",".join(str(pr["row_key"]) for pr in pe_rows[:6])))
                st["有效果数值"] += 1

        # 3b) 食材属性区间（经典服食材品质影响成品数值）
        if rc:
            ranges = {}
            for tid, _cnt in (rc.get("materials_positive") or []):
                mm = (fm.get(int(tid)) or {}).get("attrs") or {}
                for k, v in mm.items():
                    lo, hi = (v + v)[:2] if len(v) == 1 else v
                    cur = ranges.setdefault(k, [lo, hi])
                    cur[0] = min(cur[0], lo)
                    cur[1] = max(cur[1], hi)
            if ranges and not a.dry:
                it["ingredient_attr_range"] = ranges
                it["effect_value_text"] = attr_text(ranges)
                st["有效果数值"] += 1

    if not a.dry:
        board["meta"]["hide_media"] = False
        board["meta"]["icon_source"] = "PE ui/item_icon/icon_<item_id>（pe_fetch 三档实导）"
        board["meta"]["recipe_source_note"] = (
            "食谱/材料 join 自 recipe_book 板（cook_recipe_data 571 条）；"
            "效果数值列 = food_material_data 食材属性区间（成品数值由食材品质决定，"
            "配置无固定成品数值列；dish_star_data / cook_recipe_data_key_data 未解码格式，如实留缺）。")
        board["meta"]["field_labels"].update({
            "recipe_text": "制作食谱", "recipe_materials": "材料",
            "proficiency": "熟练度", "buff_duration_text": "效果时长",
            "effect_value_text": "效果数值（食材属性区间）", "recipe_id": "配方ID"})
        ts = time.strftime("%Y%m%d_%H%M%S")
        shutil.copy2(BOARD, BOARD.with_name(BOARD.name + ".bak_%s_edible" % ts))
        shutil.copy2(BOARD_JS, BOARD_JS.with_name(BOARD_JS.name + ".bak_%s_edible" % ts))
        BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
        BOARD_JS.write_text(
            "window.WIKI_BOARD_edible_catalog = "
            + json.dumps(board, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(st)
    return 0


def pe_fetch_hit(iid, suf):
    import pe_fetch
    c = pe_fetch.con()
    return pe_fetch.resolve("ui/item_icon/icon_%d" % iid, suf, c)


def export_icon(iid, suf, out: pathlib.Path):
    import pe_fetch
    c = pe_fetch.con()
    for sfx in (suf, ""):
        r = pe_fetch.resolve("ui/item_icon/icon_%d" % iid, sfx, c)
        if r:
            if pe_fetch.export(r[0], out):
                return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
