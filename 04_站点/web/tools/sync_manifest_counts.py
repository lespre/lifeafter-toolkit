# -*- coding: utf-8 -*-
r"""同步 manifest 里各板块的条目数与分类（以 data/boards/*.json 实际内容为准）。"""
from __future__ import annotations

import json
import pathlib
import re

WEB = pathlib.Path(r"E:/la拆包项目/04_站点/web")
MAN = WEB / "data/manifest.js"
BOARDS = WEB / "data/boards"


def main() -> int:
    t = MAN.read_text(encoding="utf-8")
    m = re.search(r"=\s*(\{.*\});?\s*$", t, re.S)
    d = json.loads(m.group(1))
    changed = []
    for b in d["boards"]:
        p = BOARDS / ("%s.json" % b.get("board"))
        if not p.is_file():
            continue
        bd = json.loads(p.read_text(encoding="utf-8"))
        n = len(bd.get("items") or [])
        cat = (bd.get("meta") or {}).get("category")
        if b.get("items") != n:
            changed.append("%s %s→%s" % (b["board"], b.get("items"), n))
            b["items"] = n
        if cat and b.get("category") != cat:
            b["category"] = cat
    MAN.write_text("window.WIKI_MANIFEST = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n",
                   encoding="utf-8")
    (WEB / "data/manifest.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("更新条目数", len(changed))
    for c in changed:
        print("  ", c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
