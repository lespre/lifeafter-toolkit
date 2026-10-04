"""武器皮肤 canonical 状态字段 v0.2（listing_status / name_status）。

背景（问题 1）：
- 旧 active artifact（v0.1）**没有**任何上架状态字段；Workbench 投影却硬编码 `release_state="static"`，
  导致 board.html 的「全部上架状态」筛选只有 1 个选项 → 被 fill() 隐藏（筛选看起来"没生效"）。
- 证据侧（RULES.json#acquisition_sources）已明确记录：同快照 `sale / shop / exchange` 全 = absent，
  "获取来源未闭环 != 核心 business key 未闭环；不得为凑全而猜"。

本工具**不重新调查定位链**，只做字段规范化：
1. 新增 canonical `listing_status` ∈ {verified_listed, verified_unlisted, unresolved}
   —— 现状：无同快照上架/商城证据 ⇒ 全部 `unresolved`（不伪造分类）。
2. 固化 `name_status` ∈ {verified, unresolved, unsafe}
   —— verified 必须同时具备 `name_evidence_type == verified_runtime_ui_lookup`；仅有字符串不算 verified。
3. `sale_ts` 保留为**时间戳字段**（`sale_ts_role = timestamp_only_not_listing_status`），不得当上架状态。
4. 归档 v0.1 → artifacts/historical/weapon_skin/v01/（只复制，不删）。
5. 产出 STATUS_VOCAB.json（当前到底支持哪几类）+ 更新 MANIFEST / RULES / audit（hash 锁）。
"""
from __future__ import annotations

import datetime
import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ACTIVE = REPO / "artifacts" / "active" / "weapon_skin"
HIST = REPO / "artifacts" / "historical" / "weapon_skin" / "v01"
TARGET = ACTIVE / "WEAPON_SKIN_RESOLVED.jsonl"

LISTING_CLASSES = {
    "verified_listed": "需同快照商城/上架配置（sale/shop）+ runtime 消费链证据；当前不存在",
    "verified_unlisted": "需同快照未上架/下架证据；当前不存在",
    "unresolved": "证据不足：同快照无 sale/shop/exchange 获取来源证据",
}
NAME_CLASSES = {
    "verified": "同快照 common_item_data_base 名称槽可回放，且 name_evidence_type = verified_runtime_ui_lookup",
    "unresolved": "无同快照主数据行或名称槽不可回放（不得用 SFX/模型路径/all_equips/oversea 补名）",
    "unsafe": "存在字符串但来源槽位错位/未证（禁止当作正式名，禁止计入 verified）",
}
FORBIDDEN_ALIASES = ["sale_status", "shop_status", "acquisition_status", "publication_status", "available", "unknown"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not TARGET.exists():
        print("FAIL: active artifact 不存在")
        return 1
    raw = TARGET.read_text(encoding="utf-8")
    rows = [json.loads(l) for l in raw.splitlines() if l.strip()]

    # 1) 归档 v0.1（只复制）
    HIST.mkdir(parents=True, exist_ok=True)
    for name in ("WEAPON_SKIN_RESOLVED.jsonl", "RULES.json", "audit.json", "MANIFEST.json"):
        src = ACTIVE / name
        if src.exists() and not (HIST / name).exists():
            shutil.copy2(src, HIST / name)
    print(f"已归档 v0.1 → {HIST.relative_to(REPO)}")

    # 2) 逐行规范化
    listing_counts = {"verified_listed": 0, "verified_unlisted": 0, "unresolved": 0}
    name_counts = {"verified": 0, "unresolved": 0, "unsafe": 0}
    out = []
    for row in rows:
        r = dict(row)
        # --- listing_status（无证据 ⇒ unresolved；禁止由 sale_ts 推）---
        r["listing_status"] = "unresolved"
        r["listing_evidence"] = {
            "state": "absent",
            "sources_checked": ["sale", "shop", "exchange"],
            "basis": "artifacts/active/weapon_skin/RULES.json#business_identity.acquisition_sources",
            "rule": "无同快照上架/商城配置证据 ⇒ unresolved；禁止用 sale_ts 是否存在或时间比较伪造已上架状态",
        }
        listing_counts[r["listing_status"]] += 1
        # --- sale_ts 只是时间戳 ---
        if r.get("sale_ts") is not None:
            r["sale_ts_role"] = "timestamp_only_not_listing_status"
        # --- name_status 三值规范化（有字符串 ≠ verified）---
        ns = r.get("name_status") or "unresolved"
        et = r.get("name_evidence_type")
        if ns == "verified" and et != "verified_runtime_ui_lookup":
            ns = "unsafe" if str(r.get("name") or "").strip() else "unresolved"
        elif ns not in NAME_CLASSES:
            ns = "unresolved"
        r["name_status"] = ns
        name_counts[ns] += 1
        out.append(r)

    supported_listing = [k for k, v in listing_counts.items() if v]
    # 3) 写回 active（v0.2）
    TARGET.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n", encoding="utf-8")

    vocab = {
        "domain": "weapon_skin",
        "version": "v0.2",
        "generated": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "listing_status": {
            "canonical_field": "listing_status",
            "classes": LISTING_CLASSES,
            "supported_today": supported_listing,
            "counts": listing_counts,
            "evidence_state": {"sale": "absent", "shop": "absent", "exchange": "absent",
                               "source": "artifacts/active/weapon_skin/RULES.json#business_identity.acquisition_sources",
                               "note": "获取来源未闭环；不得为凑全而猜"},
            "forbidden_aliases": FORBIDDEN_ALIASES,
            "not_listing_fields": {
                "sale_ts": "上架时间戳（字段值本身）；存在/大小都不构成'已上架'结论",
                "release_state": "旧板（data/boards/*）派生分类 on_sale/upcoming/no_sale_field/behavior_only；"
                                 "仅为 legacy 显示保留，不是本 canonical 字段，不得写回 active",
            },
            "how_to_upgrade": "补齐同快照商城/上架配置（sale/shop）+ runtime 消费链后可升级为 verified_listed/unlisted；本轮不调查",
        },
        "name_status": {"canonical_field": "name_status", "classes": NAME_CLASSES, "counts": name_counts,
                        "rule": "有字符串 ≠ verified；verified 必须 name_evidence_type = verified_runtime_ui_lookup"},
    }
    (ACTIVE / "STATUS_VOCAB.json").write_text(json.dumps(vocab, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # 4) RULES / audit 更新
    rules = json.loads((ACTIVE / "RULES.json").read_text(encoding="utf-8"))
    rules["version"] = "v0.2"
    rules["listing_status"] = {"canonical_field": "listing_status", "supported_today": supported_listing,
                               "counts": listing_counts, "forbidden_aliases": FORBIDDEN_ALIASES,
                               "not_listing_fields": ["sale_ts", "release_state(legacy board only)"],
                               "rule": "无同快照上架/商城证据 ⇒ unresolved；禁止伪造分类"}
    rules["name_status"] = {"canonical_field": "name_status", "classes": list(NAME_CLASSES), "counts": name_counts,
                            "rule": "verified 必须 name_evidence_type=verified_runtime_ui_lookup；有字符串 ≠ verified"}
    (ACTIVE / "RULES.json").write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = json.loads((ACTIVE / "audit.json").read_text(encoding="utf-8"))
    audit["version"] = "v0.2"
    audit["status_vocab"] = {"listing_status": listing_counts, "name_status": name_counts,
                             "supported_listing_classes": supported_listing,
                             "listing_evidence_state": "absent（sale/shop/exchange）"}
    audit["v02_change"] = ("新增 canonical listing_status（全部 unresolved，不伪造）+ sale_ts_role；"
                           "name_status 三值规范化（verified/unresolved/unsafe）；v0.1 归档 historical/weapon_skin/v01")
    (ACTIVE / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 5) MANIFEST 锁
    man = json.loads((ACTIVE / "MANIFEST.json").read_text(encoding="utf-8"))
    man["generated"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    man["version"] = "v0.2"
    man["files"] = {
        "resolved": {"from": "artifacts/historical/weapon_skin/v01/WEAPON_SKIN_RESOLVED.jsonl（v0.1）",
                     "to": "artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl",
                     "sha256": sha256(TARGET), "bytes": TARGET.stat().st_size},
        "rules": {"from": "artifacts/active/weapon_skin/RULES.json",
                  "to": "artifacts/active/weapon_skin/RULES.json",
                  "sha256": sha256(ACTIVE / "RULES.json"), "bytes": (ACTIVE / "RULES.json").stat().st_size},
        "audit": {"from": "artifacts/active/weapon_skin/audit.json",
                  "to": "artifacts/active/weapon_skin/audit.json",
                  "sha256": sha256(ACTIVE / "audit.json"), "bytes": (ACTIVE / "audit.json").stat().st_size},
        "status_vocab": {"from": "artifacts/active/weapon_skin/STATUS_VOCAB.json",
                         "to": "artifacts/active/weapon_skin/STATUS_VOCAB.json",
                         "sha256": sha256(ACTIVE / "STATUS_VOCAB.json"),
                         "bytes": (ACTIVE / "STATUS_VOCAB.json").stat().st_size},
    }
    man["canonical_fields"] = {"listing_status": supported_listing, "name_status": list(NAME_CLASSES)}
    (ACTIVE / "MANIFEST.json").write_text(json.dumps(man, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # 6) residual 侧登记（数据覆盖 residual，保留不追）
    res = REPO / "residuals" / "weapon_skin" / "listing_status.json"
    res.write_text(json.dumps({
        "domain": "weapon_skin", "kind": "listing_status_evidence",
        "generated": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "count": listing_counts["unresolved"], "supported_today": supported_listing,
        "reason": "同快照无 sale/shop/exchange 获取来源证据（task 现场：RULES#acquisition_sources=absent）",
        "tried_routes": ["现有 active artifact 字段族（仅 sale_ts 时间戳，无上架标记）",
                         "RULES/audit 已记录的 acquisition_sources 探测结果"],
        "rejected_routes": ["用 sale_ts 存在或与当前时间比较推'已上架'",
                            "沿用旧板 data/boards 的 release_state（on_sale/upcoming/…）作为 canonical 结论"],
        "current_gap": "同快照商城/上架配置表 + runtime 消费链（需新调查 ⇒ 本轮不做）",
        "hard_blocked": False,
        "evidence_ref": ["artifacts/active/weapon_skin/STATUS_VOCAB.json", "artifacts/active/weapon_skin/RULES.json"],
        "note": "unresolved 是正式数据层；不得为筛选好看补分类",
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(json.dumps({"rows": len(out), "listing_status": listing_counts, "name_status": name_counts,
                      "supported_listing_classes": supported_listing,
                      "artifact_sha": sha256(TARGET)[:16]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
