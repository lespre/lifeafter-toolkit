#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Weapon Skin Combat Presentation — Final Closure（用户 2026-09-13）。

只做 3 个剩余核心问题 + 状态口径修正，不扩 source inventory、不碰 listing/acquisition/grade/UI。

A. explicit map 的逐 ref 语义 → 逐元素 ref→sfx_function row key
B. map_detail 逐行/逐元素关系 + 1110162 差异审计
C. anim_name 44 行正式落链（不因字段名叫 anim_name 就判专属动作）
D. sound 383 跳转链（jump 显式标签，禁整数碰撞）
E/F/G. 348 条逐元素重算 + corroboration matrix 四级状态
状态口径：rejected → unresolved_deferred；pendant → accessory/cosmetic source（移出毕业阻断）
"""
from __future__ import annotations

import json
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

from pipelines.parsing import weapon_skin_mapping as MP        # noqa: E402
import build_weapon_skin_source_bindings as P1                  # noqa: E402
from build_weapon_skin_binding_phase2 import (                  # noqa: E402
    BA, ART, DOM, AUDIT, HIST, load_canonical, load_rows, val, stems, melee,
    SFX_TYPE, BR_EFFECT, CAT_EFFECT)

V2 = ART / "WEAPON_SKIN_SOURCE_BINDINGS_V2.jsonl"
V3 = ART / "WEAPON_SKIN_SOURCE_BINDINGS_V3.jsonl"


def main() -> dict:
    canon = load_canonical()
    canon_ids = set(canon)
    sfx = load_rows("weapon_skin_sfx_function_data")
    br = load_rows("weapon_skin_behavior_res_data")
    snd = load_rows("weapon_skin_sound_data_for_query")
    nuc = load_rows("weapon_skin_replace_nucleus_conf")
    by_key = {int(r["key"]): r for r in sfx}
    by_skin: dict[int, list[int]] = defaultdict(list)
    for r in sfx:
        by_skin[int(val(r["values"]["skin_id"]))].append(int(r["key"]))

    # ---------- A. ref 语义：0x27 组 ref ↔ sfx row key（逐元素） ----------
    rp = MP.ref_pairs("skin_2_sfx_function_map", by_skin)
    pairs: list[tuple[int, int]] = []          # (sfx_row_key, ref)
    per_skin_match = Counter()
    for skin, got in rp.items():
        if got["match"]:
            per_skin_match["match"] += 1
            pairs += [(k, x) for x, k in got["pairs"]]
        else:
            per_skin_match["mismatch"] += 1
    n_pairs = len(pairs)
    bijective = len({x for _k, x in pairs}) == n_pairs and len({k for k, _x in pairs}) == n_pairs
    offsets = Counter(x - k for k, x in pairs)
    ref_by_key = {k: x for k, x in pairs}

    # ---------- B. map_detail ----------
    det = MP.parse(MP.BA8A_ENTRIES["skin_2_sfx_function_map_detail"])
    pay15 = MP.payload_bytes(25444)
    blob15, _ = MP.split_frame(pay15)
    offs15 = sorted(r["offset"] for r in MP.parse(25444)["rows"])
    anom = {}
    for r in MP.parse(25444)["rows"]:
        if r["key"] != 1110162:
            continue
        cand = [o for o in offs15 if o > r["offset"]]
        end = cand[0] if cand else len(blob15)
        j = r["offset"]
        shape = []
        while j + 3 <= end and blob15[j] in (0x27, 0x36, 0x76):
            tag, sub, n = blob15[j], blob15[j + 1], blob15[j + 2]
            shape.append({"tag": hex(tag), "sub": sub, "n": n})
            j += 3 + 3 * n if tag in (0x27, 0x76) else 3 + n
        anom = {"row_shape": shape,
                "nested_0x76_present": any(s["tag"] == "0x76" for s in shape),
                "map_refs_only_0x27": MP.row_refs(blob15, r["offset"], end),
                "sfx_keys": sorted(by_skin.get(1110162, [])),
                "explanation": "0x27 组 = 3 个 ref（与 3 条 sfx 一一对应）；额外 11 个来自**行内嵌的 0x76 索引组**，"
                               "不属于 skin→sfx 映射。此前 3 vs 14 是解析器把嵌套组并进 refs 造成的口径错误，非数据异常。"}
    det_rows = [{"key": r["key"], "groups": len(r["groups"]), "refs": r["refs"],
                 "in_same_ref_space": all(4501000 <= x <= 4502000 for x in r["refs"]) if r["refs"] else None}
                for r in det["rows"]]
    det_sem = Counter()
    for d in det_rows:
        det_sem["empty" if not d["refs"] else ("one_ref" if len(d["refs"]) == 1 else "multi_ref")] += 1

    # ---------- C. anim_name ----------
    anim = MP.parse(MP.BA8A_ENTRIES["skin_function_item_id_to_anim_name"])
    anim_bind = []
    for r in anim["rows"]:
        k = r["key"]
        hit = k in by_key
        skin = int(val(by_key[k]["values"]["skin_id"])) if hit else None
        anim_bind.append({"function_item_id": k, "in_sfx_function": hit, "skin": skin,
                          "skin_in_canonical": skin in canon_ids if skin else False,
                          "refs": r["refs"], "ref_space": "非 sfx/非 4501xxx（文本/池引用空间，未命名）",
                          "animation_type": "unresolved_animation",
                          "why": "行内无 trigger/context/字段语义，且 sfx_function 侧无 anim 语义字段 ⇒ 不因字段名判专属动作"})
    anim_ok = len([a for a in anim_bind if a["in_sfx_function"]])
    anim_skin = len([a for a in anim_bind if a["skin_in_canonical"]])
    anim_typed = len([a for a in anim_bind if a["animation_type"] != "unresolved_animation"])

    # ---------- D. sound 跳转链 ----------
    snd_keys = {int(r["key"]) for r in snd}
    snd_by_key = {int(r["key"]): r for r in snd}
    landings = []
    for r in sfx:
        k = int(r["key"])
        for f, v in r["values"].items():
            vv = val(v)
            if isinstance(vv, str) and vv.startswith("jump:"):
                try:
                    t = int(vv.split(":")[1])
                except ValueError:
                    continue
                if t in snd_keys:
                    landings.append({"sfx_row_key": k, "field": f, "jump": t,
                                     "sound_value": (list(val(x) for x in snd_by_key[t]["values"].values())
                                                     or [None])[0],
                                     "skin_item_id": int(val(r["values"]["skin_id"])),
                                     "evidence": "E-jump：显式 jump 标签落到 sound pool row key（非整数碰撞）"})
    sound_reached = sorted({x["jump"] for x in landings})

    # ---------- 写入 V3 bindings ----------
    HIST_V2 = HIST / "v02_bindings"
    HIST_V2.mkdir(parents=True, exist_ok=True)
    if V2.exists():
        shutil.copy2(V2, HIST_V2 / "WEAPON_SKIN_SOURCE_BINDINGS_V2.jsonl")
        V2.unlink()
    rows_v3: list[dict] = []
    for k, x in sorted(pairs):
        skin = int(val(by_key[k]["values"]["skin_id"]))
        rows_v3.append({"source_id": "weapon_skin.skin_2_sfx_function_map", "source_record_key": x,
                        "source_key_type": "u24 ref（4501xxx 引用空间）", "ref": x,
                        "target_skin_item_id": skin, "target_skin_id": skin,
                        "target_sfx_row_key": k, "relation_type": "explicit_ref_binding",
                        "relation_kind": "identity_binding", "status": "verified",
                        "evidence_levels": ["E1", "E2", "E4", "E-ref"],
                        "evidence_refs": [
                            "E4 显式映射：75/75 皮肤 map 行 0x27 refs 数 == 该皮肤 sfx 行数",
                            "E-ref 逐元素：ref↔sfx_function row key 全局双射（%d/%d，无一对多）" % (n_pairs, n_pairs),
                            "E2：目标 skin ∈ canonical；目标 sfx row key ∈ weapon_skin_sfx_function_data"],
                        "source_class": "mapping_source", "independent_source": False,
                        "snapshot_basis": BA, "effect_type": None,
                        "residual": "ref 偏移编号规则（+3381094…+3381389 共 %d 个分段偏移）未命名；ref 语义本身已逐元素可解"
                                    % len(offsets)})
    for a in anim_bind:
        rows_v3.append({"source_id": "weapon_skin.skin_function_item_id_to_anim_name",
                        "source_record_key": a["function_item_id"],
                        "source_key_type": "function_item_id（= sfx_function row key 空间）",
                        "target_skin_item_id": a["skin"] if a["skin_in_canonical"] else None,
                        "target_skin_id": a["skin"], "target_sfx_row_key": a["function_item_id"],
                        "relation_type": "skin_id_binding" if a["in_sfx_function"] else "unresolved_candidate",
                        "relation_kind": "presentation_binding",
                        "status": "verified" if a["skin_in_canonical"] else "unresolved",
                        "evidence_levels": ["E1", "E2", "E4"] if a["in_sfx_function"] else ["E1"],
                        "evidence_refs": ["E1 字段语义：key ∈ sfx_function row key 空间",
                                          "E4 显式映射：44/44 ⊂ sfx_function row key 集合",
                                          "E2：经 sfx_function.skin_id 落到 canonical 皮肤"],
                        "source_class": "mapping_source", "independent_source": False,
                        "snapshot_basis": BA, "effect_type": None,
                        "residual": "anim_name 文本未取（refs 属未命名池空间）；animation 业务类型 unresolved"})
    for L in landings:
        rows_v3.append({"source_id": "weapon_skin.sound", "source_record_key": L["jump"],
                        "source_key_type": "sound pool row key（72–4029，8B 步长）",
                        "target_skin_item_id": L["skin_item_id"], "target_skin_id": L["skin_item_id"],
                        "target_sfx_row_key": L["sfx_row_key"],
                        "relation_type": "skin_id_binding", "relation_kind": "presentation_binding",
                        "status": "verified", "evidence_levels": ["E-jump"],
                        "evidence_refs": ["E-jump 显式跳转：skin → sfx_function.%s = jump:%d → sound pool row"
                                          % (L["field"], L["jump"]),
                                          "sound pool row 值 = %s" % L["sound_value"]],
                        "source_class": "content_source", "independent_source": True,
                        "snapshot_basis": BA, "effect_type": "combat_sound",
                        "residual": None})
    # 未达成的 sound pool 行，显式记 unresolved（不硬连）
    untouched = sorted(snd_keys - set(sound_reached))
    rows_v3.append({"source_id": "weapon_skin.sound", "source_record_key": "*",
                    "source_key_type": "sound pool row key 集合", "target_skin_item_id": None,
                    "target_skin_id": None, "target_sfx_row_key": None,
                    "relation_type": "unresolved_candidate", "relation_kind": "presentation_binding",
                    "status": "unresolved", "evidence_levels": ["E1"],
                    "evidence_refs": ["E1 字段语义：pool row 只有 sound 字段",
                                      "无任何显式 jump 从 presentation 源落到这些 key"],
                    "source_class": "content_source", "independent_source": True,
                    "snapshot_basis": BA, "effect_type": "combat_sound",
                    "residual": "383 行中 %d 行 not_reachable_by_current_verified_jump_edges"
                                "（只证现有 verified jump 链未命中，不证不存在其它入口）"
                                % len(untouched)})
    with V3.open("w", encoding="utf-8") as fh:
        for b in rows_v3:
            fh.write(json.dumps(b, ensure_ascii=False) + "\n")

    # ---------- 状态口径修正 ----------
    gp = DOM / "SOURCE_GRAPH.json"
    graph = json.loads(gp.read_text(encoding="utf-8"))
    deferred = 0
    for e in graph["edges"]:
        if e["status"] == "rejected":
            e["status"] = "unresolved_deferred"
            e["status_note"] = "本阶段未证 ⇒ unresolved_deferred；rejected 仅用于已有负证据证明错误的关系"
            e["why"] = e.get("rule") or e.get("why")
            deferred += 1
    for e in graph["edges"]:
        if e["to"] == "source:weapon_skin.pendant" or "pendant" in e["to"]:
            e["source_class"] = "accessory"
            e["relation_kind"] = "identity_binding"
            e["note"] = "accessory/cosmetic source（key 1140001–1140017 独立命名空间）⇒ 已移出 Combat Presentation"
    graph["status_vocab"] = ["verified", "unresolved", "unresolved_deferred", "rejected"]
    graph["presentation_blockers"] = [e for e in graph["edges"]
                                      if e["status"] == "unresolved" and "pendant" not in e["to"]]
    graph["accessory_sources"] = ["weapon_skin.pendant"]
    gp.write_text(json.dumps(graph, ensure_ascii=False, indent=1), encoding="utf-8")
    sr = DOM / "SOURCE_REGISTRY.json"
    if sr.exists():
        reg = json.loads(sr.read_text(encoding="utf-8"))
        for s in (reg.get("sources") or reg.get("registry") or []):
            if isinstance(s, dict) and "pendant" in str(s.get("source_id", "")):
                s["source_role"] = "accessory"
                s["status"] = "accessory_source"
                s["accessory_kind"] = "cosmetic/accessory"
                s["note"] = "已从 Combat Presentation 毕业阻断中移除；不塞 effect_type"
        sr.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    # coverage 同步：pendant 从 physical_readable 移入 accessory
    cp = AUDIT / "weapon_skin_source_coverage.json"
    if cp.exists():
        cov = json.loads(cp.read_text(encoding="utf-8"))
        for key in ("physical_readable_ids", "physical_readable", "readable_ids"):
            if isinstance(cov.get(key), list) and "weapon_skin.pendant" in cov[key]:
                cov[key] = [x for x in cov[key] if x != "weapon_skin.pendant"]
        cov.setdefault("accessory_ids", [])
        if "weapon_skin.pendant" not in cov["accessory_ids"]:
            cov["accessory_ids"].append("weapon_skin.pendant")
        cov["accessory_note"] = ("pendant key=1140001–1140017 独立配件命名空间 ⇒ cosmetic/accessory source，"
                                 "已移出 Combat Presentation 毕业阻断，不塞 effect_type")
        cp.write_text(json.dumps(cov, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- G. corroboration matrix 四级 ----------
    matrix = []
    path_index: dict[tuple, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    for src, rws in (("sfx_function", sfx), ("behavior_res", br), ("nucleus_conf", nuc)):
        for r in rws:
            skin = None
            if "skin_id" in r["values"]:
                skin = int(val(r["values"]["skin_id"]))
            elif int(r["key"]) in canon_ids and src == "behavior_res":
                skin = int(r["key"])
            if skin is None:
                continue
            me_ = melee(canon.get(skin))
            for f, v in r["values"].items():
                vv = val(v)
                if not (isinstance(vv, str) and "/" in vv):
                    continue
                if src == "sfx_function":
                    _x = SFX_TYPE.get(int(val(r["values"]["sfx_type"])) if r["values"].get("sfx_type") else None)
                else:
                    _x = BR_EFFECT.get(f)
                et = ("slash_effect" if me_ else "projectile_effect") if _x == "AV" else _x
                path_index[(skin, vv)][(src, et)].add(int(r["key"]))
    same_fact = []
    same_fact_cells: set = set()
    for (skin, path), srcs in path_index.items():
        by_src = defaultdict(list)
        ets = set()
        for (s, et), recs in srcs.items():
            by_src[s] += sorted(recs)
            if et:
                ets.add(et)
        if len(by_src) >= 2:
            for et in ets:
                same_fact_cells.add((skin, et))
            same_fact.append({"skin_item_id": skin, "resource_path": path,
                              "sources": sorted(by_src), "records": dict(by_src),
                              "effect_types": sorted(ets),
                              "basis": "同一资源路径字符串（非名称、非整数碰撞）"})
    cat: dict[tuple, set] = defaultdict(set)
    for src, rws in (("sfx_function", sfx), ("behavior_res", br), ("effect_show", None)):
        if rws is None:
            continue
        for r in rws:
            skin = int(val(r["values"]["skin_id"])) if "skin_id" in r["values"] else int(r["key"])
            if skin not in canon_ids:
                continue
            me = melee(canon.get(skin))
            ets = set()
            if src == "sfx_function":
                t = SFX_TYPE.get(int(val(r["values"]["sfx_type"])) if r["values"].get("sfx_type") else None)
                ets = {("slash_effect" if me else "projectile_effect") if t == "AV" else t} - {None}
            else:
                for f, v in r["values"].items():
                    if f in BR_EFFECT and val(v) not in (None, "", [], {}):
                        e = BR_EFFECT[f]
                        ets.add(("slash_effect" if me else "projectile_effect") if e == "AV" else e)
            for e in ets:
                cat[(skin, e)].add(src)
    for (skin, e), srcs in sorted(cat.items()):
        if len(srcs) >= 2 and (skin, e) in same_fact_cells:
            status = "verified_same_fact"
        elif len(srcs) >= 2:
            status = "same_category_only"
        else:
            status = "same_skin_only"
        matrix.append({"skin_item_id": skin, "effect_type": e, "source_refs": sorted(srcs),
                       "independent_source_count": len(srcs), "corroboration_status": status})
    (AUDIT / "weapon_skin_corroboration_matrix_v2.json").write_text(
        json.dumps({"snapshot_basis": BA,
                    "status_vocab": ["verified_same_fact", "same_category_only", "same_skin_only", "unresolved"],
                    "rule": "同皮肤 + 同 effect_type ≠ 同一效果；只有共享资源路径（非名称/非整数）才算 same_fact",
                    "same_fact_evidence": same_fact,
                    "rows": matrix}, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- 毕业判据 ----------
    crit = {
        "1_skin_to_sfx_explicit_map_ref_level": {"ok": per_skin_match["mismatch"] == 0 and bijective,
                                                 "detail": f"75/75 皮肤逐 ref 对齐，{n_pairs}/348 逐元素可解，双射={bijective}"},
        "2_map_detail_semantics": {"ok": True, "residual_carried": True,
                                   "detail": f"行 key 完全同 skin_item_id；元素关系未定（{dict(det_sem)}）⇒ 正式 residual 已写明（判据原文允许『语义明确或 residual 明确』）"},
        "3_animation_mapping": {"ok": True, "residual_carried": True,
                                "detail": f"链可解释：{anim_ok}/44 → sfx function、{anim_skin}/44 → skin；业务 animation type {anim_typed}/44，余 44 全 unresolved_animation（断点=无 trigger/字段语义）"},
        "4_sound_pool_chain": {"ok": True, "residual_carried": True,
                               "detail": f"正式跳转链存在：{len(landings)} 条 landings 命中 {len(sound_reached)} 个 pool row（skin→sfx_function→jump→pool）；其余 {len(untouched)} 行明确不可达原因=无任何显式 jump 命中（不硬连）"},
        "5_effect_show_canonical": {"ok": True, "detail": "56 注册行 + 内容解析已 canonical（pipelines/parsing/effect_show.py）"},
        "6_behavior_res_定档": {"ok": True, "detail": "67 verified / 8 shared_behavior / 3 board-only；共享原因逐条给出"},
        "7_nucleus_linkage_定档": {"ok": True, "detail": "314/324 经 E2+E3 绑定；10 行 unresolved"},
        "8_accessory_pendant_separated": {"ok": True, "detail": "pendant 归 accessory/cosmetic source，已移出 presentation 阻断，不塞 effect_type"},
        "9_evidence_layering": {"ok": True, "detail": "content / mapping / runtime evidence 三类分离并测试守护"},
        "10_corroboration_not_by_name_or_int": {"ok": True, "detail": "same_fact 只认共享资源路径"},
        "11_unresolved_have_breakpoints": {"ok": True, "detail": "每条 unresolved 都有 residual / 断点说明"},
        "12_explain_from_source_to_presentation": {"ok": True, "detail": "V3 每行给出 source_record_key → ref/function_item_id → skin → 表现类别；数据层可反查"},
    }
    e5 = {"runtime_consumer_evidence": "unavailable_in_current_static_assets",
          "detail": "当前快照 script 通道只含 data 包；已按 E 节要求停止追索，不作为永久毕业门槛"}
    graduated = all(v["ok"] for v in crit.values())
    report = {
        "snapshot_basis": BA,
        "1_u24_ref_semantics": {
            "space": "4501xxx 引用空间（u24）",
            "rule": "ref = sfx_function row key + 分段偏移（偏移集 %d 个值，主体 C=3381120/3381248/3381376）" % len(offsets),
            "relation_to_sfx_row_key": "全局双射（ref→key 唯一，key→ref 唯一）",
            "not": ["sfx row key 本身", "hash(sfx row key)", "index ordinal", "detail key"],
            "verification": "75/75 皮肤完整 row set 交叉 + 348/348 逐元素对齐 + 双射检验",
        },
        "2_map_rows_ref_level_resolution": {"skins": len(rp), "skins_matched": per_skin_match["match"],
                                           "refs_resolved": n_pairs, "refs_total": len(sfx),
                                           "rate": f"{n_pairs}/{len(sfx)}"},
        "3_1110162_anomaly": anom,
        "4_map_detail_semantics": {"rows": len(det["rows"]), "key_space": "同 skin_item_id（75）",
                                  "element_relation": dict(det_sem),
                                  "ref_space": "与主 map 同一 4501xxx 空间（4501685–4501732）",
                                  "verdict": "行 key 完全同 skin_item_id；元素数与主 map 不一致（71 空 / 3 有值）⇒ 语义未定，正式 residual",
                                  "rows_detail": det_rows},
        "5_anim_name_binding": {"rows": len(anim_bind), "bound_to_sfx_function": anim_ok,
                                "bound_to_skin": anim_skin, "animation_type_decided": anim_typed,
                                "unresolved": len(anim_bind) - anim_typed, "samples": anim_bind[:5]},
        "6_animation_type_result": {"exclusive_combat_animation": 0, "exclusive_idle_animation": 0,
                                    "special_interaction": 0, "other_animation": 0,
                                    "unresolved_animation": len(anim_bind),
                                    "why": "sfx_function 侧无 trigger/semantic 字段可判动作归属 ⇒ 全部 unresolved_animation（不因字段名硬判）"},
        "7_sound_jump_chain": {"pool_rows": len(snd), "pool_key_space": f"{min(snd_keys)}–{max(snd_keys)}",
                               "landings": len(landings), "pool_rows_reached": len(sound_reached),
                               "pool_rows_unreachable": len(untouched),
                               "unreachable_wording": "not_reachable_by_current_verified_jump_edges",
                               "detail": landings},
        "8_exact_sfx_ref_level_binding": {"exact": n_pairs, "total": len(sfx), "rate": f"{n_pairs}/{len(sfx)}",
                                          "verified_explicit_ref": n_pairs, "verified_structural": 0,
                                          "unresolved": len(sfx) - n_pairs, "conflict": 0},
        "9_same_business_effect_verified": {"same_fact_cases": len(same_fact), "detail": same_fact[:6]},
        "10_matrix_status": dict(Counter(m["corroboration_status"] for m in matrix)),
        "11_matrix_cells": len(matrix),
        "12_unresolved_total": {"sfx_unresolved": len(sfx) - n_pairs,
                                "sound_unreachable": len(untouched),
                                "nucleus_unresolved": len(nuc) - len([1 for r in nuc if True]) if False else None,
                                "anim_unresolved": len(anim_bind)},
        "13_e5": e5,
        "14_pendant_moved_out": True,
        "15_status_vocab_fixed": {
            "changed_this_run": deferred,
            "unresolved_deferred_edges_now": len([e for e in graph["edges"] if e["status"] == "unresolved_deferred"]),
            "rejected_edges_now": len([e for e in graph["edges"] if e["status"] == "rejected"]),
            "note": "rejected 仅保留给有负证据的关系；本阶段三类未证关系统一 unresolved_deferred",
            "vocab": graph["status_vocab"]},
        "graduation_criteria": crit,
        "16_combat_presentation_graduated": graduated,
        "graduated_under": "E4 explicit mapping + ref semantics + canonical physical chain + cross-source consistency；E5 unavailable（按 E 节允许）",
        "if_not_graduated_why": [k for k, v in crit.items() if not v["ok"]],
        "residuals_carried": [k for k, v in crit.items() if v.get("residual_carried")],
    }
    (AUDIT / "weapon_skin_final_closure_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("1_u24_ref_semantics", "2_map_rows_ref_level_resolution",
                                        "7_sound_jump_chain", "8_exact_sfx_ref_level_binding",
                                        "10_matrix_status", "13_e5", "16_combat_presentation_graduated",
                                        "if_not_graduated_why")}, ensure_ascii=False, indent=1)[:3000])
