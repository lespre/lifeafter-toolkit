# -*- coding: utf-8 -*-
"""场景加成平衡去重：把 (name, range, min_attack) 相同的行并成一张卡。

原始 1363 行里大量是同一场景在不同 scene_id / 服型 / 来源下的重复档位，
逐行成卡会显得又长又乱；并卡后把 scene_id / 服型 / 来源收进卡内清单。
"""
from __future__ import annotations
import sys

import json
import pathlib
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
BOARD = ROOT / "02_wiki/web/data/boards/scene_balance.json"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    its = d["items"]
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for it in its:
        groups[(it.get("name"), it.get("range"), it.get("min_attack"))].append(it)

    out = []
    for (name, rng, min_atk), rows in groups.items():
        first = dict(rows[0])
        first["scene_ids"] = sorted({r.get("scene_id") for r in rows if r.get("scene_id") is not None})
        first["server_types"] = sorted({r.get("server_type") for r in rows if r.get("server_type")})
        first["source_kinds"] = sorted({r.get("source_kind") for r in rows if r.get("source_kind")})
        first["row_keys"] = sorted({r.get("row_key") for r in rows if r.get("row_key") is not None})
        first["merged_rows"] = len(rows)
        # 卡面不再逐行展示冲突的 scene_id / 单一服型
        first.pop("scene_id", None)
        first.pop("server_type", None)
        first.pop("source_kind", None)
        first.pop("row_key", None)
        first["id"] = "sb_" + "_".join(str(x) for x in (name, rng, min_atk))[:80]
        out.append(first)

    out.sort(key=lambda x: (str(x.get("name")), str(x.get("range"))))
    d["items"] = out
    d.setdefault("meta", {})["merge_note"] = (
        "按 (场景名, 加成区间, 生效最低攻击) 合并；卡内列出涉及的全部 scene_id / 服型 / 来源。"
        "原 %d 行进板行 → 并卡 %d 张。" % (len(its), len(out)))
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("原 %d 行 → 并卡 %d 张" % (len(its), len(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
