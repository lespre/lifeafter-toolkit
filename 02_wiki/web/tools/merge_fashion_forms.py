# -*- coding: utf-8 -*-
r"""把「耀·XXX」这类**同件的另一个形态**并进普通款，不再单独成卡。

用户口径（2026-11-01）：耀·炽海天姿 与 炽海天姿 是两个形态，同一件，合成一张卡。
处理：
  · 普通款保留为主卡
  · 耀的方向：name_variants / row_keys 合并；图片加 form 标记，label 写成「普通·女」「耀·女」
  · 卡上新增 forms: [{name, row_keys, images}]
  · 删除耀的独立卡
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
PREFIX = "耀·"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    by_name = {i["name"]: i for i in items}

    merges = []
    for it in items:
        nm = it.get("name") or ""
        if not nm.startswith(PREFIX):
            continue
        base_name = nm[len(PREFIX):]
        base = by_name.get(base_name)
        if not base:
            continue
        merges.append((base, it))

    print(f"待合并 {len(merges)} 组")
    for base, alt in merges:
        print(f"   {alt['name']}  →  {base['name']}")

    if not a.apply:
        print("（dry-run）")
        return 0

    drop_ids = set()
    for base, alt in merges:
        b_imgs = ((base.get("_media") or {}).get("images") or [])
        a_imgs = ((alt.get("_media") or {}).get("images") or [])
        for im in b_imgs:
            im.setdefault("form", "普通")
            if not str(im.get("label", "")).startswith("普通"):
                im["label"] = "普通·" + str(im.get("label") or "图示")
        for im in a_imgs:
            im["form"] = "耀"
            im["label"] = "耀·" + str(im.get("label") or "图示")
        merged_imgs = b_imgs + a_imgs

        plain_rows = list(base.get("row_keys") or [])
        plain_imgs = list(b_imgs)
        base["name_variants"] = sorted(set((base.get("name_variants") or []) + (alt.get("name_variants") or [])))
        base["row_keys"] = sorted(set((base.get("row_keys") or []) + (alt.get("row_keys") or [])))
        base["model_ids"] = sorted({* (base.get("model_ids") or []), *(alt.get("model_ids") or [])})
        base["forms"] = [
            {"name": "普通", "row_keys": sorted(plain_rows),
             "images": [im["png"] for im in plain_imgs]},
            {"name": "耀", "row_keys": sorted(alt.get("row_keys") or []),
             "images": [im["png"] for im in a_imgs]},
        ]
        media = base.get("_media") or {}
        media["images"] = merged_imgs
        media["total"] = len(merged_imgs)
        base["_media"] = media
        base["icon_count"] = len(merged_imgs)
        base["merged_from"] = sorted(set((base.get("merged_from") or []) + [alt["name"]]))
        drop_ids.add(alt["id"])

    items[:] = [i for i in items if i["id"] not in drop_ids]
    write_board_pair(BOARD, d)
    print(f"合并完成 ｜ 删除独立卡 {len(drop_ids)} ｜ 板块 {len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
