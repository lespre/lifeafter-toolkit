# -*- coding: utf-8 -*-
"""收尾核验：两板 _media.images 引用的 png 是否真实存在；统计改后数字。"""
import json, pathlib
PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
for name, kind in (("fashion_wardrobe", None), ("avatar_catalog", "名片框")):
    p = WEB / "data/boards" / (name + ".json")
    d = json.loads(p.read_text(encoding="utf-8"))
    items = d["items"]
    if kind:
        items = [i for i in items if i.get("kind") == kind]
    have = [i for i in items if (i.get("_media") or {}).get("images")]
    miss_file = 0
    checked = 0
    for i in have:
        imgs = [x for x in i["_media"]["images"] if x.get("png")]
        if not imgs:
            continue
        f = WEB / imgs[0]["png"]
        checked += 1
        if not (f.is_file() and f.stat().st_size > 256):
            miss_file += 1
    print("%-18s 卡 %4d ｜ 有图 %4d ｜ 无图 %3d ｜ 引用文件核对 %d（缺文件 %d）"
          % (name, len(items), len(have), len(items) - len(have), checked, miss_file))
    # 无效 json 检查
    bad = [i for i in items if "_media" in i and not isinstance(i["_media"].get("images"), list)]
    print("   _media 结构异常", len(bad))
