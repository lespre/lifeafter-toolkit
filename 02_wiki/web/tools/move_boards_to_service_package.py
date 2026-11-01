"""把 6 块板从「三、综合资料」迁到新顶层「四、服务与包体」，两边都重排编号。"""
import json
import os
import re
import shutil
import time

W = r"E:/la拆包项目/02_wiki/web/data"
STAMP = time.strftime("%Y%m%d_%H%M%S")
NEW_TOP = "四、服务与包体"
MOVED = [
    ("server_types", "服务器类型"),
    ("cdn_library", "CDN 资源库"),
    ("local_restore_tree", "本地还原树"),
    ("name_restore_method", "文件名还原方法论"),
    ("server_whitelist", "测试服与白名单"),
    ("package_entries", "包体入口与版本线"),
]
MOVED_IDS = {m[0] for m in MOVED}
CN = "一二三四五六七八九十"


def num_cn(i: int) -> str:
    return CN[i] if i < 10 else CN[10] + ""


def strip_num(s: str) -> str:
    return re.sub(r"^（[一二三四五六七八九十]+）", "", s).strip()


for f in ("wiki_taxonomy.json", "wiki_taxonomy.js", "manifest.json", "manifest.js",
          "publication_policy.json", "publication_policy.js"):
    p = os.path.join(W, f)
    if os.path.exists(p):
        shutil.copy2(p, p + ".bak_" + STAMP)
print("已备份")

tax = json.load(open(os.path.join(W, "wiki_taxonomy.json"), encoding="utf-8"))
node3 = next(n for n in tax["树"] if n.get("name", "").startswith("三、综合资料"))
keep = [c for c in node3["children"] if not (set(c.get("boards", [])) & MOVED_IDS)]
moved = [c for c in node3["children"] if set(c.get("boards", [])) & MOVED_IDS]
print(f"三、综合资料：保留 {len(keep)} 项，迁出 {len(moved)} 项")

# 原节点重编号
for i, c in enumerate(keep):
    c["name"] = f"（{num_cn(i)}）{strip_num(c['name'])}"
node3["children"] = keep

# 新顶层：按 MOVED 顺序排（只收真存在的板）
label_of = {}
for c in moved:
    for b in c.get("boards", []):
        label_of[b] = strip_num(c["name"])
new_children = []
for i, (bid, default_label) in enumerate(MOVED, 1):
    if not any(bid in c.get("boards", []) for c in moved):
        print(f"  ⚠ 跳过（原树里没有）: {bid}")
        continue
    new_children.append({"name": f"（{num_cn(i-1)}）{label_of.get(bid, default_label)}", "boards": [bid]})

# 若已存在同名顶层，先移除旧的（幂等）
tax["树"] = [n for n in tax["树"] if not n.get("name", "").startswith(NEW_TOP)]
# 插在「三、综合资料」之后
idx = next(i for i, n in enumerate(tax["树"]) if n.get("name", "").startswith("三、综合资料"))
tax["树"].insert(idx + 1, {"id": "service_package", "name": NEW_TOP, "boards": [], "children": new_children})
print(f"新顶层「{NEW_TOP}」下挂 {len(new_children)} 块")

# 更新各板 meta.category
for i, child in enumerate(new_children):
    bid = child["boards"][0]
    cat = f"{NEW_TOP} / {child['name']}"
    for fn in ("boards/%s.json" % bid,):
        p = os.path.join(W, fn)
        bj = json.load(open(p, encoding="utf-8"))
        bj["meta"]["category"] = cat
        json.dump(bj, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        with open(p.replace(".json", ".js"), "w", encoding="utf-8") as fp:
            fp.write("window.WIKI_BOARD_%s = " % bid)
            json.dump(bj, fp, ensure_ascii=False)
            fp.write(";\ntry{document.body.classList.add('doc-mode');}catch(e){}\n")
    print(f"  {bid} → {cat}")

# 三、综合资料里保留的板，category 也要跟着改编号
keep_map = {}
for c in keep:
    for b in c.get("boards", []):
        keep_map[b] = f"三、综合资料 / {c['name']}"
for bid, cat in keep_map.items():
    p = os.path.join(W, "boards", bid + ".json")
    if not os.path.exists(p):
        continue
    bj = json.load(open(p, encoding="utf-8"))
    if bj["meta"].get("category") != cat:
        bj["meta"]["category"] = cat
        json.dump(bj, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        with open(p.replace(".json", ".js"), "w", encoding="utf-8") as fp:
            fp.write("window.WIKI_BOARD_%s = " % bid)
            json.dump(bj, fp, ensure_ascii=False)
            fp.write(";\n")

# manifest / policy 的 category 同步
new_cat = {}
for child in tax["树"]:
    for c in child.get("children", []) + [child]:
        for b in c.get("boards", []):
            new_cat[b] = f"{child['name']} / {c['name']}" if c is not child else child["name"]

mani = json.load(open(os.path.join(W, "manifest.json"), encoding="utf-8"))
for b in mani["boards"]:
    if b["board"] in new_cat:
        b["category"] = new_cat[b["board"]]
pol = json.load(open(os.path.join(W, "publication_policy.json"), encoding="utf-8"))
for bid, cat in new_cat.items():
    if bid in pol["boards"]:
        pol["boards"][bid]["category"] = cat

json.dump(tax, open(os.path.join(W, "wiki_taxonomy.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(mani, open(os.path.join(W, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(pol, open(os.path.join(W, "publication_policy.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for fn, var, obj in (("wiki_taxonomy.js", "WIKI_TAXONOMY", tax),
                     ("manifest.js", "WIKI_MANIFEST", mani),
                     ("publication_policy.js", "WIKI_PUBLICATION_POLICY", pol)):
    with open(os.path.join(W, fn), "w", encoding="utf-8") as fp:
        fp.write("window.%s = " % var)
        json.dump(obj, fp, ensure_ascii=False)
        fp.write(";\n")

print("\n=== 新结构 ===")
for n in tax["树"]:
    print(f"[{n['name']}]")
    for c in n.get("children", []):
        print(f"    {c['name']}: {c['boards']}")
print("\n三份 .js 已同步")
