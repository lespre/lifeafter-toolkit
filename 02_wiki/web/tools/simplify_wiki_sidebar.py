# -*- coding: utf-8 -*-
"""wiki 首页：删掉「显示已归档旧板」入口；状态行只留公开数。"""
import pathlib
import re

p = pathlib.Path("E:/la拆包项目/02_wiki/web/wiki.html")
s = p.read_text(encoding="utf-8")

# 1) 删除侧栏归档开关
s = s.replace('    <label class="arch"><input type="checkbox" id="showArchived"> 显示已归档旧板</label>\n', "", 1)

# 2) 删除事件监听块
m = re.search(r"\n\s*document\.getElementById\('showArchived'\)\.addEventListener\('change', function\(e\)\{[\s\S]*?\}\);\n", s)
if m:
    s = s[:m.start()] + "\n" + s[m.end():]

# 3) 状态行只留公开数
old = """    document.getElementById('gen').textContent =
      '公开 ' + boards + ' · 隔离 ' + (pc.quarantined || 0) + ' · 退休 ' + (pc.retired || 0) +
      ' · 未发布 ' + (pc.unpublished || 0);"""
new = """    document.getElementById('gen').textContent = '公开 ' + boards + ' 个板块';"""
assert old in s
s = s.replace(old, new, 1)

# 4) 常量固定 false（逻辑保留，不再由 UI 控制）
s = s.replace("  var showArchived = false;", "  var showArchived = false;   // 已归档旧板不再提供入口", 1)

p.write_text(s, encoding="utf-8")
print("已改：删除归档开关，状态行只显示公开数")
print("剩余 showArchived 引用:", len(re.findall(r"showArchived", s)))
