# -*- coding: utf-8 -*-
"""场景/伤害分析页收口：
1) analysis/damage_formula.html 加返回导航（Wiki 首页 / 伤害计算器）
2) 删除孤立静态表 analysis/scene_balance.html（场景平衡统一走 board.html?b=scene_balance）
3) 废弃 tools/render_scene_balance.py 的写盘（改为提示）
"""
from __future__ import annotations

import pathlib

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")

NAV = """<div class="nav" style="position:sticky;top:0;z-index:9;margin:-24px -28px 18px;padding:10px 28px;background:#0e151b;border-bottom:1px solid #1e2b33;display:flex;gap:16px;align-items:center;font-size:12.5px">
<a href="../wiki.html" style="color:#7fb2cc;text-decoration:none">← 返回 Wiki 首页</a>
<a href="../damage.html" style="color:#7fb0c9;text-decoration:none">伤害计算器</a>
<span style="margin-left:auto;color:#5f6b74">静态分析页 · 只读</span>
</div>
"""


def patch_formula() -> None:
    p = WEB / "analysis/damage_formula.html"
    s = p.read_text(encoding="utf-8")
    if 'class="nav"' in s:
        print("damage_formula 已有导航")
        return
    anchor = "<body>"
    i = s.find(anchor)
    if i < 0:
        raise SystemExit("damage_formula 找不到 <body>")
    s = s[: i + len(anchor)] + "\n" + NAV + s[i + len(anchor):]
    p.write_text(s, encoding="utf-8")
    print("damage_formula 已加导航")


def drop_scene_page() -> None:
    p = WEB / "analysis/scene_balance.html"
    if p.is_file():
        p.unlink()
        print("已删除孤立页 analysis/scene_balance.html")
    else:
        print("孤立页不存在")


def deprecate_generator() -> None:
    p = WEB / "tools/render_scene_balance.py"
    if not p.is_file():
        print("生成器不存在")
        return
    s = p.read_text(encoding="utf-8")
    if "已废弃" in s:
        print("生成器已标记废弃")
        return
    head = ('# -*- coding: utf-8 -*-\n'
            '"""【已废弃 2026-10-25】场景加成平衡统一走板块页 board.html?b=scene_balance。\n'
            '本脚本曾生成 analysis/scene_balance.html（无导航的静态表），已删除该页；\n'
            '保留脚本仅作历史参考，不再写盘。\n"""\n')
    body = s.split('"""', 2)[-1] if s.lstrip().startswith("#") or s.lstrip().startswith('"""') else s
    lines = body.splitlines()
    while lines and (lines[0].strip() == "" or lines[0].startswith("from __future__") is False):
        lines.pop(0)
        if lines and lines[0].startswith("from") or (lines and lines[0].startswith("import")):
            break
    p.write_text(head + "\n" + "\n".join(lines) + "\nraise SystemExit('已废弃：统一走 board.html?b=scene_balance')\n",
                 encoding="utf-8")
    print("生成器已标记废弃")


def main() -> int:
    patch_formula()
    drop_scene_page()
    deprecate_generator()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
