# -*- coding: utf-8 -*-
"""重排 fashion_wardrobe 部位分类：改名 + 并入 fashion_face（幂等）。

═══════════════════════════════════════════════════════════════
★ 口径（用户 2026-11-01 决策，落此脚本即规则）

  1. 改名（wardrobe 内既有 item）
       头饰 → 头发
       光源 → 荧光棒
  2. 并入 fashion_face（180 条，独立面容板）
       · 戴柳 / 笑春风         → 头饰
       · 其余 177 条           → 面饰
       · 3 条 status_tags=table-absent 且无 locator_chain 的（入侵者挂饰 /
         救救我挂饰 / 明日世界的角色用圣诞帽）按铁律「找不到证据不伪造」跳过。
  3. 溯源：face item 的 source_id=documents-py314-current，补 comparison 锁；
     upstream 规范为 {package_sha256, role}（原 {role:"SuperFashion"} 缺
     package_sha256，不过 frozen_v3 门禁）。

★ 幂等：同输入重跑结果一致；已改名的不再改、已并入的 id 跳过、锁已存在则跳过。
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ
from board_io import write_board_pair

WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
FACE = WEB / "data/boards/fashion_face.json"

RENAME = {"头饰": "头发", "光源": "荧光棒"}
HEADWEAR_ANCHORS = {"戴柳", "笑春风"}
FACE_SOURCE_ID = "documents-py314-current"
FACE_SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"
NOTE_MARK = "[部位重排]"
NOTE_TEXT = ("部位重排：头饰→头发、光源→荧光棒；并入 fashion_face "
             "（戴柳/笑春风→头饰，其余→面饰；3 条 table-absent 无溯源按铁律跳过）。")


def _norm_upstream(sha: str) -> dict:
    return {"package_sha256": sha, "role": "player_module_appear_data"}


def main() -> None:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    prov = board["meta"].setdefault("provenance", {})
    locks = prov.setdefault("source_locks", [])

    # 1) 改名（幂等）
    n_rename = 0
    for it in board["items"]:
        p = it.get("part")
        if p in RENAME:
            new = RENAME[p]
            it["part"] = new
            pb = it.get("part_bucket")
            it["part_bucket"] = [new if b == p else b for b in pb] if isinstance(pb, list) else [new]
            n_rename += 1

    # 2) 并入 fashion_face（幂等）
    face = json.loads(FACE.read_text(encoding="utf-8"))
    existing = {it["id"] for it in board["items"]}
    n_add = 0
    n_skip = 0
    for fi in face["items"]:
        if fi["id"] in existing:
            continue
        fp = fi.get("provenance") or {}
        # 无 locator_chain 的项（table-absent）按铁律跳过，不伪造
        if not isinstance(fp.get("locator_chain"), dict):
            n_skip += 1
            continue
        sha = fp.get("source_lock_sha256") or FACE_SHA
        target = "头饰" if fi.get("name") in HEADWEAR_ANCHORS else "面饰"
        new_prov = {
            "source_id": fp.get("source_id") or FACE_SOURCE_ID,
            "source_lock_sha256": sha,
            "table": "player_module_appear_data",
            "row_key": fp.get("row_key"),
            "field_refs": fp.get("field_refs"),
            "name_source": "player_module_appear_data.show_name",
            "upstream": _norm_upstream(sha),
            "locator_chain": fp.get("locator_chain"),
        }
        board["items"].append({
            "id": fi["id"],
            "name": fi.get("name"),
            "evidence": fi.get("evidence"),
            "source": fi.get("source"),
            "part": target,
            "part_bucket": [target],
            "part_source": "player_module_appear_data",
            "time_limited_variants": fi.get("time_limited_variants"),
            "desc": fi.get("desc"),
            "desc_note": fi.get("desc_note"),
            "icon_state": "无2D图（面容类）",
            "charm_value": None,
            "row_variants": fi.get("row_variants"),
            "evidence_level": fi.get("evidence_level"),
            "status_tags": fi.get("status_tags"),
            "_prov_shape": fi.get("_prov_shape"),
            "provenance": new_prov,
        })
        existing.add(fi["id"])
        n_add += 1

    # 3) 补溯源锁（幂等）
    n_lock = 0
    if not any(l.get("source_id") == FACE_SOURCE_ID for l in locks):
        locks.append({
            "source_id": FACE_SOURCE_ID,
            "role": "comparison",
            "path": "documents 实时包（player_module_appear_data 同源）",
            "sha256": FACE_SHA,
            "bytes": 196059988,
            "mtime_ns": 1792505574167464800,
        })
        n_lock += 1

    # 4) meta.notes 幂等追加（notes 为字符串）
    notes = board["meta"].get("notes")
    if not isinstance(notes, str):
        notes = notes or ""
    if NOTE_MARK not in notes:
        board["meta"]["notes"] = (notes.rstrip() + "\n\n" + NOTE_MARK + " " + NOTE_TEXT + "\n").strip() + "\n"

    write_board_pair(BOARD, board)
    print(f"改名:{n_rename} ｜ 并入face:{n_add} ｜ 跳过(table-absent):{n_skip} ｜ 新增锁:{n_lock} ｜ 总条目:{len(board['items'])}")


if __name__ == "__main__":
    main()
