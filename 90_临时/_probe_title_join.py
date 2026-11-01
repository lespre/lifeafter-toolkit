# -*- coding: utf-8 -*-
"""验证：动态称号表 key 与称号表 key 的对应关系；desc 是否带图/艺术字引用。只读。"""
import sys, json, collections
sys.path.insert(0, "02_wiki/web/tools")
import build_text_boards as B

rows = B.decode("title_conf_data")
by = {x["key"]: x for x in rows}
print("title key 范围:", min(by), max(by), "行数", len(by))

sh = B.decode("shining_title_conf_data")
ks = [x["key"] for x in sh]
print("shining key 范围:", min(ks), max(ks), "行数", len(ks))
hit = [k for k in ks if k in by]
print("与称号表同 key 的动态称号:", len(hit))
for k in hit[:12]:
    print(k, "|", B.g(by[k], "name"), "| csb:", sh[[x["key"] for x in sh].index(k)]["values"].get("cocos_csb", ("", ""))[1])

print("\ndesc 含 #p( 的称号:", sum(1 for x in rows if "#p(" in str(B.g(x, "desc"))))
print("desc 含 # 控制码的称号:", sum(1 for x in rows if "#" in str(B.g(x, "desc"))))
sample = [str(B.g(x, "desc"))[:90] for x in rows if "#p(" in str(B.g(x, "desc"))][:5]
print("样例:", sample)

print("\nstyle=4 名称:", [str(B.g(x, "name")) for x in rows if str(B.g(x, "style")) == "4"][:20])
print("style=5/6/8:", [(str(B.g(x, "name")), str(B.g(x, "style"))) for x in rows if str(B.g(x, "style")) in ("5", "6", "8")])
