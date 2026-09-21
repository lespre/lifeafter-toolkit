#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Preview board: future-dated lottery activities in the BA8 snapshot.

Scans reward_pool_data_base rows whose expiration_time is later than the
snapshot date (2026-09-10) and whose broadcast names an activity; clusters rows
by (activity name, expiration); keeps the near-term window (2026-09 .. 2027-12)
and drops already-published themes (帝皇铠甲/铠甲再临/宸世臻藏/无人机抽奖/战备工坊)
and obvious test rows. One item per activity instance: activity, instance exp
date, row count, pool set, note samples. Row-level归属 to specific pools is NOT
re-verified per activity; pool sets may include cross-activity shared rows.
This is the preview column's「（2）新奖池活动」sub-card.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import struct
import sys
from bisect import bisect_right
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from live_npk_reader import LiveNpkReader, NpkFormatError, _unpack_entry  # noqa: E402

CORE = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
sys.path.insert(0, str(CORE))
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_rows import uleb  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

SOURCE_REGISTRY = ROOT / "data" / "live_sources.json"
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "future_lottery_preview.json"
REWARD_BASE_FID = "D558884A36C972C5"
REWARD_CHS_FID = "69E58821939CB515"
SNAPSHOT_DATE = "2026-09-10"
from preview_board_contract import apply_frozen_v3  # noqa: E402


def _locator(item: dict) -> dict:
    """单条记录 = reward_pool 未来档实例（广播名 + expiration 聚类）。"""
    existing = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
    row_key = item.get("row_key") or existing.get("row_key") or 0
    return {
        "table": "reward_pool_data_base",
        "row_key": row_key,
        "field_refs": [
            f"reward_pool_data_base.key={row_key}",
            "reward_pool_data_base.broadcast_content",
            "reward_pool_data_base.expiration_time",
            "reward_pool_data_base.reward",
        ],
        "name_source": "reward_pool_data_base.broadcast_content 中的活动名（静态广播文案；预告=未来档实例，非上线断言）",
        "status_tags": ["unresolved", "static config"],
        "kind": "live-scan-cluster",
    }


SKIP_THEMES = {"帝皇铠甲", "铠甲再临", "宸世臻藏", "无人机抽奖", "战备工坊"}
ACTIVITY_RE = re.compile(r"在(.+?)活动中")


def load_registered_source(source_id: str) -> dict[str, Any]:
    raw = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    source = next((item for item in raw.get("sources", []) if item.get("source_id") == source_id), None)
    if not isinstance(source, dict):
        raise ValueError(f"{source_id} source is not registered")
    return source


def xbody(payload: bytes) -> bytes:
    offset = payload.find(b"x{")
    if offset < 0 or offset + 6 > len(payload):
        raise NpkFormatError("expected x{ BinDict container not found")
    size = struct.unpack_from("<I", payload, offset + 2)[0]
    end = offset + 6 + size
    if end > len(payload):
        raise NpkFormatError("BinDict body exceeds decoded payload")
    return payload[offset + 6:end]


def flat(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.get("values", {}).items():
        out[key] = value[1] if isinstance(value, tuple) and len(value) == 2 else value
    return out


def read_group(blob: bytes, at: int, end: int) -> list[int]:
    if blob[at:at + 2] != b"\x27\x01":
        raise ValueError(f"not a 0x27 group at {at}")
    count, pos = uleb(blob, at + 2, end)
    out: list[int] = []
    for _ in range(count):
        value, pos = uleb(blob, pos, end)
        out.append(value)
    return out


def uleb_encode(number: int) -> bytes:
    out = bytearray()
    while True:
        b = number & 0x7F
        number >>= 7
        out.append(b | (0x80 if number else 0))
        if not number:
            return bytes(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    registered = load_registered_source("documents-py314-current")
    package = Path(registered["path"])
    reader = LiveNpkReader(package, str(registered.get("server_branch") or "Documents snapshot"))
    metadata = reader.source_metadata()
    if metadata["package_sha256"] != registered.get("expected_sha256"):
        raise RuntimeError("registered source SHA mismatch")
    entries_by_fid = {f"{entry.file_id:016X}": entry for entry in reader._entries}

    def decode(fid: str) -> tuple[bytes, dict[str, Any]]:
        entry = entries_by_fid[fid]
        if entry is None:
            raise RuntimeError(f"FID missing: {fid}")
        with package.open("rb") as handle:
            handle.seek(entry.offset)
            packed = handle.read(entry.packed_size)
        payload = _unpack_entry(packed, entry.declared_size, entry.flag)
        reader._assert_unchanged()
        return payload, {
            "entry_index": entry.entry_index,
            "file_id": fid,
            "decoded_sha256": hashlib.sha256(payload).hexdigest(),
            "role": "reward_base" if fid == REWARD_BASE_FID else "reward_chs",
        }

    base_payload, base_meta = decode(REWARD_BASE_FID)
    chs_payload, chs_meta = decode(REWARD_CHS_FID)
    body = xbody(base_payload)
    pool = parse_legacy_chs_pool(chs_payload)
    rows, unbound = decode_table_rows_with_chs_slots(body, pool)
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    starts = sorted({row["start"] for row in rows})
    by_start = {row["start"]: row for row in rows}

    now_ts = dt.datetime.strptime(SNAPSHOT_DATE, "%Y-%m-%d").timestamp()
    clusters: dict[tuple[str, int], dict[str, Any]] = defaultdict(
        lambda: {"exps": Counter(), "pools": set(), "rows": 0, "notes": [], "first_row_key": None})
    for start in starts:
        i = bisect_right(starts, start)
        end = starts[i] if i < len(starts) else len(blob)
        row = by_start.get(start)
        if row is None:
            continue
        f = flat(row)
        exp = f.get("expiration_time")
        if not isinstance(exp, int) or exp <= now_ts:
            continue
        bc = f.get("broadcast_content")
        if not isinstance(bc, str) or not bc.strip():
            continue
        m = ACTIVITY_RE.search(bc)
        act = m.group(1).strip() if m else bc[:24]
        if act in SKIP_THEMES or "测试" in act:
            continue
        exp_date = dt.datetime.fromtimestamp(exp).strftime("%Y-%m-%d")
        if not ("2026-09" <= exp_date <= "2027-12"):
            continue
        key = (act, exp)
        cluster = clusters[key]
        cluster["exps"][exp] += 1
        cluster["rows"] += 1
        if cluster["first_row_key"] is None:
            cluster["first_row_key"] = row["key"]
        pos = start
        while True:
            at = blob.find(b"\x27\x01\x02", pos, end)
            if at < 0:
                break
            try:
                g = read_group(blob, at, end)
                if len(g) == 2 and g[0] >= 390000:
                    cluster["pools"].add(g[0])
            except (ValueError, IndexError):
                pass
            pos = at + 1
        note = f.get("note")
        if isinstance(note, str) and note and len(cluster["notes"]) < 4:
            cluster["notes"].append(note[:40])

    items: list[dict[str, Any]] = []
    for (act, exp), cluster in sorted(clusters.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        pool_list = sorted(cluster["pools"])
        items.append({
            "id": f"{act}-{exp}",
            "name": act,
            "activity": act,
            "instance_exp_date": dt.datetime.fromtimestamp(exp).strftime("%Y-%m-%d"),
            "instance_exp_ts": exp,
            "rows_in_window": cluster["rows"],
            "pool_count": len(pool_list),
            "pools": pool_list,
            "note_samples": cluster["notes"],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": (
                "reward_pool_data_base rows with future expiration broadcast 该活动名；"
                "活动实例=广播名+expiration 聚类；池集合含跨活动共享行可能，未逐行复核归属"
            ),
            "provenance": {
                "source_lock_sha256": metadata["package_sha256"],
                "source_entries": [base_meta, chs_meta],
                "table": "reward_pool_data_base",
                "row_key": cluster["first_row_key"],
                "field_refs": [
                    f"broadcast_content contains activity name {act}",
                    f"expiration_time={exp} ({dt.datetime.fromtimestamp(exp).strftime('%Y-%m-%d')})",
                    "clustered by (activity name, expiration_time)",
                ],
                "name_source": "reward_pool_data_base.broadcast_content activity segment; 预告=未来档实例，非上线断言",
            },
        })

    lock = {
        "sha256": metadata["package_sha256"],
        "bytes": metadata["bytes"],
        "mtime_ns": metadata["mtime_ns"],
        "path_hint": "mrzh/Documents/script.py314.lc.npk (simple-survival test snapshot)",
    }
    board = {
        "meta": {
            "name": "新奖池活动（未来档预告）",
            "category": "零、新更新与预告专栏（游戏未上线资源预告） / （2）新奖池活动",
            "source_server": registered.get("server_branch"),
            "package_sha": metadata["package_sha256"],
            "generated": dt.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                "BA8 快照（2026-09-10）中过期时间晚于快照日期的活动实例清单（时间窗至 2027-12）。"
                "含历史活动返场排期与未来新档；是否为测试服独有新内容需对照《明日之后完整历史更新汇总》"
                "逐条判定，本板不做该断言。已排除已发布主题（帝皇铠甲/铠甲再临/宸世臻藏等）与测试行。"
                "活动实例=广播活动名+expiration 聚类，池集合可能含跨活动共享行。"
            ),
            "provenance": {"audit_status": "passed", "source_locks": [lock]},
        },
        "items": items,
        "stats": {"activity_instances": len(items), "unbound_rows": len(unbound)},
    }
    # 发布门禁（strict v3）：冻结产物契约（锁=当前脚本包）+ 逐条定位链
    apply_frozen_v3(
        board,
        source_id="future-lottery-preview-live-scan-adapter",
        artifact_path=Path(registered["path"]),
        artifact_label="mrzh/Documents/script.py314.lc.npk (simple-survival test snapshot)",
        state_summary={
            "unresolved": len(items),
            "static config": len(items),
            "verified": 0,
            "runtime final unknown": len(items),
        },
        locator=_locator,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({"output": str(args.output), "items": len(items), "unbound": len(unbound)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
