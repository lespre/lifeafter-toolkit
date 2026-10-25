# -*- coding: utf-8 -*-
"""种族潜能修订（用户 2026-10-26 口径）：
- 没有「通用」这个种族 → race=1 的 15 条移出板面（留档计数）
- 现行「半感染者」= 数据里的 械骨人 → race=4 改名械骨人
- 「再生者」= 现在的 半感染者 → race=3 改名半感染者
"""
from __future__ import annotations

import json
import pathlib
from collections import Counter

ROOT = pathlib.Path("E:/la拆包项目")
BOARD = ROOT / "02_wiki/web/data/boards/gene_potential_catalog.json"

RENAME = {4: "械骨人", 3: "半感染者"}
DROP_RACE = 1


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    its = d["items"]
    dropped = [i for i in its if i.get("race") == DROP_RACE]
    kept = [i for i in its if i.get("race") != DROP_RACE]
    for it in kept:
        if it.get("race") in RENAME:
            it["race_name"] = RENAME[it["race"]]
    d["items"] = kept
    meta = d.setdefault("meta", {})
    meta["race_rule"] = ("种族按用户口径：现行为械骨人（race=4）与半感染者（race=3，旧称再生者）、人类（race=2）；"
                         "不存在「通用」种族。")
    meta["dropped_common_rows"] = len(dropped)
    meta["dropped_common_note"] = "原 race=1「通用（无种族专属）」%d 条不属任何种族，已移出板面。" % len(dropped)
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("保留 %d 条 ｜ 移出通用 %d 条" % (len(kept), len(dropped)))
    print(Counter(i["race_name"] for i in kept).most_common())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
