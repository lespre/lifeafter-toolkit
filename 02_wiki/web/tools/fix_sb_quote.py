# -*- coding: utf-8 -*-
"""修 board.html 里 sbRender 的引号语法错误（来源类型那一列）。"""
from __future__ import annotations
import sys

import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

P = pathlib.Path(WEB / "board.html")


def main() -> int:
    s = P.read_text(encoding="utf-8")
    lines = s.splitlines(keepends=True)
    fixed = 0
    for i, ln in enumerate(lines):
        if '来源类型' in ln and 'span' in ln and 'class="tag"' in ln and ln.lstrip().startswith('[""'):
            indent = ln[: len(ln) - len(ln.lstrip())]
            lines[i] = indent + '["", `<span class="tag">${esc(it["来源类型"]||"-")}</span>`],\n'
            fixed += 1
    if not fixed:
        print("未找到目标行")
        return 1
    P.write_text("".join(lines), encoding="utf-8")
    print("修复行数", fixed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
