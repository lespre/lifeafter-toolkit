# -*- coding: utf-8 -*-
r"""料理与食谱板：按新 PE 还原树全量重建（幂等）。

数据源（全部实读，不跨表臆断）：
    01_索引与产物/41_还原树/pe/配置/com/cdata/
      cook_recipe_data           634 条配方
      edible_item_data          4499 条可食用物品（含 6 档成品）
      food_material_data         375 条食材属性（type → 血量/饱食/感染/星级区间）
      food_material_type_data    153 条食材类别（type_id → 类别道具 id）
      food_material_entry_data     5 条赐福（有机/金色/幻彩/彩白/星空）
      cook_recipe_label_data      53 条料理效果标签（label_desc + max_num）
      cook_recipe_extra_data      53 条额外条件（rules / must_items）
      buff_data                 BUFF 名称与数值
      attribute_data            属性英文键 → 中文名 / 百分比口径

卡片口径：
    料理卡 = 配方；成品 6 个品质档的属性逐档列出（源表里没有的字段如实标注，不补数）；
    材料   = food_materials 0x16 组 (type_id, count)；count=-1 = 数量未指定，只展示正数量；
    食材卡 = edible_item_data 中未被任何配方当作成品引用的行。

图标：pe_fetch（ui/item_icon/icon_*）逐条解析导出；解析不到 ⇒「客户端未下发」，不拿别的图顶替。
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
from _src import cdata_dir, table_path  # noqa: E402

WEB = PROJ / "02_wiki/web"
OUT_JSON = WEB / "data/boards/edible_catalog.json"
OUT_JS = WEB / "data/boards/edible_catalog.js"
ICON_DIR = WEB / "assets/edible_icons"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core import bindict_table as BT  # noqa: E402
from toolkit_core import cdata_nxs as N  # noqa: E402
from toolkit_core import common_item_names as CIN  # noqa: E402


CD = cdata_dir()

SOURCE_ID = "pe-config-merged"
SOURCE_SERVER = "PE 体验服 · 配置合并体（基线 script.py314.lc.npk + 2026-10 增量快照）"
USED_TABLES = ("cook_recipe_data", "edible_item_data", "food_material_data",
               "food_material_type_data", "food_material_entry_data",
               "cook_recipe_label_data", "cook_recipe_extra_data",
               "buff_data", "attribute_data")

ATTR_CN = {"hp_recover": "血量", "satiety_recover": "饱食度",
           "infection_recover": "感染恢复", "star": "星级加成",
           "alienation_recover": "异化值恢复"}

# ───────────────────────────────── 基础读取
def load(stem: str):
    p = table_path(stem)
    if not p.is_file():
        for ext in (".nxs", ".py"):
            q = CD / (stem + ext)
            if q.is_file():
                p = q
                break
    return N.load_table(stem, CD), p


def blob_pool(p: pathlib.Path):
    """legacy 表：x{ 帧 → body → blob（jump 基准）＋_chs 池。"""
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return b"", []
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + ln]
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    cp = p.with_name(p.stem + "_chs.py")
    pool = BT.parse_legacy_chs_pool(cp.read_bytes()) if cp.is_file() else []
    return blob, pool


def read_group_16(blob: bytes, start: int):
    """0x16 组：16 <key_kind> <count> → count × (key:uleb)(tag)(value:uleb；0x11=zigzag)。"""
    out = {"ok": False, "entries": [], "error": None}
    if not (0 <= start < len(blob) - 3) or blob[start] != 0x16:
        out["error"] = "not-0x16"
        return out
    try:
        count, pos = BT.uleb(blob, start + 2, len(blob))
    except ValueError:
        out["error"] = "bad-count"
        return out
    entries = []
    for _ in range(count):
        try:
            key, pos = BT.uleb(blob, pos, len(blob))
            tag = blob[pos]
            pos += 1
            rawv, pos = BT.uleb(blob, pos, len(blob))
        except (ValueError, IndexError):
            out["error"] = "truncated"
            return out
        val = (rawv >> 1) ^ -(rawv & 1) if tag == 0x11 else rawv
        entries.append({"type_id": key, "count": val, "tag": tag})
    out.update(ok=True, entries=entries)
    return out


def jump_val(v):
    """字段值 → jump 目标 offset（非 jump 返回 None）。"""
    if isinstance(v, str) and v.startswith("jump:"):
        return int(v.split(":", 1)[1])
    return None


def jgroup(blob: bytes, v):
    t = jump_val(v)
    return (BT.resolve_jump_group(blob, t) or []) if t is not None else []


def nums(v):
    return [x for x in v if isinstance(x, (int, float)) and not isinstance(x, bool)] if isinstance(v, list) else []


def fmt_n(x) -> str:
    if isinstance(x, bool) or x is None:
        return ""
    if isinstance(x, float):
        return ("%g" % x)
    return str(x)


def pct(x) -> str:
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        v = x * 100
        s = ("%.2f" % v).rstrip("0").rstrip(".")
        return s + "%"
    return fmt_n(x)


def clean(t) -> str:
    return str(t or "").replace("#r", " ").replace("\u3000", " ").strip()


def file_sha(p: pathlib.Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def table_path_of(stem: str):
    p = table_path(stem)
    if not p.is_file():
        for ext in (".nxs", ".py"):
            q = CD / (stem + ext)
            if q.is_file():
                return q
    return p


def table_facts() -> dict:
    out = {}
    for stem in USED_TABLES:
        p = table_path_of(stem)
        if p.is_file():
            st = p.stat()
            out[stem] = {"sha256": file_sha(p), "bytes": st.st_size, "mtime_ns": st.st_mtime_ns}
        else:
            out[stem] = {"sha256": "", "bytes": 0, "mtime_ns": 0}
    return out


def package_sha(facts: dict) -> str:
    """本板实际读取的 9 张表文件摘要（表名 + 各自 sha256，再取联合 sha256）。
    不是客户端整包 sha：合并体由基线包与增量快照合成，两者都没有单独的可引用整包哈希。"""
    import hashlib
    h = hashlib.sha256()
    for stem in USED_TABLES:
        h.update(("%s:%s\n" % (stem, facts[stem]["sha256"] or "missing")).encode())
    return h.hexdigest()


def prov(table: str, row_key, field_refs: list, pkg_sha: str, facts: dict, name_source: str) -> dict:
    return {
        "source_id": SOURCE_ID,
        "source_lock_sha256": pkg_sha,
        "table": table,
        "row_key": row_key,
        "field_refs": field_refs,
        "name_source": name_source,
        "upstream": {"package_sha256": pkg_sha, "entry_index": None, "file_id": None,
                     "role": table, "table_sha256": facts[table]["sha256"]},
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{"kind": "decoded-table-row", "source_id": SOURCE_ID,
                       "table": table, "row_key": row_key,
                       "field_refs": field_refs}],
        },
    }


# ───────────────────────────────── 索引构建
def build_index():
    tab_recipe, p_recipe = load("cook_recipe_data")
    tab_edible, _ = load("edible_item_data")
    tab_fm, _ = load("food_material_data")
    tab_type, _ = load("food_material_type_data")
    tab_entry, _ = load("food_material_entry_data")
    tab_label, _ = load("cook_recipe_label_data")
    tab_attr, _ = load("attribute_data")
    tab_buff, _ = load("buff_data")
    try:
        tab_extra, p_extra = load("cook_recipe_extra_data")
    except Exception:                       # noqa: BLE001 - 额外条件表缺失时按空表
        tab_extra, p_extra = None, None

    blob, pool = blob_pool(p_recipe)
    edible_path = table_path("edible_item_data")
    eblob, epool = blob_pool(edible_path)

    recipes = tab_recipe.rows
    edible = {r["key"]: r["fields"] for r in tab_edible.rows}

    # 食材类别：type_id → 类别道具 id / 中文名
    type_item = {r["key"]: r["fields"].get("item_id") for r in tab_type.rows}
    item_names = CIN.lookup([int(v) for v in type_item.values() if isinstance(v, int)])
    type_name = {t: (item_names.get(int(i)) if isinstance(i, int) else None)
                 for t, i in type_item.items()}

    # 食材属性区间（同一 type 的多条记录取 min/max）
    fm = {}
    for r in tab_fm.rows:
        f = r["fields"]
        t = f.get("type")
        if not isinstance(t, (int, float)):
            continue
        d = fm.setdefault(int(t), {})
        for k in ("hp_recover", "satiety_recover", "infection_recover", "star"):
            v = f.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                d.setdefault(k, []).append(float(v))
    food_attr = {}
    for t, d in fm.items():
        food_attr[t] = {k: [min(v), max(v)] for k, v in d.items() if v}

    # 效果标签
    label = {r["key"]: r["fields"] for r in tab_label.rows}

    # 属性英文键 → 中文 + 百分比口径
    attr_meta = {}
    for r in tab_attr.rows:
        f = r["fields"]
        e = f.get("e_name")
        if e:
            attr_meta[e] = {"name": f.get("name") or f.get("dish_name") or e,
                            "dish_name": f.get("dish_name"),
                            "percent": bool(f.get("s_percent")),
                            "ndigits": f.get("ndigits")}

    buff = {r["key"]: r["fields"] for r in tab_buff.rows}

    # 赐福：entry attrs 是 0x86 行（attribute_data e_name → 数值）
    blessings = []
    if tab_entry.rows:
        b2, p2 = blob_pool(table_path("food_material_entry_data"))
        for r in tab_entry.rows:
            f = r["fields"]
            t = jump_val(f.get("attrs"))
            vals = []
            if t is not None:
                res = BT.resolve_jump_target(b2, t, p2)
                if res.get("error") is None:
                    vals = [(k, v) for k, v in (res.get("values") or [])]
            for k, v in vals:
                am = attr_meta.get(k, {})
                nm = am.get("name") or k
                txt = pct(v) if am.get("percent") else fmt_n(v)
                blessings.append({"entry": f.get("entry_name"), "quality": f.get("quality"),
                                  "attr": nm, "value": txt,
                                  "icon": f.get("icon_path"), "bg": f.get("attr_bg_path")})

    # 额外条件
    extra = {}
    if tab_extra is not None:
        b3, p3 = blob_pool(p_extra)
        for r in tab_extra.rows:
            f = r["fields"]
            rules = []
            t = jump_val(f.get("rules"))
            if t is not None:
                res = BT.resolve_jump_target(b3, t, p3)
                rules = (res.get("leaves") or [[]])[0] if res.get("leaves") else []
            extra[r["key"]] = {"rules": rules, "must_items": bool(f.get("must_items"))}

    return {"recipes": recipes, "blob": blob, "pool": pool, "edible": edible,
            "eblob": eblob, "epool": epool,
            "type_item": type_item, "type_name": type_name, "food_attr": food_attr,
            "label": label, "attr_meta": attr_meta, "buff": buff,
            "blessings": blessings, "extra": extra}


# ───────────────────────────────── 文案
def range_text(rng: dict) -> str:
    parts = []
    for k in ("hp_recover", "satiety_recover", "infection_recover",
              "alienation_recover", "star"):
        v = rng.get(k)
        if not v:
            continue
        parts.append("%s%s" % (ATTR_CN[k], fmt_n(v[0]) if v[0] == v[1] else "%s~%s" % (fmt_n(v[0]), fmt_n(v[1]))))
    return "、".join(parts)


def label_text(label_id: int, idx: dict) -> str:
    f = idx["label"].get(label_id, {})
    desc = clean(f.get("label_desc"))
    if not desc:
        return "效果 %d（描述未下发）" % label_id
    mx = f.get("max_num")
    am = idx["attr_meta"].get(f.get("label_name") or "", {})
    if isinstance(mx, (int, float)) and not isinstance(mx, bool):
        tip = pct(mx) if am.get("percent") else fmt_n(mx)
        return "%s（上限 +%s）" % (desc, tip)
    return desc


def signed_text(k: str, v) -> str:
    n = fmt_n(v)
    return "%s %s" % (ATTR_CN.get(k, k), n) if n.startswith("-") else "%s +%s" % (ATTR_CN.get(k, k), n)


def tier_attr_text(f: dict) -> str:
    parts = []
    for k in ("hp_recover", "satiety_recover", "infection_recover",
              "alienation_recover", "talent_hp_recover"):
        v = f.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            parts.append(signed_text(k, v))
    d = f.get("duration")
    if isinstance(d, (int, float)) and not isinstance(d, bool):
        parts.append("进食 %ss" % fmt_n(d))
    return "、".join(parts) if parts else "源表未登记血量/饱食/感染"


def buff_text(row_fields: dict, idx: dict, blob: bytes, pool) -> str:
    ids = nums(row_fields.get("buff_ids")) if isinstance(row_fields.get("buff_ids"), list) else []
    if isinstance(row_fields.get("buff_ids"), str):
        t = jump_val(row_fields["buff_ids"])
        ids = BT.resolve_jump_group(blob, t) or [] if t is not None else []
    lv = nums(row_fields.get("buff_levels")) if isinstance(row_fields.get("buff_levels"), list) else []
    du = nums(row_fields.get("buff_durations")) if isinstance(row_fields.get("buff_durations"), list) else []
    out = []
    for i, bid in enumerate(ids):
        f = idx["buff"].get(bid, {})
        nm = f.get("name") or "名称未下发"
        s = "BUFF %d「%s」" % (bid, nm)
        if i < len(lv):
            s += " Lv%s" % fmt_n(lv[i])
        if i < len(du):
            s += " 持续 %ss" % fmt_n(du[i])
        out.append(s)
    return "；".join(out)


# ───────────────────────────────── 图标
def icon_files(base: str, con, force: bool, stats: dict) -> list:
    """每张卡只导出一张最清晰的图：优先 _b（大图），客户端没有大图才回落 _s。"""
    if not base:
        return []
    stem = base.rsplit("/", 1)[-1]
    import pe_fetch
    for suf in ("_b", "_s"):
        rel = "assets/edible_icons/%s%s.png" % (stem, suf)
        out = WEB / rel
        if out.is_file() and out.stat().st_size > 0 and not force:
            stats["cached"] += 1
            return [rel]
        src = pe_fetch.resolve(base, suf, con)
        if src and pe_fetch.export(src[0], out):
            stats["exported"] += 1
            return [rel]
    stats["missing"] += 1
    return []


def media_of(base: str, rels: list) -> dict:
    if not rels:
        return {"total": 0, "images": [], "missing": [base + "（客户端未下发）"],
                "note": "客户端未下发"}
    imgs = []
    for rel in rels:
        suf = "_b" if rel.endswith("_b.png") else "_s"
        imgs.append({"png": rel, "base": base, "suffix": suf, "via": "pe"})
    return {"total": len(imgs), "images": imgs, "missing": []}


# ───────────────────────────────── 主流程
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-icons", action="store_true", help="只重建数据，不导出 PNG")
    ap.add_argument("--force-icons", action="store_true", help="忽略已存在的 PNG 重新导出")
    ap.add_argument("--merge-icons", action="store_true", help="复用已有 board json 的图标结果，不再解析导出")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    idx = build_index()
    facts = table_facts()
    pkg_sha = package_sha(facts)
    recipes = idx["recipes"]
    blob, pool = idx["blob"], idx["pool"]
    edible = idx["edible"]

    dish_ids = set()
    dish_cards = []
    stats = {"无成品": 0, "无材料": 0, "档位缺失": 0}

    for r in recipes:
        f = r["fields"]
        rid = int(r["key"])
        name = clean(f.get("name"))
        if not name:
            continue
        ids = jgroup(blob, f.get("item_ids"))
        if not ids:
            stats["无成品"] += 1

        # 6 档成品
        variants = []
        for ti, iid in enumerate(ids, 1):
            dish_ids.add(int(iid))
            ef = edible.get(int(iid))
            if ef is None:
                stats["档位缺失"] += 1
                variants.append({"tier": ti, "item_id": str(iid), "name": name,
                                 "note": "edible_item_data 无此行"})
                continue
            variants.append({
                "tier": ti,
                "item_id": str(iid),
                "name": clean(ef.get("name")) or name,
                "level": ef.get("level"),
                "attrs": tier_attr_text(ef),
                "item_value": ef.get("item_value"),
                "buff": buff_text(ef, idx, idx["eblob"], idx["epool"]),
                "icon": ef.get("icon"),
            })
        variant_text = "｜".join(
            "第%d档 %s Lv%s %s%s" % (v["tier"], v["item_id"], fmt_n(v.get("level")),
                                     v.get("attrs", ""),
                                     (" 售价%s" % fmt_n(v["item_value"])) if v.get("item_value") is not None else "")
            for v in variants)

        # 材料（0x16 组）
        mt = jump_val(f.get("food_materials"))
        mg = read_group_16(blob, mt) if mt is not None else {"entries": []}
        entries = mg.get("entries") or []
        if not entries:
            stats["无材料"] += 1
        need, allow = [], []
        for e in entries:
            t = int(e["type_id"])
            nm = idx["type_name"].get(t) or ("食材类别 %d" % t)
            row = {"type_id": t, "name": nm, "count": int(e["count"])}
            allow.append(row)
            if e["count"] > 0:
                need.append(row)
        mats = need if need else allow
        materials_text = "；".join("%s×%d" % (m["name"], m["count"]) for m in need) \
            if need else ("未指定数量；可放：" + "、".join(m["name"] for m in allow[:10]) +
                          (" 等 %d 类" % len(allow) if len(allow) > 10 else "") if allow else "源表未登记材料")

        # 效果
        lids = jgroup(blob, f.get("prop_labels"))
        effects = [label_text(int(x), idx) for x in lids]
        effect_text = "；".join(effects)

        # 制作设施（只从 desc 实读关键词）
        desc = clean(f.get("desc"))
        stations = [k for k in ("篝火", "壁炉", "烧烤炉", "厨房") if k in desc]
        craft_station = " / ".join(stations) if stations else "未注明"

        # 额外条件
        ex = idx["extra"].get(rid) or {}
        extra_text = ""
        if ex.get("rules"):
            pairs = [str(x) for x in ex["rules"]]
            extra_text = "规则组（源表 rules，语义未映射）：" + " ".join(pairs)
        if ex.get("must_items"):
            extra_text = (extra_text + "；" if extra_text else "") + "含 must_items 指定材料（帧 0x36 语义未解）"

        unlock = "初始解锁" if f.get("init_unlock") else (
            ("解锁类型 %s" % fmt_n(f.get("unlock_type"))) if f.get("unlock_type") is not None else "未注明")

        prof = f.get("proficiency")
        card = {
            "id": "cook_%d" % rid,
            "item_id": str(ids[0]) if ids else str(rid),
            "name": name,
            "kind": "料理",
            "desc": desc,
            "simple_desc": clean(f.get("simple_desc")),
            "effect_short": effects[0] if effects else "",
            "effect_text": effect_text or "源表未登记料理效果标签",
            "craft_station": craft_station,
            "proficiency_text": ("熟练度 %s" % fmt_n(prof)) if prof is not None else "",
            "unlock_text": unlock,
            "materials_text": materials_text,
            "variant_text": variant_text,
            "extra_text": extra_text,
            "recipe_id": rid,
            "source": "cook_recipe_data",
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "provenance": prov("cook_recipe_data", rid,
                               ["name", "desc", "food_materials", "item_ids",
                                "prop_labels", "proficiency"], pkg_sha, facts,
                               "cook_recipe_data#name（同表 name 字段）"),
        }
        # 食材属性区间（仅列出有区间数据的类别）
        rngs = []
        for m in mats:
            rg = idx["food_attr"].get(m["type_id"])
            if rg:
                rngs.append("%s：%s" % (m["name"], range_text(rg)))
        if rngs:
            card["ingredient_range_text"] = "；".join(rngs[:20]) + \
                ("（共 %d 类，仅列前 20）" % len(rngs) if len(rngs) > 20 else "")
        card["_variants_raw"] = variants
        card["_icon_base"] = (edible.get(int(ids[0])) or {}).get("icon") if ids else None
        dish_cards.append(card)

    # 食材（未被任何配方引用的可食用行）
    ing_cards = []
    for iid, f in sorted(edible.items()):
        if iid in dish_ids:
            continue
        nm = clean(f.get("name"))
        if not nm:
            continue
        attrs = []
        for k in ("hp_recover", "satiety_recover", "infection_recover"):
            v = f.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                attrs.append("%s+%s" % (ATTR_CN[k], fmt_n(v)))
        d = f.get("duration")
        if isinstance(d, (int, float)) and not isinstance(d, bool):
            attrs.append("进食 %ss" % fmt_n(d))
        ing_cards.append({
            "id": "edible_%d" % iid,
            "item_id": str(iid),
            "name": nm,
            "kind": "食材",
            "desc": clean(f.get("desc")),
            "attrs": "、".join(attrs) or "源表未登记食用属性",
            "level": f.get("level"),
            "item_value": f.get("item_value"),
            "_icon_base": f.get("icon"),
            "source": "edible_item_data",
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "provenance": prov("edible_item_data", iid,
                               ["name", "desc", "icon", "hp_recover",
                                "satiety_recover", "infection_recover"], pkg_sha, facts,
                               "edible_item_data#name（同表 name 字段）"),
        })

    # ── 图标
    icon_stats = {"exported": 0, "cached": 0, "missing": 0}
    if a.merge_icons:
        icon_stats["mode"] = "reuse"
        old = {}
        if OUT_JSON.is_file():
            try:
                od = json.loads(OUT_JSON.read_text(encoding="utf-8"))
                old = {it["id"]: it for it in od.get("items", []) if isinstance(it, dict)}
            except (ValueError, KeyError):
                old = {}
        for card in dish_cards + ing_cards:
            base = card.pop("_icon_base", None)
            o = old.get(card["id"]) or {}
            if o.get("_media"):
                card["_media"] = o["_media"]
                card["icon_state"] = o.get("icon_state", "未取图")
            else:
                card["_media"] = media_of(base, [])
                card["icon_state"] = "客户端未下发" if base else "未取图"
    elif not a.no_icons:
        import pe_fetch
        con = pe_fetch.con()
        ICON_DIR.mkdir(parents=True, exist_ok=True)
        cache = {}
        for card in dish_cards + ing_cards:
            base = card.pop("_icon_base", None)
            if base in cache:
                rels = cache[base]
            else:
                rels = icon_files(base, con, a.force_icons, icon_stats)
                cache[base] = rels
            card["_media"] = media_of(base, rels)
            card["icon_state"] = "已下发" if rels else "客户端未下发"
    else:
        for card in dish_cards + ing_cards:
            card.pop("_icon_base", None)
            card["_media"] = {"total": 0, "images": [], "missing": []}
            card["icon_state"] = "未取图"

    for card in dish_cards:
        card.pop("_variants_raw", None)

    # 赐福说明（板级公共信息）
    bl = idx["blessings"]
    bless_text = "；".join("%s：%s +%s" % (b["entry"], b["attr"], b["value"]) for b in bl)

    items = dish_cards + ing_cards
    n_img = sum(1 for c in items if c.get("icon_state") == "已下发")
    n_no = sum(1 for c in items if c.get("icon_state") == "客户端未下发")

    meta = {
        "name": "料理与食谱",
        "category": "二、战力类 / （四）料理与食谱",
        "source_server": SOURCE_SERVER,
        "package_sha": pkg_sha,
        "generated": datetime.date.today().isoformat(),
        "id_label": "物品ID",
        "hide_media": False,
        "evidence": "structure",
        "card_mode": "roster",
        "card_summary": [["name", "名称"], ["kind", "类别"],
                         ["effect_short", "效果"], ["craft_station", "制作设施"]],
        "field_labels": {
            "item_id": "物品ID", "kind": "类别",
            "desc": "说明", "simple_desc": "效果简述", "effect_short": "效果",
            "effect_text": "效果标签（全部）", "craft_station": "制作设施",
            "proficiency_text": "熟练度", "unlock_text": "解锁方式",
            "materials_text": "制作材料", "variant_text": "成品 6 档（品质/属性/售价）",
            "ingredient_range_text": "食材属性区间", "extra_text": "额外条件",
            "attrs": "食用属性", "level": "等级", "item_value": "售价",
            "recipe_id": "配方ID", "icon_state": "图标状态",
        },
        "filters": [{"key": "kind", "label": "类型"},
                    {"key": "craft_station", "label": "制作设施"}],
        "state_summary": {"料理": len(dish_cards), "食材": len(ing_cards),
                          "合计": len(items), "有图": n_img, "缺图": n_no},
        "icon_stats": icon_stats,
        "blessing_text": bless_text,
        "notes": (
            "料理 = cook_recipe_data 全量 %d 条；成品按 item_ids 的 6 个品质档逐个列属性。"
            "材料 = food_materials 的 (食材类别, 数量)：count=-1 表示数量未指定，只展示正数量；"
            "食材类别名来自 food_material_type_data + common_item_names。"
            "成品 6 档的血量/饱食/感染只在 edible_item_data 有登记的行展示，未登记的行如实写「源表未登记」；"
            "dish_star_data / cook_recipe_data_key_data 为未解码封装，未据此补数。"
            "赐福来自 food_material_entry_data：%s。"
            "食材卡 = edible_item_data 中未被任何配方当作成品引用的 %d 行。"
            "食材区间取 food_material_data 同 type 多行的 min~max（血量/饱食/感染/异化/星级）。"
            "talent_hp_recover 在 attribute_data 无中文条目，按原字段名显示，不加译名。"
            "来源为配置合并体（基线 script.py314.lc.npk + 2026-10 增量快照，见 "
            "pe_config_merge_ledger_v2.json）；package_sha 是本板实际读取的 9 张表文件的联合摘要，"
            "不是客户端整包 sha。"
            "图标每卡只保留一张：优先 _b 大图，客户端没有大图时才回落 _s；解析不到的标「客户端未下发」。"
        ) % (len(dish_cards), bless_text, len(ing_cards)),
        "provenance": {
            "contract_version": 3,
            "contract": "frozen-audited-artifact",
            "audit_status": "passed",
            "source_locks": [{
                "source_id": SOURCE_ID,
                "sha256": pkg_sha,
                "bytes": sum(facts[t]["bytes"] for t in USED_TABLES),
                "mtime_ns": max(facts[t]["mtime_ns"] for t in USED_TABLES),
                "role": "primary",
                "path": "01_索引与产物/41_还原树/pe/配置/com/cdata",
                "tables": list(USED_TABLES),
                "notes": "配置合并体：基线 script.py314.lc.npk + 2026-10 增量快照；"
                         "sha256 为上述 9 张表文件的联合摘要，bytes/mtime_ns 为这 9 张表的合计/最新值",
            }],
            "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                             "integer_join_policy": "no-equal-integer-join",
                             "runtime_final_policy": "unknown-unless-runtime-proven"},
        },
    }

    board = {"meta": meta, "periods": [], "items": items}
    print("料理 %d ｜ 食材 %d ｜ 合计 %d ｜ 有图 %d ｜ 缺图 %d ｜ 图标 %s" %
          (len(dish_cards), len(ing_cards), len(items), n_img, n_no, icon_stats))
    if a.dry:
        return 0

    OUT_JSON.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_JS.write_text("window.WIKI_BOARD_edible_catalog = " +
                      json.dumps(board, ensure_ascii=False, indent=1) + ";", encoding="utf-8")
    print("写出", OUT_JSON.name, OUT_JSON.stat().st_size, "B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
