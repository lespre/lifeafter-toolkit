# -*- coding: utf-8 -*-
"""场景平衡卡面收口：把工程数组换成人类可读文本，并把这些键从卡面隐藏。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
BOARD = ROOT / "02_wiki/web/data/boards/scene_balance.json"
HTML = ROOT / "02_wiki/web/board.html"
HIDE = ["scene_ids", "server_types", "source_kinds", "row_keys", "merged_rows"]


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    for it in d["items"]:
        ids = it.get("scene_ids") or []
        sts = it.get("server_types") or []
        sks = it.get("source_kinds") or []
        it["服型"] = " / ".join(s.replace("测试服·", "") for s in sts) or "-"
        it["场景编号"] = "%d 个：%s" % (len(ids), ", ".join(str(x) for x in ids[:8]) + ("…" if len(ids) > 8 else "")) if ids else "-"
        it["来源类型"] = " / ".join(sks) or "-"
    d.setdefault("meta", {})["card_fields_note"] = "卡面只给 服型 / 加成上下限 / 加成区间 / 生效最低攻击 / 场景编号 / 来源类型；工程数组收进技术详情。"
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    s = HTML.read_text(encoding="utf-8")
    line_i = s.index("const FIXED=new Set([")
    line_end = s.index("]);", line_i)
    block = s[line_i:line_end]
    missing = [k for k in HIDE if '"%s"' % k not in block]
    if missing:
        add = "".join(',"%s"' % k for k in missing)
        s = s[:line_end] + add + s[line_end:]
        HTML.write_text(s, encoding="utf-8")
    print("卡面字段已收口；隐藏键新增 %d 个" % len(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
