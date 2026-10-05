# -*- coding: utf-8 -*-
"""task-92 D-2：cloud.json 全文 / configs·Record·client_doc 目录 / http 串搜索 / launcher_conf 单字节混淆暴力。只读。"""
import json, os, re, sys, glob
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
DOC = r"E:\LifeAfter\Documents"; LF = r"E:\LifeAfter"
OUT = r"E:\la拆包项目\03拆包产物\_target_1110171\h16c2"
res = {}
# 1) cloud.json 全文 + client.ini
for p in ("cloud.json", "client.ini", "ext_pack_config", "downloaded_packages", "bindict_mmap_enabled"):
    fp = os.path.join(DOC, p)
    if os.path.exists(fp) and os.path.getsize(fp) < 200000:
        res[p] = open(fp, "rb").read().decode("utf-8", "replace")
# 2) configs / Record / client_doc@* 目录清单
for sub in ("configs", "Record"):
    fp = os.path.join(DOC, sub)
    lst = []
    if os.path.isdir(fp):
        for dp, dn, fn in os.walk(fp):
            for f in fn[:200]:
                x = os.path.join(dp, f)
                try: lst.append({"rel": os.path.relpath(x, fp), "bytes": os.path.getsize(x)})
                except Exception: pass
    res["dir_" + sub] = {"n": len(lst), "sample": lst[:60]}
docs = sorted(glob.glob(os.path.join(DOC, "client_doc@*")))
res["client_doc_dirs"] = {"n": len(docs), "sample": [os.path.basename(d) for d in docs[:8]]}
if docs:
    d0 = docs[-1]
    lst = []
    for dp, dn, fn in os.walk(d0):
        for f in fn[:100]:
            x = os.path.join(dp, f)
            try: lst.append({"rel": os.path.relpath(x, d0), "bytes": os.path.getsize(x)})
            except Exception: pass
    res["client_doc_sample"] = {"dir": d0, "n": len(lst), "sample": lst[:60]}
# 3) http/wpk 串搜索（有界）
hits = []
roots = [DOC, LF]
seen = 0; scanned = 0
for root in roots:
    for dp, dn, fn in os.walk(root):
        if dp.count(os.sep) - root.count(os.sep) > 2: continue
        for f in fn:
            x = os.path.join(dp, f)
            try:
                sz = os.path.getsize(x)
            except Exception: continue
            if sz == 0 or sz > 300000: continue
            if x.lower().endswith((".dll", ".exe", ".npk", ".wpk", ".gpk", ".fpk", ".zip")): continue
            seen += 1; scanned += sz
            try: b = open(x, "rb").read()
            except Exception: continue
            for pat in (b"http://", b"https://", b".wpk", b"effect3", b"effect1", b"cdn", b"patch"):
                if pat in b:
                    hits.append({"file": x, "pat": pat.decode(), "bytes": sz})
                    break
res["text_scan"] = {"files_scanned": seen, "bytes_scanned": scanned, "hits": hits[:80], "n_hits": len(hits)}
# 4) launcher_conf 单字节 XOR / 加法暴力
lp = os.path.join(LF, "launcher_conf")
b = open(lp, "rb").read()
def score(t):
    if not t: return 0
    ok = sum(1 for c in t if 32 <= c < 127 or c in (10, 13, 9))
    return ok / len(t)
best = []
for k in range(256):
    x = bytes(c ^ k for c in b); best.append(("xor%02x" % k, round(score(x), 3), x[:60]))
    y = bytes((c + k) & 0xFF for c in b); best.append(("add%02x" % k, round(score(y), 3), y[:60]))
best.sort(key=lambda z: -z[1])
res["launcher_conf"] = {"bytes": len(b), "head_hex": b[:48].hex(), "top_decodes": [
    {"mode": m, "printable_ratio": r, "head": t.decode("latin1")} for m, r, t in best[:6]]}
json.dump(res, open(os.path.join(OUT, "stepD2_launcher.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("cloud.json:", res.get("cloud.json"))
print("dir_configs:", json.dumps(res.get("dir_configs"), ensure_ascii=False)[:400])
print("dir_Record:", json.dumps(res.get("dir_Record"), ensure_ascii=False)[:300])
print("client_doc dirs:", json.dumps(res.get("client_doc_dirs"), ensure_ascii=False))
print("client_doc_sample:", json.dumps(res.get("client_doc_sample"), ensure_ascii=False)[:500])
print("text_scan:", json.dumps(res["text_scan"], ensure_ascii=False)[:900])
print("launcher_conf top:", json.dumps(res["launcher_conf"]["top_decodes"][:4], ensure_ascii=False)[:600])
print("[out] h16c2/stepD2_launcher.json")
