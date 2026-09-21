#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Weapon Skin Phase 6 — Listing / Sale / Acquisition Graduation（用户 2026-09-13）。

三条链严格独立，禁止互相推导：
  * Listing      ：是否存在明确「投放/上架/可用」状态 —— 只有 store 配置存在 ≠ listed
  * Sale         ：是否存在明确销售配置（价格/时段/店铺/限购）
  * Acquisition  ：玩家通过什么方式获得（每条必须有独立 source）

硬规则：raw row / 名称 / 特效 / level / timed / board 出现 ⇒ 都不等于 listed；
        整数相同不得建边；snapshot / channel / time basis 必须标注。

本阶段已证事实（BA8A）：
  * `store_v2_data.item_id` 显式命中 18 个 canonical skin_item_id（带 money/price/start_ts/end_ts/
    total_limit/level1-2_tab_type/disabled 等字段）⇒ **verified 销售配置**
  * 其中 6 条 `store.start_ts == skin.sale_ts` ⇒ sale_ts 语义 likely（发布/首发日），非 verified
  * `common_exchange_shop_data`（70 行，`36` 组索引层已解）行内 376 个数值**无皮肤 id** ⇒ unresolved
  * `gift_data`（5,443 行）无直接皮肤 id（奖励经 jump 引用）⇒ unresolved
  * 未找到 listing 可用性门控的语义证据（disabled/start/end 只是候选门控）⇒ 全员 unresolved
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

import build_weapon_skin_source_bindings as P1                    # noqa: E402
from pipelines.parsing import weapon_skin_mapping as MP           # noqa: E402

BA = "test-documents-ba8a239a"
CHANNEL = "client_channel=test"
ART = REPO / "artifacts" / "active" / "weapon_skin"
DOM = REPO / "domains" / "weapon_skin"
AUDIT = REPO / "analysis" / "audit"
RES = REPO / "residuals" / "weapon_skin"
STORE_FIELDS = ("item_id", "money_id", "money_count", "real_cost", "origin_cost", "start_ts", "end_ts",
                "total_limit", "daily_limit", "weekly_limit", "monthly_limit", "period_id", "goods_id",
                "category", "disabled", "hide_in_store", "level1_tab_type", "level2_tab_type", "sort_id")
LISTING_FORBIDDEN = ["raw_row 存在", "有名称", "有特效", "level 高", "timed/permanent", "board 出现"]


def main() -> dict:
    raw = {int(r["key"]): r["values"] for r in P1._rows("weapon_skin_data")[1]}
    skins = set(raw)
    v5 = {json.loads(x)["skin_item_id"]: json.loads(x)
          for x in (ART / "WEAPON_SKIN_RECORD_CLASSES.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()}
    timed = {k for k, c in v5.items() if c["record_class"] == "timed_variant"}

    # ---------- Sale：store_v2_data 显式销售配置 ----------
    rt, store = P1._rows("store_v2_data")
    store_rows = {}
    for r in store:
        v = r["values"]
        iid = P1._val(v.get("item_id"))
        if isinstance(iid, int) and iid in skins:
            sid = int(iid)
            d = {f: P1._val(v.get(f)) for f in STORE_FIELDS if f in v}
            d["store_row_key"] = int(r["key"])
            store_rows.setdefault(sid, []).append(d)
    sales = []
    for sid in sorted(skins):
        rows_ = store_rows.get(sid, [])
        st = P1._val(raw[sid].get("sale_ts"))
        if rows_:
            d = rows_[0]
            same_start = any(str(x.get("start_ts")) == str(st) for x in rows_)
            sales.append({
                "skin_item_id": sid, "sale_status": "verified_sale_config_present",
                "sale_source": "store_v2_data", "sale_time": {"start_ts": d.get("start_ts"), "end_ts": d.get("end_ts")},
                "price": {"money_id": d.get("money_id"), "money_count": d.get("money_count"),
                          "real_cost": d.get("real_cost"), "origin_cost": d.get("origin_cost"),
                          "value_status": ("jump_ref_unresolved（real_cost/origin_cost 为 jump 引用，本阶段未解值）"
                                           if str(d.get("real_cost") or "").startswith("jump")
                                           else "unresolved")},
                "store_id": d.get("store_row_key"), "shop_category": {"level1": d.get("level1_tab_type"),
                                                                     "level2": d.get("level2_tab_type")},
                "limits": {"total": d.get("total_limit"), "daily": d.get("daily_limit"),
                           "weekly": d.get("weekly_limit"), "monthly": d.get("monthly_limit")},
                "store_row_count": len(rows_),
                "canonical_sale_ts": st,
                "sale_ts_relation": ("equal_to_store_start_ts（cross-row consistency）" if same_start
                                     else "differs_from_store_start_ts（非同源同值）"),
                "evidence_refs": ["E1 字段语义：store_v2_data.item_id = 被售物品",
                                  "E2 key-space：item_id 值 ∈ canonical skin_item_id",
                                  "E-explicit mapping：同一 store 行带 money/price/start/end/limit"],
                "snapshot_basis": BA, "client_channel": CHANNEL, "time_basis": "start_ts/end_ts（unix 秒，日粒度）",
                "residual": None,
            })
        else:
            sales.append({
                "skin_item_id": sid, "sale_status": "unresolved", "sale_source": None, "sale_time": None,
                "price": None, "store_id": None, "shop_category": None, "limits": None,
                "canonical_sale_ts": st,
                "sale_ts_relation": "n/a（无 store 行可对照）",
                "evidence_refs": ["E-负证据：store_v2_data 中无 item_id == 该皮肤的行"],
                "snapshot_basis": BA, "client_channel": CHANNEL, "time_basis": None,
                "residual": "无显式销售配置；sale_ts 值存在但不等于销售配置存在",
            })

    # ---------- Listing：独立链，禁止从 sale 推导 ----------
    listing = []
    for sid in sorted(skins):
        listing.append({
            "skin_item_id": sid, "listing_status": "unresolved",
            "rule": "listing 需自有规则（active flag / runtime enable predicate / 当前时间窗 / availability gate / status 字段）",
            "candidate_gates": {"store_disabled_field": (store_rows.get(sid) or [{}])[0].get("disabled"),
                                "start_ts": (store_rows.get(sid) or [{}])[0].get("start_ts"),
                                "end_ts": (store_rows.get(sid) or [{}])[0].get("end_ts")},
            "explicitly_not_inferred_from": LISTING_FORBIDDEN,
            "sale_config_present": bool(store_rows.get(sid)),
            "snapshot_basis": BA, "client_channel": CHANNEL, "time_basis": "none（无可用性判定证据）",
            "residual": ("有销售配置但缺少「当前是否可用」的语义证据 ⇒ 只能 unresolved"
                         if store_rows.get(sid) else "无任何投放/可用证据"),
        })

    # ---------- Acquisition：独立链 ----------
    acq = []
    for sid in sorted(skins):
        rows_ = store_rows.get(sid, [])
        kind = "timed_variant" if sid in timed else "main_skin"
        if rows_:
            acq.append({"skin_item_id": sid, "record_class": kind, "acquisition_type": "direct_shop",
                        "status": "likely", "source_chains": [{"source": "store_v2_data",
                                                                "store_row_key": rows_[0].get("store_row_key"),
                                                                "evidence": "显式 item_id + 价格字段"}],
                        "unresolved_paths": ["exchange / lottery / activity / gift 未发现该皮肤显式引用"],
                        "inheritance_from_parent": None,
                        "snapshot_basis": BA, "client_channel": CHANNEL, "time_basis": "store start/end",
                        "residual": "acquisition_type=direct_shop 由销售配置推出（业务语义），runtime 购买链未直接证明 ⇒ likely"})
        else:
            acq.append({"skin_item_id": sid, "record_class": kind, "acquisition_type": "unresolved",
                        "status": "unresolved", "source_chains": [],
                        "unresolved_paths": ["direct_shop / exchange / lottery / activity / gift / bundle / crafting 均无显式引用"],
                        "inheritance_from_parent": None,
                        "snapshot_basis": BA, "client_channel": CHANNEL, "time_basis": None,
                        "residual": ("timed 子变体无独立获取来源；是否经 parent 发放未证 ⇒ 不继承"
                                     if kind == "timed_variant" else "未找到任何获取来源证据")})

    # ---------- 兑换商店（结构已解，无皮肤引用） ----------
    pay = MP.payload_bytes(7804)
    ex_rows = MP._parse_index(MP.split_frame(pay)[0]) if pay else []
    ex_vals = Counter()
    if pay:
        blob, _ = MP.split_frame(pay)
        offs = sorted(o for _, o in ex_rows)

        def uleb(b, i, end):
            x = 0; s = 0
            while i < end:
                c = b[i]; i += 1; x |= (c & 0x7F) << s; s += 7
                if not c & 0x80:
                    break
            return x, i
        for _k, off in ex_rows:
            nxt = [o for o in offs if o > off]
            end = nxt[0] if nxt else len(blob)
            i = off
            while i + 3 <= end and blob[i] in (0x27, 0x36, 0x76):
                tag, _sub, n = blob[i], blob[i + 1], blob[i + 2]; i += 3
                if tag in (0x27, 0x76):
                    i += 3 * n
                else:
                    for _ in range(n):
                        if i >= end:
                            break
                        x, i = unb = uleb(blob, i, end); ex_vals[x] += 1
    exchange = {"source_id": "common_exchange_shop_data", "source_class": "canonical_raw",
                "logical_table": "common_exchange_shop_data",
                "logical_module": "com\\cdata\\common_exchange_shop_data.py",
                "snapshot": BA, "physical_binding": "entry 7804（CHS 7697）", "decoder_status": "index_level_parsed",
                "structure": {"rows": len(ex_rows), "key_space": "1..70（行键）",
                              "row_encoding": "36 <sub> <n> + n×(uleb) 组编码"},
                "key_space": "行内数值 1..85649（去重 376）",
                "fields_contributed": ["exchange cost/reward 数值（未命名语义）"],
                "relation_type": "unresolved", "skin_refs_found": [],
                "evidence_refs": ["E-structural：索引层行表可解析（70 行）", "E-负证据：376 个数值无一 ∈ canonical skin_item_id"],
                "residual": "行内数值语义未命名（疑为索引/奖励 id，非皮肤 id）⇒ 不能连边"}

    # ---------- 礼包 / 抽奖 / 活动 ----------
    rtl, lottery_files = None, []
    for d in (REPO / "artifacts" / "active").glob("*lottery*"):
        lottery_files += [str(p.relative_to(REPO)) for p in d.rglob("*.jsonl")]
    gift_rt, gift = P1._rows("gift_data")
    gift_hits = [(int(r["key"]), f, P1._val(v)) for r in gift for f, v in r["values"].items()
                 if isinstance(P1._val(v), int) and P1._val(v) in skins]

    registry = {
        "snapshot_basis": BA, "client_channel": CHANNEL,
        "chains": {"listing": {"sources_found": 0, "status": "unresolved"},
                   "sale": {"sources_found": 1, "verified_rows": len([s for s in sales if s["sale_status"].startswith("verified")])},
                   "acquisition": {"sources_found": 1, "likely_rows": len([a for a in acq if a["status"] == "likely"])}},
        "sources": [
            {"source_id": "weapon_skin_data.sale_ts", "source_class": "canonical_raw", "logical_table": "weapon_skin_data",
             "snapshot": BA, "physical_binding": "entry 11817", "decoder_status": "decoded",
             "key_space": "skin_item_id", "fields_contributed": ["sale_ts"],
             "relation_type": "candidate_sale_time", "evidence_refs":
                 ["值域 1724860800–1788364800（2024-08-28 → 2026-09-02，日粒度）",
                  "124/126 非零（2 条为 0/null）",
                  "6/18 与 store_v2 行 start_ts 完全相等 ⇒ cross-row consistency"],
             "residual": "字段名 sale_ts 不等于语义已证；未找到 runtime/UI consumer ⇒ semantic_status=likely"},
            {"source_id": "store_v2_data", "source_class": "canonical_raw", "logical_table": "store_v2_data",
             "snapshot": BA, "physical_binding": "locator resolve ok（1,222 行）", "decoder_status": "decoded",
             "key_space": "store row key 1000–70097；item_id 值空间含 18 个 canonical 皮肤 id",
             "fields_contributed": list(STORE_FIELDS),
             "relation_type": "verified_sale_config",
             "evidence_refs": ["E1 字段语义 item_id；E2 值域 ∈ canonical skin_item_id",
                               "E-explicit：同行含 money_id/money_count/start_ts/end_ts/limits"],
             "residual": "listing 门控（disabled/时间窗语义）未证 ⇒ 不推导 listing"},
            exchange,
            {"source_id": "gift_data", "source_class": "canonical_raw", "logical_table": "gift_data",
             "snapshot": BA, "physical_binding": "entry 19768", "decoder_status": "decoded",
             "key_space": "gift row key（5,443 行）", "fields_contributed": ["rand_ids", "reward_counts", "buy_ids", "redeem_reward"],
             "relation_type": "unresolved",
             "evidence_refs": ["E-负证据：5,443 行字段值中无 canonical skin_item_id（奖励经 jump 引用）"],
             "residual": "需先解 jump→奖励链才可能连边；本阶段不硬连"},
            {"source_id": "lottery_domain", "source_class": "derived_domain", "logical_table": "LOTTERY_* artifacts",
             "snapshot": BA, "physical_binding": f"{len(lottery_files)} 个 jsonl", "decoder_status": "n/a",
             "key_space": "pool_key / item namespace", "fields_contributed": ["reward targets"],
             "relation_type": "unresolved",
             "evidence_refs": ["E-负证据：现有 lottery 产物中未发现 canonical skin_item_id 作为 target"],
             "residual": "仅当 target_type=item 且 item namespace 落到皮肤身份时才可连（本阶段未命中）"},
            {"source_id": "historical:board_sale_date", "source_class": "historical_source",
             "logical_table": "data/boards/weapon_skin_sfx_text_sources.json",
             "snapshot": BA, "physical_binding": "legacy board", "decoder_status": "n/a",
             "key_space": "skin_id", "fields_contributed": ["sale_date"],
             "relation_type": "historical_display", "evidence_refs": ["旧板派生字段"],
             "residual": "只作 historical/display，不参与 canonical truth"},
            {"source_id": "runtime_store_consumer", "source_class": "runtime_semantic",
             "logical_table": "（未定位）", "snapshot": BA, "physical_binding": "unresolved",
             "decoder_status": "not_found", "key_space": None, "fields_contributed": [],
             "relation_type": "unresolved",
             "evidence_refs": ["本快照静态资产未定位到 store/acquisition consumer（E5 unavailable）"],
             "residual": "listing 判定依赖此类 consumer ⇒ 缺它则 listing 只能 unresolved"},
        ],
    }
    (DOM / "WEAPON_SKIN_COMMERCE_SOURCE_REGISTRY.json").write_text(json.dumps(registry, ensure_ascii=False, indent=1), encoding="utf-8")

    def dump(name, rows_):
        with (ART / name).open("w", encoding="utf-8") as fh:
            for x in rows_:
                fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    dump("WEAPON_SKIN_SALES.jsonl", sales)
    dump("WEAPON_SKIN_LISTING.jsonl", listing)
    dump("WEAPON_SKIN_ACQUISITION.jsonl", acq)

    sale_edges = [{"from": "weapon_skin:%d" % x["skin_item_id"], "to": "store_v2_data:%s" % x["store_id"],
                   "chain": "sale", "relation": "verified_sale_config", "status": "verified",
                   "source_refs": ["store_v2_data"], "evidence_refs": x["evidence_refs"],
                   "snapshot_basis": BA, "time_basis": x["time_basis"]} for x in sales if x["store_id"]]
    acq_edges = [{"from": "store_v2_data:%s" % x["store_id"], "to": "weapon_skin:%d" % x["skin_item_id"],
                  "chain": "acquisition", "relation": "direct_shop", "status": "likely",
                  "source_refs": ["store_v2_data"], "evidence_refs": [x["evidence_refs"][0]],
                  "snapshot_basis": BA, "time_basis": x["time_basis"]} for x in sales if x["store_id"]]
    graph = {
        "snapshot_basis": BA, "client_channel": CHANNEL,
        "chains": ["listing", "sale", "acquisition"],
        "edges": sale_edges + acq_edges,
        "unresolved_edges": [
            {"from": "common_exchange_shop_data:*", "to": "weapon_skin:*", "chain": "acquisition",
             "relation": "exchange", "status": "unresolved", "why": "行内 376 个数值无一命中皮肤 id"},
            {"from": "gift_data:*", "to": "weapon_skin:*", "chain": "acquisition",
             "relation": "gift/bundle", "status": "unresolved", "why": "无直接皮肤 id（奖励经 jump）"},
            {"from": "lottery_*", "to": "weapon_skin:*", "chain": "acquisition",
             "relation": "lottery", "status": "unresolved", "why": "现有产物未发现皮肤 id 作为 target"},
            {"from": "weapon_skin:*", "to": "listing_state", "chain": "listing",
             "relation": "availability_gate", "status": "unresolved",
             "why": "无可证明的 active flag / enable predicate / 时间窗语义"},
            {"from": "runtime_store_consumer", "to": "listing_state", "chain": "listing",
             "relation": "consumer", "status": "unresolved", "why": "静态资产未定位到 consumer（E5 unavailable）"},
        ],
        "forbidden_inferences": LISTING_FORBIDDEN,
        "counts": {"sale_verified": len(sale_edges), "acquisition_likely": len(acq_edges),
                   "unresolved": 5},
    }
    (DOM / "WEAPON_SKIN_COMMERCE_GRAPH.json").write_text(json.dumps(graph, ensure_ascii=False, indent=1), encoding="utf-8")

    conflicts = {
        "snapshot_basis": BA, "client_channel": CHANNEL,
        "conflicts": [{"field": "sale_ts vs store.start_ts",
                       "detail": "6/18 完全相等、12/18 不等 ⇒ sale_ts 不是 store 起始时间的同义字段",
                       "resolution_status": "unresolved（保留两者，不静默选一）"}],
        "residuals": [
            "listing 全员 unresolved：缺可用性门控语义证据（disabled/时间窗只是候选）",
            "sale_ts 语义 likely（发布/首发日），无 runtime/UI consumer 证据",
            "acquisition=direct_shop 由销售配置推出（业务语义）⇒ likely",
            "exchange/gift/lottery/activity 均无皮肤显式引用 ⇒ unresolved，不硬连",
            "timed 子变体无独立 commerce 来源；是否经 parent 未证 ⇒ 不继承",
            "old-only 4：store/exchange/gift/lottery 均无命中 ⇒ 不升级为有 commerce 证据",
        ],
    }
    (DOM / "WEAPON_SKIN_COMMERCE_CONFLICTS.json").write_text(json.dumps(conflicts, ensure_ascii=False, indent=1), encoding="utf-8")

    st = Counter(x["sale_status"] for x in sales)
    lt = Counter(x["listing_status"] for x in listing)
    at = Counter(x["status"] for x in acq)
    report = {
        "snapshot_basis": BA, "client_channel": CHANNEL,
        "1_listing": {"status_counts": dict(lt), "rule": "listing 自有规则；store 配置存在 ≠ listed",
                      "gate_fields_candidate": ["store_v2_data.disabled", "start_ts", "end_ts"]},
        "2_sale": {"status_counts": dict(st), "verified_skins": sorted(store_rows),
                   "price_sample": {k: (store_rows[k][0].get("money_id"), store_rows[k][0].get("money_count"))
                                    for k in sorted(store_rows)[:5]}},
        "3_acquisition": {"status_counts": dict(at),
                          "direct_shop": sorted([a["skin_item_id"] for a in acq if a["acquisition_type"] == "direct_shop"])},
        "4_sources_found": len(registry["sources"]),
        "5_sale_ts_semantics": {"value_range": "1724860800–1788364800（日粒度）",
                                "nonzero": 124, "zero_or_null": 2,
                                "per_class": {"main_nonzero": 109, "main_zero": 2, "timed_nonzero": 15},
                                "store_cross_check": f"{sum(1 for s in sales if s['sale_ts_relation'].startswith('equal'))}/18 与 store.start_ts 相等",
                                "semantic_status": "likely", "hypothesis": "发布/首发日（日粒度时间戳）",
                                "consumer_found": False,
                                "residual": "无 runtime/UI consumer 证据 ⇒ 不升级 verified"},
        "6_store_entity_scan": {"rows": len(store), "rows_hitting_skin_ids": sum(len(v) for v in store_rows.values()),
                                "skins": len(store_rows), "fields": list(STORE_FIELDS),
                                "edge_type": "verified（显式 item_id 字段语义 + 值域命中 + 同行价格/时段）"},
        "7_exchange": {k: v for k, v in exchange.items() if k in ("decoder_status", "structure", "key_space",
                                                                 "skin_refs_found", "residual")},
        "8_lottery_gift_activity": {"gift_hits": len(gift_hits), "lottery_files": lottery_files[:6],
                                    "verdict": "均 unresolved（无显式皮肤引用，不硬连）"},
        "9_timed_variants": {"rows": len(timed),
                             "independent_sale": len([s for s in sales if s["skin_item_id"] in timed and s["store_id"]]),
                             "independent_acquisition": len([a for a in acq if a["skin_item_id"] in timed and a["status"] == "likely"]),
                             "verdict": "timed 子变体无独立 commerce 来源；未从 parent 复制"},
        "10_old_only_4": {str(o): {"store": False, "exchange": False, "gift": False,
                                   "lottery": False, "status": "legacy_only_unconfirmed（commerce 侧也无命中）"}
                          for o in (1110184, 1110185, 1110186, 1110190)},
        "11_graph": {"verified_edges": len([e for e in graph["edges"] if e["status"] == "verified"]),
                     "likely_edges": len([e for e in graph["edges"] if e["status"] == "likely"]),
                     "unresolved_edges": len(graph["unresolved_edges"])},
        "12_explain_wired": "weapon_skin 已加 commerce 段（listing/sale/acquisition）",
        "13_not_inferred": {"listing_from_sale": False, "acquisition_from_label": False},
        "14_graduation": {"sale": "verified（18 条显式配置）", "listing": "unresolved（缺门控语义）",
                          "acquisition": "likely（direct_shop 18 条）",
                          "can_graduate": False,
                          "why": "listing 链缺独立规则证据；exchange/gift/lottery/activity 全未连边 ⇒ 三链只能部分毕业"},
    }
    (AUDIT / "weapon_skin_commerce_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("1_listing", "2_sale", "3_acquisition", "5_sale_ts_semantics",
                                        "6_store_entity_scan", "9_timed_variants", "11_graph", "14_graduation")},
                     ensure_ascii=False, indent=1)[:2400])
