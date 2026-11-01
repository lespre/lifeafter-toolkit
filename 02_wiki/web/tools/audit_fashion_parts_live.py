# -*- coding: utf-8 -*-
r"""分类审计：用活树 fashion_data 重算部件，和板上的 part 对照。

口径（本轮实测确立）：
- fashion_data 里 `part_type` 与 `new_fashion_id_str` 前缀**互斥**：
  9,538 行有 part_type（cloth/hat/bag/light/suit），1,631 行 part_type 为空但 fid 前缀能补（cloth/hat/bag/light/suit）。
  ⇒ 正确规则是「取二者之一」，不是谁优先。
- 挂饰（pendant）不在 fashion_data 里，来自 player_appear_data.part_code。

输出只读报告：分类冲突卡、重名重卡、无 model 卡。
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import add_fashion_style_fields as A  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
OUT = PROJ / "01_索引与产物/30_分析/时装分类审计_20261101.md"

MAP = {"cloth": "衣服", "hat": "头饰", "bag": "背包", "light": "光源", "suit": "整套"}


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def main() -> int:
    rows, _, _ = A.load("fashion_data")
    cfg = {}
    for r in rows:
        v = r["values"]
        key = r["key"]
        part = str(sv(v.get("part_type")) or "")
        fid = str(sv(v.get("new_fashion_id_str")) or "")
        if not part:
            part = fid.split("_")[0]
        cfg[int(key)] = {
            "part": MAP.get(part, part or None),
            "model": sv(v.get("model_id")),
            "name": str(sv(v.get("name")) or ""),
            "fid": fid,
        }
    print(f"活树 fashion_data 行 {len(cfg)} ｜ 有 part 的 {sum(1 for c in cfg.values() if c['part'])}")

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    print(f"板 {len(items)} 张")

    conflicts, unmatched, by_pair = [], 0, collections.Counter()
    for it in items:
        rks = [int(k) for k in (it.get("row_keys") or []) if str(k).isdigit()]
        ref = next((cfg[k] for k in rks if k in cfg), None)
        if ref is None:
            unmatched += 1
            continue
        if it.get("part") != ref["part"]:
            conflicts.append((it["name"], it.get("part"), ref["part"],
                              it.get("part_source"), ref["model"]))
        by_pair[(it["name"], it.get("part"))] += 1

    dups = {k: v for k, v in by_pair.items() if v > 1}
    print(f"能对上行键的卡 {len(items)-unmatched} ｜ 对不上 {unmatched}")
    print(f"分类与配置不一致 {len(conflicts)} ｜ 同名同部件重复 {len(dups)} 组")

    lines = ["# 时装分类审计（2026-11-01，活树口径）", "",
             f"- 板卡 {len(items)} ｜ 能按 row_key 对上配置 {len(items)-unmatched} ｜ 对不上 {unmatched}",
             f"- 分类与配置不一致：{len(conflicts)}",
             f"- 同名同部件重复：{len(dups)} 组", ""]
    lines.append("## 分类不一致（样例 40）")
    for c in conflicts[:40]:
        lines.append(f"- {c[0]}：板上「{c[1]}」 ← 配置「{c[2]}」（来源 {c[3]}，model {c[4]}）")
    lines.append("")
    lines.append("## 同名同部件重复")
    for k, v in list(dups.items())[:30]:
        lines.append(f"- {k[0]} / {k[1]} × {v}")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("报告 →", OUT)
    print("\n前 12 条冲突：")
    for c in conflicts[:12]:
        print(f"  {c[0]:<20} 板「{c[1]}」 配置「{c[2]}」 src={c[3]} model={c[4]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
