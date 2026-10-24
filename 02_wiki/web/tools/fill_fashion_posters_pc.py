# -*- coding: utf-8 -*-
"""12 条仅 PC(ui_01.gpk) 命中的时装补图：尝试 pc 取图并回写 board。"""
import json, pathlib, sys
PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core import img_fetch

DET = PROJ / "01_索引与产物/10_索引/热更检测"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
OUT = PROJ / "02_wiki/web/assets/fashion_posters"
hits = json.loads((DET / "_fashion_pc_hits_tmp.json").read_text(encoding="utf-8"))
board = json.loads(BOARD.read_text(encoding="utf-8"))
by_id = {it["id"]: it for it in board["items"]}
ok, bad = [], []
for iid, (rel, pack, row) in hits.items():
    base = rel
    for e in (".bc7", ".ktx", ".dds", ".png"):
        if base.lower().endswith(e):
            base = base[: -len(e)]
            break
    dst = OUT / (iid + ".png")
    try:
        src = img_fetch.export(base, dst)
    except Exception as ex:                                    # noqa: BLE001
        src = ""
        bad.append((iid, rel, "exc:%s" % str(ex)[:40]))
        continue
    if src and dst.is_file() and dst.stat().st_size > 512:
        ok.append((iid, rel, src))
    else:
        bad.append((iid, rel, "no_src"))
print("PC 补成功", len(ok), "失败", len(bad), bad[:4])
for iid, rel, src in ok:
    it = by_id[iid]
    it["_media"] = {"images": [{"png": "assets/fashion_posters/%s.png" % iid, "label": "图标",
                                "base": rel, "source": "fashion_data.icons → PC(ui_01) 补图 20261024"}],
                    "total": 1}
    it["icon_state"] = "有图"
    it["icon_count"] = 1
    for ic in it.get("icons_all") or []:
        if ic.get("path") == rel.rsplit(".", 1)[0] or ic.get("path") == rel:
            ic["png"] = "assets/fashion_posters/%s.png" % iid
if ok:
    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
have = sum(1 for it in board["items"] if (it.get("_media") or {}).get("images"))
print("现在有图", have, "/", len(board["items"]))
(DET / "_fashion_pc_fail.json").write_text(json.dumps(bad, ensure_ascii=False, indent=1), encoding="utf-8")
