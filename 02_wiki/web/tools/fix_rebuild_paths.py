# -*- coding: utf-8 -*-
r"""修 rebuild_wiki_v01.py 里 "str" / "str" 的路径拼接（会 TypeError）。"""
from __future__ import annotations

import pathlib
import re

P = pathlib.Path(r"E:/la拆包项目/02_wiki/web/tools/rebuild_wiki_v01.py")


def main() -> int:
    t = P.read_text(encoding="utf-8")
    # 把 "..." / 包成 Path("...") /
    pat = re.compile(r'(?<!Path\()("(?:[^"\\]|\\.)*")\s*/\s*')
    t2, n = pat.subn(lambda m: "Path(%s) / " % m.group(1), t)
    P.write_text(t2, encoding="utf-8")
    print("包裹", n, "处")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
