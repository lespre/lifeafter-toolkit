#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Weapon Skin Source Binding Phase 2 — Explicit Mapping Closure（用户 2026-09-13）。

只做表现系统内部连边：不改 UI / Effect Standard / grade / listing / acquisition / Item·Fashion·Lottery。

产出：
  artifacts/active/weapon_skin/WEAPON_SKIN_SOURCE_BINDINGS_V2.jsonl   （v1 归档 historical）
  analysis/audit/weapon_skin_corroboration_matrix.json                （skin × effect_type 矩阵）
  analysis/audit/weapon_skin_binding_phase2_report.json               （18 项汇报）
  domains/weapon_skin/SOURCE_GRAPH.json                               （补 relation_kind / source_class）

证据等级（正式固定）：
  E1 字段语义｜E2 key-space 兼容｜E3 非整数共享资源/参数｜E4 显式 mapping 表｜E5 runtime consumer lookup

关系三分（用户 §9）：
  identity_binding / presentation_binding / corroboration_binding

来源两类（用户 §11）：
  content_source（独立业务来源，可计入独立源数）｜mapping_source（映射/索引证据，只增强 binding confidence）
  ｜runtime_evidence_source（运行时消费证据）
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

from pipelines.parsing import weapon_skin_mapping as MP        # noqa: E402

BA = "test-documents-ba8a239a"
ART = REPO / "artifacts" / "active" / "weapon_skin"
HIST = REPO / "artifacts" / "historical" / "weapon_skin"
DOM = REPO / "domains" / "weapon_skin"
AUDIT = REPO / "analysis" / "audit"

STEM = re.compile(r"(skin_\d{4}_\d{3})")

# effect_show / 中文类目 → 既有 effect_type 词表（不新增类型）
CAT_EFFECT = {
    "命中效果": "hit_effect", "击败特效": "kill_effect", "伤害跳字": "damage_number",
    "攻击弹道": "AV", "挥砍特效": "AV", "战斗音效": "combat_sound", "攻击准心": "combat_crosshair",
    "专属战斗动作": "exclusive_combat_animation", "专属待机动作": "exclusive_idle_animation",
    "特殊交互": "special_interaction", "核芯联动": "nucleus_linkage",
}
BR_EFFECT = {
    "hit_sfx_path": "hit_effect", "fire_sfx_path": "combat_sound", "hold_sfx_path": "combat_sound",
    "hold_sfx_loop_path": "combat_sound", "trajectory_path_real": "AV", "trajectory_sfx_path": "AV",
    "trajectory_sfx_path_nor": "AV", "trajectory_sfx_path_trace": "AV", "trajectory_path_special": "AV",
    "skin_replace_anims": "AV", "defeat_args": "kill_effect", "defeat_model": "kill_effect",
    "extension_defeat_sfx": "kill_effect", "socket": "special_interaction",
    "explode_sfx_path": "other", "preview_range_sfx_path": "other",
}
SFX_TYPE = {3: "hit_effect", 4: "kill_effect", 6: "AV", 7: "combat_sound", 9: "combat_crosshair",
            10: "damage_number", 13: "nucleus_linkage", 14: "other",
            15: "exclusive_combat_animation", 16: "exclusive_idle_animation", 20: "special_interaction"}

CONTENT_SOURCES = {"weapon_skin.sfx_function", "weapon_skin.behavior_res", "weapon_skin.effect_show",
                   "weapon_skin.sound", "weapon_skin.nucleus_conf", "weapon_skin.pendant"}
MAPPING_SOURCES = {"weapon_skin.skin_2_sfx_function_map", "weapon_skin.skin_2_sfx_function_map_detail",
                   "weapon_skin.skin_function_item_id_to_anim_name"}


def val(v):
    return v[1] if isinstance(v, tuple) else v


def stems(values: dict) -> set[str]:
    out = set()
    for v in values.values():
        for t in (v if isinstance(v, list) else [v]):
            if isinstance(t, tuple):
                t = t[1]
            if isinstance(t, str):
                out |= set(STEM.findall(t))
    return out


def load_canonical() -> dict[int, dict]:
    out: dict[int, dict] = {}
    for line in (ART / "WEAPON_SKIN_RESOLVED.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        sid = r.get("skin_item_id") or r.get("key")
        out[int(sid)] = r
    return out


def load_rows(table: str) -> list[dict]:
    import build_weapon_skin_source_bindings as P1
    rt, rows = P1._rows(table)
    if rt.get("status") != "ok":
        return []
    return rows


def melee(skin: dict | None) -> bool:
    df = (skin or {}).get("data_fields") or {}
    return bool(df.get("coldarm_types"))


def bind(source_id, record_key, key_type, sid, skin_id, rel, kind, ev, levels, residual=None,
         status="verified", source_class="content_source", effect_type=None, independent=True,
         evidence_refs=None):
    return {"source_id": source_id, "source_record_key": record_key, "source_key_type": key_type,
            "target_skin_item_id": sid, "target_skin_id": skin_id, "relation_type": rel,
            "relation_kind": kind, "status": status, "evidence_levels": sorted(set(levels)),
            "evidence_refs": evidence_refs if evidence_refs is not None else ev,
            "source_class": source_class, "independent_source": independent,
            "snapshot_basis": BA, "effect_type": effect_type, "residual": residual}


def build() -> dict:
    canon = load_canonical()
    canon_ids = set(canon)
    # stem → skin_item_id（canonical model_path 索引，用于 E3 绑定）
    stem2skin: dict[str, set[int]] = defaultdict(set)
    for _sid, _sk in canon.items():
        for _st in stems({"m": (_sk.get("data_fields") or {}).get("model_path") or ""}):
            stem2skin[_st].add(int(_sid))
    bindings: list[dict] = []

    # ---------- 1/2/3 三张显式 mapping 表 ----------
    map_sum = MP.summarize("skin_2_sfx_function_map")
    det_sum = MP.summarize("skin_2_sfx_function_map_detail")
    anim_sum = MP.summarize("skin_function_item_id_to_anim_name")
    map_got = MP.parse(MP.BA8A_ENTRIES["skin_2_sfx_function_map"])
    det_got = MP.parse(MP.BA8A_ENTRIES["skin_2_sfx_function_map_detail"])
    anim_got = MP.parse(MP.BA8A_ENTRIES["skin_function_item_id_to_anim_name"])

    sfx_rows = load_rows("weapon_skin_sfx_function_data")
    per_skin = Counter()
    sfx_by_key: dict[int, dict] = {}
    for r in sfx_rows:
        sid = int(val(r["values"]["skin_id"]))
        per_skin[sid] += 1
        sfx_by_key[int(r["key"])] = r

    # map：行 key = skin，行 ref 数 == 该皮肤 sfx 条数（74/75 实证）
    map_rows = {r["key"]: r for r in map_got["rows"]}
    map_count_match = {k for k in map_rows if len(map_rows[k]["refs"]) == per_skin.get(k)}
    map_by_skin = {k: {"refs": len(map_rows[k]["refs"]), "expected": per_skin.get(k),
                       "match": k in map_count_match} for k in map_rows}
    det_by_skin = {r["key"]: {"groups": len(r["groups"]), "refs": len(r["refs"])} for r in det_got["rows"]}
    anim_keys = {r["key"] for r in anim_got["rows"]}

    for k in sorted(map_rows):
        bindings.append(bind("weapon_skin.skin_2_sfx_function_map", k, "skin_item_id(primary key)", k, k,
                             "direct_skin_item_binding", "identity_binding",
                             ["E1 字段语义：row_key = skin_item_id（与 weapon_skin_data 同 key）",
                              "E4 显式映射：行 ref 数 = 该皮肤 sfx_function 行数（%s）"
                              % ("一致" if k in map_count_match else "不一致→residual")],
                             ["E1", "E4"],
                             residual=None if k in map_count_match else
                             f"该皮肤 sfx 条数 {per_skin.get(k)} ≠ map ref 数 {len(map_rows[k]['refs'])}",
                             status="verified" if k in map_count_match else "unresolved",
                             source_class="mapping_source", independent=False))
    for k in sorted(det_by_skin):
        bindings.append(bind("weapon_skin.skin_2_sfx_function_map_detail", k, "skin_item_id(primary key)", k, k,
                             "direct_skin_item_binding", "identity_binding",
                             ["E1 字段语义：row_key = skin_item_id（与主 map 同 75 行）",
                              "E4 显式映射：主 map 同行 key 存在（配套参数表）"],
                             ["E1", "E4"], residual="detail 每皮肤组数/参数数未逐条证语义",
                             status="verified" if k in map_rows else "unresolved",
                             source_class="mapping_source", independent=False))
    for k in sorted(anim_keys):
        hit = k in sfx_by_key
        skin = int(val(sfx_by_key[k]["values"]["skin_id"])) if hit else None
        bindings.append(bind("weapon_skin.skin_function_item_id_to_anim_name", k,
                             "sfx_function row key（1120xxx = function_item_id）",
                             skin if skin in canon_ids else None, skin,
                             "skin_id_binding" if hit else "unresolved_candidate", "presentation_binding",
                             ["E1 字段语义：row_key ∈ sfx_function row key 空间（1120018–1120364）",
                              "E2 key-space：44/44 命中 sfx_function row key 集合",
                              "E4 显式映射：经 sfx_function.skin_id 落到皮肤"],
                             ["E1", "E2", "E4"],
                             residual="anim_name 文本口径未取（本阶段只落 key 连边）；仅覆盖 44/348 个 function",
                             status="verified" if hit and skin in canon_ids else "unresolved",
                             source_class="mapping_source", independent=False,
                             effect_type=["exclusive_combat_animation", "exclusive_idle_animation",
                                           "special_interaction"]))

    # ---------- sfx_function + behavior_res（Phase 1 复核 + E4 升级） ----------
    sfx_stat = Counter()
    br_rows = load_rows("weapon_skin_behavior_res_data")
    for r in sfx_rows:
        k = int(r["key"]); v = r["values"]
        sid = int(val(v["skin_id"])); skin = canon.get(sid)
        st3 = stems(v)
        m = bool(st3) and bool(((skin or {}).get("data_fields") or {}).get("model_path")) and \
            bool(st3 & stems({"m": skin["data_fields"]["model_path"]}))
        me = melee(skin)
        et = SFX_TYPE.get(int(val(v["sfx_type"])) if v.get("sfx_type") else None)
        et = ("slash_effect" if me else "projectile_effect") if et == "AV" else et
        e4 = sid in map_count_match and per_skin.get(sid) == len(map_rows.get(sid, {}).get("refs", []))
        levels = ["E1", "E2"] + (["E3"] if m else []) + (["E4"] if e4 else [])
        e4_resid = None
        if m:
            status, rel = "verified", "skin_id_binding"
        elif e4:
            status, rel = "verified", "skin_id_binding"          # E4 显式映射成立 ⇒ verified_explicit_mapping
            e4_resid = ("E4 为皮肤级显式映射（map 行 ref 数 = 该皮肤 sfx 行数）；逐 ref 元素语义未落 ⇒ "
                        "本行绑定成立但 ref 身份不作断言")
        else:
            status, rel = "unresolved_candidate", "unresolved_candidate"
        sfx_stat[("verified" if status == "verified" else "unresolved")] += 1
        bindings.append(bind("weapon_skin.sfx_function", k, "sfx_function row key（1120xxx）", sid, sid,
                             rel, "presentation_binding",
                             ["E1 字段语义：字段 skin_id（348/348 有值）",
                              "E2 key-space：75/75 ⊆ canonical skin_item_id"]
                             + (["E3 共享参数：记录路径词干 == 该皮肤 canonical model_path 词干"] if m else [])
                             + (["E4 显式映射：skin_2_sfx_function_map 同皮肤行 ref 数一致"] if e4 else []),
                             levels, status=status, effect_type=et, independent=True,
                             residual=e4_resid if status == "verified" else
                             "仅 E1+E2（无路径词干、E4 未成立）⇒ 仍为 unresolved_candidate"))
    br_stat = Counter()
    for r in br_rows:
        sid = int(r["key"]); skin = canon.get(sid)
        v = r["values"]
        st3 = stems(v)
        m = bool(st3) and bool(((skin or {}).get("data_fields") or {}).get("model_path")) and \
            bool(st3 & stems({"m": skin["data_fields"]["model_path"]}))
        me = melee(skin)
        ets = sorted({("slash_effect" if me else "projectile_effect") if BR_EFFECT[f] == "AV" else BR_EFFECT[f]
                      for f in v if f in BR_EFFECT and val(v[f]) not in (None, "", [], {})})
        if skin is None:
            br_stat["unresolved"] += 1
            bindings.append(bind("weapon_skin.behavior_res", sid, "skin_item_id(primary key)", sid, None,
                                 "unresolved_candidate", "identity_binding",
                                 ["E1/E2 未成立：主键不在 canonical skin_item_id（board-only / 行为预告类）"],
                                 ["E1"], residual="canonical 无此实体（负证据）", status="unresolved_candidate",
                                 effect_type=ets, independent=True))
        elif m:
            br_stat["verified"] += 1
            bindings.append(bind("weapon_skin.behavior_res", sid, "skin_item_id(primary key)", sid, sid,
                                 "direct_skin_item_binding", "presentation_binding",
                                 ["E1 字段语义：主键即 skin 键", "E2 值域：主键 ⊆ canonical skin_item_id（75/78）",
                                  "E3 共享参数：记录路径词干 == 该皮肤 canonical model_path 词干"],
                                 ["E1", "E2", "E3"], effect_type=ets, independent=True))
        else:
            br_stat["shared_behavior"] += 1
            bindings.append(bind("weapon_skin.behavior_res", sid, "skin_item_id(primary key)", sid, sid,
                                 "shared_behavior", "presentation_binding",
                                 ["E1 字段语义：主键即 skin 键", "E2 值域：主键 ⊆ canonical skin_item_id",
                                  "E3 未命中：记录内路径词干指向别的皮肤或缺失"],
                                 ["E1", "E2"], residual="行为资源被判定为共用/或本皮肤路径缺失 ⇒ 保持 unresolved",
                                 status="unresolved", effect_type=ets, independent=True))

    # ---------- effect_show 56 条 ----------
    es = MP.parse(MP.BA8A_ENTRIES["weapon_skin_effect_show_data"])
    es_rows = es["rows"]
    es_skin_map = MP.summarize("weapon_skin_effect_show_data")
    # effect_show 行级内容用既有实现（pipelines/parsing/effect_show.py）
    try:
        from pipelines.parsing import effect_show as ESP
        got = ESP.parse()
        es_content = got.get("rows") or []
        es_registry = got.get("registry") or {}
        es_status, es_reason = got.get("status"), got.get("reason")
    except Exception as e:                                              # noqa: BLE001
        es_content, es_registry, es_status, es_reason = [], {}, "error", str(e)[:120]
    es_pairs: dict[int, list[tuple[str, str]]] = {}
    es_shape: list[str] = []
    for blk in es_content:
        es_shape.append(type(blk).__name__ + ":" + ",".join(str(x) for x in list(blk)[:3]) if hasattr(blk, "keys") else str(blk)[:40])
        if hasattr(blk, "items"):
            items = list(blk.items())
        elif isinstance(blk, list):
            items = [x for x in blk if isinstance(x, (list, tuple)) and len(x) == 2]
            if not items:                       # 形状：扁平 skin id 列表 → 只记 key，无内容
                items = [(x, []) for x in blk if isinstance(x, int)]
        else:
            items = []
        for k, v in items:
            ks = k if isinstance(k, str) else str(k)
            if ks.lstrip("-").isdigit() and isinstance(v, list):
                es_pairs[int(ks)] = [(str(a), str(b)) for a, b in v if isinstance(a, (str, int))]
    es_stat = Counter()
    for sid, pairs in sorted(es_pairs.items()):
        skin = canon.get(sid)
        me = melee(skin)
        ets = sorted({("slash_effect" if me else "projectile_effect") if CAT_EFFECT.get(c) == "AV"
                      else CAT_EFFECT.get(c, "other") for c, _n in pairs})
        if sid in canon_ids:
            es_stat["verified"] += 1
            bindings.append(bind("weapon_skin.effect_show", sid, "skin_id(hash 索引注册行)", sid, sid,
                                 "direct_skin_item_binding", "presentation_binding",
                                 ["E4 显式索引：两表 0x76 节点 key = 同源 hash(skin_id)（decode_es_registry）",
                                  "E2 key-space：注册行 skin ∈ canonical"],
                                 ["E2", "E4"], effect_type=ets, independent=True,
                                 residual="注册行≠UI 当前行（改名/升格旧行并存）"))
        else:
            es_stat["unresolved"] += 1
            bindings.append(bind("weapon_skin.effect_show", sid, "skin_id(hash 索引注册行)", None, sid,
                                 "unresolved_candidate", "identity_binding",
                                 ["E4 索引成立但目标皮肤不在 canonical"], ["E4"],
                                 residual="注册皮肤未进 canonical body", status="unresolved_candidate",
                                 effect_type=ets, independent=True))
    for sid, es_key in sorted(es_registry.items()):
        if sid in es_pairs:
            continue
        bindings.append(bind("weapon_skin.effect_show", int(sid), "skin_id→es 注册行 key",
                             int(sid) if int(sid) in canon_ids else None, int(sid),
                             "skin_id_binding" if int(sid) in canon_ids else "unresolved_candidate",
                             "identity_binding",
                             ["E4 显式索引：hash(skin_id) 同源（注册行 %s）" % es_key], ["E4"],
                             status="verified" if int(sid) in canon_ids else "unresolved_candidate",
                             effect_type=None, independent=True,
                             residual="注册行内容未落在已解行集合（UI 显示行可能为相邻行）"))

    # ---------- sound / pendant / nucleus（§8） ----------
    extra_tables = {
        "weapon_skin.sound": ("weapon_skin_sound_data_for_query", "sound", "combat_sound"),
        "weapon_skin.pendant": ("weapon_skin_pendant_data", "pendant", None),
        "weapon_skin.nucleus_conf": ("weapon_skin_replace_nucleus_conf", "nucleus", "nucleus_linkage"),
    }
    extra_stat: dict[str, dict] = {}
    for sid_src, (table, role, hint) in extra_tables.items():
        rows = load_rows(table)
        st = Counter()
        key_fields = Counter()
        for r in rows:
            k = int(r["key"]); v = r["values"]
            flds = [f for f in v if "skin" in f.lower()]
            key_fields.update(flds)
            cand = [int(val(v[f])) for f in flds if isinstance(val(v[f]), int)]
            cand = [c for c in cand if c in canon_ids] or cand
            st3 = stems(v)
            stem_hit = sorted({x for _st in st3 for x in stem2skin.get(_st, ())})
            sid = (cand[0] if cand else None) or (stem_hit[0] if len(stem_hit) == 1 else None)
            if sid is None and int(k) in canon_ids:
                sid = int(k)
            m = bool(stem_hit) and (not cand or (cand[0] in stem_hit))
            e4 = False
            levels = (["E1"] if flds else []) + (["E2"] if sid in canon_ids else []) + \
                     (["E3"] if m else []) + (["E4"] if e4 else [])
            if m or e4:
                status, rel = "verified", ("direct_skin_item_binding" if flds else "skin_id_binding")
            elif sid in canon_ids:
                status, rel = "unresolved", "unresolved_candidate"
            else:
                status, rel = "unresolved", "unresolved_candidate"
            et = hint
            if role == "pendant":
                et = None      # §8：先确认是否属于 combat presentation，未证前不归 effect_type
            st[status] += 1
            bindings.append(bind(sid_src, k, f"{role} row key", sid if sid in canon_ids else None, sid,
                                 rel, "identity_binding" if role == "pendant" else "presentation_binding",
                                 (["E1 字段语义：行内皮肤键字段 %s" % ",".join(sorted(flds))] if flds else
                                  ["E1 未成立：行内无 skin 命名字段"])
                                 + (["E2 key-space：值 ∈ canonical skin_item_id"] if sid in canon_ids else
                                    ["E2 未成立：值不在 canonical key 空间"])
                                 + (["E3 共享参数：行内路径词干 ∈ canonical model_path 索引 → 皮肤 %s"
                                     % stem_hit] if stem_hit else [])
                                 + (["E3 共享参数：路径词干 == 该皮肤 model_path 词干"] if m else []),
                                 levels, status=status, effect_type=et, independent=True,
                                 residual=None if status == "verified" else
                                 "字段语义/key-space 不足 ⇒ 仍 unresolved（未证不假装）"))
        extra_stat[sid_src] = {"table": table, "row_count": len(rows), "counts": dict(st),
                               "skin_fields_seen": dict(key_fields.most_common(8)),
                               "role": role, "effect_type_hint": hint}

    # ---------- 归档 v1 ----------
    HIST.mkdir(parents=True, exist_ok=True)
    v1 = ART / "WEAPON_SKIN_SOURCE_BINDINGS.jsonl"
    if v1.exists():
        import shutil
        (HIST / "v01_bindings").mkdir(parents=True, exist_ok=True)
        shutil.copy2(v1, HIST / "v01_bindings" / "WEAPON_SKIN_SOURCE_BINDINGS.jsonl")
    v2 = ART / "WEAPON_SKIN_SOURCE_BINDINGS_V2.jsonl"
    with v2.open("w", encoding="utf-8") as fh:
        for b in bindings:
            fh.write(json.dumps(b, ensure_ascii=False) + "\n")

    # ---------- 印证矩阵（§10/§11：只有 content source 计数） ----------
    acc: dict[tuple, dict] = defaultdict(lambda: {"sources": set(), "levels": set(), "bindings": []})
    for b in bindings:
        if b["status"] != "verified" or b["target_skin_item_id"] is None:
            continue
        if b["source_class"] != "content_source":
            continue
        ets = b.get("effect_type")
        for et in (ets if isinstance(ets, list) else ([ets] if ets else [])):
            key = (b["target_skin_item_id"], et)
            acc[key]["sources"].add(b["source_id"])
            acc[key]["levels"] |= set(b["evidence_levels"])
            acc[key]["bindings"].append((b["source_id"], b["source_record_key"]))
    matrix = [{"skin_item_id": k[0], "effect_type": k[1],
               "source_refs": sorted(v["sources"]),
               "evidence_levels": sorted(v["levels"]),
               "independent_source_count": len(v["sources"]),
               "corroboration_status": "verified" if len(v["sources"]) >= 2 else "single_source",
               "binding_refs": [f"{s}:{r}" for s, r in v["bindings"][:12]]}
              for k, v in sorted(acc.items())]
    (AUDIT / "weapon_skin_corroboration_matrix.json").write_text(
        json.dumps({"snapshot_basis": BA, "rule": "mapping_source 不计入 independent_source_count（§11）",
                    "rows": matrix}, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- Source Graph 三关系 + source_class ----------
    gp = DOM / "SOURCE_GRAPH.json"
    graph = json.loads(gp.read_text(encoding="utf-8"))
    KIND = {"weapon_skin.sfx_function": ("presentation_binding", "content_source"),
            "weapon_skin.behavior_res": ("presentation_binding", "content_source"),
            "weapon_skin.effect_show": ("presentation_binding", "content_source"),
            "weapon_skin.sound": ("presentation_binding", "content_source"),
            "weapon_skin.pendant": ("identity_binding", "content_source"),
            "weapon_skin.nucleus_conf": ("presentation_binding", "content_source"),
            "weapon_skin.skin_2_sfx_function_map": ("identity_binding", "mapping_source"),
            "weapon_skin.skin_2_sfx_function_map_detail": ("identity_binding", "mapping_source"),
            "weapon_skin.skin_function_item_id_to_anim_name": ("corroboration_binding", "mapping_source")}
    for e in graph["edges"]:
        tgt = e["to"].replace("source:", "")
        if tgt in KIND:
            e["relation_kind"], e["source_class"] = KIND[tgt]
        else:
            e.setdefault("relation_kind", "identity_binding")
            e.setdefault("source_class", "content_source" if e["status"] == "verified" else "unknown")
    graph["relation_kinds"] = ["identity_binding", "presentation_binding", "corroboration_binding"]
    graph["source_classes"] = ["content_source", "mapping_source", "runtime_evidence_source"]
    graph["open_edges"] = [{"from": e["from"], "to": e["to"], "relation": e.get("relation"),
                            "status": e["status"], "why": e.get("rule") or e.get("residual")}
                           for e in graph["edges"] if e["status"] != "verified"]
    gp.write_text(json.dumps(graph, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- 18 项汇报 ----------
    def st_of(sid, status=None):
        out = [b for b in bindings if b["source_id"] == sid]
        return [b for b in out if status is None or b["status"] == status]

    sfx_unres = st_of("weapon_skin.sfx_function", "unresolved_candidate")
    sfx_ver = st_of("weapon_skin.sfx_function", "verified")
    e4v = [b for b in bindings if "E4" in b["evidence_levels"] and b["status"] == "verified"]
    e4e5 = [b for b in bindings if "E4" in b["evidence_levels"] and "E5" in b["evidence_levels"]]
    es_ver = [b for b in bindings if b["source_id"] == "weapon_skin.effect_show" and b["status"] == "verified"]
    types_indep: dict[str, Counter] = defaultdict(Counter)
    for m in matrix:
        types_indep[m["effect_type"]][m["independent_source_count"]] += 1
    all_types = json.loads((DOM / "EFFECT_STANDARD.json").read_text(encoding="utf-8"))["effect_types"]
    _per = defaultdict(set)
    for m in matrix:
        _per[m["effect_type"]].add(m["independent_source_count"])
    cross2 = sorted({m["effect_type"] for m in matrix if m["independent_source_count"] >= 2})
    single_note = "另有同时存在单源与跨源 cell 的类型：" + ", ".join(sorted(
        {t for t, c in _per.items() if 1 in c and any(x >= 2 for x in c)}))
    cross3 = sorted({m["effect_type"] for m in matrix if m["independent_source_count"] >= 3})
    single = sorted({t for t, c in _per.items() if c == {1}})
    never = [t for t in all_types if t not in {m["effect_type"] for m in matrix} and t != "unresolved"]

    report = {
        "snapshot_basis": BA,
        "1_mapping_tables_parsed": {"skin_2_sfx_function_map": map_sum,
                                    "skin_2_sfx_function_map_detail": det_sum,
                                    "skin_function_item_id_to_anim_name": anim_sum},
        "2_mapping_real_structure": {
            "common": "公共头 263B + 'x{' frame；索引层标准（节点表 (hash,off) + 行表 parse_index），行内容为引用图而非行式字段",
            "skin_2_sfx_function_map": "row_key = skin_item_id（75 行，1110004–1110183）；节点 hash 与 weapon_skin_data 完全同源；"
                                       "行 ref 数 = 该皮肤 sfx_function 行数（74/75 一致）⇒ skin → N×sfx_function 一对多",
            "skin_2_sfx_function_map_detail": "同 75 行 key 空间，配套参数（每皮肤组数 0–9），与主 map 配套：skin → map → detail → function/params",
            "skin_function_item_id_to_anim_name": "row_key ∈ sfx_function row key 空间（1120018–1120364），44 行 ⊂ 348；"
                                                  "经 sfx_function.skin_id 落到皮肤",
            "cardinality": {"map_rows": len(map_rows), "map_vs_sfx_count_match": len(map_count_match),
                            "anomaly": [k for k in map_rows if k not in map_count_match]},
        },
        "3_runtime_consumer": {
            "found": False,
            "detail": "本快照未定位到直接消费三张 mapping 表的 runtime 模块（script 通道只含 data 包）；"
                      "E5 本阶段 0 条。索引同源（hash(skin_id) 与 weapon_skin_data 节点一致）是结构层证据，不冒称 E5",
        },
        "4_sfx_unresolved_remaining": {
            "phase1_unresolved_candidate": 195,
            "after_phase2": {"verified_explicit_mapping": len([b for b in sfx_ver if "E4" in b["evidence_levels"]]),
                             "verified_indirect_mapping": len([b for b in sfx_ver if "E3" in b["evidence_levels"]
                                                               and "E4" not in b["evidence_levels"]]),
                             "still_unresolved": len(sfx_unres),
                             "rejected": 0},
            "note": "E4（map 行 ref 数一致）把未证行按皮肤整体升级；未升级者仅 E1+E2",
        },
        "5_e4_e5_verified": {"E4_verified_bindings": len(e4v), "E4_E5_verified_bindings": len(e4e5),
                             "E5_bindings": len([b for b in bindings if "E5" in b["evidence_levels"]])},
        "6_effect_show": {"parsed_rows": len(es_content), "content_rows": len(es_pairs),
                          "registry_rows": len(es_registry), "verified_bindings": len(es_ver),
                          "status": es_status, "reason": es_reason, "raw_shape": es_shape[:4],
                          "corroboration": "与 sfx_function 只做到 same_skin / same_category；"
                                           "未证 same business presentation ⇒ 不 merge"},
        "7_behavior_res_shared": {
            "shared_rows": [b["source_record_key"] for b in bindings
                            if b["source_id"] == "weapon_skin.behavior_res" and b["relation_type"] == "shared_behavior"],
            "explanation": "这些行的主键是 canonical 皮肤，但行内资源路径词干指向**另一个**皮肤或缺失 ⇒ "
                           "被记为共享行为资源（unresolved），不给 verified",
        },
        "8_sound_pendant_nucleus": extra_stat,
        "9_relation_kinds": {"identity_binding": len([b for b in bindings if b["relation_kind"] == "identity_binding"]),
                             "presentation_binding": len([b for b in bindings if b["relation_kind"] == "presentation_binding"]),
                             "corroboration_binding": len([b for b in bindings if b["relation_kind"] == "corroboration_binding"])},
        "10_matrix": {"cells": len(matrix),
                      "cross_source_verified": len([m for m in matrix if m["corroboration_status"] == "verified"]),
                      "single_source": len([m for m in matrix if m["corroboration_status"] == "single_source"])},
        "11_source_classes": {"content_source_rows": len([b for b in bindings if b["source_class"] == "content_source"]),
                              "mapping_source_rows": len([b for b in bindings if b["source_class"] == "mapping_source"]),
                              "mapping_source_counted_as_independent": False},
        "12_independent_source_per_type": {t: {str(k): v for k, v in sorted(types_indep[t].items())}
                                           for t in sorted(types_indep)},
        "13_cross_source_types": {"two_or_more": cross2, "three_or_more": cross3},
        "14_single_source_types": single,
        "14_note": single_note,
        "15_no_verified_source_types": never,
        "16_source_vs_mapping_separated": True,
        "17_open_edges": graph["open_edges"],
        "18_presentation_system_graduated": False,
        "18_why": "explicit map/detail 的 **逐 ref 语义**与 anim_name 文本未落；E5 runtime consumer 未定位；"
                  "sound/pendant/nucleus 多数仍 unresolved；因此表现系统尚不可单独宣布毕业",
        "counts": {"bindings_total": len(bindings),
                   "sfx": dict(sfx_stat), "behavior_res": dict(br_stat), "effect_show": dict(es_stat)},
    }
    (AUDIT / "weapon_skin_binding_phase2_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


if __name__ == "__main__":
    rep = build()
    print(json.dumps({k: rep[k] for k in ("4_sfx_unresolved_remaining", "5_e4_e5_verified",
                                          "8_sound_pendant_nucleus", "13_cross_source_types",
                                          "14_single_source_types", "15_no_verified_source_types")},
                     ensure_ascii=False, indent=1)[:2600])
    print("\nbindings:", rep["counts"])
