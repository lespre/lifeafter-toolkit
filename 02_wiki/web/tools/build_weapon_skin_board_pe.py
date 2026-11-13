#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""（二）武器皮肤 · PE 源重建（不依赖历史基线与 PC 包）。

与旧 builder（rebuild_weapon_skin_catalog_current.py）的区别：
  · 只读 PE 客户端脚本包（data/live_sources_pe.json → 雷电拉下来的 script.py314.lc.npk）
  · 不做「相对 8-27 基线的新增/移除」对比 —— 基线包本机已不存在，标「无基线（不可比）」
  · 缺 common_item 道具行不再中止：该条目标「无道具行」，名字退回表内 name/内部名
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

import rebuild_weapon_skin_catalog_current as W  # noqa: E402

BOARD_ID = "weapon_skin_catalog_pe"
OUT_JSON = W.ROOT / "data" / "boards" / f"{BOARD_ID}.json"
LOCK_ID = "pe-client-script-npk"


def main() -> int:
    src = W.load_current_source()
    reader = W.LiveNpkReader(Path(src["path"]), str(src.get("server_branch") or "playertest"))
    meta = reader.source_metadata()
    if meta["package_sha256"] != src["expected_sha256"]:
        raise RuntimeError("PE 源包 SHA 与注册表不一致（包变了，先重跑 build_pe_live_sources.py）")
    print("源包", Path(src["path"]).name, meta["package_sha256"][:12], meta["bytes"])

    entries = {f"{e.file_id:016X}": e for e in reader._entries}
    payloads = {}
    for k in ("weapon_skin_base", "weapon_skin_chs", "weapon_skin_sfx_base", "weapon_skin_sfx_chs",
              "common_item_base", "common_item_chs"):
        payloads[k] = W.read_payload(reader, Path(src["path"]), entries, W.FIDS[k], k)[0]

    skin_rows, _ = W.table_rows(payloads["weapon_skin_base"], payloads["weapon_skin_chs"])
    item_rows, _ = W.table_rows(payloads["common_item_base"], payloads["common_item_chs"])
    item_by_key = {}
    for r in item_rows:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in r.get("values", {}).items()}
        item_by_key[r["key"]] = v

    sfx_by_skin: dict[int, int] = {}
    try:
        sfx_rows, _ = W.table_rows(payloads["weapon_skin_sfx_base"], payloads["weapon_skin_sfx_chs"])
        for r in sfx_rows:
            v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in r.get("values", {}).items()}
            sid = v.get("skin_id")
            if isinstance(sid, int):
                sfx_by_skin[sid] = sfx_by_skin.get(sid, 0) + 1
    except Exception as exc:  # noqa: BLE001
        print("⚠ SFX 表解不出，音效列置空：", exc)

    items = []
    for r in skin_rows:
        skin_id = r["key"]
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in r.get("values", {}).items()}
        item = item_by_key.get(skin_id) or {}
        name = item.get("name") or v.get("name") or v.get("skin_name")
        grade = v.get("level") or item.get("quality")
        wt = v.get("weapon_type")
        ts = v.get("sale_ts") or v.get("start_ts")
        sale_date = ""
        if isinstance(ts, (int, float)) and ts > 0:
            try:
                sale_date = dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            except (OSError, ValueError):
                sale_date = ""
        items.append({
            "id": str(skin_id),
            "skin_id": skin_id,
            "name": str(name) if name else f"皮肤 {skin_id}",
            "name_source": "common_item" if item.get("name") else ("weapon_skin_data" if name else "none"),
            "grade_level": grade,
            "weapon_type": wt,
            "weapon_type_label": W.type_label(wt),
            "name_status": "verified" if name else "unresolved",
            "sale_ts": ts,
            "sale_date": sale_date,
            "has_item_row": bool(item),
            "sfx_count": sfx_by_skin.get(skin_id, 0),
            "version_status": "无基线（不可比）",
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["static config", "runtime final unknown"],
            "source": "PE 客户端 script.py314.lc.npk（weapon_skin_data + common_item_data）",
            "provenance": {
                "source_id": LOCK_ID,
                "table": "weapon_skin_data",
                "row_key": skin_id,
                "field_refs": ["name", "level", "weapon_type", "sale_ts"],
                "name_source": "common_item_data#name" if item else "weapon_skin_data#skin_name",
                "locator_chain": {
                    "steps": [{"kind": "decoded-table-row", "source_id": LOCK_ID,
                               "table": "weapon_skin_data", "row_key": skin_id,
                               "field_refs": ["name", "level", "weapon_type", "sale_ts"]}],
                    "chain_status": "replayed-structural",
                    "scope": "record",
                    "no_cross_source_field_join": True,
                },
                "source_lock_sha256": meta["package_sha256"],
                "upstream": {"package_sha256": meta["package_sha256"], "entry_index": None, "file_id": None},
            },
        })

    items.sort(key=lambda x: (-(x["sale_ts"] or 0), str(x["skin_id"])))
    board = {
        "meta": {
            "name": "（二）武器皮肤 · 当前包图鉴",
            "category": "一、时装类 / （二）武器皮肤",
            "generated": dt.date.today().strftime("%Y-%m-%d"),
            "evidence": "structure",
            "source_server": "PE 体验服客户端 script.py314.lc.npk（雷电 11-12 热更后）",
            "package_sha": meta["package_sha256"],
            "id_label": "皮肤ID",
            "hide_media": True,
            "card_mode": "roster",
            "filters": [{"key": "weapon_type_label", "label": "武器类型"},
                        {"key": "grade_level", "label": "品级"}],
            "card_summary": [["name", "名称"], ["weapon_type_label", "武器类型"],
                             ["grade_level", "品级"], ["sale_date", "上架"], ["sfx_count", "音效条数"]],
            "field_labels": {"name": "名称", "skin_id": "皮肤ID",
                             "weapon_type": "武器类型码", "weapon_type_label": "武器类型",
                             "name_status": "命名状态",
                             "grade_level": "品级", "sale_date": "上架日期", "sfx_count": "音效条数",
                             "has_item_row": "有道具行", "version_status": "版本状态"},
            "hide_fields": ["source", "id", "provenance", "evidence", "evidence_level",
                            "status_tags", "sale_ts", "name_source"],
            "state_summary": {"条目": len(items),
                              "有道具行": sum(1 for i in items if i["has_item_row"]),
                              "有音效": sum(1 for i in items if i["sfx_count"])},
            "notes": ("只读 PE 客户端包；不依赖历史基线（基线容器本机不存在）⇒ 版本状态一律「无基线（不可比）」。"
                      "名字优先 common_item_data，缺行时退回表内名并标 has_item_row=false。"),
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                                 "integer_join_policy": "no-equal-integer-join",
                                 "runtime_final_policy": "unknown-unless-runtime-proven"},
                "source_locks": [{
                    "source_id": LOCK_ID, "role": "primary",
                    "sha256": meta["package_sha256"], "bytes": meta["bytes"],
                    "mtime_ns": meta["mtime_ns"], "path": str(src["path"]),
                    "desc": "PE 体验服客户端脚本包（雷电 g66/Documents）",
                }],
            },
        },
        "periods": [],
        "items": items,
    }

    text = json.dumps(board, ensure_ascii=False, indent=1)
    OUT_JSON.write_text(text, encoding="utf-8")
    (OUT_JSON.with_suffix(".js")).write_text(
        f"window.WIKI_BOARD_{BOARD_ID} = " + text + ";", encoding="utf-8")
    print(f"{BOARD_ID}: {len(items)} 条 → {OUT_JSON.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
