"""给（十二）补 2 张「版本考古」卡 + 在 CDN 报告里补一节。"""
import csv
import json
import os
import shutil
import time
from collections import Counter

W = r"E:/la拆包项目/02_wiki/web/data"
IDX = r"E:/la拆包项目/01_索引与产物/10_索引/热更检测"
BID = "package_entries"
STAMP = time.strftime("%Y%m%d_%H%M%S")

# ── 读时间线，取几个关键数字 ──
tl = list(csv.DictReader(open(IDX + "/CDN版本时间线_按线路.csv", encoding="utf-8-sig")))
alive = list(csv.DictReader(open(IDX + "/CDN历史目录探活.csv", encoding="utf-8-sig")))
n_alive = sum(1 for r in alive if r["存活"] == "200")
earliest = min(r["版本目录"] for r in tl)

def pick(line, idx=-1):
    vs = [r for r in tl if r["线路"] == line and r["平台"] == "newpc"]
    return vs[idx] if vs else None

rel = pick("release")
pt = pick("playertest")

for f in ("manifest.json", "manifest.js", "publication_policy.json", "publication_policy.js",
          "boards/%s.json" % BID, "boards/%s.js" % BID):
    p = os.path.join(W, f)
    if os.path.exists(p):
        shutil.copy2(p, p + ".bak_" + STAMP)
print("已备份")

bj = json.load(open(os.path.join(W, "boards", BID + ".json"), encoding="utf-8"))
items = bj["items"]
have = {i["id"] for i in items}

NEW = [
    {
        "id": "cdn_archaeology",
        "name": f"版本考古 · {n_alive} 个历史目录仍在线，最早回到 {earliest[:4]}-{earliest[4:6]}",
        "desc": (f"历史内容目录没有下线，仍可逐个拉分片清单：端游正式线 9-15→9-17→10-26（条目 441,979→441,980→465,981，"
                 f"最后一次 +{rel['较同线路上一版新增'] if rel else '—'}/-{rel['较同线路上一版移除'] if rel else '—'}）；"
                 f"端游测试线 9-23→9-28→10-15→10-30（最后一次 +{pt['较同线路上一版新增'] if pt else '—'}/-{pt['较同线路上一版移除'] if pt else '—'}）；"
                 "安卓测试线 10-14→10-30 增加 116,445 条。"
                 "★ 必须按「平台＋线路」分组相减——跨线路相减会得到几十万的假差集。"),
        "evidence": "structure", "state": "verified", "status_tags": ["verified"],
        "类别": "版本考古", "存活目录": n_alive,
    },
    {
        "id": "cdn_archaeology_naming",
        "name": "★ 版本考古对还原文件名没用（三条依据）",
        "desc": ("第一，分片清单是纯 8 字节标识数组，里面没有名字；第二，历史目录只放分片清单与覆盖包，不放资源容器本体；"
                 "第三，名字来源（界面清单、材质引用）全在资源容器里，与目录属哪个版本无关。"
                 "⇒ 版本考古记在「溯源账」：能回答某资源首次出现在哪一版、每版真实增删多少，但不产生任何文件名。"),
        "evidence": "structure", "state": "verified", "status_tags": ["verified"],
        "类别": "纪律",
    },
]

added = 0
for it in NEW:
    if it["id"] not in have:
        items.append(it)
        added += 1

bj["meta"]["state_summary"] = dict(Counter(i["state"] for i in items))
json.dump(bj, open(os.path.join(W, "boards", BID + ".json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(W, "boards", BID + ".js"), "w", encoding="utf-8") as fp:
    fp.write("window.WIKI_BOARD_%s = " % BID)
    json.dump(bj, fp, ensure_ascii=False)
    fp.write(";\ntry{document.body.classList.add('doc-mode');}catch(e){}\n")

mani = json.load(open(os.path.join(W, "manifest.json"), encoding="utf-8"))
for b in mani["boards"]:
    if b.get("board") == BID:
        b["items"] = len(items)
        b["state_summary"] = bj["meta"]["state_summary"]
pol = json.load(open(os.path.join(W, "publication_policy.json"), encoding="utf-8"))
if BID in pol["boards"]:
    pol["boards"][BID]["items"] = len(items)

json.dump(mani, open(os.path.join(W, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(pol, open(os.path.join(W, "publication_policy.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for fn, var, obj in (("manifest.js", "WIKI_MANIFEST", mani), ("publication_policy.js", "WIKI_PUBLICATION_POLICY", pol)):
    with open(os.path.join(W, fn), "w", encoding="utf-8") as fp:
        fp.write("window.%s = " % var)
        json.dump(obj, fp, ensure_ascii=False)
        fp.write(";\n")
print(f"追加 {added} 张，现有 {len(items)} 张；json+js 已同步")

# ── 报告补一节 ──
md = IDX + "/CDN目录清单_分类_20261101.md"
lines = ["", "---", "", "## 十、版本考古（实测：30 个历史目录全部在线）", "",
         "| 平台/线路 | 版本 | 条目 | 较同线路上一版 |", "|---|---|---|---|"]
for r in tl:
    add = r["较同线路上一版新增"]
    rm = r["较同线路上一版移除"]
    delta = f"+{add} / -{rm}" if add not in ("", None) else "—"
    lines.append(f"| {r['平台']}/{r['线路']} | {r['版本目录'][:15]} | {int(r['条目']):,} | {delta} |")
lines += ["", "**纪律**：只有同一「平台+线路」的相邻两版才能相减；跨线路相减会得到几十万条假差集（首版实测踩到过）。", "",
          "**对命名的结论**：没用。分片清单是纯标识数组、历史目录不放资源容器本体、名字来源都在资源容器里 —— 版本考古只回答「哪版出现/增删多少」，不产生文件名。", ""]
open(md, "a", encoding="utf-8").write("\n".join(lines))
print("报告已补第十节")
