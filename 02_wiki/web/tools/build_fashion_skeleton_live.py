# -*- coding: utf-8 -*-
r"""用活树 fashion_data 重建卡片骨架，并与现有板做差异对比（不改板）。

口径（本轮实测确立，写进报告）：
- `part_type` 与 `new_fashion_id_str` 前缀互斥：9,538 行有 part_type，1,631 行只有前缀 ⇒ 取两者之一
- cloth→衣服 / hat→头饰 / bag→背包 / light→荧光棒 / suit→整套
- 同一 (model_id, part) 的时限变体（-1天/-3天/…）合并成一张卡，row_keys 全收

用法：
  python tools/build_fashion_skeleton_live.py            # dry-run，打印差异
  python tools/build_fashion_skeleton_live.py --dump x.json   # 另存新骨架快照
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import add_fashion_style_fields as A  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
MAP = {"cloth": "衣服", "hat": "头发", "bag": "背包", "light": "荧光棒", "suit": "整套"}
TIME_RE = re.compile(r"-(1|3|5|7|14|30)天$")


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def base(n: str) -> str:
    n = (n or "").strip()
    prev = None
    while prev != n:
        prev = n
        n = TIME_RE.sub("", n).strip()
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump")
    a = ap.parse_args()

    rows, _, _ = A.load("fashion_data")
    groups = collections.OrderedDict()
    skipped = 0
    for r in rows:
        v = r["values"]
        name = base(str(sv(v.get("name")) or ""))
        part_raw = str(sv(v.get("part_type")) or "")
        fid = str(sv(v.get("new_fashion_id_str")) or "")
        if not part_raw:
            part_raw = fid.split("_")[0]
        part = MAP.get(part_raw)
        model = sv(v.get("model_id"))
        if not name or not part or model in (None, "", 0):
            skipped += 1
            continue
        key = (str(model), part)
        g = groups.setdefault(key, {"name": name, "part": part, "model": model,
                                    "row_keys": [], "names": set(), "charm": None,
                                    "level": None, "icons": None, "desc": None,
                                    "gender": None, "brand": None})
        g["row_keys"].append(int(r["key"]))
        g["names"].add(name)
        ch = sv(v.get("charm_value"))
        if isinstance(ch, int) and (g["charm"] is None or ch > g["charm"]):
            g["charm"] = ch
        lv = sv(v.get("level"))
        if isinstance(lv, int) and g["level"] is None:
            g["level"] = lv
        ic = sv(v.get("icons"))
        if ic and not g["icons"]:
            g["icons"] = str(ic)
        ds = sv(v.get("desc"))
        if ds and not g["desc"]:
            g["desc"] = str(ds)

    print(f"配置行 {len(rows)} ｜ 成卡 {len(groups)} ｜ 跳过（无名/无部件/无 model）{skipped}")
    print("部件分布", dict(collections.Counter(g['part'] for g in groups.values())))

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    keyed = {}
    for it in items:
        mids = it.get("model_ids") or ([it["model_id"]] if it.get("model_id") else [])
        for m in mids:
            keyed[(str(m), it.get("part"))] = it
    print(f"板卡 {len(items)} ｜ 可按 (model,part) 对齐 {len(keyed)}")

    new_keys = [k for k in groups if k not in keyed]
    gone_keys = [k for k in keyed if k not in groups]
    print(f"\n配置有、板上没有：{len(new_keys)}")
    for k in new_keys[:12]:
        g = groups[k]
        print(f"   {g['name']} ({g['part']}, model {g['model']}) rows={len(g['row_keys'])}")
    print(f"\n板上有、配置里没有：{len(gone_keys)}")
    for k in gone_keys[:12]:
        it = keyed[k]
        print(f"   {it['name']} ({it.get('part')}, model {k[0]}) src={it.get('part_source')}")

    if a.dump:
        snap = [{k: g[k] for k in ("name", "part", "model", "row_keys", "charm", "level", "desc")}
                | {"model_id": g["model"]} for g in groups.values()]
        pathlib.Path(a.dump).write_text(json.dumps(snap, ensure_ascii=False), encoding="utf-8")
        print("\n骨架快照 →", a.dump)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
