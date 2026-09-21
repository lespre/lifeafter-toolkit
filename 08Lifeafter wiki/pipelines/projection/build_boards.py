"""唯一 presentation projection 入口（Phase 3-5；v1.3 重新定位）。

数据流（单向，禁止回读 legacy）：
    artifacts/active → domain service → projection → Web Client（Wiki View / Workbench View）

v1.3 投影分两类：
    lightweight          首页 / 分类 / 统计 / 小 Domain —— 默认生成，体积小（KB 级）
    offline_full_projection  用户显式导出/离线时才生成完整数据（item 30k / lottery 23k 行，数十 MB）
                          标记 `web_default=false`，**不作为默认 Web 路径**（Web 默认走 API 分页）

产物：
    data/workbench_boards/<projection_id>.json + .js     （window.WIKI_BOARD_<id>，与旧板同格式）
    data/workbench_manifest.json + .js                   （含 profile / web_default / artifact hash）
    data/workbench_status.js                             （状态页兜底数据）

禁止：回读 data/boards/*.json、retired board、historical artifact。
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from services import FashionService, ItemService, LotteryService, StatusService, WeaponSkinService  # noqa: E402
from services.store import load_json  # noqa: E402

OUT_BOARDS = REPO / "data" / "workbench_boards"
MANIFEST_JSON = REPO / "data" / "workbench_manifest.json"
MANIFEST_JS = REPO / "data" / "workbench_manifest.js"
STATUS_JS = REPO / "data" / "workbench_status.js"
NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

LIGHTWEIGHT = "lightweight"
OFFLINE_FULL = "offline_full_projection"
# 默认不重新生成全量导出（几十 MB）；仅在 --offline-full/--export 或文件缺失时生成
OFFLINE_FULL_BOARDS = {"item_master_active", "lottery_pool_active", "lottery_rewards_active"}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def artifact_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_board(projection_id: str, payload: dict, entries: list, *, profile: str = LIGHTWEIGHT,
                web_default: bool = True) -> None:
    OUT_BOARDS.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=1)
    (OUT_BOARDS / f"{projection_id}.json").write_text(text + "\n", encoding="utf-8")
    (OUT_BOARDS / f"{projection_id}.js").write_text(f"window.WIKI_BOARD_{projection_id} = " + text + ";\n", encoding="utf-8")
    entries.append({
        "domain": payload["meta"]["domain"], "projection_id": projection_id,
        "source_artifact": payload["meta"]["source_artifact"], "artifact_hash": payload["meta"]["artifact_hash"],
        "generated_at": NOW, "status": payload["meta"]["status"], "row_count": len(payload.get("items") or []),
        "json": f"data/workbench_boards/{projection_id}.json", "js": f"data/workbench_boards/{projection_id}.js",
        "residual_ref": payload["meta"].get("residual_ref"),
        "profile": profile, "web_default": web_default,
        "web_default_note": ("Web 默认走 Workbench API 分页（/api/items、/api/lottery/*）；本投影仅离线/导出/兼容"
                             if not web_default else "静态投影可直接加载")})


def _offline_stub(projection_id: str, domain: str, source_artifact: str, rows: int, entries: list) -> None:
    """离线全量投影已存在于磁盘：只在 manifest 登记（不重新生成几十 MB 文件）。"""
    path = REPO / source_artifact
    js = OUT_BOARDS / f"{projection_id}.js"
    entries.append({
        "domain": domain, "projection_id": projection_id, "source_artifact": source_artifact,
        "artifact_hash": artifact_hash(path), "generated_at": NOW,
        "status": "offline_full_projection（未重新生成；用 --offline-full 刷新）",
        "row_count": rows, "json": f"data/workbench_boards/{projection_id}.json",
        "js": f"data/workbench_boards/{projection_id}.js", "residual_ref": None,
        "profile": OFFLINE_FULL, "web_default": False,
        "present": js.exists(),
        "web_default_note": "legacy/offline_full_projection：不作为默认 Web 路径（Web 默认 API 分页）"})


# ---------- lightweight 投影 ----------
def project_item_stats(entries: list) -> None:
    svc = ItemService()
    meta = {"name": "物品统计（lightweight）", "category": "一、道具总表 / （一）统计", "board_id": "item_stats",
            "domain": "item", "status": "active", "source_artifact": "artifacts/active/item/ITEM_MASTER.jsonl",
            "artifact_hash": artifact_hash(REPO / "artifacts" / "active" / "item" / "ITEM_MASTER.jsonl"),
            "generated": NOW, "evidence": "structure + runtime dispatch/consumer",
            "source_server": "test 客户端静态快照（server_branch unresolved）",
            "notes": "首页/分类/统计用；全量行请走 /api/items 分页"}
    write_board("item_stats", {"meta": meta, "stats": {"rows": svc.count(), **svc.facets()}, "items": []}, entries)


def project_lottery_stats(entries: list) -> None:
    svc = LotteryService()
    rows = svc.reward_targets_page(page_size=1)
    meta = {"name": "奖池统计（lightweight）", "category": "四、奖池 / （一）统计", "board_id": "lottery_stats",
            "domain": "lottery", "status": "active", "source_artifact": "artifacts/active/lottery/LOTTERY_POOL.jsonl",
            "artifact_hash": artifact_hash(REPO / "artifacts" / "active" / "lottery" / "LOTTERY_POOL.jsonl"),
            "generated": NOW, "evidence": "static", "source_server": "test 客户端静态快照（server_branch unresolved）",
            "notes": "池层与 target 层永不合并；全量行请走 /api/lottery/pools 与 /api/lottery/rewards"}
    write_board("lottery_stats", {"meta": meta,
                                  "stats": {"pool": svc.pool_stats(), "target_total": rows["total"],
                                            "target_facets": rows["facets"]}, "items": []}, entries)


# ---------- 离线全量投影（显式） ----------
def project_item(entries: list) -> None:
    svc = ItemService()
    items = []
    for row in svc._rows():  # noqa: SLF001
        items.append({"id": str(row["item_id"]), "item_id": row["item_id"], "name": row.get("name"),
                      "evidence": "verified" if row.get("business_identity") == "verified_runtime_business_key" else "unresolved",
                      "evidence_level": row.get("business_identity"), "source": f"ITEM_MASTER {row.get('item_namespace')}",
                      "item_namespace": row.get("item_namespace"), "runtime_module": row.get("runtime_module"),
                      "raw_table": row.get("raw_table"), "name_status": row.get("name_status"),
                      "raw_presence": row.get("raw_presence"), "status_tags": ["verified", row.get("item_namespace")],
                      "search_text": f"{row['item_id']} {row.get('name')} {row.get('item_namespace')}",
                      "provenance": {"source_id": "ITEM_MASTER_active", "table": row.get("raw_table"),
                                     "row_key": row.get("raw_row_key"), "snapshot_id": (row.get("provenance") or {}).get("snapshot"),
                                     "snapshot_basis": (row.get("provenance") or {}).get("identity_snapshot_basis"),
                                     "residuals": row.get("residuals")}})
    meta = {"name": "ITEM_MASTER（active · 统一业务物品索引 · 离线全量）", "category": "一、道具总表 / （一）ITEM_MASTER active",
            "board_id": "item_master_active", "domain": "item", "status": "active",
            "source_artifact": "artifacts/active/item/ITEM_MASTER.jsonl",
            "artifact_hash": artifact_hash(REPO / "artifacts" / "active" / "item" / "ITEM_MASTER.jsonl"),
            "generated": NOW, "residual_ref": "residuals/item/unresolved_namespace_ids.json",
            "package_sha": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
            "evidence": "structure + runtime dispatch/consumer", "notes": "offline_full_projection：默认 Web 路径为 /api/items 分页",
            "source_server": "test 客户端静态快照（server_branch unresolved）"}
    write_board("item_master_active", {"meta": meta, "stats": {"items": len(items), "namespaces": svc.namespaces()},
                                       "items": items}, entries, profile=OFFLINE_FULL, web_default=False)


def project_lottery(entries: list) -> None:
    svc = LotteryService()
    from services.store import cached_jsonl
    pool = svc._pool_rows()  # noqa: SLF001  （嵌套 schema 已归一）
    targets = list(cached_jsonl(str(svc._targets)))  # noqa: SLF001
    hash_pool = artifact_hash(svc._pool)  # noqa: SLF001
    hash_tgt = artifact_hash(svc._targets)  # noqa: SLF001
    items = []
    for row in pool:
        items.append({"id": row.get("record_id") or f"lpr01:{row.get('pool_key')}:{row.get('item_no')}",
                      "name": f"池 {row.get('pool_key')} · 槽位 {row.get('item_no')}", "evidence": "structure",
                      "evidence_level": row.get("static_config_state") or "static-config",
                      "source": f"LOTTERY_POOL active（{row.get('component')}）",
                      "pool_key": row.get("pool_key"), "item_no": row.get("item_no"),
                      "static_reward_raw": row.get("static_reward_raw"),
                      "component": row.get("component"), "reliability_state": row.get("reliability_state"),
                      "runtime_final_state": row.get("runtime_final_state"), "schema_ref": row.get("schema_ref"),
                      "status_tags": ["static", str(row.get("runtime_final_state"))],
                      "search_text": f"{row.get('pool_key')} {row.get('item_no')} {row.get('static_reward_raw')} pool",
                      "provenance": {"source_id": "LOTTERY_POOL_active", "dataset_partition": row.get("dataset_partition")}})
    meta = {"name": "奖池结构（active · LOTTERY_POOL · 离线全量）", "category": "四、奖池 / （一）LOTTERY_POOL active",
            "board_id": "lottery_pool_active", "domain": "lottery", "status": "active", "layer": "pool_structure",
            "source_artifact": "artifacts/active/lottery/LOTTERY_POOL.jsonl", "artifact_hash": hash_pool, "generated": NOW,
            "residual_ref": "residuals/lottery/replacement_overlay.json",
            "package_sha": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
            "evidence": "structure", "source_server": "test 客户端静态快照（server_branch unresolved）",
            "notes": "offline_full_projection：默认 Web 路径为 /api/lottery/pools 分页"}
    write_board("lottery_pool_active", {"meta": meta, "stats": svc.pool_stats(), "items": items}, entries,
                profile=OFFLINE_FULL, web_default=False)

    titems = []
    for row in targets:
        titems.append({"id": f"rt01:{row.get('pool_key')}:{row.get('item_no')}",
                       "name": f"池 {row.get('pool_key')} · 槽位 {row.get('item_no')}", "evidence": "static",
                       "evidence_level": row.get("target_identity_status"), "source": "LOTTERY_REWARD_TARGETS active",
                       "pool_key": row.get("pool_key"), "item_no": row.get("item_no"),
                       "static_reward_raw": row.get("static_reward_raw"), "reward_target_type": row.get("reward_target_type"),
                       "item_id": row.get("item_id"), "item_namespace": row.get("item_namespace"),
                       "target_identity_status": row.get("target_identity_status"),
                       "runtime_final_status": row.get("runtime_final_status"),
                       "status_tags": [row.get("reward_target_type") or "unknown"],
                       "search_text": f"{row.get('pool_key')} {row.get('item_no')} {row.get('reward_target_type')} {row.get('item_id')}",
                       "provenance": {"source_id": "LOTTERY_REWARD_TARGETS_active",
                                      "criterion": (row.get("evidence") or {}).get("runtime_resolution", {}).get("criterion")}})
    meta2 = {"name": "奖池奖励目标（active · 静态分类，runtime_final 未解析 · 离线全量）",
             "category": "四、奖池 / （二）LOTTERY_REWARD_TARGETS active", "board_id": "lottery_rewards_active",
             "domain": "lottery", "status": "active", "layer": "static_reward_target",
             "source_artifact": "artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl", "artifact_hash": hash_tgt,
             "generated": NOW, "residual_ref": ["residuals/lottery/unresolved_targets.json",
                                                "residuals/lottery/replacement_overlay.json"],
             "package_sha": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad", "evidence": "static",
             "source_server": "test 客户端静态快照（server_branch unresolved）",
             "notes": "offline_full_projection：默认 Web 路径为 /api/lottery/rewards 分页"}
    write_board("lottery_rewards_active", {"meta": meta2, "stats": {"items": len(titems), "by_type": svc.target_type_counts()},
                                           "items": titems}, entries, profile=OFFLINE_FULL, web_default=False)


# ---------- 小 Domain（轻量静态投影） ----------
def project_weapon_skin(entries: list) -> None:
    svc = WeaponSkinService()
    items = []
    for row in svc._rows():  # noqa: SLF001
        verified = row.get("runtime_row_binding") == "verified"
        sk = svc._as_skin(row)          # 含展示层（presentation_only：官方描述 / 特效名 / 历史参考 / 类型中文）
        items.append({**sk,
                      "id": str(row.get("skin_item_id") or row.get("skin_id")),
                      "skin_item_id": row.get("skin_item_id") or row.get("skin_id"),
                      "skin_id": row.get("skin_item_id") or row.get("skin_id"),
                      "name": row.get("name") or "（未解析）", "name_display": row.get("name"),
                      "name_status": row.get("name_status"), "name_resolution": row.get("name_binding"),
                      # 品级：canonical level/priority；旧中文 grade 为 board 派生（deprecated，仅 legacy 展示字段）
                      "level": row.get("level"), "priority": row.get("priority"),
                      "grade_status": row.get("grade_status"), "legacy_grade_label": row.get("legacy_grade_label"),
                      "weapon_type": row.get("weapon_type"),
                      "weapon_type_label": str(row.get("weapon_type")), "weapon_type_state": row.get("weapon_type_state"),
                      "sale_ts": row.get("sale_ts"), "sale_ts_role": row.get("sale_ts_role"),
                      # v1.3.1：上架状态用 canonical 字段（禁止硬编码 release_state="static"）
                      "listing_status": row.get("listing_status") or "unresolved",
                      "listing_status_label": {"verified_listed": "已上架（已核验）", "verified_unlisted": "未上架（已核验）",
                                               "unresolved": "未解析（证据不足）"}.get(row.get("listing_status") or "unresolved"),
                      "listing_evidence": row.get("listing_evidence"),
                      "evidence": "verified" if verified else "unresolved", "evidence_level": row.get("business_identity") or "unresolved",
                      "source": "WEAPON_SKIN_RESOLVED(active)", "variant_items": row.get("timed_variants") or [],
                      "variant_item_count": len(row.get("timed_variants") or []),
                      "status_tags": [row.get("listing_status") or "unresolved", row.get("name_status") or "unresolved"],
                      "search_text": f"{row.get('skin_item_id')} {row.get('name')}",
                      "field_provenance": {"source_chain": row.get("source_chain"), "name_evidence_type": row.get("name_evidence_type")},
                      "provenance": {"source_id": "WEAPON_SKIN_RESOLVED_active", "residuals": row.get("residuals")}})
    vocab = svc.status_vocab()
    meta = {"name": "武器皮肤（active·内部投影）", "category": "（内部·审计）武器皮肤 active 投影（非图鉴入口）", "board_id": "weapon_skin_active",
            "domain": "weapon_skin", "status": "internal",
            "note": "图鉴正式入口 = weapon_skin_sfx_text_sources（115，当前包 328b8446 基准）；本投影为 active 结构视图，仅供审计/交叉核对", "source_artifact": "artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl",
            "artifact_hash": artifact_hash(REPO / "artifacts" / "active" / "weapon_skin" / "WEAPON_SKIN_RESOLVED.jsonl"),
            "generated": NOW, "residual_ref": "residuals/weapon_skin/unresolved_ids.json",
            # canonical 状态词表（前端只显示，不做业务判断）
            "status_vocab": {"listing_status": {"supported_today": (vocab.get("listing_status") or {}).get("supported_today"),
                                                "counts": (vocab.get("listing_status") or {}).get("counts"),
                                                "classes": list(((vocab.get("listing_status") or {}).get("classes") or {}).keys()),
                                                "evidence_state": (vocab.get("listing_status") or {}).get("evidence_state")},
                             "name_status": {"classes": list(((vocab.get("name_status") or {}).get("classes") or {}).keys()),
                                             "counts": (vocab.get("name_status") or {}).get("counts")}},
            "package_sha": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad", "evidence": "runtime_ui_lookup",
            "source_server": "test 客户端静态快照（server_branch unresolved）"}
    write_board("weapon_skin_active", {"meta": meta, "stats": {"items": len(items)}, "items": items}, entries,
                profile="internal", web_default=False)


def project_fashion(entries: list) -> None:
    svc = FashionService()
    st = svc.status()
    items = [{"id": "fashion:verified_semantic", "name": "已证：appear_id → A2F → runtime_fashion_key → FASHION_DATA（语义链）",
              "evidence": "verified", "evidence_level": st["verified"]["status"], "source": "FASHION_IDENTITY_STATE(active)",
              "status_tags": ["verified"], "detail": st["verified"]["consumer_chain"]}]
    for k, v in (st["unresolved"] or {}).items():
        items.append({"id": f"fashion:unresolved:{k}", "name": f"未证：{k}", "evidence": "unresolved",
                      "evidence_level": "unresolved", "source": "FASHION_IDENTITY_STATE(active)",
                      "status_tags": ["unresolved"], "detail": v})
    meta = {"name": "时装身份状态（active · 不生成 resolved 主表）", "category": "二、时装类 / （一）时装身份状态（active）",
            "board_id": "fashion_active", "domain": "fashion", "status": "active_state_only",
            "source_artifact": "artifacts/active/fashion/FASHION_IDENTITY_STATE.json",
            "artifact_hash": artifact_hash(REPO / "artifacts" / "active" / "fashion" / "FASHION_IDENTITY_STATE.json"),
            "generated": NOW, "residual_ref": "residuals/fashion/binding_residuals.json",
            "package_sha": "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad", "evidence": "mixed",
            "source_server": "test 客户端静态快照（server_branch unresolved）",
            "notes": "31,112 条 unresolved candidates 不在本投影中，避免冒充 resolved 时装目录"}
    write_board("fashion_active", {"meta": meta, "stats": {"items": len(items)}, "items": items}, entries)


def write_status() -> dict:
    st = StatusService()
    regression = load_json(REPO / "state" / "REGRESSION.json") if (REPO / "state" / "REGRESSION.json").exists() else None
    web = load_json(REPO / "registry" / "web_client.json")
    payload = {"generated": NOW, "workbench_version": "v1.3",
               "chains": st.chains()["chains"], "residual_manifest": st.residual_manifest(),
               "status": st.status(), "regression": regression,
               "web_client": {"api_first_boards": list((web.get("api_first_boards") or {}).keys()),
                              "offline_full_projection": web.get("offline_full_projection"),
                              "view_modes": list((web.get("view_modes") or {}).keys())}}
    STATUS_JS.write_text("window.WIKI_WORKBENCH_STATUS = " + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--publish-to-boards", action="store_true", help="同时写入 data/boards/（默认关闭；会改变 Wiki 展示）")
    ap.add_argument("--offline-full", action="store_true", help="重新生成离线全量导出（数十 MB；默认只在文件缺失时生成）")
    ap.add_argument("--export", action="store_true", help="--offline-full 的别名（用户显式导出）")
    args = ap.parse_args()
    want_full = args.offline_full or args.export
    entries: list = []

    # lightweight（默认）+ 小 Domain
    project_item_stats(entries)
    project_lottery_stats(entries)
    project_weapon_skin(entries)
    project_fashion(entries)

    # 离线全量：显式导出，或文件缺失时补生成（保证离线打开可用）
    need_full = want_full or any(not (OUT_BOARDS / f"{pid}.js").exists() for pid in OFFLINE_FULL_BOARDS)
    if need_full:
        project_item(entries)
        project_lottery(entries)
    else:
        _offline_stub("item_master_active", "item", "artifacts/active/item/ITEM_MASTER.jsonl", ItemService().count(), entries)
        lt = LotteryService()
        _offline_stub("lottery_pool_active", "lottery", "artifacts/active/lottery/LOTTERY_POOL.jsonl", lt.pool_stats()["records"], entries)
        _offline_stub("lottery_rewards_active", "lottery", "artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl",
                      lt.reward_targets_page(page_size=1)["total"], entries)

    manifest = {"generated": NOW, "generator": "pipelines/projection/build_boards.py v1.3",
                "dataflow": "artifacts/active → domain service → projection / API → Web Client",
                "source_of_truth_only": "artifacts/active（禁止 legacy board / historical）",
                "default_web_path": "Workbench API 分页（/api/items、/api/lottery/pools、/api/lottery/rewards）",
                "profiles": {"lightweight": [e["projection_id"] for e in entries if e["profile"] == LIGHTWEIGHT],
                             "offline_full_projection": [e["projection_id"] for e in entries if e["profile"] == OFFLINE_FULL]},
                "web_client_registry": "registry/web_client.json",
                "projections": entries}
    MANIFEST_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    MANIFEST_JS.write_text("window.WIKI_WORKBENCH_MANIFEST = " + json.dumps(manifest, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    status = write_status()
    if args.publish_to_boards:
        for e in entries:
            (REPO / "data" / "boards" / Path(e["json"]).name).write_text((OUT_BOARDS / Path(e["json"]).name).read_text(encoding="utf-8"), encoding="utf-8")
            (REPO / "data" / "boards" / Path(e["js"]).name).write_text((OUT_BOARDS / Path(e["js"]).name).read_text(encoding="utf-8"), encoding="utf-8")
        print("已写入 data/boards/（需更新 publication_policy 才会展示）")
    print(json.dumps({"offline_full_regenerated": need_full,
                      "projections": [{k: e[k] for k in ("domain", "projection_id", "profile", "row_count", "web_default")} for e in entries],
                      "workbench_status_domains": list(status["status"]["domains"])}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
