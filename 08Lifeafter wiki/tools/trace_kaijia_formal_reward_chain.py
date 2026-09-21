#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trace formal-client Kaijia lottery reward records from raw BinDict bytes.

This is deliberately a provenance extractor, not a renderer.  It records the
literal 0x27 [pool_id, slot] container, its containing reward row, the original
prob_note text, and the final reward jump group.  It does not treat a reward
item ID that happens to equal a pool ID as a proved child-pool edge.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from bisect import bisect_right
from pathlib import Path
from typing import Any

WORKCOPY = Path(
    r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_79c0d06f53db"
)
CORE_DIR = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
DEFAULT_OUTPUT = WORKCOPY / "kaijia_formal_reward_trace.json"
POOL_IDS = (390704, 391536, 391533, 391772, 391782, 391783)


def uleb_encode(number: int) -> bytes:
    output = bytearray()
    while True:
        value = number & 0x7F
        number >>= 7
        output.append(value | (0x80 if number else 0))
        if not number:
            return bytes(output)


def xbody(payload: bytes) -> bytes:
    offset = payload.find(b"x{")
    if offset < 0:
        raise ValueError("BinDict x{ frame not found")
    length = struct.unpack_from("<I", payload, offset + 2)[0]
    end = offset + 6 + length
    if end > len(payload):
        raise ValueError("truncated x{ frame")
    return payload[offset + 6:end]


def plain(values: dict[str, tuple[str, Any]]) -> dict[str, Any]:
    return {field: value for field, (_kind, value) in values.items()}


def read_group(blob: bytes, offset: int, end: int, uleb: Any) -> list[int]:
    if blob[offset:offset + 2] != b"\x27\x01":
        raise ValueError(f"expected 0x27 inline group at {offset}")
    count, position = uleb(blob, offset + 2, end)
    elements: list[int] = []
    for _ in range(count):
        value, position = uleb(blob, position, end)
        elements.append(value)
    return elements


def load_table(workcopy: Path, base_name: str, chs_name: str) -> tuple[bytes, Any, list[dict[str, Any]], list[dict[str, Any]]]:
    sys.path[:0] = [str(CORE_DIR), str(Path.cwd() / "tools")]
    from toolkit_core.bindict_table import parse_index, parse_legacy_chs_pool  # noqa: PLC0415
    from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: PLC0415

    manifest = json.loads((workcopy / "manifest.json").read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in manifest["entries"]}
    base = (workcopy / by_name[base_name]["output_file"]).read_bytes()
    chs = (workcopy / by_name[chs_name]["output_file"]).read_bytes()
    body = xbody(base)
    rows, unbound = decode_table_rows_with_chs_slots(body, parse_legacy_chs_pool(chs))
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + count * 4:]
    starts = sorted({start for _key, start in parse_index(blob)})
    return blob, starts, rows, unbound


def trace(workcopy: Path, pool_ids: tuple[int, ...]) -> dict[str, Any]:
    sys.path[:0] = [str(CORE_DIR), str(Path.cwd() / "tools")]
    from toolkit_core.bindict_rows import uleb  # noqa: PLC0415
    from toolkit_core.bindict_table import resolve_jump_group  # noqa: PLC0415

    manifest = json.loads((workcopy / "manifest.json").read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in manifest["entries"]}
    reward_blob, starts, reward_rows, reward_unbound = load_table(
        workcopy, "reward_pool_data_base", "reward_pool_data_base_chs"
    )
    super_blob, _super_starts, super_rows, super_unbound = load_table(
        workcopy, "super_fashion_lottery_conf_data", "super_fashion_lottery_conf_data_chs"
    )
    decoded_by_start = {row["start"]: row for row in reward_rows}
    default_end = len(reward_blob)
    records: list[dict[str, Any]] = []

    for pool_id in pool_ids:
        marker = b"\x27\x01\x02" + uleb_encode(pool_id)
        search_from = 0
        while True:
            anchor = reward_blob.find(marker, search_from)
            if anchor < 0:
                break
            search_from = anchor + 1
            start_at = bisect_right(starts, anchor) - 1
            if start_at < 0:
                continue
            row_start = starts[start_at]
            row_end = starts[start_at + 1] if start_at + 1 < len(starts) else default_end
            try:
                group = read_group(reward_blob, anchor, row_end, uleb)
            except (IndexError, ValueError):
                continue
            if len(group) != 2 or group[0] != pool_id:
                continue
            row = decoded_by_start.get(row_start)
            fields = plain(row["values"]) if row else None
            reward_group: list[int] | None = None
            reward_target: int | None = None
            if fields and isinstance(fields.get("reward"), str) and fields["reward"].startswith("jump:"):
                reward_target = int(fields["reward"].split(":", 1)[1])
                try:
                    reward_group = resolve_jump_group(reward_blob, reward_target)
                except (IndexError, ValueError):
                    reward_group = None
            records.append({
                "pool_id": pool_id,
                "slot": group[1],
                "pool_slot_encoding": {"blob_offset": anchor, "bytes": marker.hex()},
                "containing_row": None if row is None else {
                    "key": row["key"], "start": row_start, "end": row_end,
                },
                "fields": fields,
                "reward_jump": reward_target,
                "final_reward_group": reward_group,
                "pool_id_reused_as_reward_item": bool(
                    reward_group and reward_group[0] in set(pool_ids)
                ),
            })

    records.sort(key=lambda record: (record["pool_id"], record["slot"], record["pool_slot_encoding"]["blob_offset"]))
    config = next((row for row in super_rows if row["key"] == 232), None)
    if config is None:
        raise KeyError("formal super_fashion_lottery_conf_data key 232 missing")
    config_fields = plain(config["values"])
    fortune_target = int(str(config_fields["fortune_bag_dct"]).split(":", 1)[1])
    # Exact one-pair numeric map layout currently stored at this jump target:
    # 36 <key-type=0b> <value-type=01> <pair-count> <key> <value>.
    prefix = super_blob[fortune_target:fortune_target + 3]
    if prefix != b"\x36\x0b\x01":
        raise ValueError(f"unexpected fortune_bag_dct map types: {prefix.hex()}")
    pair_count, fortune_position = uleb(super_blob, fortune_target + 3, len(super_blob))
    if pair_count != 1:
        raise ValueError(f"unexpected fortune_bag_dct pair count: {pair_count}")
    fortune_key, fortune_position = uleb(super_blob, fortune_position, len(super_blob))
    fortune_pool_id, fortune_end = uleb(super_blob, fortune_position, len(super_blob))
    if fortune_end > int(str(config_fields["panel_show_item_ids"]).split(":", 1)[1]):
        raise ValueError("fortune_bag_dct overlaps the next known jump target")

    return {
        "schema": "lifeafter-kaijia-formal-reward-trace-v1",
        "source": manifest["source"],
        "reward_table": {
            "name": "reward_pool_data_base",
            "entry": by_name["reward_pool_data_base"],
            "decoded_rows": len(reward_rows),
            "unbound_rows": len(reward_unbound),
        },
        "activity_config": {
            "table": "super_fashion_lottery_conf_data",
            "key": 232,
            "fields": config_fields,
            "fortune_bag_dct": {
                "jump": fortune_target,
                "map_type_prefix": prefix.hex(),
                "pair_count": pair_count,
                "singleton_key": fortune_key,
                "pool_id": fortune_pool_id,
                "end_offset": fortune_end,
            },
            "unbound_rows_in_table": len(super_unbound),
        },
        "pool_ids_scanned": list(pool_ids),
        "records": records,
        "limits": [
            "A record's final_reward_group is a proved reward leaf only.",
            "An item ID equal to a pool ID is recorded as a possible continuation, not a proved parent-child pool relation.",
            "prob_note is configuration text and must be rendered as 配置概率, not server-side comprehensive odds.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workcopy", type=Path, default=WORKCOPY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = trace(args.workcopy, POOL_IDS)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    by_pool: dict[int, int] = {}
    for record in report["records"]:
        by_pool[record["pool_id"]] = by_pool.get(record["pool_id"], 0) + 1
    print(json.dumps({
        "output": str(args.output),
        "records": len(report["records"]),
        "by_pool": by_pool,
        "fortune_bag_pool": report["activity_config"]["fortune_bag_dct"]["pool_id"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
