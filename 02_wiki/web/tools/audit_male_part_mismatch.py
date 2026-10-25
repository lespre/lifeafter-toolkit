# -*- coding: utf-8 -*-
"""审计时装卡里「男图部位不匹配」的情况。

规则：
  卡部位只含 头饰 → 男图 base 必须是 icon_h_m_*
  卡部位只含 衣服 → 男图 base 必须是 icon_b_m_*（或编号式 icon_<num>_1）
  卡部位只含 背包 → icon_bag_m_*
  卡部位只含 光源 → icon_light_m_*
  卡部位含多个 → 男图数量应 ≥ 部位数，且前缀齐全
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import Counter, defaultdict

BOARD = pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/fashion_wardrobe.json")
PREFIX = {"衣服": "icon_b", "头饰": "icon_h", "背包": "icon_bag",
          "光源": "icon_light", "整套": "icon_suit"}


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    wrong = []
    for it in d["items"]:
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        male = [x for x in imgs if "男" in str(x.get("label", ""))]
        if not male:
            continue
        parts = [p for p in (it.get("part_bucket") or []) if p in PREFIX]
        if not parts:
            continue
        want = {PREFIX[p] for p in parts}
        for m in male:
            base = str(m.get("base") or "")
            ok = any(base.startswith(w) for w in want)
            # 编号式（icon_<num>_1）无法判部位，视为未知不算错
            if re.match(r"^icon_\d+_1", base):
                continue
            if not ok:
                wrong.append((it["name"], "/".join(parts), base, sorted(want)))

    print("男图部位不匹配 %d 张" % len(wrong))
    grp = Counter(w[1] for w in wrong)
    print("按部位：", grp.most_common())
    for w in wrong[:15]:
        print("  %-22s 部位=%-8s 男图=%-22s 应为=%s" % (w[0], w[1], w[2], w[3]))

    # 六载星辰 / 童话镇 / 桂月清辉 逐个看
    print("\n重点核对：")
    for key in ("六载星辰", "童话镇", "桂月清辉"):
        for it in d["items"]:
            if key in it["name"]:
                imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
                print("  %-24s 部位=%-10s 图=%s" % (it["name"], "/".join(it.get("part_bucket") or []),
                                                    [(x.get("label"), x.get("base")) for x in imgs]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
