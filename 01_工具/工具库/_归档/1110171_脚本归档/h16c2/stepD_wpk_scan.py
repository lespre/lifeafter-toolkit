# -*- coding: utf-8 -*-
"""task-92 D：effect<N>.wpk 下载坐标侦察（只读）。
扫 version.ini / launcher_conf / mrzh_installer.txt / pkg_left_files / cloud.json /
downloaded_packages / download_*_patch / ext_pack_config / multi_cloud1|2 / extract / configs。
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DOC = r"E:\LifeAfter\Documents"
LF = r"E:\LifeAfter"
OUT = r"E:\la拆包项目\03拆包产物\_target_1110171\h16c2"
os.makedirs(OUT, exist_ok=True)
res = {"dirs": {}, "text_files": {}, "wpk_refs": [], "effect_refs": [], "urls": [], "notes": []}

def rd(p, n=400000):
    d = open(p, "rb").read(n)
    for enc in ("utf-8", "gbk"):
        try: return d.decode(enc), enc
        except Exception: pass
    return d.decode("latin1"), "latin1"

# 1) 目录清单（两级）
for root in (os.path.join(DOC, "multi_cloud1"), os.path.join(DOC, "multi_cloud2"),
             os.path.join(LF, "Documents", "multi_cloud1"), os.path.join(DOC, "extract"),
             os.path.join(LF, "Documents", "extract"), os.path.join(DOC, "configs")):
    if not os.path.isdir(root):
        res["dirs"][root] = "MISSING"; continue
    lst = []
    for dp, dn, fn in os.walk(root):
        for f in fn:
            fp = os.path.join(dp, f)
            try: lst.append({"rel": os.path.relpath(fp, root), "bytes": os.path.getsize(fp)})
            except Exception: pass
        if len(lst) > 4000: break
    res["dirs"][root] = {"n_files": len(lst), "sample": lst[:40],
                         "wpk": [x for x in lst if x["rel"].lower().endswith(".wpk")]}

# 2) 小配置文件全文
for p in ("version.ini", "launcher_conf", "mrzh_installer.txt", "Documents/client.ini",
          "Documents/cloud.json", "Documents/downloaded_packages", "Documents/download_futuretest_patch",
          "Documents/download_gray_patch", "Documents/download_playertest_patch",
          "Documents/download_playertest_kol_zy_patch", "Documents/ext_pack_config",
          "Documents/pkg_left_files", "Documents/multi_cloud1", "Documents/fo_version",
          "Documents/cfs_version", "Documents/compress_pc", "Documents/file_hash_pack.bin"):
    fp = os.path.join(LF, p)
    if not os.path.exists(fp): res["text_files"][p] = "MISSING"; continue
    sz = os.path.getsize(fp)
    if os.path.isdir(fp): res["text_files"][p] = "DIR"; continue
    if sz > 400000: res["text_files"][p] = {"bytes": sz, "note": "too_big_skip"}; continue
    t, enc = rd(fp)
    res["text_files"][p] = {"bytes": sz, "enc": enc, "head": t[:1200]}
    for m in re.finditer(r'[^\s"\'<>]{0,120}\.wpk[^\s"\'<>]{0,80}', t, re.I):
        res["wpk_refs"].append({"file": p, "text": m.group(0)[:200]})
    for m in re.finditer(r'[^\s"\'<>]{0,80}effect[^\s"\'<>]{0,120}', t, re.I):
        res["effect_refs"].append({"file": p, "text": m.group(0)[:200]})
    for m in re.finditer(r'https?://[^\s"\'<>]{4,200}', t):
        res["urls"].append({"file": p, "url": m.group(0)[:220]})

# 3) 全盘找 effect*.wpk 实体 + effect1..N 名引用
res["wpk_on_disk"] = []
for root in (r"E:\LifeAfter", r"E:\mrzh"):
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if f.lower().endswith(".wpk"):
                fp = os.path.join(dp, f)
                try: res["wpk_on_disk"].append({"path": fp, "bytes": os.path.getsize(fp)})
                except Exception: pass
res["effect_wpk_on_disk"] = [x for x in res["wpk_on_disk"] if re.search(r'effect\d+\.wpk$', x["path"], re.I)]
json.dump(res, open(os.path.join(OUT, "stepD_wpk_scan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("=== D 侦察 ===")
print("wpk 实体数:", len(res["wpk_on_disk"]), "| 其中 effect<N>.wpk:", len(res["effect_wpk_on_disk"]))
for x in res["effect_wpk_on_disk"]: print("   ", x)
print("config 文件里 .wpk 引用:", len(res["wpk_refs"]), "| effect 引用:", len(res["effect_refs"]), "| URL:", len(res["urls"]))
for x in res["wpk_refs"][:12]: print("   wpk_ref:", x["file"], "|", x["text"][:150])
for x in res["urls"][:8]: print("   url:", x["file"], "|", x["url"][:150])
for k, v in res["text_files"].items():
    if isinstance(v, dict) and "head" in v: print("   %-46s %7d B enc=%s head=%s" % (k, v["bytes"], v["enc"], v["head"][:90].replace("\n", "⏎")))
print("[out] h16c2/stepD_wpk_scan.json")
