# -*- coding: utf-8 -*-
"""修正上一轮被 \f 转义破坏的路径，并处理剩余三类声明。"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
BS = chr(92)
FASHION_EXPORT = "com" + BS + "cdata" + BS + "fashion_data_for_export.py"
FASHION = "com" + BS + "cdata" + BS + "fashion_data.py"


def fix_board(name, fn):
    p = WEB / "data/boards" / (name + ".json")
    if not p.is_file():
        return 0
    d = json.loads(p.read_text(encoding="utf-8"))
    n = 0
    for it in d.get("items", []):
        pr = it.get("provenance") or {}
        if fn(pr):
            n += 1
    if n:
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        (WEB / "data/boards" / (name + ".js")).write_text(
            "window.WIKI_BOARD_%s = %s;" % (name, json.dumps(d, ensure_ascii=False, indent=1)),
            encoding="utf-8")
    return n


def main() -> int:
    # 1) 修复被 \f 破坏的路径
    def fix_ff(pr):
        t = pr.get("table")
        if t and "fashion_data_for_export.py" in t and "cdata" not in t:
            pr["table"] = FASHION_EXPORT
            return True
        if t and t.endswith("cdata") is False and "cdata" in t and chr(12) in t:
            pr["table"] = FASHION_EXPORT
            return True
        return False

    print("fashion_identity_unresolved_v01 修复", fix_board("fashion_identity_unresolved_v01", fix_ff))

    # 2) unknown.py → fashion_data.py
    def fix_unknown(pr):
        if (pr.get("table") or "").endswith("unknown.py"):
            pr["table_raw"] = pr["table"]
            pr["table"] = FASHION
            return True
        return False

    print("fashion_wardrobe unknown 修复", fix_board("fashion_wardrobe", fix_unknown))

    # 3) lottery_periods 归档自引用
    def fix_archive(pr):
        if "lottery_periods(archive)" == (pr.get("table") or ""):
            pr["table_status"] = "archive-self"
            pr["table_note"] = "本站归档板（非源表），期次信息由 huodong_conf 回证"
            return True
        return False

    print("lottery_periods 归档标注", fix_board("lottery_periods", fix_archive))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
