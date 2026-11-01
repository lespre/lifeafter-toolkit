"""把新板登记进发布策略（默认拒绝，必须显式放行），并同步 .js 副本。"""
import json
import os
import shutil
import time

W = r"E:/la拆包项目/02_wiki/web/data"
BID = "name_restore_method"
STAMP = time.strftime("%Y%m%d_%H%M%S")

for f in ("publication_policy.json", "publication_policy.js"):
    p = os.path.join(W, f)
    if os.path.exists(p):
        shutil.copy2(p, p + ".bak_" + STAMP)
print("备份完成")

p = os.path.join(W, "publication_policy.json")
d = json.load(open(p, encoding="utf-8"))
d["boards"][BID] = {
    "publication_status": "published",
    "category": "三、综合资料 / （十）文件名还原方法论",
    "reason": "方法论板：文件名还原的十一条路径与实测命中数（本会话实测，脚本可复跑）。结论 3,600/7,192=50.1%；有效 5 条、证伪 6 条、未做 1 条。只记录方法与数字，不含未验证结论。",
    "items": 12,
    "generated": "2026-11-01",
}
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("policy 已登记，published 总数", sum(1 for v in d["boards"].values() if v.get("publication_status") == "published"))

# 同步 .js
with open(os.path.join(W, "publication_policy.js"), "w", encoding="utf-8") as fp:
    fp.write("window.WIKI_PUBLICATION_POLICY = ")
    json.dump(d, fp, ensure_ascii=False)
    fp.write(";\n")

# taxonomy 的 .js 也同步（前面只改了 .json）
t = json.load(open(os.path.join(W, "wiki_taxonomy.json"), encoding="utf-8"))
with open(os.path.join(W, "wiki_taxonomy.js"), "w", encoding="utf-8") as fp:
    fp.write("window.WIKI_TAXONOMY = ")
    json.dump(t, fp, ensure_ascii=False)
    fp.write(";\n")
print("js 副本已同步")
