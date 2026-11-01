# -*- coding: utf-8 -*-
"""把「男女图内容相同」的卡标成通用，不按缺图算。

背景：去重时发现不少卡的 女图 与 男图 是同一个文件（背包、挂饰类常见），
这类不是「缺一侧」，而是游戏本来就用一张图给两个性别。
判据：从 git 上一版取旧数据，若旧数据里同时有 女/男 标签、且两张图的 sha256 相同 → 通用。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from board_io import write_board_pair  # noqa: E402

B = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
WEB = PROJ / "02_wiki/web"


def sha(im):
    p = WEB / str(im.get("png") or "")
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None


def main() -> int:
    old = json.loads(subprocess.run(
        ["git", "show", "HEAD:02_wiki/web/data/boards/fashion_wardrobe.json"],
        capture_output=True, cwd=str(PROJ)).stdout.decode("utf-8"))
    cur = json.loads(B.read_text(encoding="utf-8"))
    old_by_id = {i["id"]: i for i in old["items"]}

    shared = 0
    for it in cur["items"]:
        o = old_by_id.get(it["id"])
        if not o:
            continue
        oi = ((o.get("_media") or {}).get("images") or [])
        labels = {str(x.get("label")) for x in oi}
        if not ({"女", "男"} <= labels):
            continue
        hashes = {sha(x) for x in oi if x.get("label") in ("女", "男")}
        hashes.discard(None)
        if len(hashes) != 1:
            continue                       # 男女图确实不同，跳过
        imgs = ((it.get("_media") or {}).get("images") or [])
        if not imgs:
            continue
        for im in imgs:
            im["label"] = "通用"
        it.pop("gender_icon_state", None)
        shared += 1
    write_board_pair(B, cur)
    print("同图共用 → 通用：", shared)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
