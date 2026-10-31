# -*- coding: utf-8 -*-
r"""回填（一）人物时装·头饰 / 面饰 / 挂饰（并入自 fashion_face 的 face_* 条目）魅力值。

溯源结论：
  这批条目来自独立面容板 fashion_face，行源表是 com/cdata/player_module_appear_data.py，
  该表字段 charm_value 就是魅力值（取值 10 / 15 / 50 / 100 / 200 / 350 …）。
  并入主板时只带了 名称 / 部位，charm_value 没跟过来，导致头饰 111 条、面饰 53 条全空。

规则：
  - 只处理 id 以 "face_" 开头的条目（即 merge 自 fashion_face 的条目），不碰其它部位来源；
  - 以 provenance.row_key 去 player_module_appear_data 取 charm_value；
    取到则写 charm_value + charm_note，并在 provenance 追加独立 charm_source 块
    （不并入 locator_chain，遵守 no-cross-source-field-join）；
  - 源行 charm_value 为 null / 无源行 → 保持空，写明原因，绝不伪造。

幂等：同输入重跑结果不变（取到值就写同一个值）；meta.notes 用 append_note 幂等追加。
"""
from __future__ import annotations

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

TBL = "player_module_appear_data"
TBL_PATH = CD / f"{TBL}.py"
TBL_CHSE = CD / f"{TBL}_chs.py"
SRC_ID = "fashion-face-player_module_appear_data-charm"


def load_table():
    raw = TBL_PATH.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    from toolkit_core import bindict_table as BT
    pool = BT.parse_legacy_chs_pool(TBL_CHSE.read_bytes()) if TBL_CHSE.exists() else {}
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)
    out = {}
    for r in rows:
        v = {k: (vv[1] if isinstance(vv, tuple) else vv) for k, vv in r["values"].items()}
        try:
            out[int(r.get("key"))] = v
        except (TypeError, ValueError):
            continue
    return out


def main() -> int:
    src = load_table()
    d = json.loads(BOARD.read_text(encoding="utf-8"))

    filled = 0
    kept_empty = 0
    no_row = 0
    for it in d["items"]:
        if not str(it.get("id", "")).startswith("face_"):
            continue
        prov = it.setdefault("provenance", {})
        rk = prov.get("row_key")
        try:
            rk = int(rk)
        except (TypeError, ValueError):
            rk = None
        row = src.get(rk) if rk is not None else None
        cv = row.get("charm_value") if row else None
        if cv is None:
            no_row += 1
            it["charm_value"] = None
            it["charm_note"] = (f"{TBL}.charm_value 为空" if row
                                else "该行不在 %s（魅力值待补，不伪造）" % TBL)
            continue
        it["charm_value"] = cv
        it["charm_note"] = f"{TBL}.charm_value（行 {rk}）"
        prov["charm_source"] = {
            "source_id": SRC_ID,
            "source_lock_sha256": prov.get("source_lock_sha256"),
            "table": TBL,
            "row_key": rk,
            "field_refs": ["charm_value"],
        }
        filled += 1
        if it.get("charm_value") == cv:
            kept_empty += 0

    note = ("头饰/面饰/挂饰（并入自 fashion_face 的 face_* 条目）魅力值回填："
            f"来源 {TBL}.charm_value（按 provenance.row_key 取行），"
            f"命中 {filled} 条；源行 charm_value 为空或不在表内的保持留空，不伪造。")
    notes_util.append_note(d, note)
    write_board_pair(BOARD, d)
    print(f"face_* 魅力回填：命中 {filled} 条｜源行为空/无行 {no_row} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
