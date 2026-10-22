# -*- coding: utf-8 -*-
"""整理 wiki：清掉失效导航、隐藏两份重复/未解析板、修 三、活动类 编号。"""
from __future__ import annotations

import json
import pathlib
import re

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
CN = "零一二三四五六七八九十"

STALE = ["weapon_skins", "new_textures", "shop_static_candidates",
         "nucleus_entry_slots", "weapon_skin_structure_v01", "weapon_skin_static_candidates_v01"]
HIDE = {
    "talent_catalog": ("published_hidden", "已被 talent_battle / talent_prof 拆分替代"),
    "fashion_identity_unresolved_v01": ("published_hidden", "身份待解析的历史记录，未达到发布标准"),
}


def main() -> int:
    # 1) 政策：隐藏两份
    pol_path = WEB / "data/publication_policy.json"
    pol = json.loads(pol_path.read_text(encoding="utf-8"))
    for b, (st, why) in HIDE.items():
        e = pol["boards"].setdefault(b, {})
        e["publication_status"] = st
        e["note"] = why
    pol_path.write_text(json.dumps(pol, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/publication_policy.js").write_text(
        "window.WIKI_PUBLICATION_POLICY = " + json.dumps(pol, ensure_ascii=False, indent=2) + ";", encoding="utf-8")

    # 2) 导航：去失效引用 + 去隐藏板
    tax_path = WEB / "data/wiki_taxonomy.json"
    tax = json.loads(tax_path.read_text(encoding="utf-8"))
    removed = []

    def clean(node):
        bs = node.get("boards") or []
        keep = []
        for b in bs:
            if b in STALE or b in HIDE:
                removed.append(b)
            else:
                keep.append(b)
        node["boards"] = keep
        for c in node.get("children") or []:
            clean(c)

    for top in tax["树"]:
        clean(top)

    # 3) 三、活动类 重排编号
    for top in tax["树"]:
        if not str(top.get("name", "")).startswith("三"):
            continue
        ch = top.get("children") or []
        for i, c in enumerate(ch):
            base = re.sub(r"^（[^）]*）", "", c.get("name", ""))
            c["name"] = "（%s）%s" % (CN[i] if i < len(CN) else str(i), base)
        print("三、活动类 编号:", [c["name"] for c in ch])

    tax_path.write_text(json.dumps(tax, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/wiki_taxonomy.js").write_text(
        "window.WIKI_TAXONOMY = " + json.dumps(tax, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")
    print("导航移除", len(removed), sorted(set(removed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
