# -*- coding: utf-8 -*-
r"""按「内部部位代码」重分 fashion_wardrobe 里来自 fashion_face 的条目。

判定规则（唯一口径，可复算）：
  player_module_appear_data.part 是游戏内部部位代码，描述文字不可信：
    part == 2       -> 头饰
    part == 20001   -> 面饰
    part == 1       -> 挂饰
    其他 / 无源行    -> 保持不变（含已知的 3 个无源行跳过项）

只动 id 以 "face_" 开头的条目（即 merge 自 fashion_face 的条目），不碰其它部位来源。
幂等：同输入重跑结果不变；meta.notes 用 append_note 幂等追加。
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

# 内部部位代码 -> 部位名
PART_MAP = {2: "头饰", 20001: "面饰", 1: "挂饰"}


def load_appear_src():
    p = CD / "player_module_appear_data.py"
    c = CD / "player_module_appear_data_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    from toolkit_core import bindict_table as BT
    pool = BT.parse_legacy_chs_pool(c.read_bytes()) if c.exists() else {}
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)
    src = {}
    for r in rows:
        d = {k: (vv[1] if isinstance(vv, tuple) else vv) for k, vv in r["values"].items()}
        try:
            src[int(r.get("key"))] = d
        except (TypeError, ValueError):
            src[r.get("key")] = d
    return src


def main() -> int:
    src = load_appear_src()
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]

    moved = {k: 0 for k in PART_MAP.values()}
    unchanged = 0
    no_src = 0
    for it in items:
        if not str(it.get("id", "")).startswith("face_"):
            continue
        rk = (it.get("provenance") or {}).get("row_key")
        try:
            rki = int(rk)
        except (TypeError, ValueError):
            rki = rk
        sd = src.get(rki)
        if sd is None:
            no_src += 1
            continue
        code = sd.get("part")
        bucket = PART_MAP.get(code)
        if bucket is None:
            unchanged += 1
            continue
        if it.get("part") != bucket:
            moved[bucket] += 1
        it["part"] = bucket
        it["part_bucket"] = [bucket]

    note = ("按内部部位代码重分 face_* 条目：player_module_appear_data.part "
            "2->头饰, 20001->面饰, 1->挂饰（描述文字不可信，已弃用）。")
    notes_util.append_note(d, note)
    write_board_pair(BOARD, d)  # 一次性写回 .json + .js（含 note），保持二者一致

    print("重分结果（相对当前改动计数）：")
    for b, n in moved.items():
        print(f"  -> {b}: 本次变更 {n} 条")
    print(f"  无源行跳过: {no_src}")
    print(f"  其它代码/不变: {unchanged}")
    # 最终计数
    from collections import Counter
    cc = Counter(i.get("part") for i in d["items"])
    print("最终各部位条数:", dict(cc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
