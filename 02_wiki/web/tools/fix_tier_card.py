"""修正（十二）板的档位卡，并补一张「画质额外资产」卡。"""
import json
import os
import shutil
import time
from collections import Counter

W = r"E:/la拆包项目/02_wiki/web/data"
BID = "package_entries"
STAMP = time.strftime("%Y%m%d_%H%M%S")

for f in ("manifest.json", "manifest.js", "publication_policy.json", "publication_policy.js",
          "boards/%s.json" % BID, "boards/%s.js" % BID):
    p = os.path.join(W, f)
    if os.path.exists(p):
        shutil.copy2(p, p + ".bak_" + STAMP)
print("已备份")

bj = json.load(open(os.path.join(W, "boards", BID + ".json"), encoding="utf-8"))
items = bj["items"]

# ① 修正原卡
for it in items:
    if it["id"] == "cdn_tier":
        it["name"] = "档位实测 · 小档是索引、大档是资源本体；画质确实带一片独立资产"
        it["desc"] = (
            "抽三层验证：最小档（28MB 整包）里材质与贴图引用全为 0，只是索引与元数据；"
            "内容档（803MB，取前 20MB）有 96 个容器但材质与贴图引用同样为 0；"
            "本地 2.5GB 主图层包全扫也只有 29 条贴图引用。⇒ 省体积可行（每模块最小档合计仅 3.09GB，全量 149.9GB），"
            "但对还原文件名没有帮助，因为材质都在 gpk 里。"
            "★ 修正：画质开关不是四套完整文件集（低画质只是同清单里少下块，省 4.7GB），"
            "但高画质会额外拉 res.textures.layers 这类图层包 —— 那是一片独立资产，见下一张卡。"
        )
        print("已修正 cdn_tier")

# ② 补一张「画质额外资产」
NEW = {
    "id": "cdn_quality_assets",
    "name": "★ 画质额外资产 · 1,028 张地表高清贴图（两套索引都查不到）",
    "desc": ("高画质会额外下载 res.textures.layers 图层包。实测 res.textures.layers.1.1.npk（251MB / 1,099 条）："
             "其中 1,028 张是贴图，解压后 402MB，最大一张 16.7MB（约 4096²）；"
             "尺寸以 512²（496 张）和 1024²（345 张）为主，另有 256²、2048²。"
             "与热更包索引、端游索引的重合都是 0% —— 因为它是基础地表材质，从不进热更包。"
             "内容为泥土、草地、岩石、沙砾、苔藓、雪遮罩与法线图，属场景材质，不是立绘或图标，对图鉴价值低。"),
    "evidence": "structure", "state": "verified", "status_tags": ["verified"],
    "类别": "画质档", "贴图数": 1028, "解压MB": 402,
}
if not any(i["id"] == NEW["id"] for i in items):
    items.append(NEW)
    print("已追加 cdn_quality_assets")

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
print(f"现有 {len(items)} 张卡；json+js 已同步")
