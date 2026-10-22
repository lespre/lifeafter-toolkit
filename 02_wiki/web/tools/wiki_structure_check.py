# -*- coding: utf-8 -*-
"""wiki 结构体检：板块是否都被导航覆盖、编号是否连续、有无孤儿节点。"""
from __future__ import annotations

import json
import pathlib
import re

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")


def walk(node, path, out):
    name = node.get("name", "")
    here = path + [name]
    for b in node.get("boards") or []:
        out.append((b, " / ".join(here)))
    for c in node.get("children") or []:
        walk(c, here, out)


def main() -> int:
    man = json.loads(re.search(r"window\.WIKI_MANIFEST\s*=\s*(\{.*\})",
                               (WEB / "data/manifest.js").read_text(encoding="utf-8"), re.S).group(1))
    pub = [b["board"] for b in man["boards"]]
    tax = json.loads((WEB / "data/wiki_taxonomy.json").read_text(encoding="utf-8"))

    refs = []
    for top in tax["树"]:
        walk(top, [], refs)
    ref_ids = [r[0] for r in refs]
    print("已发布板块", len(pub))
    print("导航引用", len(ref_ids), "去重", len(set(ref_ids)))
    orphan = [b for b in pub if b not in set(ref_ids)]
    missing = [b for b in set(ref_ids) if b not in set(pub)]
    print("导航没覆盖的板块", orphan)
    print("导航指向不存在的板块", missing)

    print("\n各章节目录（编号检查）：")
    CN = "零一二三四五六七八九十十一十二十三十四十五"
    for top in tax["树"]:
        print(" ", top.get("name"))
        names = [c.get("name", "") for c in top.get("children") or []]
        for n in names:
            print("    ", n, " boards=", [c.get("boards") for c in top["children"] if c.get("name") == n][0])
        # 编号连续性
        nums = []
        for n in names:
            m = re.match(r"^（([^）]+)）", n)
            if m:
                nums.append(m.group(1))
        print("     编号序列:", nums)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
