# -*- coding: utf-8 -*-
"""名片框 spine 贴图页补件：atlas 里列出的 page 若 spine_live 缺失，
从 还原树 同名 png 复制，否则按 PE/PC 索引取 <page_stem>.ktx 解码成 png。
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core import img_fetch

LIVE = PROJ / "02_wiki/web/assets/spine_live"
TREE = PROJ / "01_索引与产物/41_还原树"
CAT = PROJ / "02_wiki/web/data/boards/avatar_catalog.json"


def pages_of(atlas: pathlib.Path):
    out = []
    for line in atlas.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            out.append(s)
    return out


def main() -> int:
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    pool = [i for i in cat["items"] if i.get("kind") == "名片框" and i.get("spine_path")
            and not ((i.get("_media") or {}).get("images"))]
    ok = fail = 0
    for it in pool:
        sp = it["spine_path"].replace("\\", "/").lstrip("/")
        d = LIVE / sp.rsplit("/", 1)[0]
        name = sp.rsplit("/", 1)[-1]
        atlas = d / (name + ".atlas")
        if not atlas.is_file():
            print(it["id"], "无 atlas")
            fail += 1
            continue
        for pg in pages_of(atlas):
            dst = d / pg
            if dst.is_file() and dst.stat().st_size > 1024:
                continue
            # 1) 还原树同名 png
            cands = list(TREE.rglob(pg))
            got = False
            for c in cands:
                if c.stat().st_size > 1024:
                    shutil.copy2(c, dst)
                    got = True
                    print(it["id"], "复制", c.relative_to(TREE), "->", dst.name)
                    break
            if got:
                ok += 1
                continue
            # 2) 按索引取 ktx/png
            stem = pg.rsplit(".", 1)[0]
            src = img_fetch.export(str(d.relative_to(LIVE)).replace("\\", "/") + "/" + stem, dst)
            if src:
                ok += 1
                print(it["id"], "索引取件", src, "->", dst.name)
            else:
                fail += 1
                print(it["id"], "贴图缺", pg)
    print("贴图页 补齐 %d ｜ 缺 %d" % (ok, fail))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
