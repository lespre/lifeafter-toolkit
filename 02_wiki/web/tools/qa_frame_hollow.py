# -*- coding: utf-8 -*-
"""名片框/头像框「中空检测」。

边框图（frame）：中心大面积透明（游戏里头像/名牌就露在中间）。
场景底图（scene）：整幅不透明。
→ 用中心区域的不透明像素占比判定当前挂的是不是错图。
"""
import json, pathlib, sys
from PIL import Image
import numpy as np

WEB = pathlib.Path(__file__).resolve().parents[1]
BOARD = WEB / "data/boards/avatar_catalog.json"


def solid_ratio(p):
    """中心 50%×50% 区域的不透明像素占比。"""
    im = Image.open(p).convert("RGBA")
    a = np.asarray(im)[:, :, 3]
    h, w = a.shape
    cy, cx = h // 4, w // 4
    c = a[cy:cy + h // 2, cx:cx + w // 2]
    return float((c > 8).mean()), im.size


def main():
    d = json.load(open(BOARD, encoding="utf-8"))
    kinds = sys.argv[1].split(",") if len(sys.argv) > 1 else ["名片框"]
    for kind in kinds:
        rows = []
        for it in d["items"]:
            if it.get("kind") != kind:
                continue
            m = it.get("_media") or {}
            imgs = m.get("images") or []
            if not imgs:
                rows.append((it["id"], it.get("name"), None, None, "NOIMG"))
                continue
            p = WEB / imgs[0]["png"]
            if not p.is_file():
                rows.append((it["id"], it.get("name"), None, None, "MISSING"))
                continue
            try:
                ratio, size = solid_ratio(p)
            except Exception as e:
                rows.append((it["id"], it.get("name"), None, None, "ERR %s" % e))
                continue
            tag = "SCENE" if ratio > 0.25 else "frame"
            rows.append((it["id"], it.get("name"), ratio, size, tag))
        n_scene = sum(1 for r in rows if r[4] == "SCENE")
        n_none = sum(1 for r in rows if r[4] in ("NOIMG", "MISSING"))
        print("\n=== %s：共 %d ｜ 判为场景底图 %d ｜ 无图 %d ==="
              % (kind, len(rows), n_scene, n_none))
        for iid, nm, ratio, size, tag in rows:
            if tag != "frame":
                print("  [%s] %-12s %-22s ratio=%s size=%s" %
                      (tag, iid, (nm or "")[:22],
                       ("%.2f" % ratio) if ratio is not None else "-", size))


if __name__ == "__main__":
    main()
