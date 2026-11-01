"""给（十二）包体入口与版本线补 6 张 CDN 目录卡，并同步全部清单。"""
import json
import os
import shutil
import time
from collections import Counter

W = r"E:/la拆包项目/02_wiki/web/data"
BID = "package_entries"
STAMP = time.strftime("%Y%m%d_%H%M%S")

for f in ("wiki_taxonomy.json", "manifest.json", "manifest.js", "publication_policy.json",
          "publication_policy.js", "boards/%s.json" % BID, "boards/%s.js" % BID):
    p = os.path.join(W, f)
    if os.path.exists(p):
        shutil.copy2(p, p + ".bak_" + STAMP)
print("已备份")

bj = json.load(open(os.path.join(W, "boards", BID + ".json"), encoding="utf-8"))
items = bj["items"]
have = {i["id"] for i in items}

NEW = [
    {
        "id": "cdn_total",
        "name": "CDN 目录五分类 · 3,428 条 / 246.4 GB",
        "desc": "把安卓测试线与端游测试线两份版本清单合并去重后，全站可下东西分五类：资源层包 2,231 条 220.9GB（占 90%）、包体容器 102 条 21.4GB、引擎与可执行 1,056 条 4.0GB、补丁分片 38 条 0.05GB。",
        "evidence": "structure", "state": "verified", "status_tags": ["verified"],
        "类别": "目录总览", "条目": 3428, "总量GB": 246.4,
    },
    {
        "id": "cdn_layers",
        "name": "资源层包按模块 · 模型最重、多语言最小",
        "desc": "命名规律「模块.图层.分块[.分卷]」。体积前六：模型 50.2GB／角色 47.7GB／场景带宽 25.7GB／界面图层 23.5GB／场景 22.2GB／高清模型 18.9GB。小模块里武器 1.65GB、界面动画 2.3GB、多语言 3.3GB。",
        "evidence": "structure", "state": "verified", "status_tags": ["verified"],
        "类别": "资源层包", "模块数": 183,
    },
    {
        "id": "cdn_tier",
        "name": "档位实测 · 最小档是索引，内容档也不含材质",
        "desc": "抽三层验证：最小档（28MB 整包）里材质与贴图引用全为 0，只是索引与元数据；内容档（803MB，取前 20MB）有 96 个容器但材质与贴图引用同样为 0；本地 2.5GB 主图层包全扫也只有 29 条贴图引用。⇒ 省体积可行（每模块最小档合计仅 3.09GB，全量 149.9GB），但对还原文件名没有帮助，因为材质都在 gpk 里。",
        "evidence": "structure", "state": "verified", "status_tags": ["verified"],
        "类别": "档位机制", "最小档GB": 3.09, "全量GB": 149.9,
    },
    {
        "id": "cdn_abi",
        "name": "引擎四套变体 · 只需匹配本机那一套",
        "desc": "运行库按 ABI 与系统兼容线切成四套：x64（275 个）、x64-2（251）、x64-3（276）、x64-win7（251），合计 4.0GB。同一批 dll 的四份，实际只需要与机器匹配的一套。",
        "evidence": "structure", "state": "verified", "status_tags": ["verified"],
        "类别": "引擎", "套数": 4,
    },
    {
        "id": "cdn_patch",
        "name": "补丁分片 · 18 个里 9 个是空占位",
        "desc": "每个版本 18 个分片清单，但其中 5/6/7/9/10/11/12/14/17 这九个只有 8 字节（空占位），真内容只落在 pkg_1/2/3/4/8/13/15/16/18。分片清单本身是全站最小的一类，合计 50MB。",
        "evidence": "structure", "state": "verified", "status_tags": ["verified"],
        "类别": "补丁分片", "空占位": 9,
    },
    {
        "id": "cdn_recipe",
        "name": "★ 下载配方 · 三个关键参数缺一就 404",
        "desc": "请求头必须带客户端标识：UA 用 Orbit/1.0、加 X-NTES-PROJECT: 66，否则一律 404。资源层包的目录用清单里的 version 字段（如 20261020_080153_playertest_android），而补丁分片用内容目录（如 20261030_182900_playertest_newpc）——两套目录不能混用。支持 Range 断点续传与分片采样。",
        "evidence": "structure", "state": "verified", "status_tags": ["verified"],
        "类别": "操作配方",
    },
]

added = 0
for it in NEW:
    if it["id"] not in have:
        items.append(it)
        added += 1

bj["meta"]["state_summary"] = dict(Counter(i["state"] for i in items))
bj["meta"]["notes"] = ("结论：包体入口不是一个数——国内 47 个真入口（另有 18 个假 200 占位）、海外 63 个。"
                       "最新构建永远在国内提前测试线；海外没有测试服体系。"
                       "CDN 全站 3,428 条 / 246.4GB，按类别取用即可：补名字不需要下任何资源层包，"
                       "要资源本体只需取对应模块的内容档，每个模块最小档合计仅 3.09GB。")

json.dump(bj, open(os.path.join(W, "boards", BID + ".json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(W, "boards", BID + ".js"), "w", encoding="utf-8") as fp:
    fp.write("window.WIKI_BOARD_%s = " % BID)
    json.dump(bj, fp, ensure_ascii=False)
    fp.write(";\ntry{document.body.classList.add('doc-mode');}catch(e){}\n")
print(f"追加 {added} 张卡，现有 {len(items)} 张")

# 同步 manifest / policy（json 与 js 一起写）
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
with open(os.path.join(W, "manifest.js"), "w", encoding="utf-8") as fp:
    fp.write("window.WIKI_MANIFEST = ")
    json.dump(mani, fp, ensure_ascii=False)
    fp.write(";\n")
with open(os.path.join(W, "publication_policy.js"), "w", encoding="utf-8") as fp:
    fp.write("window.WIKI_PUBLICATION_POLICY = ")
    json.dump(pol, fp, ensure_ascii=False)
    fp.write(";\n")
print("manifest / policy 的 json+js 已同步")
