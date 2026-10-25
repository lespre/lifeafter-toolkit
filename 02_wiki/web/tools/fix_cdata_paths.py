# -*- coding: utf-8 -*-
"""cdata 归一后修引用：把硬编码的 配置_增量快照 / 配置_基线包 指向唯一一份 配置。

只改 .py（工具代码），不改产物/文档正文里的历史叙述。
"""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path("E:/la拆包项目")
DIRS = [ROOT / "00_规范与工具", ROOT / "02_wiki", ROOT / "01_索引与产物/10_索引"]
REPL = [
    ("41_还原树/pe/配置/com/cdata", "41_还原树/pe/配置/com/cdata"),
    ("41_还原树\\\\pe\\\\配置_增量快照\\\\com\\\\cdata", "41_还原树\\\\pe\\\\配置\\\\com\\\\cdata"),
    ("41_还原树/pe/配置/com/cdata", "41_还原树/pe/配置/com/cdata"),
    ("41_还原树\\\\pe\\\\配置_基线包\\\\com\\\\cdata", "41_还原树\\\\pe\\\\配置\\\\com\\\\cdata"),
]


def main() -> int:
    changed, files = 0, []
    for base in DIRS:
        if not base.is_dir():
            continue
        for p in base.rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            try:
                s = p.read_text(encoding="utf-8")
            except Exception:  # noqa: BLE001
                continue
            o = s
            for a, b in REPL:
                s = s.replace(a, b)
            if s != o:
                p.write_text(s, encoding="utf-8")
                changed += sum(o.count(a) for a, _ in REPL)
                files.append(str(p.relative_to(ROOT)))
    print("改动引用 %d 处，涉及文件 %d 个" % (changed, len(files)))
    for f in files[:10]:
        print("  ", f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
