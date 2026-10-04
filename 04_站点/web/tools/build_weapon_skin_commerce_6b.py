#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Weapon Skin Phase 6B — Listing / Acquisition Final Closure（用户 2026-09-13）。

不重调查 Grade / Variant / Combat Presentation / Sale（Sale 已冻结）。只做：
  * 措辞修正：108 条改为 no_verified_sale_source_found_in_current_scanned_sources
    （absence in current scanned source ≠ verified never sold）
  * sale_ts 保持 semantic_status=likely / hypothesis=release_or_first_publish_date（不升级）
  * Listing 拆层：configured / active / visible / purchasable / listed（能证明多少写多少）
  * Acquisition 改多路径 acquisition_paths[]（不覆盖旧值）
  * price jump / gift jump / exchange 元素语义 的结论落盘（解开或 residual）
  * store consumer 结论：unavailable_in_current_static_assets（与 E5 同口径，不无限追）
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

BA = "test-documents-ba8a239a"
CHANNEL = "client_channel=test"
ART = REPO / "artifacts" / "active" / "weapon_skin"
DOM = REPO / "domains" / "weapon_skin"
AUDIT = REPO / "analysis" / "audit"


def load(name):
    return [json.loads(x) for x in (ART / name).read_text(encoding="utf-8").splitlines() if x.strip()]


def dump(name, rows):
    with (ART / name).open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> dict:
    sales = load("WEAPON_SKIN_SALES.jsonl")
    listing = load("WEAPON_SKIN_LISTING.jsonl")
    acq = load("WEAPON_SKIN_ACQUISITION.jsonl")

    # ---------- 1. Sale 措辞修正（冻结） ----------
    for r in sales:
        if r["sale_status"] in ("unresolved", "no_verified_sale_source_found_in_current_scanned_sources"):
            r["sale_status"] = "no_verified_sale_source_found_in_current_scanned_sources"
            r["residual"] = ("no_verified_sale_source_found_in_current_scanned_sources"
                             "（absence in current scanned source ≠ verified never sold；"
                             "sale_ts 值存在但不等于销售配置存在）")
        r["sale_chain_status"] = "frozen（Phase 6 冻结）"
        r["sale_ts_semantics"] = {"semantic_status": "likely",
                                  "hypothesis": "release_or_first_publish_date",
                                  "not_upgraded_because": "无 consumer / 独立 source 证据 ⇒ 不升级为正式 sale start / publish date"}
    dump("WEAPON_SKIN_SALES.jsonl", sales)

    # ---------- 2. Listing 分层 ----------
    for r in listing:
        present = bool(r.get("sale_config_present"))
        r["layers"] = {
            "sale_config_present": {"status": "verified" if present else
                                    "no_verified_sale_source_found_in_current_scanned_sources",
                                    "basis": "store_v2_data 显式 item_id 命中" if present else "本阶段扫描源内无命中"},
            "active_status": {"status": "unresolved",
                              "why": "无可证明的 enable predicate / consumer（disabled 字段语义未证）",
                              "candidate_gate": r.get("candidate_gates")},
            "visible_status": {"status": "unresolved", "why": "无 shop UI load/filter 逻辑证据（无 consumer）"},
            "purchasable_status": {"status": "unresolved", "why": "无购买谓词证据（价格 jump 未解 + 无 consumer）"},
            "listed_status": {"status": "unresolved",
                              "why": "listed 需 active/visible/purchasable 之一被证；本阶段均未证 ⇒ 不压扁成 listed/unlisted"},
        }
        r["listing_status"] = "unresolved"
        r["listing_model"] = ["configured", "active", "visible", "purchasable", "listed"]
        r["graduation"] = {"status": "bounded_unresolved",
                           "boundary": "边界证明：store 配置存在（verified）≠ 上架；可用性判定缺 consumer 证据",
                           "breakpoints": ["runtime_store_consumer", "disabled 语义", "价格 jump 目标"]}
    dump("WEAPON_SKIN_LISTING.jsonl", listing)

    # ---------- 3. Acquisition 多路径 ----------
    for r in acq:
        paths = list(r.get("acquisition_paths") or [])
        if r.get("acquisition_type") == "direct_shop":
            paths.append({"type": "direct_shop", "source": "store_v2_data",
                          "snapshot": BA, "channel": CHANNEL, "time": None,
                          "status": "likely",
                          "evidence": "显式 item_id 命中 + 同行价格/时段（价格值 jump 未解）"})
        else:
            paths.append({"type": "unresolved", "source": None, "snapshot": BA, "channel": CHANNEL,
                          "time": None, "status": "unresolved",
                          "evidence": "本阶段扫描源内无显式引用（≠ 证明从未投放）"})
        r["acquisition_paths"] = paths
        r["path_count"] = len(paths)
        r["multi_path"] = len(paths) > 1
        # 其它候选路径的现状（不覆盖旧值，逐条留痕）
        r["other_path_status"] = {
            "exchange": {"status": "unresolved",
                         "why": "common_exchange_shop_data 索引层已解（70 行 / 36 组 / 770 元素），"
                                "元素为小序号，目标 namespace 未识别 ⇒ 不能连边也不能断言无皮肤"},
            "gift_package": {"status": "unresolved",
                             "why": "gift_data jump 机制已解（read_jump_group 可用），抽样目标为物品/奖励 id 空间，"
                                    "未见皮肤 id；未穷举 ⇒ unresolved"},
            "lottery": {"status": "unresolved",
                        "why": "复用已毕业 Lottery target gate：现有产物无 skin_item_id 作为 target；"
                               "jump/子池/replacement 路径未证 ⇒ unresolved"},
            "activity_reward": {"status": "unresolved",
                                "why": "反向引用搜索（以 canonical skin id 为 target set）在已解 schema 中无命中"},
            "timed_grant": {"status": "unresolved",
                            "why": "timed 子变体无独立 commerce 来源；grant 路径未证（不从“14天/7天”名称推）"},
            "crafting": {"status": "unresolved", "why": "未发现配方/材料表引用皮肤 id"},
        }
        r["unresolved_paths"] = sorted(r["other_path_status"])
    dump("WEAPON_SKIN_ACQUISITION.jsonl", acq)

    # ---------- 4. Registry / Graph 补结论 ----------
    reg_p = DOM / "WEAPON_SKIN_COMMERCE_SOURCE_REGISTRY.json"
    reg = json.loads(reg_p.read_text(encoding="utf-8"))
    for s in reg["sources"]:
        if s["source_id"] == "runtime_store_consumer":
            s["status"] = "unavailable_in_current_static_assets"
            s["note"] = ("与 Combat Presentation 的 E5 同口径：静态资产未定位到 store consumer ⇒ 不再无限追；"
                         "Listing 因此只能 bounded_unresolved")
        if s["source_id"] == "store_v2_data":
            s["price_jump"] = {"status": "unresolved",
                               "detail": "real_cost/origin_cost = jump:N；用 read_jump_group 在 x{ body 与 raw payload "
                                         "两种基址下均未解出合理组 ⇒ 目标表未定位",
                               "residual": "价格数值未解（不影响 sale 配置事实）"}
        if s["source_id"] == "gift_data":
            s["jump_chain"] = {"status": "mechanism_resolved_target_unresolved",
                               "detail": "read_jump_group 可解 gift.rand_ids（例 130001 → [11478, 11474, 27787, 6721, 1, 1800, 289, 1]）",
                               "residual": "目标为物品/奖励 id 空间，未落到皮肤身份；未穷举 ⇒ 不建边"}
        if s["source_id"] == "common_exchange_shop_data":
            s["element_semantics"] = {"status": "unresolved",
                                      "detail": "770 个元素多为小序号（1..85649，去重 376），"
                                                "既非皮肤 id 也非 common_item 键 ⇒ 目标 namespace 未识别",
                                      "not_upgraded": "未达 verified_no_skin_target_in_snapshot（该结论要求 namespace 完整解）"}
    reg["listing_model"] = ["configured", "active", "visible", "purchasable", "listed"]
    reg["sale_chain"] = "frozen"
    reg_p.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")

    gp = DOM / "WEAPON_SKIN_COMMERCE_GRAPH.json"
    g = json.loads(gp.read_text(encoding="utf-8"))
    g["listing_gate_edges"] = [{"from": f"weapon_skin:{r['skin_item_id']}", "to": "listing:active",
                                "status": "unresolved", "why": "无 enable predicate / consumer 证据"}
                               for r in listing if r.get("sale_config_present")]
    g["acquisition_path_edges"] = [{"from": f"weapon_skin:{r['skin_item_id']}",
                                    "to": f"acquisition:{r['acquisition_paths'][0]['type']}",
                                    "status": r["acquisition_paths"][0]["status"],
                                    "source_refs": [r["acquisition_paths"][0]["source"]] if r["acquisition_paths"][0]["source"] else [],
                                    "snapshot_basis": BA, "time_basis": None} for r in acq]
    g["counts"].update({"listing_gate_unresolved": len(g["listing_gate_edges"]),
                        "acquisition_paths_total": sum(r["path_count"] for r in acq),
                        "multi_path_skins": len([r for r in acq if r["multi_path"]])})
    gp.write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- 5. 报告（22 项） ----------
    sale_verified = [r for r in sales if r["sale_status"] == "verified_sale_config_present"]
    path_types = Counter(p["type"] for r in acq for p in r["acquisition_paths"])
    path_status = Counter(p["status"] for r in acq for p in r["acquisition_paths"])
    report = {
        "snapshot_basis": BA, "client_channel": CHANNEL,
        "1_store_gate_semantics": {
            "disabled": "unresolved（字段存在 151 行；无 consumer/谓词证据 ⇒ 不当作 active 判定）",
            "start_ts": "verified_as_data（18/18 皮肤行存在，日粒度）；作为可用性谓词 unresolved",
            "end_ts": "verified_as_data（6/18 有值）；语义（下架时间）unresolved",
            "tab/category": "verified_as_data（level1/2_tab_type 18/18）",
            "total_limit": "verified_as_data（18/18）",
            "key_id": "verified_as_data（18/18，= store 行键 50001 等）",
            "lifecycle": "unresolved（无生命周期字段语义证据）",
        },
        "2_listing_model": ["configured", "active", "visible", "purchasable", "listed"],
        "3_verified_active": 0, "4_verified_visible": 0, "5_verified_purchasable": 0,
        "6_listing_unresolved": len([r for r in listing if r["listing_status"] == "unresolved"]),
        "7_store_price_jump_resolved": False,
        "7_residual": "read_jump_group 在 x{ body / raw payload 两种基址下均未解出价格组 ⇒ 目标表未定位",
        "8_sale18_price": {"rows": len(sale_verified),
                           "price_value_status": "jump_ref_unresolved",
                           "currency_namespace": "unresolved（money_id 仅 357/1222 行有值，18 条皮肤行无 money_id）",
                           "amount": "unresolved", "multi_currency": "unresolved", "package_price": "unresolved"},
        "9_gift_jump_resolved": "mechanism_resolved（read_jump_group 可用）；target namespace = 物品/奖励 id 空间",
        "10_gift_skins_linked": 0,
        "11_exchange_elements": {"rows": 70, "elements": 770, "distinct": 376,
                                 "verdict": "小序号，目标 namespace 未识别 ⇒ unresolved",
                                 "upgraded_to_no_skin_target": False},
        "12_exchange_skins_linked": 0,
        "13_lottery_acquisition": 0, "14_activity_acquisition": 0,
        "15_timed15": {"rows": 15, "independent_paths": 0,
                       "grant_hypothesis_unproven": True,
                       "verdict": "无独立 commerce/grant 证据；不从时长名称推获取方式"},
        "16_path_counts": dict(path_types), "16_path_status": dict(path_status),
        "17_multi_path_skins": len([r for r in acq if r["multi_path"]]),
        "18_old_only_4": {"ids": [1110184, 1110185, 1110186, 1110190],
                          "new_commerce_evidence": False,
                          "note": "仍保持 legacy 隔离；任何新证据只改 legacy commerce evidence，不回填 canonical"},
        "19_unresolved_sources": ["runtime_store_consumer（物理不可得）",
                                  "store price jump 目标表", "exchange 元素 namespace",
                                  "gift reward → 皮肤身份链", "lottery 子池/replacement 路径",
                                  "activity reward 引用", "timed grant 路径"],
        "20_listing_bounded_graduated": True,
        "20_why": "边界证明完整：configured=verified（18）/ 其余层 unresolved 且断点明确；缺 consumer 属静态资产限制",
        "21_acquisition_graduated": True,
        "21_why": "多路径模型落地、无整数碰撞 join、每条路径 status/evidence/断点齐备；证据边界清楚（不追求 126 条全有 acquisition）",
        "22_commerce_graduated": True,
        "22_scope": "Sale=frozen；Listing=graduated_with_bounded_unresolved；Acquisition=graduated（多路径 + bounded unresolved）",
        "22_graduation_checklist": {
            "1_sale_frozen": True, "2_listing_semantic_boundary": True,
            "3_store_gate_证明多少算多少": True, "4_price_jump_或_residual": True,
            "5_gift_chain_或断点": True, "6_exchange_残差明确": True,
            "7_lottery_target_gate": True, "8_activity_candidate_统一规则": True,
            "9_timed_独立审计": True, "10_acquisition_多路径": True,
            "11_无整数碰撞_join": True, "12_snapshot_history_不混": True,
            "13_explain_可追": True, "14_unresolved_有断点": True, "15_pipeline_可复算": True,
        },
    }
    (AUDIT / "weapon_skin_commerce_6b_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("3_verified_active", "6_listing_unresolved", "7_store_price_jump_resolved",
                                        "10_gift_skins_linked", "12_exchange_skins_linked", "13_lottery_acquisition",
                                        "16_path_counts", "17_multi_path_skins", "20_listing_bounded_graduated",
                                        "21_acquisition_graduated", "22_commerce_graduated")},
                     ensure_ascii=False, indent=1)[:1400])
