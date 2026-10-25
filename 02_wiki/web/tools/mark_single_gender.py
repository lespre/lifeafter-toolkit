# -*- coding: utf-8 -*-
"""标记「单性别款」：player_appear_data 里 force_gender 有值的 model ⇒ 只做一种性别，不追男图。"""
from __future__ import annotations

import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
v = lambda x: x[1] if isinstance(x, tuple) else x


def main() -> int:
    raw = (CD / "player_appear_data.py").read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    pool = BT.parse_legacy_chs_pool((CD / "player_appear_data_chs.py").read_bytes())
    rows = BT.decode_table_rows(raw[at + 6:at + 6 + L], pool, resolve_jumps=False, lenient=True)[0]

    forced = {}
    for r in rows:
        val = r["values"]
        fg = v(val.get("force_gender"))
        mid = v(val.get("model_id"))
        if fg is not None and mid is not None:
            forced[str(mid)] = str(fg)
    print("force_gender 锁定的 model 数", len(forced))

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    marked = 0
    for it in board["items"]:
        mid = str(it.get("model_id"))
        if mid in forced:
            it["gender_scope"] = "仅单性别（force_gender=%s）" % forced[mid]
            it.setdefault("gender_scope_note",
                          "player_appear_data 该 model 带 force_gender=%s ⇒ 游戏只做一种性别，"
                          "没有另一性别的图" % forced[mid])
            marked += 1
    board["meta"]["notes"] = str(board["meta"].get("notes") or "") + \
        "\n\n【单性别款】%d 张卡的 model 在 player_appear_data 带 force_gender，游戏只做一种性别（如 不湮之花、白月魁、嘉心予梦、贝极星愿、琳夜柔歌），不追男图。" % marked
    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    print("标记单性别款 %d 张" % marked)

    samples = [i["name"] for i in board["items"] if i.get("gender_scope")][:12]
    print("样例:", samples)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
