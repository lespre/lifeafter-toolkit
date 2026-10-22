# -*- coding: utf-8 -*-
"""打包 wiki 数据包：板块 JSON/JS + live_sources + 图标素材（不含 3D/Spine/音频）。"""
import pathlib
import zipfile

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
OUT = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/rel/la-wiki-data-v1.3.0.zip")

ICON_DIRS = ["core_icons", "chip_icons", "drone_icons", "nucleus_icons", "skin_posters",
             "fashion_icon_refs", "item_icons", "avatar_icons", "vehicle_icons",
             "recipe_icons", "lottery_icons", "show_reward_icons"]

count = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
    for p in (WEB / "data/boards").glob("*"):
        if p.is_file():
            z.write(p, "02_wiki/web/data/boards/" + p.name)
            count += 1
    for extra in ("live_sources.json", "manifest.js", "wiki_taxonomy.js", "publication_policy.js"):
        f = WEB / "data" / extra
        if f.exists():
            z.write(f, "02_wiki/web/data/" + extra)
    for d in ICON_DIRS:
        base = WEB / "assets" / d
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                z.write(p, "02_wiki/web/assets/" + d + "/" + str(p.relative_to(base)))
                count += 1

print("写入", count, "个文件；zip 大小 %.1f MB" % (OUT.stat().st_size / 1048576))
