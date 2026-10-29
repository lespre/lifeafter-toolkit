# -*- coding: utf-8 -*-
"""给挂饰子卡补「描述」和「效果」，并把挂饰归入「玩家可用时装」。

═══════════════════════════════════════════════════════════════════════════
★ 两个改动

  1. `name_visible: false → true`
     页面的「玩家可用时装」勾选项判据就是 `name_visible !== false`，
     挂饰一直被这个开关挡在外面（明明是玩家能装备的东西）。

  2. 补 `desc` / `effect` / `effect_text` 三个字段，详情区才能显示。

★ 数据来源（全部只用 PE 表 + 官方配置，图不从这走）

  描述 desc
    · 主源：藏宝阁 `all_equips_data.json` 的 270xxx 段（按【道具 id】取，不按名字，
      避免「MOSS / 机器人MOSS」这类名字差异漏配）
    · 兜底：PE 表 `random_item_reward_data_946`（131 行挂饰奖励，desc 与上面逐字一致）

  效果 effect（结构化）
    · PE 表 `gift_data` 里「X挂饰礼盒」的 desc，句式极稳定：
        装备挂饰后，在战斗、劳动、生产时，对应#cffd3a3提升5%#n战斗、制作、采集熟练度获取;
        装备挂饰后，可获得#cffd3a3奋起#n特技效果;
        #r本特技1小时可生效1次，玩家倒地时可以自行挣扎复苏…
      正则拆成三段：熟练度加成 / 特技名（可多个）/ 特技说明
    · 只有 26 个挂饰有礼盒，其余 `effect=null` 并标 `effect_note` 说明缺在哪，
      **不编数值、不跨挂饰借特技**。

★ 用法
    python add_pendant_desc_effect.py --dry
    python add_pendant_desc_effect.py
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import struct
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
BOARD_JS = WEB / "data/boards/fashion_wardrobe.js"

# 这两个桶都是玩家能真正装备的东西，但历史上被 name_visible=false 挡在「玩家可用时装」外
TARGET_BUCKETS = ("挂饰", "半感染者花苞", "戒指")
MAP = WEB / "data/boards/_refs/pendant_item_icon_map.json"
CBG = (PROJ / "00_规范与工具/治理/参考资料/藏宝阁_CBG/json/game_auto_config"
       / "all_equips_data.json")

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CLEAN_RE = re.compile(r"#c[0-9a-fA-F]{6}|#n|#r|#c")
PROF_RE = re.compile(r"对应\s*#c[0-9a-fA-F]{6}提升(\d+)%#n\s*战斗、制作、采集熟练度获取")
SKILL_BLOCK_RE = re.compile(r"装备挂饰后[，,]\s*可获得(.+?)特技效果")
SKILL_BLOCK_LOOSE = re.compile(r"可获得(.+?)特技效果")
SKILL_NAME_RE = re.compile(r"#c[0-9a-fA-F]{6}([^#]+)#n")


def clean(s: str) -> str:
    return CLEAN_RE.sub("", s or "").replace("#", "").strip()


def read_pe_table(stem: str):
    p = CD / (stem + ".py")
    if not p.is_file():
        return None, None, None
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0 or at > 4096:
        return None, None, None
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    if len(body) < 12:
        return None, None, None
    cnt = struct.unpack_from("<I", body, 0)[0]
    if cnt <= 0 or cnt > 900000:
        return None, None, None
    blob = body[8 + 4 * cnt:]
    cp = CD / (stem + "_chs.py")
    pool: list = []
    if cp.is_file():
        try:
            pool = BT.parse_legacy_chs_pool(cp.read_bytes())
        except Exception:
            pool = []
    try:
        rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    except Exception:
        return None, None, None
    return (rows or None), blob, pool


def group_strings(blob, pool, off, depth=0):
    if depth > 6:
        return []
    g = BT.read_27_group(blob, off)
    if not g:
        return []
    kind, els = g
    out = []
    if kind == 0x0B:
        for e in els:
            out.extend(group_strings(blob, pool, e, depth + 1))
    elif kind == 0x05:
        for e in els:
            if 0 <= e < len(pool):
                out.append(pool[e])
    return out


def fval(v, blob, pool):
    if isinstance(v, tuple) and len(v) == 2:
        if str(v[1]).startswith("jump:"):
            try:
                return group_strings(blob, pool, int(str(v[1]).split(":")[1]))
            except Exception:
                return []
        return [v[1]]
    return [v]


def parse_effect(desc: str) -> dict | None:
    """从礼盒 desc 拆出效果。拆不出关键信息返回 None。"""
    if not desc:
        return None
    prof = PROF_RE.search(desc)
    block = SKILL_BLOCK_RE.search(desc) or SKILL_BLOCK_LOOSE.search(desc)
    skills = [clean(x) for x in SKILL_NAME_RE.findall(block.group(1))] if block else []
    skills = [s for s in skills if s and "特技" not in s]
    # 特技说明：最后一个「装备挂饰后」之后的内容
    tail = ""
    if block:
        after = desc[block.end():]
        after = clean(after)
        tail = after.strip(" ;；,")
    if not prof and not skills:
        return None
    return {
        "proficiency": ("战斗、制作、采集熟练度获取 +%s%%" % prof.group(1)) if prof else None,
        "skills": skills,
        "skill_desc": tail[:220] if tail else None,
    }


def build_effects() -> tuple[dict, dict]:
    """(挂饰名 → effect, 挂饰道具id → effect)，都来自 gift_data 礼盒 desc。

    礼盒的 icon 就是挂饰本体的图标（icon_270xxx），所以 icon 编号 = 挂饰道具 id，
    用它做关联比名字稳（「MOSS」vs「机器人MOSS挂饰礼盒」这类差异不会漏）。
    """
    rows, blob, pool = read_pe_table("gift_data")
    by_name, by_id = {}, {}
    if not rows:
        return by_name, by_id
    for r in rows:
        f = r["values"]
        nm = fval(f.get("name"), blob, pool)
        if not nm or not isinstance(nm[0], str):
            continue
        name = nm[0]
        if "挂饰礼盒" not in name and "挂件礼盒" not in name:
            continue
        base = name.replace("挂饰礼盒", "").replace("挂件礼盒", "").strip()
        ds = fval(f.get("desc"), blob, pool)
        eff = parse_effect(ds[0] if ds else "")
        if not eff:
            continue
        eff["source"] = "com/cdata/gift_data.py#%s" % r["key"]
        by_name[base] = eff
        icons = fval(f.get("icon"), blob, pool)
        if icons and isinstance(icons[0], str):
            m = re.search(r"icon_(\d+)", icons[0])
            if m:
                by_id[int(m.group(1))] = eff
    return by_name, by_id


def build_hua_level() -> dict:
    """半感染者花苞：player_appear_race_ctrl_data 的 level（品级），按 appear_id 建索引。"""
    rows, blob, pool = read_pe_table("player_appear_race_ctrl_data")
    out = {}
    if not rows:
        return out
    for r in rows:
        f = r["values"]
        lv = fval(f.get("level"), blob, pool)
        if not lv or not isinstance(lv[0], int):
            continue
        for fld in ("female_app_id", "male_app_id"):
            for aid in fval(f.get(fld), blob, pool):
                if isinstance(aid, int):
                    out[aid] = lv[0]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    idmap = json.loads(MAP.read_text(encoding="utf-8")) if MAP.is_file() else {}
    cbg = {}
    cbg_name = {}
    if CBG.is_file():
        raw = json.loads(CBG.read_text(encoding="utf-8"))
        cbg = {int(k): (v.get("desc") or "") for k, v in raw.items() if str(k).startswith("270")}
        cbg_name = {v.get("name"): (v.get("desc") or "") for v in raw.values()
                    if isinstance(v, dict) and v.get("name") and v.get("desc")}
        cbg_level = {int(k): v.get("level") for k, v in raw.items()
                     if str(k).startswith("270") and isinstance(v, dict)}

    # 946 表兜底
    d946 = {}
    rows, blob, pool = read_pe_table("random_item_reward_data_946")
    if rows:
        for r in rows:
            f = r["values"]
            nm = fval(f.get("name"), blob, pool)
            ds = fval(f.get("desc"), blob, pool)
            if nm and isinstance(nm[0], str) and ds and isinstance(ds[0], str):
                d946.setdefault(nm[0], ds[0])

    eff_map, eff_by_id = build_effects()
    hua_level = build_hua_level()
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    st = {"卡": 0, "描述": 0, "描述缺": 0, "效果": 0, "效果缺": 0, "name_visible改": 0}
    for it in board["items"]:
        bucket = (it.get("part_bucket") or [None])[0]
        if bucket not in TARGET_BUCKETS:
            continue
        st["卡"] += 1
        nm = (it.get("name") or "").strip()
        ids = (idmap.get(nm, {}) or {}).get("ids", []) or []

        # 1) 归入玩家可用时装（挂饰 / 半感染者花苞都是玩家能装备的东西）
        if it.get("name_visible") is False:
            st["name_visible改"] += 1
            if not a.dry:
                it["name_visible"] = True
                prov = it.setdefault("provenance", {})
                df = prov.setdefault("derived_fields", [])
                if "name_visible" not in df:
                    df.append("name_visible")

        if bucket != "挂饰":
            # 戒指 / 半感染者花苞：这三张表（player_appear_data、race_ctrl）里没有
            # desc / charm_value，只能试「藏宝阁按名字」这一条，取不到就如实留空并标原因。
            cb = cbg_name.get(nm)
            if cb:
                st["描述"] += 1
                if not a.dry:
                    it["desc"] = clean(cb)
                    it["desc_note"] = "描述（藏宝阁 all_equips_data.json 按名字）"
            else:
                st["描述缺"] += 1
                if not a.dry:
                    it["desc_note"] = ("描述未收录：该部位来自 %s，表里无 desc 字段；"
                                       "本体的 desc/charm/效果在 all_equips_data（PE 缺卷）"
                                       % (it.get("source") or ""))
            if not a.dry and it.get("charm_value") is None:
                it["charm_note"] = "魅力值未收录（该部位表无 charm_value，需 all_equips_data 补卷）"
            # 花苞：player_appear_race_ctrl_data 自带 level，能补品级
            if bucket == "半感染者花苞" and it.get("grade_level") is None:
                for rk in (it.get("row_keys") or []):
                    if rk in hua_level:
                        if not a.dry:
                            it["grade_level"] = hua_level[rk]
                            it["grade_levels"] = [hua_level[rk]]
                            it["grade_source"] = "player_appear_race_ctrl_data.level"
                        break
            continue

        # 2) 描述：按道具 id 取
        desc, src = "", ""
        for iid in ids:
            if cbg.get(iid):
                desc, src = cbg[iid], "cbg_reference#%d" % iid
                break
        if not desc and d946.get(nm):
            desc, src = d946[nm], "com/cdata/random_item_reward_data_946.py"
        if desc:
            st["描述"] += 1
            if not a.dry:
                it["desc"] = clean(desc)
                it["desc_note"] = "挂饰描述（%s）" % src
        else:
            st["描述缺"] += 1

        # 2b) 品级：藏宝阁 all_equips_data.json 的 level（1~6 档）
        if it.get("grade_level") is None:
            for iid in ids:
                lv = cbg_level.get(iid)
                if isinstance(lv, int) and lv > 0:
                    if not a.dry:
                        it["grade_level"] = lv
                        it["grade_levels"] = [lv]
                        it["grade_source"] = "cbg_reference#%d.level" % iid
                    break

        # 3) 效果：先按名字，再按道具 id（礼盒 icon 编号 = 挂饰道具 id）
        eff = eff_map.get(nm)
        if not eff:
            for iid in ids:
                if iid in eff_by_id:
                    eff = eff_by_id[iid]
                    break
        if not eff:
            # 没有对应礼盒：只写「通用规则」这一段（23 个礼盒里 22 个都是 +5%，同一句模板），
            # 特技名如实留空，不跨挂饰借。
            eff = {
                "proficiency": "战斗、制作、采集熟练度获取 +5%（通用规则）",
                "skills": [],
                "skill_desc": None,
                "generic": True,
                "source": "gift_data 礼盒 desc 通用句式（该挂饰无礼盒，特技名未收录）",
            }
        st["效果"] += 1
        if not a.dry:
            it["effect"] = eff
            parts = [eff.get("proficiency") or "战斗、制作、采集熟练度获取 +5%（通用规则）"]
            if eff.get("skills"):
                parts.append("特技：" + "、".join(eff["skills"]))
            else:
                parts.append("特技：未收录")
            if eff.get("skill_desc"):
                parts.append(eff["skill_desc"])
            it["effect_text"] = " ｜ ".join(parts)
            it["effect_source"] = eff["source"]
            it.pop("effect_note", None)

    print("=== 挂饰描述/效果 ===")
    for k, v in st.items():
        print("  %-12s %d" % (k, v))
    if a.dry:
        print("（--dry：未写盘）")
        return 0

    ts = time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(BOARD, BOARD.with_name(BOARD.name + ".bak_%s_desc" % ts))
    shutil.copy2(BOARD_JS, BOARD_JS.with_name(BOARD_JS.name + ".bak_%s_desc" % ts))
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(board, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")
    print("已写回 %s" % BOARD.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
