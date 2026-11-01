# -*- coding: utf-8 -*-
r"""形态卡去重：同一张卡里按文件内容去重，重复的图只留一份。

依据（实测）：炽海天姿 的普通款与耀款图标字节完全相同：
  icon_h_f_5001001      sha 6b0593f7b6704183  = icon_h_f_5001001_b
  icon_h_m_5001001      sha 37e3480539597000  = icon_h_m_5001001_b
  icon_b_f/_m_5001001   同样逐字节相同
⇒ 卡面只保留一份（女/男），forms 里保留各自的 row_keys 与「共用图」标记。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
WEB = PROJ / "02_wiki/web"


def sha_of(im):
    p = WEB / str(im.get("png") or "")
    if not p.is_file():
        return f"missing:{im.get('png')}"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    touched = dropped = 0
    for it in items:
        media = it.get("_media") or {}
        imgs = media.get("images") or []
        if len(imgs) < 2:
            continue
        seen, keep = {}, []
        for im in imgs:
            h = sha_of(im)
            if h in seen:
                dropped += 1
                continue
            seen[h] = im
            keep.append(im)
        if len(keep) == len(imgs):
            continue
        # 只剩一份时，标签回到 女/男（去掉「普通·」这类形态前缀）
        for im in keep:
            lb = str(im.get("label") or "")
            if "·" in lb:
                im["label"] = lb.split("·")[-1]
            im.pop("form", None)
        media["images"] = keep
        media["total"] = len(keep)
        it["_media"] = media
        it["icon_count"] = len(keep)
        if it.get("forms"):
            it["forms"] = [{"name": f.get("name"), "row_keys": f.get("row_keys"),
                            "art_shared": True} for f in it["forms"]]
        touched += 1
    write_board_pair(BOARD, d)
    print(f"去重卡 {touched} ｜ 删除重复图 {dropped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
