# -*- coding: utf-8 -*-
"""量化称号的颜色/稀有/动态文本线索覆盖率。只读。"""
import sys, re, collections
sys.path.insert(0, "02_wiki/web/tools")
import build_text_boards as B

rows = B.decode("title_conf_data")
names = [str(B.g(x, "name")) for x in rows]
descs = [str(B.g(x, "desc") or "") for x in rows]

def cnt(pred):
    return sum(1 for n, d in zip(names, descs) if pred(n, d))

checks = {
    "名字含 炫彩": lambda n, d: "炫彩" in n,
    "desc 含 动态/闪光/特效": lambda n, d: any(k in d for k in ("动态", "闪光", "特效")),
    "desc 含 紫色": lambda n, d: "紫色" in d,
    "desc 含 金色": lambda n, d: "金色" in d,
    "desc 含 蓝色": lambda n, d: "蓝色" in d,
    "desc 含 稀有": lambda n, d: "稀有" in d,
    "名字含 金色/紫色/蓝色": lambda n, d: any(k in n for k in ("金色", "紫色", "蓝色")),
}
for k, f in checks.items():
    print(f"{k}: {cnt(f)}")

print("\n名字含炫彩 样例:", [n for n in names if "炫彩" in n][:10])
print("desc含紫色/金色 样例:", [(n, d[:60]) for n, d in zip(names, descs) if ("紫色" in d or "金色" in d)][:8])
print("\ndesc 里出现『称号』前带颜色的短语:")
ph = collections.Counter()
for d in descs:
    for m in re.finditer(r"(紫色|金色|蓝色|绿色|白色|红色|橙色)(基础版|版|的)?称号", d):
        ph[m.group(0)] += 1
print(ph.most_common(10))
