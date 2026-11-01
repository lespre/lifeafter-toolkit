# -*- coding: utf-8 -*-
"""重建「装备属性（武器·护甲）」板 —— 总览卡 + 三张分服卡（2026-11-01 用户定版）。

本版改动（用户原话要点）：
  1. 按服别拆独立卡：简单生存服 / 经典服 / 月卡服 各一张，另出一张三服总览卡（带服别筛选）。
     ★ 月卡服数据通道 yk（源表 oversea_data_yk）。
  2. 字段完善：desc（官方描述）、level（品级）、durability、max_shield、
     shield_type（1/2/3 → 基础/蔚蓝/磺骨护盾）、weapon_kind（细类码 + 按装备名归纳的中文标签）、
     model_path、base_score、charm_value。
  3. 2D 图：大图 _b → assets/equip_icons/（按路径扁平化命名，三服同路径共用）。
     客户端无素材的条目不补图，标 icon_missing + status_tags file-missing。
  4. 筛选：总览卡 服别/类型/主属性/武器细类；分服卡 类型/主属性/武器细类。

数据源（★ 只用 PE 还原树家族源包，2026-10-29 node 索引法冻结产物，2026-11-01 就地扩字段）：
  01_索引与产物/30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_{kj1,classic,yk}.json
  提取脚本 03_执行/all_equips_full_extract.py

图标清单：02_wiki/web/assets/equip_icons/_index.json（由 tools/build_equip_icons.py 生成）

护臂/进化武器定性（如实记录）：琥珀护臂家族名字在热更池中，但三张表物理活跃行均无其行数据；
行数值在热更 inc 分片（all_equips_data_base/_inc/_del）内，该分片在库内所有留盘 npk 均不存在，
数据源硬缺口，待增量载荷入库后重跑 03_执行/all_equips_full_extract.py 补全。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

WEB = pathlib.Path(__file__).resolve().parents[1]
PROJ = WEB.parents[1]
FREEZE = PROJ / "01_索引与产物/30_分析/all_equips_全量_node索引_20261029"
ICON_INDEX = WEB / "assets/equip_icons/_index.json"
BOARDS = WEB / "data/boards"
BASE_NAME = "（内测版）装备属性（武器 · 护甲）"
CATEGORY = "二、战力类 / （五）装备属性（武器·护甲）"

SERVERS = {
    "简单生存服": {
        "channel": "kj1",
        "board": "equipment_attrs_kj1",
        "src": FREEZE / "all_equips_attrs_kj1.json",
        "table_desc": ("all_equips_data oversea kj1（简单生存服行表，玩家称「共创服」；"
                       "PE pe_20261020 快照 com/cdata/oversea/"
                       "all_equips_data_auto_oversea_data_kj1.py 行表 + …_kj1_chs.py 专用池，"
                       "fid 3D123F2BEE73ED47 / 9B6BE39D902BD6D6；node 索引法 100% 解码："
                       "声明 5,248 槽 = 1,553 活跃行全解 + 1,238 墓碑 + 2,457 空槽）"),
        "chain_table": "30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_kj1.json",
        "full_note": (
            "源表声明 5,248 槽，物理活跃行 1,553 行 100% 解出（attrs 966/966 全命中），"
            "无未解键遗留；护臂、进化武器名字在热更池中但行数值在未留盘的热更 inc 分片"
            "（all_equips_data_base/_inc/_del）内，属数据源硬缺口。"),
    },
    "经典服": {
        "channel": "classic",
        "board": "equipment_attrs_classic",
        "src": FREEZE / "all_equips_attrs_classic.json",
        "table_desc": ("all_equips_data（经典服行表；PE 测试服安卓客户端安装基线包 "
                       "源包/apk_20261002/mumu_5.0.679/assets/script.py314.lc.npk，"
                       "fid 1F8E9684E1B97CE0 行表 + 94AB0B3FD057EF01 池；node 索引法 100% "
                       "解码：声明 10,949 槽 = 3,287 活跃行全解 + 7,662 空槽）"),
        "chain_table": "30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_classic.json",
        "full_note": (
            "源表声明 10,949 槽，物理活跃行 3,287 行 100% 解出（attrs 2,102/2,102 全命中），"
            "无未解键遗留；护臂、进化武器为 2026-10-02 基线之后的热更内容，inc/del 增量未留盘。"),
    },
    "月卡服": {
        "channel": "yk",
        "board": "equipment_attrs_yk",
        "src": FREEZE / "all_equips_attrs_yk.json",
        "table_desc": ("all_equips_data oversea yk（月卡服行表；PE pe_20261020 快照 "
                       "com/cdata/oversea/all_equips_data_auto_oversea_data_yk.py 行表 + "
                       "…_yk_chs.py 专用池，fid 5790A7683EB6AAA8 / D1D2E03CF2901EBC；"
                       "node 索引法 100% 解码：声明 9,483 槽 = 2,228 活跃行全解）"),
        "chain_table": "30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_yk.json",
        "full_note": (
            "源表声明 9,483 槽，物理活跃行 2,228 行 100% 解出（attrs 1,453/1,453 全命中），"
            "无未解键遗留；护臂、进化武器同样因热更 inc 分片未留盘而缺席。"),
    },
}
OVERVIEW = {"board": "equipment_attrs", "server_branch": "三服总览"}

NPC_PAT = re.compile(r"怪物|利维坦")
TRIAL_PAT = re.compile(r"体验版(?:（\d+天）)?$")
PENDANT_PAT = re.compile(r"挂件|挂饰|掛件")

CN = {"hurt": "伤害", "power": "功率", "armor": "护甲", "max_hp_addition": "生命上限加成",
      "hurt_reduction_rate": "减伤率", "hp_recover": "回血", "affect_temp": "保温",
      "silver_coin_addition_rate": "银币加成", "move_speed": "移速"}

EQUIP_LABEL = {0: "护甲·护盾", 1: "武器", 2: "工具"}
SLOT_LABEL = {3001: "护甲", 3100: "基础护盾", 3200: "蔚蓝护盾", 3300: "磺骨护盾"}
SHIELD_LABEL = {1: "基础护盾", 2: "蔚蓝护盾", 3: "磺骨护盾"}
# weapon_kind 是数值码，客户端没有「码→中文」名称表；以下标签按装备名归纳（页面注明「归纳」）。
KIND_LABEL = {1: "步枪", 2: "冲锋枪", 3: "弓", 4: "霰弹枪", 5: "狙击枪", 6: "手枪",
              7: "火箭筒/榴弹", 8: "电磁", 20: "喷火器", 21: "重机枪", 50: "冷兵器",
              999: "特殊/怪物专用"}
DRONE_BODY = (182000, 183000)
DRONE_SEG_LO = 180000


def DRONE_SEG(key) -> bool:
    return 180000 <= int(key) < DRONE_BODY[1]


def classify(r: dict):
    """返回 label 或 None。None = 不进板。判据全部可复算（键段/槽位/名字）。"""
    key = int(r["key"])
    name = r.get("name") or ""
    et = r.get("equip_type")
    wt = r.get("weapon_type")
    if name.endswith("体验版") or TRIAL_PAT.search(name):
        return None
    if "测试" in name or NPC_PAT.search(name):
        return None
    if 270000 <= key < 280000 or PENDANT_PAT.search(name):
        return None
    if et in (0, 1, 2):
        label = EQUIP_LABEL.get(et, "其他")
        if et == 0 and wt in SLOT_LABEL:
            label = "护甲·护盾/" + SLOT_LABEL[wt]
        return label
    if et in ("", None):
        if wt == 4001:
            return "投掷物"
        if wt == 6001:
            return "陷阱·地雷"
        return None


def attr_names() -> dict:
    """attribute_data.e_name → 中文（游戏自己的属性字典）。"""
    import sys
    cands = [
        PROJ / "01_索引与产物/41_还原树/pe/配置/Documents/script.py314.lc.npk/com/cdata/attribute_data.py",
        PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata/attribute_data.py",
    ]
    ATTR_TABLE = next((p for p in cands if p.exists()), None)
    if ATTR_TABLE is None:
        return {}
    sys_path = str(PROJ / "00_规范与工具/工具/工具库/00_共享核心")
    if sys_path not in sys.path:
        sys.path.insert(0, sys_path)
    from toolkit_core import bindict_table as BT
    raw = ATTR_TABLE.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return {}
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = ATTR_TABLE.with_name("attribute_data_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    rows = BT.decode_table_rows(raw[at + 6:at + 6 + L], pool,
                                resolve_jumps=False, lenient=True)[0]
    out = {}
    for r in rows:
        v = r["values"]
        g = lambda k: (v.get(k)[1] if isinstance(v.get(k), tuple) else v.get(k))
        e, cn = g("e_name"), g("name")
        if isinstance(e, str) and isinstance(cn, str):
            out[e] = cn
    return out


def attrs_text(attrs, NAME) -> str:
    return " ｜ ".join("%s %s" % (NAME.get(k, k), v) for k, v in attrs)


def load_icons() -> dict:
    if not ICON_INDEX.is_file():
        return {}
    return (json.loads(ICON_INDEX.read_text(encoding="utf-8")) or {}).get("icons") or {}


def icon_fields(r: dict, ICONS: dict) -> dict:
    """图标：命中 → icon/png + _media；缺 → icon=null + icon_missing。"""
    raw = r.get("icon")
    raw = raw.strip() if isinstance(raw, str) else ""
    if not raw:
        return {"icon": None, "icon_state": "无图标字段", "icon_missing": True,
                "status_tags": ["static config", "file-missing"]}
    info = ICONS.get(raw) or {}
    if info.get("png"):
        return {"icon": info["png"], "icon_state": "有图", "icon_missing": False,
                "_media": {
                    "images": [{"png": info["png"],
                                "base": raw.rsplit("/", 1)[-1],
                                "suffix": info.get("suffix") or "b",
                                "label": "图标（大图 _b）" if info.get("suffix") == "b" else "图标（小图 _s）",
                                "source": "PE · %s:%s · %s" % (info.get("pack"), info.get("row"),
                                                               info.get("source_path") or raw)}],
                    "total": 1,
                    "note": "客户端 ui/item_icon 大图直出；三服同路径共用同一张"},
                "status_tags": ["static config"]}
    return {"icon": None, "icon_state": "缺图（客户端无素材）", "icon_missing": True,
            "icon_missing_reason": "客户端 ui/item_icon 索引内无该路径（_b/_s 均未命中）",
            "status_tags": ["static config", "file-missing"]}


def provenance(row_keys: list, sha: str, sv: str, fields: list) -> dict:
    cfg = SERVERS[sv]
    return {
        "source_id": "equipment-attrs-%s" % cfg["channel"],
        "source_lock_sha256": sha,
        "table": cfg["table_desc"],
        "row_key": row_keys[0],
        "row_keys": row_keys,
        "field_refs": fields,
        "name_source": "all_equips_data#name（chs 池）",
        "upstream": {"package_sha256": sha, "entry_index": None, "file_id": None,
                     "decoded_sha256": None, "role": "frozen-extract"},
        "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                          "no_cross_source_field_join": True,
                          "steps": [{"kind": "decoded-table-row",
                                     "source_id": "equipment-attrs-%s" % cfg["channel"],
                                     "table": cfg["chain_table"],
                                     "row_key": row_keys[0],
                                     "field_refs": fields}]},
    }


def item_base(key, name, et, wt, attrs, NAME, label, sha, sv, row, ICONS, source_extra=None):
    ic = icon_fields(row, ICONS)
    wk = row.get("weapon_kind")
    stype = row.get("shield_type")
    fields = ["attrs", "name", "equip_type", "weapon_type"]
    for k in ("icon", "desc", "level", "durability", "max_shield", "shield_type",
              "weapon_kind", "model_path", "base_score", "charm_value"):
        if row.get(k) not in (None, "", []):
            fields.append(k)
    return {
        "id": "eq_%s_%s" % (SERVERS[sv]["channel"], key),
        "name": name,
        "row_key": key,
        "server_branch": sv,
        "equip_label": label,
        "equip_type": et,
        "weapon_type": wt,
        "attr_first": NAME.get(attrs[0][0], attrs[0][0]) if attrs else "",
        "属性": attrs_text(attrs, NAME),
        "desc": row.get("desc") or None,
        "level": row.get("level"),
        "durability": row.get("durability"),
        "max_shield": row.get("max_shield"),
        "shield_type": stype,
        "shield_label": SHIELD_LABEL.get(stype) if isinstance(stype, int) else None,
        "weapon_kind": wk,
        "weapon_kind_label": (KIND_LABEL.get(wk, "未归类码 %s" % wk) if wk is not None else None),
        "model_path": row.get("model_path") or None,
        "base_score": row.get("base_score"),
        "charm_value": row.get("charm_value"),
        "trial_variants": None,
        "icon": ic["icon"],
        "icon_state": ic["icon_state"],
        "icon_missing": ic["icon_missing"],
        **({"icon_missing_reason": ic["icon_missing_reason"]} if ic.get("icon_missing_reason") else {}),
        **({"_media": ic["_media"]} if ic.get("_media") else {}),
        "evidence": "structure",
        "evidence_level": "structure-only",
        "status_tags": ic["status_tags"],
        "source": SERVERS[sv]["table_desc"] + "；attrs 走 0xC6/0x86 嵌套行帧解出"
                   + "；字段 icon/desc/level/durability/max_shield/shield_type/weapon_kind/"
                     "model_path/base_score/charm_value 为同行直读（2026-11-01 扩字段）"
                   + (source_extra or ""),
        "provenance": provenance([key], sha, sv, fields),
    }


def build_items(rows, NAME, sha, sv, ICONS):
    """两遍法：先定主行集合（classify），再挂体验版。返回 (条目, 统计)。"""
    eligible = {}
    stats = {"npc_dropped": 0, "acc_dropped": 0, "no_attrs": 0, "pendant": 0}
    for r in rows:
        name = r.get("name") or ""
        et = r.get("equip_type")
        attrs = r.get("attrs") or []
        if TRIAL_PAT.search(name):
            continue
        if "测试" in name:
            stats["acc_dropped"] += 1
            continue
        if NPC_PAT.search(name):
            if attrs or et in (0, 1, 2):
                stats["npc_dropped"] += 1
            continue
        if 270000 <= int(r["key"]) < 280000 or PENDANT_PAT.search(name):
            if attrs:
                stats["pendant"] += 1
            continue
        if not attrs:
            stats["no_attrs"] += 1
            continue
        label = classify(r)
        if label is None:
            if et not in (0, 1, 2):
                stats["acc_dropped"] += 1
            continue
        eligible[r["key"]] = r

    eligible_names = [(r.get("name") or "", r) for r in eligible.values()]
    grouped, orphans = {}, []
    for t in rows:
        name = t.get("name") or ""
        m = TRIAL_PAT.search(name)
        if not m:
            continue
        stem = name[:m.start()]
        hits = [r for nm, r in eligible_names if nm.startswith(stem)]
        if hits:
            exact = [r for nm, r in eligible_names if nm == stem]
            tw = t.get("weapon_type")
            cand = exact or [r for r in hits if r.get("weapon_type") == tw] or hits
            best = min(cand, key=lambda r: int(r["key"]))
            grouped.setdefault(best["key"], []).append(t)
        else:
            orphans.append(t)
    merged_orphans = {}
    for t in orphans:
        merged_orphans.setdefault(t.get("name"), []).append(t)
    orphans = []
    orphan_extra_keys = {}
    for nm, v in merged_orphans.items():
        s = sorted(v, key=lambda r: (not r.get("attrs"), int(r["key"])))
        if DRONE_SEG(s[0]["key"]):
            stats["acc_dropped"] += len(s)
            continue
        orphans.append(s[0])
        if len(s) > 1:
            orphan_extra_keys[s[0]["key"]] = [r["key"] for r in s[1:]]

    out = []
    for r in eligible.values():
        key = r["key"]
        name = r.get("name") or ("装备 %s" % key)
        attrs = r.get("attrs") or []
        et, wt = r.get("equip_type"), r.get("weapon_type")
        it = item_base(key, name, et, wt, attrs, NAME, classify(r), sha, sv, r, ICONS)
        tv = grouped.get(key) or []
        if tv:
            by_name = {}
            for t in tv:
                e = by_name.setdefault(t.get("name"),
                                       {"name": t.get("name"), "row_key": t.get("key"),
                                        "属性": attrs_text(t.get("attrs") or [], NAME) or None,
                                        "has_attrs": bool(t.get("attrs")), "_keys": [t.get("key")]})
                if t.get("attrs") and not e["has_attrs"]:
                    e.update({"row_key": t.get("key"),
                              "属性": attrs_text(t["attrs"], NAME), "has_attrs": True})
                if t.get("key") not in e["_keys"]:
                    e["_keys"].append(t.get("key"))
            it["trial_variants"] = [{k: v for k, v in e.items() if k != "_keys"}
                                    | {"row_keys": e["_keys"]}
                                    for e in by_name.values()]
            it["provenance"]["row_keys"] += [k for e in by_name.values() for k in e["_keys"]]
            it["provenance"]["locator_chain"]["steps"][0]["row_key"] = it["provenance"]["row_keys"][0]
        out.append(it)
    for t in orphans:
        key = t["key"]
        attrs = t.get("attrs") or []
        et, wt = t.get("equip_type"), t.get("weapon_type")
        it = item_base(key, t.get("name"), et, wt, attrs, NAME,
                       "体验版（正式版行不在活跃行内）", sha, sv, t, ICONS,
                       source_extra="；正式版本体行不在源表物理活跃行内"
                                    "（热更内容，行数值在未留盘 inc 分片中）")
        it["status_tags"] = [x for x in it["status_tags"] if x != "file-missing"] + ["unresolved"]
        if not attrs:
            it["属性"] = "（本行 attrs 未解出/为空）"
        if key in orphan_extra_keys:
            it["provenance"]["row_keys"] = [key] + orphan_extra_keys[key]
        out.append(it)
    out.sort(key=lambda x: (str(x["equip_type"]), str(x["row_key"])))
    return out, stats


def write_board(path_json: pathlib.Path, data: dict):
    path_json.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    var = "window.WIKI_BOARD_%s = " % path_json.stem
    path_json.with_suffix(".js").write_text(var + json.dumps(data, ensure_ascii=False),
                                            encoding="utf-8")


def meta_common(name, items, source_locks, notes, server_branch, sibling_cards, filters):
    return {
        "name": name,
        "category": CATEGORY,
        "generated": "2026-11-01",
        "evidence": "structure",
        "package_sha": hashlib.sha256(
            b"".join(l["sha256"].encode() for l in source_locks)).hexdigest(),
        "source_server": "PE 测试服源包 · all_equips_data · " + " + ".join(
            "%s（%s）" % (sv, cfg["channel"]) for sv, cfg in SERVERS.items()),
        "server_branch": server_branch,
        "sibling_cards": sibling_cards,
        "filters": filters,
        "notes": notes,
        "state_summary": {"unresolved": len(items), "static config": len(items),
                          "verified": 0, "runtime final unknown": len(items),
                          "有属性": sum(1 for i in items if i.get("属性")),
                          "有图标": sum(1 for i in items if i.get("icon"))},
        "provenance": {
            "contract_version": 3, "audit_status": "passed",
            "contract": "frozen-audited-artifact",
            "source_locks": source_locks,
            "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                             "integer_join_policy": "no-equal-integer-join",
                             "runtime_final_policy": "unknown-unless-runtime-proven"},
        },
    }


def main() -> int:
    NAME = dict(CN)
    got = attr_names()
    if got:
        NAME.update(got)
    ICONS = load_icons()
    ics = {"total": len(ICONS),
           "hit": sum(1 for v in ICONS.values() if v.get("png")),
           "miss": sum(1 for v in ICONS.values() if not v.get("png"))}

    per = {}
    all_items = []
    for sv, cfg in SERVERS.items():
        payload = json.loads(cfg["src"].read_text(encoding="utf-8"))
        rows = payload["rows"]
        sha = hashlib.sha256(cfg["src"].read_bytes()).hexdigest()
        items, stats = build_items(rows, NAME, str(sha), sv, ICONS)
        n_trial_merged = sum(len(i["trial_variants"] or []) for i in items)
        n_trial_alone = sum(1 for i in items if "unresolved" in i["status_tags"])
        n_icon = sum(1 for i in items if i.get("icon"))
        n_missing = sum(1 for i in items if i.get("icon_missing"))
        per[sv] = {"cfg": cfg, "sha": sha, "rows": rows, "items": items, "stats": stats,
                   "n": len(items), "n_trial_merged": n_trial_merged,
                   "n_trial_alone": n_trial_alone, "n_icon": n_icon, "n_missing": n_missing,
                   "src_path": cfg["src"]}
        all_items.extend(items)
        print("%s（%s）条数 %d ｜ 体验版并入 %d ｜ 单列 %d ｜ 有图 %d ｜ 缺图 %d ｜ "
              "剔配件 %d ｜ 剔NPC %d ｜ 无attrs行 %d"
              % (sv, cfg["channel"], len(items), n_trial_merged, n_trial_alone,
                 n_icon, n_missing, stats["acc_dropped"], stats["npc_dropped"],
                 stats["no_attrs"]))

    # ── 分服卡 ──
    for sv, v in per.items():
        cfg = v["cfg"]
        siblings = [OVERVIEW["board"] + "（三服总览）"] + [
            c["board"] + "（%s）" % s for s, c in SERVERS.items() if s != sv]
        locks = [{"source_id": "equipment-attrs-%s" % cfg["channel"],
                  "role": "primary",
                  "path": str(v["src_path"]).replace("\\", "/").split("la拆包项目/")[-1],
                  "sha256": v["sha"], "bytes": v["src_path"].stat().st_size,
                  "mtime_ns": v["src_path"].stat().st_mtime_ns}]
        notes = (
            "分服卡（%s · 数据通道 %s）。"
            "① 收录：武器/护甲·护盾/工具（equip_type 0/1/2）+ 投掷物（wt 4001）+ 陷阱·地雷（wt 6001），"
            "均需 attrs 非空；剔 无人机、挂饰（270xxx，%d 行）、配件杂物（%d 行）、NPC 装备（%d 行）、测试件。"
            "② 体验版：%d 条并入正式版条目「体验版子项」；%d 条正式版行不在活跃行内，单列。"
            "③ 字段：desc/level/durability/max_shield/shield_type/weapon_kind/model_path/"
            "base_score/charm_value 为同行直读；weapon_kind 是数值码，客户端无码→中文名称表，"
            "板面中文标签按装备名归纳（非官方枚举）。"
            "④ 图标：大图 _b 直出到 assets/equip_icons/，本卡有图 %d 条、缺图 %d 条"
            "（客户端无素材，留空并标 icon_missing / file-missing）。"
            "⑤ 全量边界：%s"
            "⑥ 数据链路：03_执行/all_equips_full_extract.py → 30_分析 冻结 JSON → 本构建脚本。"
            % (sv, cfg["channel"], v["stats"]["pendant"], v["stats"]["acc_dropped"],
               v["stats"]["npc_dropped"], v["n_trial_merged"], v["n_trial_alone"],
               v["n_icon"], v["n_missing"], cfg["full_note"]))
        d = {
            "meta": meta_common(BASE_NAME + " · " + sv, v["items"], locks, notes,
                                sv, siblings,
                                [{"key": "equip_label", "label": "类型"},
                                 {"key": "attr_first", "label": "主属性"},
                                 {"key": "weapon_kind_label", "label": "武器细类"}]),
            "items": v["items"],
        }
        out = BOARDS / (cfg["board"] + ".json")
        write_board(out, d)
        print("写出", out.name, len(v["items"]), "条")

    # ── 总览卡 ──
    locks = [{"source_id": "equipment-attrs-%s" % v["cfg"]["channel"],
              "role": "primary",
              "path": str(v["src_path"]).replace("\\", "/").split("la拆包项目/")[-1],
              "sha256": v["sha"], "bytes": v["src_path"].stat().st_size,
              "mtime_ns": v["src_path"].stat().st_mtime_ns} for v in per.values()]
    notes = (
        "三服总览卡：%s，共 %d 条；页内「服别」下拉筛选区分三服，"
        "逐条带 server_branch，不混排（简单生存服=kj1、经典服=base、月卡服=yk）。"
        "① 筛选同三张分服卡（服别/类型/主属性/武器细类），收录与剔除规则见各分服卡说明。"
        "② 体验版：三服合计并入 %d 条、单列 %d 条。"
        "③ 图标：大图 _b 直出到 assets/equip_icons/（按路径扁平化命名，三服同路径共用同一张，"
        "唯一路径 %d 条：命中 %d、客户端无素材 %d）；本卡有图 %d 条、缺图 %d 条"
        "（缺图标 icon_missing + file-missing，不补占位）。"
        "④ 字段：desc/level/durability/max_shield/shield_type/weapon_kind/model_path/"
        "base_score/charm_value；weapon_kind 中文标签按装备名归纳（1 步枪/2 冲锋枪/3 弓/4 霰弹枪/"
        "5 狙击枪/6 手枪/7 火箭筒·榴弹/8 电磁/20 喷火器/21 重机枪/50 冷兵器/999 特殊），非官方枚举。"
        "⑤ 全量边界：三服各自 100%% 解出活跃行；护臂/进化武器因热更 inc 分片未留盘缺席，属数据源硬缺口。"
        "⑥ 数据链路：03_执行/all_equips_full_extract.py（2026-11-01 扩字段就地覆盖）→ "
        "30_分析 冻结 JSON → tools/build_equip_icons.py → 本构建脚本。"
        % ("/".join("%s %d" % (sv, v["n"]) for sv, v in per.items()), len(all_items),
           sum(v["n_trial_merged"] for v in per.values()),
           sum(v["n_trial_alone"] for v in per.values()),
           ics["total"], ics["hit"], ics["miss"],
           sum(1 for i in all_items if i.get("icon")),
           sum(1 for i in all_items if i.get("icon_missing"))))
    d = {"meta": meta_common(BASE_NAME + " · 三服总览", all_items, locks, notes,
                             OVERVIEW["server_branch"],
                             [c["board"] + "（%s）" % sv for sv, c in SERVERS.items()],
                             [{"key": "server_branch", "label": "服别"},
                              {"key": "equip_label", "label": "类型"},
                              {"key": "attr_first", "label": "主属性"},
                              {"key": "weapon_kind_label", "label": "武器细类"}]),
         "items": all_items}
    write_board(BOARDS / "equipment_attrs.json", d)
    print("写出总览卡", len(all_items), "条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
