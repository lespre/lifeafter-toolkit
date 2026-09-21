#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Weapon Skin Effect Source Binding（用户 2026-09-13 阶段：只做连边，不改分类/UI）。

把表现来源（sfx_function / behavior_res / effect_show）与 canonical Weapon Skin Entity 建立
**可证明**的连边，产出：

  artifacts/active/weapon_skin/WEAPON_SKIN_SOURCE_BINDINGS.jsonl
  analysis/audit/weapon_skin_binding_report.json        §10 的 15 项
  domains/weapon_skin/SOURCE_GRAPH.json                 （更新边：verified / unresolved / rejected）

证据分层（禁止"整数相同即连边"）：
  E1 字段语义：source 里存在 skin 键字段（sfx_function.skin_id 348/348；behavior_res 主键=skin id）
  E2 值域：该字段取值 ⊆ canonical skin_item_id 集合
  E3 共享参数：source 记录里的资源路径词干 skin_XXXX_YYY == 该皮肤 canonical model_path 的词干（非整数证据）
  E4 显式映射表：skin_2_sfx_function_map / _detail / skin_function_item_id_to_anim_name
     —— 目前 payload 可读但通用 decoder 出 0 行（decode gap），记 pending，不冒充已证
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipelines.locator.resolve_table import resolve_table      # noqa: E402
from pipelines.parsing.decoder import decode_table             # noqa: E402

BA = "test-documents-ba8a239a"
ART = ROOT / "artifacts" / "active" / "weapon_skin"
BINDINGS = ART / "WEAPON_SKIN_SOURCE_BINDINGS.jsonl"
REPORT = ROOT / "analysis" / "audit" / "weapon_skin_binding_report.json"
GRAPH = ROOT / "domains" / "weapon_skin" / "SOURCE_GRAPH.json"
STD = ROOT / "domains" / "weapon_skin" / "EFFECT_STANDARD.json"

STEM = re.compile(r"(skin_\d{4}_\d{3})")

# behavior_res 自身字段语义 → 既有 effect_type（沿用 Effect Standard 词表，不新增类型）
BR_FIELD_EFFECT = {
    "hit_sfx_path": "hit_effect",
    "fire_sfx_path": "combat_sound",
    "hold_sfx_path": "combat_sound",
    "hold_sfx_loop_path": "combat_sound",
    "trajectory_path_real": "AV",               # AV = 按武器类别落 projectile_effect / slash_effect
    "trajectory_sfx_path": "AV",
    "trajectory_sfx_path_nor": "AV",
    "trajectory_sfx_path_trace": "AV",
    "trajectory_path_special": "AV",
    "skin_replace_anims": "AV",
    "defeat_args": "kill_effect",
    "defeat_model": "kill_effect",
    "extension_defeat_sfx": "kill_effect",
    "socket": "special_interaction",
    "explode_sfx_path": "other",
    "preview_range_sfx_path": "other",
}


def _val(v):
    return v[1] if isinstance(v, tuple) and len(v) == 2 else v


def _rows(table: str):
    rt = resolve_table(BA, table)
    if rt.get("status") != "ok":
        return rt, []
    return rt, list(decode_table(rt).rows)


def _stem(text) -> str | None:
    m = STEM.search(str(text or ""))
    return m.group(1) if m else None


def _path_values(values: dict) -> list[str]:
    return [str(_val(v)) for v in values.values()
            if isinstance(_val(v), str) and ("/" in str(_val(v)) or str(_val(v)).endswith(".sfx"))]


def build() -> dict:
    canon = {}
    for line in (ART / "WEAPON_SKIN_RESOLVED.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            canon[int(r["skin_item_id"])] = r
    std = json.loads(STD.read_text(encoding="utf-8"))
    type_by_field = {f: v["effect_type"] for f, v in std["field_semantic_map"].items()}

    bindings: list[dict] = []

    # ── 1) sfx_function：E1 字段 skin_id + E2 值域 + E3 路径词干 ──
    rt, sfx_rows = _rows(r"com\cdata\weapon_skin_sfx_function_data.py")
    sfx_by_skin: dict[int, list[int]] = {}
    for r in sfx_rows:
        v = {k: _val(x) for k, x in (r.get("values") or {}).items()}
        sid = v.get("skin_id")
        if sid is None:
            bindings.append(_bind("weapon_skin.sfx_function", r["key"], "sfx_row_key(1120xxx)", None, None,
                                  "unresolved_candidate", ["字段 skin_id 缺失"], "E1 缺失"))
            continue
        sid = int(sid)
        skin = canon.get(sid)
        skin_stem = _stem((skin or {}).get("data_fields", {}).get("model_path")) if skin else None
        src_stems = {s for s in (_stem(p) for p in _path_values(r.get("values") or {})) if s}
        ev, status, rel = [], "unresolved_candidate", "unresolved_candidate"
        if skin is None:
            ev.append("E2 值域：skin_id 不在 canonical skin_item_id 集合")
        else:
            ev.append("E1 字段语义：sfx_function.skin_id（348/348 行有值）")
            ev.append("E2 值域：skin_id ⊆ canonical skin_item_id（75/75）")
            if skin_stem and src_stems and skin_stem in src_stems:
                ev.append(f"E3 共享参数：路径词干 {skin_stem} 与 canonical model_path 一致")
                status, rel = "verified", "skin_id_binding"
            elif not src_stems:
                ev.append("E3 缺失：该行无资源路径（如 jump:NNNN）⇒ 只有 E1+E2，不构成连边证据")
                ev.append("residual：需要 skin_2_sfx_function_map（decode gap）或 runtime consumer 才能升级")
            elif src_stems and skin_stem:
                ev.append(f"E3 不一致：记录路径词干 {sorted(src_stems)[:2]} ≠ canonical {skin_stem}")
                rel = "shared_effect"
        if status == "verified":
            sfx_by_skin.setdefault(sid, []).append(r["key"])
        bindings.append(_bind("weapon_skin.sfx_function", r["key"], "sfx_row_key(1120xxx)", sid, sid,
                              rel, ev, (None if status == "verified" else "；".join(ev[-2:])[:200] or None),
                              status=status,
                              effect_type=_sfx_effect_type(v.get("sfx_type"),
                                                            bool((skin or {}).get("data_fields", {}).get("coldarm_types"))),
                              path_stems=sorted(src_stems)[:3]))

    # ── 2) behavior_res：主键=skin key + E3 路径词干 ──
    rt2, br_rows = _rows(r"com\cdata\weapon_skin_behavior_res_data.py")
    for r in br_rows:
        sid = int(r["key"])
        skin = canon.get(sid)
        skin_stem = _stem((skin or {}).get("data_fields", {}).get("model_path")) if skin else None
        src_stems = {s for s in (_stem(p) for p in _path_values(r.get("values") or {})) if s}
        if skin is None:
            bindings.append(_bind("weapon_skin.behavior_res", sid, "skin_item_id(primary key)", sid, None,
                                  "unresolved_candidate",
                                  ["E1/E2 未成立：主键不在 canonical skin_item_id（board-only / 行为预告类）"],
                                  "负证据：canonical 无此实体", status="unresolved_candidate"))
            continue
        _df = {k: _val(v) for k, v in (r.get("values") or {}).items()}
        _melee = bool(((canon or {}).get(sid, {}).get("data_fields") or {}).get("coldarm_types"))
        _ets = sorted({("slash_effect" if _melee else "projectile_effect") if BR_FIELD_EFFECT[k] == "AV" else BR_FIELD_EFFECT[k]
                       for k in _df if k in BR_FIELD_EFFECT and _df[k] not in (None, "", [], {})})
        ev = ["E1 字段语义：behavior_res 主键即 skin 键", "E2 值域：主键 ⊆ canonical skin_item_id（75/78）"]
        if skin_stem and src_stems and skin_stem in src_stems:
            ev.append(f"E3 共享参数：路径词干 {skin_stem} 与 canonical model_path 一致")
            bindings.append(_bind("weapon_skin.behavior_res", sid, "skin_item_id(primary key)", sid, sid,
                                  "direct_skin_item_binding", ev, None, path_stems=sorted(src_stems)[:3],
                                  effect_type=_ets))
        else:
            bindings.append(_bind("weapon_skin.behavior_res", sid, "skin_item_id(primary key)", sid, sid,
                                  "shared_behavior", ev + ["E3 未命中：记录路径词干与 canonical model_path 不一致或缺失"],
                                  "缺非整数证据 ⇒ 保持 unresolved", status="unresolved",
                                  path_stems=sorted(src_stems)[:3], effect_type=_ets))

    # ── 3) effect_show：专用解析（pipelines/parsing）+ 注册行定位 ──
    es_info = _effect_show()
    if es_info.get("rows_decoded"):
        for sid, rowkey in (es_info.get("registry") or {}).items():
            if int(sid) in canon:
                bindings.append(_bind("weapon_skin.effect_show", rowkey, "es_row_key", int(sid), None,
                                      "direct_skin_item_binding",
                                      ["E4 显式索引：两表 0x76 节点 key = 同源 hash(skin_id)（decode_es_registry）",
                                       "residual：注册行≠UI 当前行（改名/升格旧行并存）"], None))
    else:
        bindings.append(_bind("weapon_skin.effect_show", None, "es_row_key", None, None, "unresolved_candidate",
                              ["payload 已定位（BA8A entry 3671/19852）", es_info.get("note", "")],
                              es_info.get("residual") or "解析未完成", status="unresolved_candidate"))

    BINDINGS.write_text("".join(json.dumps(b, ensure_ascii=False) + "\n" for b in bindings), encoding="utf-8")

    # ── §10 报告 ──
    def st(sid, status=None, rel=None):
        return [b for b in bindings if (sid is None or b["source_id"] == sid)
                and (status is None or b["status"] == status) and (rel is None or b["relation_type"] == rel)]
    sfx_all, br_all = st("weapon_skin.sfx_function"), st("weapon_skin.behavior_res")
    shared_sfx = {}
    for b in sfx_all:
        if b["target_skin_item_id"] and b["status"] == "verified":
            shared_sfx.setdefault(b["source_record_key"], []).append(b["target_skin_item_id"])
    multi = {k: v for k, v in shared_sfx.items() if len(v) > 1}
    per_type: dict[str, int] = {}
    for b in bindings:
        if b["status"] == "ok" or b["status"] != "verified":
            continue
        ets = b.get("effect_type")
        for et in (ets if isinstance(ets, list) else ([ets] if ets else [])):
            per_type[et] = per_type.get(et, 0) + 1
    report = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "snapshot_basis": BA,
        "1_sfx_function_rows_bound": {"total": len(sfx_all), "verified": len(st("weapon_skin.sfx_function", "verified"))},
        "2_behavior_res_rows_bound": {"total": len(br_all), "verified": len(st("weapon_skin.behavior_res", "verified"))},
        "3_effect_show_parsed": es_info.get("rows_decoded", 0),
        "4_effect_show_bound": len(st("weapon_skin.effect_show", "verified")),
        "5_direct_binding": len(st(None, "verified", "direct_skin_item_binding")),
        "6_indirect_binding": {
            "count": len(st(None, "verified")) - len(st(None, "verified", "direct_skin_item_binding")),
            "note": "均为『经 skin_id 型字段 + E2 值域 + E3 共享参数』直达 skin_item_id，无中间函数调用（若有 get_skin_item_id 类中间步骤会在 evidence_refs 记录）"},
        "7_unresolved_candidate": len(st(None, "unresolved_candidate")),
        "8_shared_effect_or_behavior": {"shared_effect_records": len(st(None, None, "shared_effect")),
                                        "shared_behavior_records": len(st(None, None, "shared_behavior")),
                                        "single_record_multi_skin": len(multi)},
        "9_bindings_per_effect_type": per_type,
        "10_cross_source_verified_effect_types": _cross_source(bindings),
        "11_single_source_effect_types": _single_source_split(bindings),
        "12_ui_items_previously_duplicated": {"note": "上一阶段已合并「特效详情」+「战斗表现」；本轮不改 UI"},
        "13_combat_presentation_entity_count": {"entities": len(canon),
                                                "with_verified_effect_source": len({b["target_skin_item_id"] for b in bindings if b["status"] == "verified"}),
                                                "note": "不做 entity 合并改写（本轮只建边）"},
        "14_merge_depends_on_name_equality": False,
        "15_graph_can_explain_source_to_entity": {
            "data_layer": True,
            "how": "WEAPON_SKIN_SOURCE_BINDINGS.jsonl 每行给出 source_id + source_record_key → target_skin_item_id + evidence_refs；可按 (source_id, record_key) 反查实体",
            "cli": "未接线（api.cli 尚无 weapon_skin_source 指令）——不声称已支持 CLI explain"},
        "evidence_layers": {"E1_field_semantic": True, "E2_value_space": True, "E3_shared_parameter": True,
                            "E4_explicit_map": False, "E4_note": "skin_2_sfx_function_map / _detail / skin_function_item_id_to_anim_name 仍 decode gap"},
        "residuals": [es_info.get("residual")] if es_info.get("residual") else [],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    # ── 更新 Source Graph 的边（verified / unresolved / rejected）──
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    edges = [e for e in graph["edges"] if e["to"] not in
             ("source:weapon_skin.sfx_function", "source:weapon_skin.behavior_res", "source:weapon_skin.effect_show")]
    edges.append({"from": "source:weapon_skin.main", "to": "source:weapon_skin.sfx_function",
                  "relation": "effect records（多对一）", "status": "verified", "snapshot": BA,
                  "evidence_ref": ["artifacts/active/weapon_skin/WEAPON_SKIN_SOURCE_BINDINGS.jsonl",
                                   "domains/weapon_skin/SOURCE_GRAPH.json"],
                  "rule": f"skin_id 字段（348/348）+ 值域 ⊆ canonical + 共享路径词干：verified {report['1_sfx_function_rows_bound']['verified']}/{len(sfx_all)}",
                  "rejected_alternatives": ["按 name 相等配对（禁止）"]})
    edges.append({"from": "source:weapon_skin.main", "to": "source:weapon_skin.behavior_res",
                  "relation": "behavior records（主键=skin 键）", "status": "verified", "snapshot": BA,
                  "evidence_ref": ["artifacts/active/weapon_skin/WEAPON_SKIN_SOURCE_BINDINGS.jsonl"],
                  "rule": f"主键 ⊆ canonical（75/78）+ 共享路径词干：verified {report['2_behavior_res_rows_bound']['verified']}/{len(br_all)}"})
    edges.append({"from": "source:weapon_skin.main", "to": "source:weapon_skin.effect_show",
                  "relation": "注册行（hash(skin_id) 同源索引）",
                  "status": "verified" if report["4_effect_show_bound"] else "unresolved", "snapshot": BA,
                  "evidence_ref": ["artifacts/active/weapon_skin/WEAPON_SKIN_SOURCE_BINDINGS.jsonl"],
                  "rule": "两表 0x76 节点 key 同源 hash(skin_id) ⇒ 注册行定位；注册行≠UI 当前行（residual）",
                  "residual": None if report["4_effect_show_bound"] else es_info.get("residual")})
    for t in ("weapon_kind.skin_item", "coldarm_type.skin_item", "skin.replace_anims"):
        edges.append({"from": "source:weapon_skin.main", "to": f"source:{t}",
                      "relation": "候选（本阶段未解）", "status": "rejected", "snapshot": BA, "evidence_ref": [],
                      "rule": "payload 可读但 decoder 出 0 行 ⇒ 本轮无法证明连边（不是'不存在'，是'暂无证据'）；"
                              "按纪律记 rejected-for-this-phase 而非 verified",
                      "residual": "需要专用解析后才能升级"})
    seen, uniq = set(), []
    for e in edges:
        key = (e["from"], e["to"], e.get("relation"))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(e)
    graph["edges"] = uniq
    graph["generated"] = report["generated_at"]
    GRAPH.write_text(json.dumps(graph, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("1_sfx_function_rows_bound", "2_behavior_res_rows_bound",
                                             "3_effect_show_parsed", "4_effect_show_bound",
                                             "5_direct_binding", "6_indirect_binding",
                                             "7_unresolved_candidate", "8_shared_effect_or_behavior",
                                             "9_bindings_per_effect_type")}, ensure_ascii=False))
    return report


def _single_source_split(bindings: list[dict]) -> dict:
    """哪些 effect_type 仍只有单源 / 完全无绑定。"""
    from collections import defaultdict
    acc: dict[tuple, set] = defaultdict(set)
    for b in bindings:
        if b["status"] != "verified" or b["target_skin_item_id"] is None:
            continue
        ets = b.get("effect_type")
        for et in (ets if isinstance(ets, list) else ([ets] if ets else [])):
            acc[(b["target_skin_item_id"], et)].add(b["source_id"])
    single = sorted({k[1] for k, v in acc.items() if len(v) == 1})
    cross = sorted({k[1] for k, v in acc.items() if len(v) >= 2})
    all_types = [x for x in json.loads(STD.read_text(encoding="utf-8"))["effect_types"]]
    bound = {k[1] for k in acc}
    return {"single_source_only_types": [x for x in single if x not in cross],
            "unbound_types": [x for x in all_types if x not in bound and x != "unresolved"]}


def _cross_source(bindings: list[dict]) -> list[dict]:
    """同一 (skin_item_id, effect_type) 是否被 ≥2 个独立来源 binding 支撑（都须 verified）。"""
    acc: dict[tuple, set] = {}
    for b in bindings:
        if b["status"] != "verified" or b["target_skin_item_id"] is None:
            continue
        ets = b.get("effect_type")
        ets = ets if isinstance(ets, list) else ([ets] if ets else [])
        for et in ets:
            acc.setdefault((b["target_skin_item_id"], et), set()).add(b["source_id"])
    return [{"skin_item_id": k[0], "effect_type": k[1], "sources": sorted(v)} for k, v in acc.items() if len(v) >= 2]


def _sfx_effect_type(sfx_type, melee: bool = False) -> str | None:
    """sfx_type → 既有 effect_type 词表（6=弹道/挥砍按武器类别落 projectile/slash，不新增类型）。"""
    base = {3: "hit_effect", 4: "kill_effect", 7: "combat_sound", 9: "combat_crosshair",
            10: "damage_number", 13: "nucleus_linkage", 14: "other", 15: "exclusive_combat_animation",
            16: "exclusive_idle_animation", 20: "special_interaction"}.get(sfx_type)
    if sfx_type == 6:
        return "slash_effect" if melee else "projectile_effect"
    return base


def _bind(source_id, key, key_type, sid, skin_id, rel, ev, residual=None, status="verified",
          effect_type=None, path_stems=None) -> dict:
    return {"source_id": source_id, "source_record_key": key, "source_key_type": key_type,
            "target_skin_item_id": sid, "target_skin_id": skin_id, "relation_type": rel, "status": status,
            "evidence_refs": ev, "snapshot_basis": BA, "residual": residual,
            "effect_type": effect_type, "path_stems": path_stems or [],
            "evidence_layers": {"E1_field_semantic": True, "E2_value_space": True,
                                "E3_shared_parameter": any("E3 共享参数" in x for x in ev),
                                "E4_explicit_map": False}}


def _effect_show() -> dict:
    """经 pipelines/parsing/effect_show.py（专用解析唯一入口）取行与注册行。"""
    try:
        from pipelines.parsing import effect_show as _es
        got = _es.parse()
        rows = got.get("rows") or []
        reg = got.get("registry") or {}
        if rows:
            return {"rows_decoded": len(rows), "registry": reg,
                    "note": f"专用解析成功（{len(rows)} 行 / 注册行 {len(reg)}）",
                    "residual": "注册行≠UI 当前行（改名/升格旧行并存）"}
        return {"rows_decoded": 0, "registry": {}, "note": f"专用解析未产出（{got.get('status')}）",
                "residual": got.get("reason") or "effect_show 仍为 decode gap"}
    except Exception as e:                                     # noqa: BLE001
        return {"rows_decoded": 0, "note": f"专用解析入口异常：{str(e)[:120]}",
                "residual": "effect_show 仍为 decode gap"}


def _effect_show_legacy() -> dict:
    """effect_show 专用解析（复用仓库既有实现；失败则如实返回，不冒充）。"""
    try:
        sys.path.insert(0, str(ROOT / "tools"))
        import importlib
        mod = importlib.import_module("rebuild_weapon_skin_catalog_current")
        es_base = ROOT / "03拆包产物" / "config_work" / "script_py314_docs_BA8A239A" / "entries" / "003671.bin"
        skin_base = ROOT / "03拆包产物" / "config_work" / "script_py314_docs_BA8A239A" / "entries" / "011817.bin"
        if not (es_base.exists() and skin_base.exists()):
            return {"rows_decoded": 0, "note": "BA8A 原始 entry 文件不在本仓库路径下",
                    "residual": "需要 BA8A entry 原始 payload 字节才能跑专用解析"}
        return {"rows_decoded": 0, "note": f"专用解析函数可用={hasattr(mod, 'decode_effect_show_rows')}",
                "residual": "本轮未完成 payload 读取接线（需 LiveNpkReader 的 _unpack_entry 路径）"}
    except Exception as e:                                     # noqa: BLE001
        return {"rows_decoded": 0, "note": f"专用解析调用失败：{str(e)[:120]}",
                "residual": "effect_show 仍为 decode gap（parser 入口已定位在 pipelines/parsing 待接线）"}


if __name__ == "__main__":
    build()
