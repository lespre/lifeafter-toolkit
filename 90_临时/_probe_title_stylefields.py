# -*- coding: utf-8 -*-
"""看称号表里 shining_style / style_icon / special_style / ui_light 等字段的值。只读。"""
import sys, collections, json
sys.path.insert(0, "02_wiki/web/tools")
import build_text_boards as B

rows = B.decode("title_conf_data")
def v(x, k):
    return B.g(x, k)

for f in ("shining_style", "style_icon", "normal_name_icon", "special_style",
          "wear_special_effects", "ui_light", "shining_style_opacity", "ui_chat_visible"):
    vals = [(x["key"], str(v(x, "name")), v(x, f)) for x in rows if v(x, f) not in (None, "")]
    print(f"\n== {f}  非空 {len(vals)}")
    for k, n, val in vals[:8]:
        print("  ", k, n, "->", str(val)[:120])
    if vals:
        c = collections.Counter(str(x[2]) for x in vals)
        print("   取值分布前8:", c.most_common(8))

# shining_style 是否等于 shining_title_conf_data 的 key
sh_keys = {x["key"] for x in B.decode("shining_title_conf_data")}
ss = [v(x, "shining_style") for x in rows if v(x, "shining_style") not in (None, "")]
int_ss = [int(s) for s in ss if str(s).isdigit()]
print("\nshining_style 数值样例:", int_ss[:20])
print("命中 shining 表 key 的比例:", sum(1 for s in int_ss if s in sh_keys), "/", len(int_ss))
