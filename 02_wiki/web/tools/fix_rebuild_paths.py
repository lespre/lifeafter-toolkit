# -*- coding: utf-8 -*-
r"""修 rebuild_wiki_v01.py 里 "str" / "str" 的路径拼接（会 TypeError）。"""
from __future__ import annotations
import sys

import pathlib
import re

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

P = pathlib.Path(WEB / "tools/rebuild_wiki_v01.py")


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
