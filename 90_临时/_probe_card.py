# -*- coding: utf-8 -*-
import json, pathlib, collections, re

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
cat = json.loads((WEB / "data/boards/avatar_catalog.json").read_text(encoding="utf-8"))
items = cat["items"]
cards = [it for it in items if it.get("kind") == "名片框"]
print("名片框条数:", len(cards))
print("--- 样例1 ---")
print(json.dumps(cards[0], ensure_ascii=False, indent=1)[:2500])

print("\n--- 字段出现率 ---")
c = collections.Counter()
for it in cards:
    for k in it.keys():
        c[k] += 1
print(dict(c))

print("\n--- image_path / resource_path 形态 ---")
cnt = collections.Counter()
samples = {}
for it in cards:
    ip = it.get("image_path") or ""
    rp = it.get("resource_path") or ""
    stem = (ip.rsplit(".", 1)[0] if ip else "")
    has_b_ip = "_b_" in stem
    has_b_rp = "_b_" in (rp.rsplit(".", 1)[0] if rp else "")
    key = (bool(ip), has_b_ip, bool(rp), has_b_rp)
    cnt[key] += 1
    samples.setdefault(key, (it["id"], it.get("name"), ip, rp))
for k, v in cnt.items():
    print("  有image_path=%s 其含_b_=%s | 有resource_path=%s 其含_b_=%s  -> %d 条  例:%s" % (k[0], k[1], k[2], k[3], v, samples[k]))

print("\n--- _media.images 现状 ---")
roles = collections.Counter()
nimg = collections.Counter()
for it in cards:
    m = it.get("_media") or {}
    imgs = m.get("images") or []
    nimg[len(imgs)] += 1
    for x in imgs:
        roles[(x.get("role"), x.get("label"))] += 1
print("images 数量分布:", dict(nimg))
print("role/label 分布:", dict(roles))

print("\n--- 有 background 的样例 ---")
bg = [it for it in cards if any(x.get("role") == "background" for x in ((it.get("_media") or {}).get("images") or []))]
print("带 background 的条数:", len(bg))
for it in bg[:5]:
    print("  ", it["id"], it.get("name"), json.dumps(it["_media"], ensure_ascii=False)[:400])
