# -*- coding: utf-8 -*-
r"""回填（一）人物时装·投影 条目的魅力值。

溯源结论（用户锚点核对）：
  投影的真实魅力值来自 com/cdata/follow_charm_conf_data.py，
  该表以 buff_id 为主键，字段 charm_value 即魅力值；source_content 说明获取途径。
  用户锚点核对：
    浮游炮(buff 24523)=1000、悠游天地(buff 20358)=1000、
    星河流淌(buff 20301)=2000、九尾蓝狐(buff 20350)=2000 —— 全部命中。

规则：
  - 投影条目若其 buff_id 在 follow_charm_conf_data 中，则 charm_value = 该表 charm_value；
    charm_note 记录来源 + source_content；provenance 追加 charm_source 块（独立溯源，
    不并入 locator_chain，遵守 no-cross-source-field-join）。
  - 5 个以 buff_data 为源、buff_id 为 None 的投影子类（伴身投影·花弄蝶 等）
    在 follow_charm_conf_data 中无命中，charm 留空并写明原因，绝不伪造。

幂等：同输入重跑结果不变；meta.notes 用 notes_util.append_note 幂等追加。
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
SHARED = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
if SHARED.exists():
    sys.path.insert(0, str(SHARED))
from board_io import write_board_pair  # noqa: E402
import notes_util  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/fashion_wardrobe.json"

FC_NAME = "follow_charm_conf_data"
FC_PATH = CD / f"{FC_NAME}.py"
FC_CHSE = CD / f"{FC_NAME}_chs.py"
SRC_ID = "fashion-projection-follow_charm_conf_data"


def load_fc():
    raw = FC_PATH.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    from toolkit_core import bindict_table as BT
    pool = BT.parse_legacy_chs_pool(FC_CHSE.read_bytes()) if FC_CHSE.exists() else {}
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)
    out = {}
    for r in rows:
        v = {k: (vv[1] if isinstance(vv, tuple) else vv) for k, vv in r["values"].items()}
        out[r.get("key")] = v
    return out


def main() -> int:
    fc = load_fc()
    fc_sha = hashlib.sha256(FC_PATH.read_bytes()).hexdigest()
    rel = "01_索引与产物/41_还原树/pe/配置/com/cdata/" + FC_PATH.name

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    # 注册 source_lock（comparison，唯一来源口径）
    locks = d["meta"]["provenance"].setdefault("source_locks", [])
    if not any(l.get("source_id") == SRC_ID for l in locks):
        st = FC_PATH.stat()
        locks.append({
            "source_id": SRC_ID, "role": "comparison",
            "path": rel, "sha256": fc_sha,
            "bytes": st.st_size, "mtime_ns": int(st.st_mtime_ns),
        })

    filled = 0
    skipped = 0
    for it in d["items"]:
        if it.get("part") != "投影":
            continue
        bid = it.get("buff_id")
        prov = it.get("provenance") or {}
        if isinstance(bid, int) and bid in fc:
            row = fc[bid]
            cv = row.get("charm_value")
            src_content = row.get("source_content") or ""
            it["charm_value"] = cv
            it["charm_note"] = (f"follow_charm_conf_data.buff_id={bid}.charm_value"
                                + (f"（{src_content}）" if src_content else ""))
            prov["charm_source"] = {
                "source_id": SRC_ID,
                "source_lock_sha256": fc_sha,
                "table": FC_NAME,
                "row_key": bid,
                "field_refs": ["charm_value"],
                "note": src_content,
            }
            it["provenance"] = prov
            filled += 1
        else:
            # buff_id 缺失或不在 follow_charm_conf_data：留空，写明原因，不伪造
            it["charm_value"] = None
            it["charm_note"] = ("follow_charm_conf_data 未命中"
                                "（本条以 buff_data 为源、buff_id 缺失，魅力值待补，不伪造）")
            skipped += 1

    note = ("投影魅力值溯源补齐：来源 com/cdata/follow_charm_conf_data.py"
            "（buff_id 主键，charm_value 字段），与用户锚点 浮游炮/悠游天地=1000、"
            "星河流淌/九尾蓝狐=2000 全部吻合；另 5 个 buff_data 子类投影未命中，留空待补。")
    notes_util.append_note(d, note)
    write_board_pair(BOARD, d)
    print(f"投影魅力回填：命中 {filled} 条，未命中留空 {skipped} 条。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
