#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""奖池全量发现：扫 cdata 下所有 lottery / pool 相关表，判定它们能不能给出「池 → 道具」。

不改任何数据，只产出报告：
  01_索引与产物/30_分析/奖池表扫描_<date>.json / .md

判定口径：
  · rows     普通 bindict 行表；统计哪些字段是 jump:N 且解出的 0x27 组里含“像道具 id”的数
  · map      0x36 映射表（无普通行）；key = 池号/选项号，slot → 0x86 明细行 → 行内 0x27 组
  · 其它     解不出行也不出映射（0x73 字节码 / 空壳 / 纯 UI 资源）
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))

import rebuild_lottery_periods as R  # noqa: E402

TREE = R.TREE
OUT_DIR = Path(r"E:\la拆包项目\01_索引与产物\30_分析")
GEN = dt.date.today().strftime("%Y%m%d")

ID_LO, ID_HI = 10000, 3_000_000_000


def looks_item(v: int) -> bool:
    """够大、又不是时间戳/权重的数。"""
    if not isinstance(v, int):
        return False
    if v < ID_LO or v > ID_HI:
        return False
    if 1_500_000_000 < v < 2_000_000_000:   # ts
        return False
    return True


def scan_rows(t: R.Table) -> dict:
    fields: Counter[str] = Counter()
    item_fields: Counter[str] = Counter()
    sample: dict[str, list[int]] = {}
    for row in t.rows:
        for k, v in row["values"].items():
            val = v[1] if isinstance(v, tuple) else v
            if isinstance(val, str) and val.startswith("jump:"):
                fields[k] += 1
                hit = []
                try:
                    grp = t.jump_values(val)
                except Exception:
                    grp = []
                items = [x for x in grp if looks_item(x)]
                if items:
                    item_fields[k] += 1
                    if k not in sample:
                        sample[k] = items[:8]
    return {"kind": "rows", "row_count": len(t.rows),
            "jump_fields": dict(fields.most_common(12)),
            "item_fields": dict(item_fields.most_common(12)),
            "item_sample": sample}


def scan_map(t: R.Table) -> dict:
    keys = sorted(t.map_start.items())[:200]
    pools, sample = [], {}
    for key, off in keys:
        try:
            slots = R.parse_map_row(t, off)
        except Exception:
            continue
        ids = []
        for _slot, soff in slots:
            try:
                inner = R.row86(t, soff)
            except Exception:
                inner = {}
            # 行内 0x27 组（本族成员在行字节区间内，这里用行内近邻扫描）
            try:
                bound = soff + 400
                grps = R.slot_groups(t, soff, min(bound, len(t.blob)))
            except Exception:
                grps = []
            for g in grps:
                ids += [x for x in g if looks_item(x)]
        if ids:
            pools.append(key)
            sample[key] = sorted(set(ids))[:8]
    return {"kind": "map", "map_keys": len(t.map_start),
            "pools_with_items": len(pools), "item_sample": sample}


def main() -> int:
    files = []
    for p in sorted(TREE.glob("*.py")):
        if p.name.endswith("_chs.py"):
            continue
        if not any(w in p.stem.lower() for w in ("lottery", "pool")):
            continue
        if p.stat().st_size > 3_000_000:
            continue
        files.append(p)
    print(f"候选表 {len(files)}")

    out = []
    for i, p in enumerate(files, 1):
        chs = p.with_name(p.stem + "_chs.py")
        rec = {"table": p.stem, "size": p.stat().st_size}
        try:
            t = R.Table(p, chs if chs.exists() else None)
        except Exception as exc:
            rec.update({"kind": "fail", "error": str(exc)[:120]})
            out.append(rec)
            continue
        if len(t.rows) >= 3:
            rec.update(scan_rows(t))
        elif len(t.map_start) >= 3:
            try:
                rec.update(scan_map(t))
            except Exception as exc:
                rec.update({"kind": "map_fail", "error": str(exc)[:120]})
        else:
            rec.update({"kind": "other", "row_count": len(t.rows), "map_keys": len(t.map_start)})
        out.append(rec)
        if i % 25 == 0:
            print(f"  {i}/{len(files)} …")

    hits_rows = [r for r in out if r.get("kind") == "rows" and r.get("item_fields")]
    hits_map = [r for r in out if r.get("kind") == "map" and r.get("pools_with_items")]
    print(f"\n行表里带道具组: {len(hits_rows)} | 映射表里有道具: {len(hits_map)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jp = OUT_DIR / f"奖池表扫描_{GEN}.json"
    jp.write_text(json.dumps({"generated": GEN, "tree": str(TREE), "tables": out},
                             ensure_ascii=False, indent=1), encoding="utf-8")

    lines = [f"# 奖池表全量扫描（{GEN}）", "",
             f"- 候选表 {len(files)} 张",
             f"- 行表带道具组：**{len(hits_rows)}** 张",
             f"- 映射表单里出道具：**{len(hits_map)}** 张", "",
             "## 行表（jump 组里有道具）", "",
             "| 表 | 行数 | 道具字段（命中行数/示例） |", "|---|---|---|"]
    for r in sorted(hits_rows, key=lambda x: -x["row_count"])[:60]:
        f0 = next(iter(r["item_fields"]), "")
        lines.append(f"| `{r['table']}` | {r['row_count']} | "
                     f"`{f0}` {r['item_fields'][f0]} · {r['item_sample'].get(f0, [])[:4]} |")
    lines += ["", "## 映射表（池号/选项号 → 道具）", "",
              "| 表 | 映射键数 | 有道具的池 | 示例 |", "|---|---|---|---|"]
    for r in sorted(hits_map, key=lambda x: -x["pools_with_items"])[:60]:
        k = next(iter(r["item_sample"]), None)
        lines.append(f"| `{r['table']}` | {r['map_keys']} | {r['pools_with_items']} | "
                     f"{k}: {r['item_sample'].get(k, [])[:5]} |")
    mp = OUT_DIR / f"奖池表扫描_{GEN}.md"
    mp.write_text("\n".join(lines), encoding="utf-8")
    print("写出:", jp.name, "/", mp.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
