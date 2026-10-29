# -*- coding: utf-8 -*-
"""重建「装备属性（武器·护甲）」板 —— 分服子卡版（2026-10-29 用户定版）。

用户要求（原话要点）：
  1. 筛选不严不全量：不该进去的夹层、涂层进去了；该进去的进化武器、护臂没进去。
  2. 体验版合并到正式版下当子项目。
  3. 全量补充完后补图（本次不补图，icon 字段留空待数据全量后统一补）。
  4. 分服子卡：简单生存服与经典服分开，不混排（2026-10-29 定版口径；
     ★ 官方口径叫「简单生存服」（数据通道 kj1），「共创服」是玩家称呼，
     只作备注不入卡名——2026-10-29 夜曾误改为共创服，已回退）。

数据源（★ 只用 PE 还原树家族源包，2026-10-29 用户定版）：
  01_索引与产物/30_分析/all_equips_全量_node索引_20261029/（三表 100% 解码冻结产物）
  - 简单生存服（玩家称"共创服"，通道 kj1）：pe_20261020 快照 oversea_data_kj1
    行表+专用池 → 1,553 行全解
  - 经典服 base：apk_20261002 基线 all_equips_data 行表+chs 池 → 3,287 行全解
  提取脚本 03_执行/all_equips_full_extract.py（node 索引法，2026-10-29 结案）。

★ 2026-10-29 结案补全（遗留①关闭）：0x7B 行表索引尾 = 76 01 0b + uleb(bc) +
  bc×8B 桶数组 + node 溢出区连续 (key, row_start) 键对；「0x7B 头 cnt」是扩容声明
  容量（含墓碑/空槽）≠ 物理行数。旧法 1,226/2,721 的缺口全是索引回收不完整 +
  行尾 inline list variant 被严格模式丢弃；node 索引 + lenient 后三表 100% 解出。

护臂/进化武器定性（如实记录）：琥珀护臂家族名字在热更池（还原树 chs 池 11,632
  串）中，但三张表物理活跃行均无其行数据 —— 行数值在热更 inc 分片
  （all_equips_data_base/_inc/_del）内，该分片在库内所有留盘 npk 均不存在，
  数据源硬缺口，待增量载荷入库后重跑 03_执行/all_equips_full_extract.py 补全。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re

WEB = pathlib.Path(__file__).resolve().parents[1]
PROJ = WEB.parents[1]
# 分服数据源（均为 PE 测试服家族源包的行级冻结产物，node 索引法 100% 解码版）
SRC_KJ1 = PROJ / "01_索引与产物/30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_kj1.json"
SRC_CLASSIC = PROJ / "01_索引与产物/30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_classic.json"
OUT_KJ1 = WEB / "data/boards/equipment_attrs.json"
OUT_CLASSIC = WEB / "data/boards/equipment_attrs_classic.json"

SERVERS = {
    "简单生存服": {
        # 官方口径「简单生存服」；「共创服」为玩家称呼，只作备注（2026-10-29 定版）
        "channel": "kj1",
        "src": SRC_KJ1,
        "out": OUT_KJ1,
        "sibling": "equipment_attrs_classic（经典服 · 数据卡）",
        "table_desc": ("all_equips_data oversea kj1（简单生存服行表，玩家称「共创服」；"
                       "PE pe_20261020 快照 com/cdata/oversea/"
                       "all_equips_data_auto_oversea_data_kj1.py 行表 + …_kj1_chs.py 专用池，"
                       "fid 3D123F2BEE73ED47 / 9B6BE39D902BD6D6；node 索引法 100% 解码："
                       "声明 5,248 槽 = 1,553 活跃行全解 + 1,238 墓碑 + 2,457 空槽）"),
        "chain_table": "30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_kj1.json",
        "extract_script": "03_执行/all_equips_full_extract.py",
        "full_note": (
            "③ 全量边界（2026-10-29 node 索引法结案）：源表声明 5,248 槽，物理活跃行 "
            "1,553 行 100% 解出（含 1,238 墓碑、2,457 空槽），attrs 966/966 全命中，"
            "无未解键遗留；护臂、进化武器名字在热更池中但行数值在未留盘的热更 inc 分片"
            "（all_equips_data_base/_inc/_del）内，属数据源硬缺口，待增量载荷入库后按 "
            "03_执行/all_equips_full_extract.py 重跑补全。"),
    },
    "经典服": {
        # 经典服数据通道 base；行表取自 PE 测试服安卓安装基线包
        "channel": "base",
        "src": SRC_CLASSIC,
        "out": OUT_CLASSIC,
        "sibling": "equipment_attrs（简单生存服 · 数据卡）",
        "table_desc": ("all_equips_data（经典服行表；PE 测试服安卓客户端安装基线包 "
                       "源包/apk_20261002/mumu_5.0.679/assets/script.py314.lc.npk，"
                       "fid 1F8E9684E1B97CE0 行表 + 94AB0B3FD057EF01 池；node 索引法 100% "
                       "解码：声明 10,949 槽 = 3,287 活跃行全解 + 7,662 空槽。还原树内同名"
                       "文件已被增量热更 808B MergedTableData 存根覆盖，base/_inc/_del 分片"
                       "在所有留盘 npk 均不存在 → 安装基线即库内最新全量行数据）"),
        "chain_table": "30_分析/all_equips_全量_node索引_20261029/all_equips_attrs_classic.json",
        "extract_script": "03_执行/all_equips_full_extract.py",
        "full_note": (
            "③ 全量边界（2026-10-29 node 索引法结案）：源表声明 10,949 槽，物理活跃行 "
            "3,287 行 100% 解出（含 7,662 空槽），attrs 2,102/2,102 全部命中，无未解键"
            "遗留；护臂、进化武器为 2026-10-02 基线之后的热更内容，inc/del 增量未留盘，"
            "待增量载荷入库后按 03_执行/all_equips_full_extract.py 重跑补全。"),
    },
}
NPC_PAT = re.compile(r"怪物|利维坦")
TRIAL_PAT = re.compile(r"体验版(?:（\d+天）)?$")
PENDANT_PAT = re.compile(r"挂件|挂饰|掛件")
THROW_BAD_PAT = re.compile(r"测试|文字提示|Boss|UGC")

CN = {"hurt": "伤害", "power": "功率", "armor": "护甲", "max_hp_addition": "生命上限加成",
      "hurt_reduction_rate": "减伤率", "hp_recover": "回血", "affect_temp": "保温",
      "silver_coin_addition_rate": "银币加成", "move_speed": "移速"}

EQUIP_LABEL = {0: "护甲·护盾", 1: "武器", 2: "工具"}
SLOT_LABEL = {3001: "护甲", 3100: "基础护盾", 3200: "蔚蓝护盾", 3300: "磺骨护盾"}
# equip_type 为空但确属玩家装备的键段/槽位（2026-10-29 用户判定：无人机不进、挂饰不进）
DRONE_BODY = (182000, 183000)   # 无人机整机（暗夜精灵/追风海鸥/体验版…）
DRONE_MOD = (181000, 182000)    # 无人机模块（能量核心/发动机/结构框架/导航仪）


def DRONE_SEG(key) -> bool:
    return 180000 <= int(key) < DRONE_BODY[1]


def classify(r: dict):
    """返回 (label 或 None)。None = 不进板。判据全部可复算（键段/槽位/名字）。"""
    key = int(r["key"])
    name = r.get("name") or ""
    et = r.get("equip_type")
    wt = r.get("weapon_type")
    if name.endswith("体验版") or TRIAL_PAT.search(name):
        return None  # 体验版行走合并通道
    if "测试" in name or NPC_PAT.search(name):
        return None
    # 挂饰：270xxx 整段（蓝白猫咪等名字不带"挂件"字样）+ 名字带挂件/挂饰
    if 270000 <= key < 280000 or PENDANT_PAT.search(name):
        return None
    if et in (0, 1, 2):
        label = EQUIP_LABEL.get(et, "其他")
        if et == 0 and wt in SLOT_LABEL:
            label = "护甲·护盾/" + SLOT_LABEL[wt]
        return label
    if et in ("", None):
        # equip_type 为空的玩家装备段（有 attrs 才会被调用）
        # 无人机整机 182xxx / 模块 181xxx：2026-10-29 用户判定不进（此前误输"该进"，已更正）
        if wt == 4001:
            return "投掷物"
        if wt == 6001:
            return "陷阱·地雷"
        # wt 14001 背包：2026-10-29 用户判定不进（红粉救生包等）
        return None


def attr_names() -> dict:
    """attribute_data.e_name → 中文（游戏自己的属性字典）。"""
    import struct
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


def provenance(row_keys: list, sha: str, sv: str) -> dict:
    cfg = SERVERS[sv]
    return {
        "source_id": "equipment-attrs",
        "source_lock_sha256": sha,
        "table": cfg["table_desc"],
        "row_key": row_keys[0],
        "row_keys": row_keys,
        "field_refs": ["attrs", "name", "equip_type", "weapon_type"],
        "name_source": "all_equips_data#name（chs 池）",
        "upstream": {"package_sha256": sha, "entry_index": None, "file_id": None,
                     "decoded_sha256": None, "role": "frozen-extract"},
        "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                          "no_cross_source_field_join": True,
                          "steps": [{"kind": "frozen-json-extract",
                                     "source_id": "equipment-attrs",
                                     "table": cfg["chain_table"],
                                     "row_key": row_keys[0],
                                     "field_refs": ["attrs", "name"]}]},
    }


def item_base(key, name, et, wt, attrs, NAME, label, sha, sv, source_extra=None):
    return {
        "id": "eq_%s" % key,
        "name": name,
        "row_key": key,
        "server_branch": sv,
        "equip_label": label,
        "equip_type": et,
        "weapon_type": wt,
        "attr_first": NAME.get(attrs[0][0], attrs[0][0]) if attrs else "",
        "属性": attrs_text(attrs, NAME),
        "trial_variants": None,
        "icon": None,
        "evidence": "structure",
        "evidence_level": "structure-only",
        "status_tags": ["static config"],
        "source": SERVERS[sv]["table_desc"] + ("；attrs 走 0xC6/0x86 嵌套行帧解出") + (source_extra or ""),
        "provenance": None,
        "_row_keys": [key],
    }


def build_items(rows, NAME, sha, sv):
    """两遍法：先定主行集合（classify），再挂体验版。返回 (条目, 统计)。"""
    # --- pass 1：主行资格 ---
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
                stats["pendant"] += 1  # 挂饰（蓝白猫咪等）：用户判定不该进
            continue
        if not attrs:
            stats["no_attrs"] += 1  # 装备行但 attrs 未解出：结案遗留，暂不进板
            continue
        label = classify(r)
        if label is None:
            if et not in (0, 1, 2):
                stats["acc_dropped"] += 1  # 夹层/涂层/握把等配件杂物
            continue
        eligible[r["key"]] = r

    # --- pass 2：体验版 → 合格正式版 ---
    # 匹配规则：剥「体验版（N天）」尾巴后前缀命中；精确同名 > 同 weapon_type > 全部；
    # 再取 row_key 最小（本体行通常是最低键）。
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
    # 同名孤立体验版（不同行键）合并为一条，row_keys 并列
    merged_orphans = {}
    for t in orphans:
        merged_orphans.setdefault(t.get("name"), []).append(t)
    orphans = []
    orphan_extra_keys = {}
    for nm, v in merged_orphans.items():
        s = sorted(v, key=lambda r: (not r.get("attrs"), int(r["key"])))
        # 无人机体验版（181xxx/182xxx）：2026-10-29 用户判定整体不进，本体未解出也不单列
        if DRONE_SEG(s[0]["key"]):
            stats["acc_dropped"] += len(s)
            continue
        orphans.append(s[0])
        if len(s) > 1:
            orphan_extra_keys[s[0]["key"]] = [r["key"] for r in s[1:]]

    # --- pass 3：产出 ---
    out = []
    for r in eligible.values():
        key = r["key"]
        name = r.get("name") or ("装备 %s" % key)
        attrs = r.get("attrs") or []
        et, wt = r.get("equip_type"), r.get("weapon_type")
        it = item_base(key, name, et, wt, attrs, NAME, classify(r), sha, sv)
        tv = grouped.get(key) or []
        if tv:
            # 同名体验版（不同行键，如新旧两版）合并为一条子项，row_keys 并列
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
            it["_row_keys"] += [k for e in by_name.values() for k in e["_keys"]]
        out.append(it)
    for t in orphans:
        key = t["key"]
        attrs = t.get("attrs") or []
        et, wt = t.get("equip_type"), t.get("weapon_type")
        it = item_base(key, t.get("name"), et, wt, attrs, NAME,
                       "体验版（正式版行不在活跃行内）", sha, sv,
                       source_extra="；正式版本体行不在源表物理活跃行内"
                                    "（热更内容，行数值在未留盘 inc 分片中）")
        it["status_tags"].append("trial-unmatched")
        if not attrs:
            it["属性"] = "（本行 attrs 未解出/为空）"
        if key in orphan_extra_keys:
            it["_row_keys"] = [key] + orphan_extra_keys[key]
        out.append(it)
    for it in out:
        it["provenance"] = provenance(it.pop("_row_keys"), sha, sv)
    out.sort(key=lambda x: (str(x["equip_type"]), str(x["row_key"])))
    return out, stats


def write_board(path_json: pathlib.Path, data: dict):
    path_json.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    js = path_json.with_suffix(".js")
    var = "window.WIKI_BOARD_%s = " % path_json.stem
    js.write_text(var + json.dumps(data, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    NAME = dict(CN)
    got = attr_names()
    if got:
        NAME.update(got)

    # 两服各建条目（逐条带 server_branch 服标），合并输出为一张卡（2026-10-29 用户定版：
    # 「本来就是一个子卡」——目录只出一张卡，页内「服别」下拉筛选区分两服）。
    all_items = []
    per_server = {}
    for sv, cfg in SERVERS.items():
        src_path = cfg["src"]
        payload = json.loads(src_path.read_text(encoding="utf-8"))
        rows = payload.get("rows") if isinstance(payload, dict) else payload
        if rows is None:
            rows = payload if isinstance(payload, list) else []
        sha = hashlib.sha256(src_path.read_bytes()).hexdigest()
        items, stats = build_items(rows, NAME, sha, sv)
        all_items.extend(items)
        from collections import Counter
        per_server[sv] = {
            "cfg": cfg, "sha": sha, "src_path": src_path, "stats": stats,
            "n": len(items),
            "n_trial_merged": sum(len(i["trial_variants"] or []) for i in items),
            "n_trial_alone": sum(1 for i in items if "trial-unmatched" in i["status_tags"]),
            "label_dist": Counter(i["equip_label"].split("/")[0] for i in items).most_common(),
        }
        print(sv, "条数", len(items), "｜ 体验版并入", per_server[sv]["n_trial_merged"],
              "｜ 体验版单列", per_server[sv]["n_trial_alone"],
              "｜ 剔配件", stats["acc_dropped"], "｜ 剔NPC", stats["npc_dropped"],
              "｜ 无attrs装备行", stats["no_attrs"],
              "｜ 类型分布", per_server[sv]["label_dist"])

    n_trial_merged = sum(v["n_trial_merged"] for v in per_server.values())
    n_trial_alone = sum(v["n_trial_alone"] for v in per_server.values())
    st = {sv: v["stats"] for sv, v in per_server.items()}
    branches = "/".join("%s %d" % (sv, v["n"]) for sv, v in per_server.items())
    scope_notes = "".join(
        "③ 全量边界 · %s（数据通道 %s）：%s" % (sv, v["cfg"]["channel"], v["cfg"]["full_note"][2:].lstrip("③").strip())
        for sv, v in per_server.items())
    source_locks = [{"source_id": "equipment-attrs-%s" % v["cfg"]["channel"],
                     "role": "primary-frozen-extract",
                     "path": str(v["src_path"]).replace("\\", "/").split("la拆包项目/")[-1],
                     "sha256": v["sha"], "bytes": v["src_path"].stat().st_size,
                     "mtime_ns": v["src_path"].stat().st_mtime_ns}
                    for v in per_server.values()]
    d = {
        "meta": {
            "name": "装备属性（武器 · 护甲）",
            "category": "二、战力类 / （五）装备属性（武器·护甲）",
            "generated": "2026-10-29",
            "evidence": "structure",
            "package_sha": hashlib.sha256(
                b"".join(v["sha"].encode() for v in per_server.values())).hexdigest(),
            "source_server": "PE 测试服源包 · all_equips_data · 简单生存服（kj1）+ 经典服（base）",
            "server_branch": "简单生存服+经典服（条目级 server_branch，页内服别筛选）",
            "sibling_cards": [],
            "filters": [{"key": "server_branch", "label": "服别"},
                        {"key": "equip_label", "label": "类型"},
                        {"key": "attr_first", "label": "主属性"}],
            "notes": (
                "单卡双服（%s）；目录一张卡，页内「服别」下拉筛选区分两服，分服行数据不混排"
                "（逐条带 server_branch 服标，简单生存服=kj1 通道、经典服=base 通道）。"
                % branches
                +
                "① 筛选（两服同规则，2026-10-29 用户判定落规则）：收 武器/护甲·护盾/工具（equip_type 0/1/2）"
                "+ 投掷物（wt 4001）+ 陷阱·地雷（wt 6001），均需 attrs 非空；"
                "剔 无人机（整机/模块/体验版）、挂饰（270xxx 整段，简单生存服 %d 行 / 经典服 %d 行，含蓝白猫咪）、"
                "配件杂物（夹层/涂层/握把/热成像辅助器/背包救生包等 equip_type 空行，简单生存服 %d 行 / 经典服 %d 行）、"
                "NPC 装备（名字含 怪物/利维坦，简单生存服 %d 行 / 经典服 %d 行）、测试件。"
                "② 体验版合并（两服同规则）：%d 条体验版（含「体验版（N天）」限时形式）并入正式版条目"
                "「体验版子项」（trial_variants，同名多行合并 row_keys）；"
                "%d 条体验版的正式版行不在活跃行内（热更缺口，label 已注明）、单列标注 trial-unmatched。"
                % (st["简单生存服"]["pendant"], st["经典服"]["pendant"],
                   st["简单生存服"]["acc_dropped"], st["经典服"]["acc_dropped"],
                   st["简单生存服"]["npc_dropped"], st["经典服"]["npc_dropped"],
                   n_trial_merged, n_trial_alone)
                +
                scope_notes +
                "④ 图标：按定版在全量补完后再统一补图，本板 icon 字段留空。"
                "⑤ 数据链路：03_执行 提取脚本（03_执行/all_equips_full_extract.py）→ 30_分析 冻结 JSON"
                "（sha256 见 source_locks，两服各一份）→ 本构建脚本，可复算可回放。"
            ),
            "state_summary": {"unresolved": len(all_items), "static config": len(all_items),
                              "verified": 0, "runtime final unknown": len(all_items),
                              "有属性": sum(1 for i in all_items if i["属性"])},
            "provenance": {
                "contract_version": 3, "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": source_locks,
                "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                                 "integer_join_policy": "no-equal-integer-join",
                                 "runtime_final_policy": "unknown-unless-runtime-proven"},
            },
        },
        "items": all_items,
    }
    write_board(OUT_KJ1, d)
    print("合并卡", len(all_items), "条 →", OUT_KJ1.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
