#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preview board: weapon skins whose only presence is BA8 behavior resources.

Subset of the published weapon_skin_sfx_text_sources board (row chains are
deep-copied with their provenance): rows whose version_status starts with
「仅当前 BA8 行为资源」— no weapon_skin_data parent row, no item row, no name.
Listed skin ids: 1110184 / 1110186 / 1110190. This is the「（1）仅行为资源
未上线的武器皮肤」sub-card of the preview column; it does not claim those ids
are coming to any server, only that behavior resources exist in the snapshot.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_BOARD = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "skin_behavior_preview.json"
MARKER = "仅当前 BA8 行为资源"

from preview_board_contract import apply_frozen_v3  # noqa: E402


def _locator(item: dict) -> dict:
    """单条记录 = 冻结源板里的一条预告行（不引入新身份链）。"""
    skin_id = item.get("skin_id")
    existing = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
    field_refs = list(existing.get("field_refs") or [f"weapon_skin_data.key={skin_id}"])
    if item.get("preview_group") == "upcoming_named":
        field_refs += ["weapon_skin_data.sale_ts (晚于快照日 → upcoming)", "common_item_data_base.key=skin_id (正式名)"]
        name_source = "same-snapshot common_item_data_base row (verified formal name); release not yet reached per skin row sale_ts"
        tags = ["static config", "runtime final unknown"]
    else:
        field_refs += ["weapon_skin_data.absent_parent_row", "common_item_data_base.absent_item_row"]
        name_source = "no item row in the current snapshot; preview layer stays unfilled (no name claim)"
        tags = ["unresolved", "static config"]
    return {
        "table": str(existing.get("table") or "weapon_skin_data"),
        "row_key": skin_id if skin_id is not None else existing.get("row_key"),
        "field_refs": field_refs,
        "name_source": name_source,
        "status_tags": tags,
        "kind": "sanitized-existing-board-record",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    source = json.loads(SOURCE_BOARD.read_text(encoding="utf-8"))
    # 预告口径（两族，均来自冻结源板行，不新增身份断言）：
    #  ① upcoming_named：皮肤行 sale_ts 晚于包快照日 → 已配正式名+上架时间但快照时未到
    #  ② behavior_only：仅行为资源行（无父项、无道具行、无名称）
    selected: list[dict] = []
    for raw in source["items"]:
        item = copy.deepcopy(raw)
        if item.get("release_state") == "upcoming":
            item["preview_group"] = "upcoming_named"
            item["preview_note"] = (
                f"包内已配正式名「{item.get('name')}」与上架时间 {item.get('sale_date')}（晚于包快照日），"
                "快照时尚未上架；不表示到期必上、不代表价格/概率。"
            )
            selected.append(item)
        elif item.get("catalog_layer") == "behavior_preview_only":
            item["preview_group"] = "behavior_only_no_name"
            item["preview_note"] = "仅行为资源行：无 weapon_skin_data 父项、无道具行，故无正式名与品级。"
            selected.append(item)
    selected.sort(key=lambda it: (it.get("preview_group") != "upcoming_named", it.get("skin_id") or 0))
    if not selected:
        raise RuntimeError("no weapon-skin preview rows selected")

    meta = {
        "name": "武器皮肤 · 未上线预告（已配名未上架 + 仅行为资源）",
        "category": "零、新更新与预告专栏（游戏未上线资源预告） / （1）武器皮肤 · 未上线预告",
        "source_server": source["meta"]["source_server"],
        "package_sha": source["meta"]["package_sha"],
        "generated": dt.date.today().isoformat(),
        "evidence": "structure",
        "notes": (
            "预告口径（两族，均自冻结源板行深拷贝，未重新解码）："
            "①已配正式名未上架=皮肤行 sale_ts 晚于包快照日（快照时尚未到）；"
            "②仅行为资源=有 behavior_res 行但无父项/无道具行/无名称。"
            "均不表示上线、价格、概率或可得。"
        ),
        "provenance": copy.deepcopy(source["meta"].get("provenance", {})),
    }
    board = {"meta": meta, "items": selected}
    # 发布门禁（strict v3）：冻结产物契约 + 逐条定位链（继承源板行，不重新解码）
    apply_frozen_v3(
        board,
        source_id="weapon-skin-behavior-preview-adapter",
        artifact_path=SOURCE_BOARD,
        state_summary={
            "unresolved": len(selected),
            "static config": len(selected),
            "verified": 0,
            "runtime final unknown": len(selected),
        },
        locator=_locator,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({
        "output": str(args.output),
        "items": len(selected),
        "skin_ids": [it.get("skin_id") for it in selected],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
