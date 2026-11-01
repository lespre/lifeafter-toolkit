# -*- coding: utf-8 -*-
"""称号的档位(style)/参数分布探查。只读。"""
import sys, pathlib, collections
sys.path.insert(0, "02_wiki/web/tools")
import build_text_boards as B

rows = B.decode("title_conf_data")
CD = B.CD
print("title 相关表:", sorted(p.name for p in CD.glob("*title*")))

def v(x, k):
    return B.g(x, k)

print("\nstyle 分布:")
c = collections.Counter(str(v(x, "style")) for x in rows)
print(dict(c))

for s in sorted(c, key=lambda z: (len(z), z)):
    if s == "None":
        continue
    sample = [str(v(x, "name")) for x in rows if str(v(x, "style")) == s][:6]
    print(f"style={s} n={c[s]} 例: {sample}")

print("\nquest_params 样例:")
qp = collections.Counter(str(v(x, "quest_params")) for x in rows)
print(qp.most_common(8))
print("\nbuff_ids 非空:", sum(1 for x in rows if v(x, "buff_ids")))
print("start_times 非空:", sum(1 for x in rows if v(x, "start_times")))
print("\n名称含 '耀' 的样例:", [str(v(x, "name")) for x in rows if "耀" in str(v(x, "name"))][:10])
print("名称含 '炽海' 的样例:", [str(v(x, "name")) for x in rows if "炽海" in str(v(x, "name"))][:10])
