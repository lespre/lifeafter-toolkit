#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「按期次还原的奖池成员」落进奖池板（幂等）。

读：01_索引与产物/30_分析/奖池成员_<date>.json
写：02_wiki/web/data/boards/lottery_periods.json(+ .js)

规则：
  · 只新增板上没有的 item_id（同 id 以既有结构条目为准，避免重复）
  · 每期写 pool_ids / pool_count / member_source
  · 该期合并后有结构成员时，撤掉它的「候选」条目（候选只在该期无结构成员时保留）
  · 重复运行先删本脚本写过的条目（pool_mapped=true）
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))

import rebuild_lottery_periods as R  # noqa: E402
from board_io import write_board_pair  # noqa: E402

ANALYSIS = Path(r"E:\la拆包项目\01_索引与产物\30_分析")
INDEX = Path(r"E:\la拆包项目\01_索引与产物\10_索引")
BOARD = WEB / "data/boards/lottery_periods.json"
ASSETS = WEB / "assets"
GEN = dt.date.today().strftime("%Y%m%d")


def load_names() -> dict:
    out: dict[str, str] = {}
    for f in ("common_item_names.json", "show_item_names.json"):
        p = INDEX / "items" / f
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for k, v in (d.get("items") or {}).items():
            nm = v.get("name") if isinstance(v, dict) else v
            if isinstance(nm, str) and nm.strip():
                out.setdefault(str(k), nm.strip())
    # 时装：fashion_wardrobe 的 row_keys 就是 637xxx / 74xxx 这类道具 id
    fw = WEB / "data/boards/fashion_wardrobe.json"
    if fw.exists():
        d = json.loads(fw.read_text(encoding="utf-8"))
        for it in (d.get("items") or []):
            nm = it.get("name")
            if not isinstance(nm, str) or not nm.strip():
                continue
            for rk in (it.get("row_keys") or []):
                out.setdefault(str(rk), nm.strip())
    ns = INDEX / "items" / "item_names_ns.json"
    if ns.exists():
        d = json.loads(ns.read_text(encoding="utf-8"))
        for _ns, table in (d.get("by_ns") or {}).items():
            if not isinstance(table, dict):
                continue
            for k, v in table.items():
                nm = v.get("name") if isinstance(v, dict) else v
                if isinstance(nm, str) and nm.strip():
                    out.setdefault(str(k), nm.strip())
    return out


def main() -> int:
    src = ANALYSIS / f"奖池成员_{GEN}.json"
    if not src.exists():
        print("找不到成员文件:", src)
        return 2
    doc = json.loads(src.read_text(encoding="utf-8"))
    per_items = doc["periods"]

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    meta = board["meta"]
    lock = meta["provenance"]["source_locks"][0]
    src_id, src_sha = lock["source_id"], lock["sha256"]
    periods = {p["period_id"]: p for p in board["periods"]}

    before = len(board["items"])
    board["items"] = [i for i in board["items"] if not i.get("pool_mapped")]

    names_map = load_names()
    # 先用 R.Names（fashion/gift/recipe/索引 多表合判），补不上的再退回本地表
    try:
        Rnames = R.Names()
    except Exception:
        Rnames = None
    board_names = {str(i.get("item_id")): i.get("name")
                   for i in board["items"] if i.get("name")}

    added, touched_added = 0, set()
    for pid, rec in per_items.items():
        per = periods.get(pid)
        if not per:
            continue
        have = {str(i.get("item_id")) for i in board["items"]
                if i.get("period_id") == pid and i.get("evidence") == "structure"}
        n = 0
        for ent in rec["items"]:
            iid = int(ent["item_id"])
            if str(iid) in have:
                continue
            have.add(str(iid))
            name, name_src = None, None
            if Rnames is not None:
                try:
                    n0, nsrc0, _alts0 = Rnames.resolve(iid)
                    if n0:
                        name, name_src = n0, nsrc0
                except Exception:
                    pass
            if not name:
                name = names_map.get(str(iid)) or board_names.get(str(iid))
                name_src = "index:item_names" if names_map.get(str(iid)) else "board:existing" 
            icon_rel = None
            png = ASSETS / "lottery_icons" / f"{iid}.png"
            if not png.exists():
                png = ASSETS / "item_icons" / f"{iid}.png"
            if png.exists():
                icon_rel = f"assets/{png.parent.name}/{png.name}"
            item = {
                "id": f"{pid}:m{iid}",
                "period_id": pid,
                "period_label": per.get("label"),
                "period_start": per.get("start"),
                "period_end": per.get("end"),
                "family": per.get("family"),
                "family_key": per.get("family_key"),
                "name": name or f"未识别道具 {iid}",
                "item_id": str(iid),
                "kind": R.kind_of(iid),
                "evidence": "structure",
                "evidence_level": "structure-only",
                "status_tags": (["unresolved", "static config"] if not name
                                else ["verified", "static config", "runtime final unknown"]),
                "_media": {"images": [], "total": 0},
                "icon_state": "已下发" if icon_rel else "未下发",
                "icon": icon_rel,
                "_media": {"images": ([{"png": icon_rel}] if icon_rel else []),
                           "total": (1 if icon_rel else 0)},
                "source": f"{rec['source']} · 槽位 {ent.get('slot')}",
                "pool_id": ent.get("pool_id"),
                "slot": ent.get("slot"),
                "pool_mapped": True,
                "provenance": {
                    "source_id": src_id,
                    "table": rec["source"].split(".")[0],
                    "row_key": ent.get("pool_id") or per.get("conf_key"),
                    "field_refs": ["slot", "item_id"],
                    "name_source": name_src or "unresolved",
                    "locator_chain": {
                        "steps": [{
                            "kind": "decoded-table-row",
                            "source_id": src_id,
                            "table": rec["source"].split(".")[0],
                            "row_key": ent.get("pool_id") or per.get("conf_key"),
                            "field_refs": ["slot", "item_id"],
                        }],
                        "chain_status": "replayed-structural",
                        "scope": "record",
                        "no_cross_source_field_join": True,
                    },
                    "source_lock_sha256": src_sha,
                    "upstream": {"package_sha256": src_sha, "entry_index": None, "file_id": None},
                },
            }
            board["items"].append(item)
            n += 1
        if n:
            touched_added.add(pid)
            added += n

    # 只对「本轮真加了成员」的期次清候选
    dropped = [i for i in board["items"]
               if i.get("evidence") == "candidate" and i.get("period_id") in touched_added]
    board["items"] = [i for i in board["items"] if i not in dropped]

    cnt = Counter(i["period_id"] for i in board["items"])
    pools_by_period: dict[str, set] = {}
    for i in board["items"]:
        if i.get("pool_id") is not None:
            pools_by_period.setdefault(i["period_id"], set()).add(i["pool_id"])
    for pid, per in periods.items():
        per["member_count"] = cnt.get(pid, 0)
        if pid in pools_by_period:
            per["pool_ids"] = sorted(pools_by_period[pid], key=str)
            per["pool_count"] = len(pools_by_period[pid])
    for pid in per_items:
        if pid in periods:
            periods[pid]["member_source"] = "structure:pool-map"

    meta["generated"] = GEN
    write_board_pair(BOARD, board)
    print(f"items {before} → {len(board['items'])}（新增 {added}，撤候选 {len(dropped)}）")
    print(f"有成员期次 {len(cnt)}；本轮动过的期次 {len(touched_added)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
