# -*- coding: utf-8 -*-
"""确认 10-30 刷新的名片框配置表里是否真有 217~220 这批新道具。"""
import sys, json, pathlib
sys.path.insert(0, r"e:\la拆包项目\02_wiki\web\tools")
import build_avatar_full as B

rows, bad = B.decode(B.TREE / "business_card_scheme_data.py")
print("解码行数:", len(rows), "坏行:", len(bad))
hits = []
imgs = set()
for r in rows:
    v = r.get("values") or {}
    icon = (B.val(v, "frame_img_path") or "").strip().replace("\\", "/")
    res = (B.val(v, "resource_path") or "").strip().replace("\\", "/")
    nm = (B.val(v, "item_name") or "").strip()
    key = str(r.get("key"))
    if icon:
        imgs.add(icon.rsplit(".", 1)[0])
    if any(s in (icon + res) for s in ("217", "218", "219", "220", "2197")):
        hits.append((key, nm, icon, res))
print("含 217~220 的行 %d:" % len(hits))
for h in hits[:20]:
    print("   ", h)

old = json.loads((pathlib.Path(r"e:\la拆包项目\02_wiki\web") / "data/boards/avatar_catalog.json")
                 .read_text(encoding="utf-8"))
old_ids = {it["item_id"] for it in old["items"] if it.get("kind") == "名片框"}
new_keys = {str(r.get("key")) for r in rows}
print("\n旧 catalog 名片框 %d 条；新表 %d 行；新增 %d 条:" % (
    len(old_ids), len(new_keys), len(new_keys - old_ids)))
print("   ", sorted(new_keys - old_ids)[:20])
print("消失 %d 条:" % len(old_ids - new_keys), sorted(old_ids - new_keys)[:10])
