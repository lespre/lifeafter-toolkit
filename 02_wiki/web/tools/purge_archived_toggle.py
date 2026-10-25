# -*- coding: utf-8 -*-
"""彻底清掉 wiki.html 里 showArchived（已归档旧板）相关代码分支。"""
import pathlib
import re

p = pathlib.Path("E:/la拆包项目/02_wiki/web/wiki.html")
s = p.read_text(encoding="utf-8")
before = len(re.findall(r"showArchived", s))

# 删除 3 处 else if(showArchived ...) 整行
s = re.sub(r"\n\s*else if\(showArchived[^\n]*\n", "\n", s)

# 删除变量声明及其注释
s = re.sub(r"\n\s*var showArchived = false;[^\n]*\n", "\n", s)

after = len(re.findall(r"showArchived", s))
p.write_text(s, encoding="utf-8")
print("showArchived 引用 %d → %d" % (before, after))
leftover = [i + 1 for i, line in enumerate(s.splitlines()) if "showArchived" in line]
print("残留行号:", leftover)
