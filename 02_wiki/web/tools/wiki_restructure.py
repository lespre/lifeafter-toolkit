# -*- coding: utf-8 -*-
"""整理结构 + 换 hero 图（随机传世/典藏）+ 头像板改名。"""
from __future__ import annotations

import json
import pathlib
import random
import re

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
CN = "零一二三四五六七八九十"


def load(name):
    return json.loads((WEB / "data/boards" / (name + ".json")).read_text(encoding="utf-8"))


def save(name, d):
    (WEB / "data/boards" / (name + ".json")).write_text(
        json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards" / (name + ".js")).write_text(
        "window.WIKI_BOARD_%s = %s;" % (name, json.dumps(d, ensure_ascii=False, indent=1)), encoding="utf-8")


def main() -> int:
    # 1) 选 3 张传世/典藏海报
    w = load("weapon_skin_sfx_text_sources")
    pool = []
    for it in w["items"]:
        g = it.get("grade") or ""
        media = (it.get("_media") or {}).get("images") or []
        if ("传世" in g or "典藏" in g) and media:
            png = media[0].get("png")
            if png and (WEB / png).is_file():
                pool.append((it.get("name"), png, g))
    rnd = random.Random(20261021)
    picks = rnd.sample(pool, 3) if len(pool) >= 3 else pool
    print("hero 选中：", picks)

    # 2) 改 wiki.html 的 hero art
    wp = WEB / "wiki.html"
    s = wp.read_text(encoding="utf-8")
    imgs = "\n".join('      <img src="%s" alt="%s" title="%s">' % (p, n, g) for n, p, g in picks)
    s = re.sub(r'(<div class="wp-hero-art"[^>]*>)(.*?)(</div>)',
               lambda m: m.group(1) + "\n" + imgs + "\n    " + m.group(3), s, flags=re.S)
    wp.write_text(s, encoding="utf-8")

    # 3) 头像板改名
    a = load("avatar_catalog")
    a["meta"]["name"] = "名片框外观总表"
    a["meta"]["notes"] = (a["meta"].get("notes", "") +
                          " ｜ 含头像框 250 + 动态头像 204；图形资源在 UI 图集内，暂未导出。").strip()
    save("avatar_catalog", a)

    # 4) 结构重排
    tp = WEB / "data/wiki_taxonomy.json"
    tax = json.loads(tp.read_text(encoding="utf-8"))
    keep_power = {"mutation_core_full", "tactical_chip_full", "drone_catalog", "edible_catalog", "scene_balance"}
    moved = []
    power = next(n for n in tax["树"] if str(n.get("name", "")).startswith("二"))
    rest, keep = [], []
    for c in power["children"]:
        if set(c.get("boards") or []) & keep_power:
            keep.append(c)
        elif c.get("boards"):
            moved.append(c)
    # 移出的按原名放资料层
    power["children"] = keep
    for i, c in enumerate(power["children"]):
        base = re.sub(r"^（[^）]*）", "", c.get("name", ""))
        c["name"] = "（%s）%s" % (CN[i] if i < len(CN) else str(i), base)

    data = next(n for n in tax["树"] if str(n.get("name", "")).startswith("四"))
    for c in moved:
        data["children"].append(c)
    # 资料层重编号
    for i, c in enumerate(data["children"]):
        base = re.sub(r"^（[^）]*）", "", c.get("name", ""))
        c["name"] = "（%s）%s" % (CN[i] if i < len(CN) else str(i), base)

    # 活动类：去掉 PvP 节点（已移走）+ 空节点
    act = next(n for n in tax["树"] if str(n.get("name", "")).startswith("三"))
    act["children"] = [c for c in act["children"]
                       if "PvP" not in c.get("name", "") and (c.get("boards") or c.get("children"))]
    for i, c in enumerate(act["children"]):
        base = re.sub(r"^（[^）]*）", "", c.get("name", ""))
        c["name"] = "（%s）%s" % (CN[i] if i < len(CN) else str(i), base)

    tp.write_text(json.dumps(tax, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/wiki_taxonomy.js").write_text(
        "window.WIKI_TAXONOMY = " + json.dumps(tax, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")

    print("战力类：", [c["name"] for c in power["children"]])
    print("移入资料层：", [c["name"] for c in moved])
    print("活动类：", [c["name"] for c in act["children"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
