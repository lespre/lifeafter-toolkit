# -*- coding: utf-8 -*-
"""场景平衡：按服型拆行，让「服型 / 来源类型」下拉筛选真正可用。

合并口径改为 (场景名, 加成区间, 生效最低攻击, 服型)：
同一档位若同时存在于经典服源与简单生存服源，就拆成两行——筛选才准。
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path("E:/la拆包项目")
BOARD = ROOT / "02_wiki/web/data/boards/scene_balance.json"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    out = []
    for it in items:
        sts = it.get("server_types") or [it.get("服型") or "经典服源"]
        srcs = it.get("来源类型") or "-"
        for st in sts:
            row = {k: v for k, v in it.items()
                   if k not in ("scene_ids", "server_types", "source_kinds", "row_keys", "merged_rows",
                                "服型", "场景编号", "来源类型")}
            row["服型"] = str(st).replace("测试服·", "")
            row["server_type"] = row["服型"]
            row["来源类型"] = srcs
            row["source_kind"] = srcs
            out.append(row)
    for i, it in enumerate(out, 1):
        it["id"] = "sb_%04d" % i
    d["items"] = out
    meta = d.setdefault("meta", {})
    meta["filters"] = [{"key": "server_type", "label": "服型"},
                       {"key": "source_kind", "label": "来源类型"}]
    meta["merge_note"] = ("按 (场景名, 加成区间, 生效最低攻击, 服型) 分行；"
                          "同档位跨服时拆成多行，保证服型筛选准确。共 %d 行。" % len(out))
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("拆行后 %d 条" % len(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
