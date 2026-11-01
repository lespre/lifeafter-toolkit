#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按期次还原奖池成员（当前还原树 · 无 oversea 变体口径）。

与旧流程的区别：绑定不再靠「conf 里随便哪个 pool 字段」，而是**逐家族写死取法**——
每个家族的池号语义不一样，混用会得到 0 命中（实测 205 个绑定池全部对不上映射表）。

产物：
  01_索引与产物/30_分析/奖池成员_<date>.json
    { "periods": {period_id: {"family":…, "source":…, "items":[{item_id, slot, …}]}},
      "pools":  {pool_id: {"table":…, "items":[…]}},
      "stats":  {...} }
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
OUT = Path(r"E:\la拆包项目\01_索引与产物\30_分析")
BOARD = WEB / "data/boards/lottery_periods.json"
GEN = dt.date.today().strftime("%Y%m%d")
ID_LO, ID_HI = 10000, 3_000_000_000


def looks_item(v) -> bool:
    return isinstance(v, int) and ID_LO <= v <= ID_HI and not (1_500_000_000 < v < 2_000_000_000)


def T(name: str):
    p = TREE / f"{name}.py"
    if not p.exists():
        return None
    chs = p.with_name(p.stem + "_chs.py")
    try:
        return R.Table(p, chs if chs.exists() else None)
    except Exception as exc:
        print(f"  ! {name}: {exc}")
        return None


def map_items(t, key: int) -> list[dict]:
    """映射表：key → 槽位道具。

    两条路，先走 0x86 明细行的 jump 字段（本树里多时装表的时装 id 就挂在字段 12），
    再用槽位字节窗口兜底（纯外观那族的成员是行内内联组）。
    """
    off = t.map_start.get(key)
    if off is None:
        return []
    try:
        slots = R.parse_map_row(t, off)
    except Exception:
        return []
    ids = []
    for slot, soff in slots:
        row = R.row86(t, soff)
        for f, v in row.items():
            if not (isinstance(v, str) and v.startswith("jump:")):
                continue
            try:
                grp = t.jump_values(v)
            except Exception:
                continue
            ids_here = [x for x in grp if looks_item(x)]
            if ids_here and len(ids_here) <= 8:
                for x in ids_here:
                    ids.append((slot, x))
    if ids:
        rep = Counter(x for _s, x in ids)
        out, seen = [], set()
        for slot, x in sorted(ids):
            if rep[x] > 2 or x in seen:
                continue
            seen.add(x)
            out.append({"slot": slot, "item_id": x})
        return out
    ids = []
    for slot, soff in slots:
        j, grp = soff, None
        while j < min(soff + 32, len(t.blob)):
            g = R.read_27(t.blob, j)
            if g and g.get("values"):
                grp = g
                break
            j += 1
        if not grp:
            continue
        for x in grp["values"]:
            if looks_item(x):
                ids.append((slot, x))
    rep = Counter(x for _s, x in ids)
    out, seen = [], set()
    for slot, x in sorted(ids):
        if rep[x] > 2 or x in seen:
            continue
        seen.add(x)
        out.append({"slot": slot, "item_id": x})
    return out


def jump_items(t, row: dict, field: str) -> list[int]:
    v = row["values"].get(field)
    if not isinstance(v, str) or not v.startswith("jump:"):
        return []
    return [x for x in t.jump_values(v) if looks_item(x)]


def main() -> int:
    periods_doc = json.loads(BOARD.read_text(encoding="utf-8"))
    periods = periods_doc["periods"]
    out_periods: dict[str, dict] = {}
    pools: dict[str, dict] = {}
    by_fam = Counter()

    # ── A. 纯外观抽奖：base_conf(key=活动号).slot_7=期号 → lottery_conf(期号).reward_pool_id → 池表
    of_base = T("only_fashion_hd_base_conf")
    of_conf = T("only_fashion_hd_lottery_conf")
    of_pool = T("only_fashion_hd_reward_pool_conf")
    if of_base and of_conf and of_pool:
        for row in of_base.by_key.values():
            hd_id = row["key"]
            pno = row["values"].get("lottery_conf_id") or row["values"].get("<slot_7>")
            conf = of_conf.by_key.get(int(pno) if isinstance(pno, int) else -1, {}).get("values", {})
            pool_id = conf.get("reward_pool_id")
            per = next((p for p in periods
                        if str(p.get("activity_id")) == str(hd_id)
                        and "OnlyFashion" in str(p.get("family_key") or "")), None)
            if per is None or not isinstance(pool_id, int):
                continue
            pid = per["period_id"]
            items = map_items(of_pool, pool_id)
            if items:
                pools[str(pool_id)] = {"table": "only_fashion_hd_reward_pool_conf", "items": items,
                                       "family": "纯外观抽奖"}
                for it in items:
                    it["pool_id"] = pool_id
                out_periods[pid] = {"family": "纯外观抽奖", "pool_ids": [pool_id],
                                    "source": "only_fashion_hd_reward_pool_conf",
                                    "items": items}
                by_fam["纯外观抽奖"] += 1

    # ── B. 多时装抽奖：conf key 与 option_data key 同一号段，直接按 key 取
    mo_conf = T("multi_optional_lottery_conf_data")
    mo_opt = T("multi_optional_lottery_option_data")
    if mo_conf and mo_opt:
        for key in mo_conf.by_key:
            pid = f"multi_optional:{key}"
            per = next((p for p in periods if p["period_id"] == pid), None)
            if per is None:
                # 板上期次 id 可能是活动号形式，退回按 conf_key + family_key 找
                per = next((p for p in periods
                            if str(p.get("conf_key")) == str(key)
                            and "MultiOptional" in str(p.get("family_key") or "")), None)
            if per is None:
                continue
            items = map_items(mo_opt, key)
            if not items:
                continue
            for it in items:
                it["option_key"] = key
            out_periods[per["period_id"]] = {"family": "多时装抽奖", "pool_ids": [key],
                                             "source": "multi_optional_lottery_option_data",
                                             "items": items}
            by_fam["多时装抽奖"] += 1

    # ── C. 典藏（SuperFashion）：conf key → lottery_id + panel_show_item_ids + 入口件
    sf = T("super_fashion_lottery_conf_data")
    if sf:
        for key, row in sf.by_key.items():
            per = next((p for p in periods
                        if str(p.get("conf_key")) == str(key)
                        and "SuperFashion" in str(p.get("family_key") or "")), None)
            if per is None:
                per = next((p for p in periods
                            if str(p.get("conf_key")) == str(key)
                            and ("BlessingsAlways" in str(p.get("family_key") or "")
                                 or "DragonBlessing" in str(p.get("family_key") or ""))), None)
            if per is None:
                continue
            pool_id = row["values"].get("lottery_id")
            items = []
            for iid in jump_items(sf, row, "panel_show_item_ids"):
                items.append({"slot": None, "item_id": iid})
            for fld in ("left_item_id", "right_item_id", "right_bag_item_id"):
                v = row["values"].get(fld)
                if isinstance(v, int) and v > 1000:
                    items.append({"slot": None, "item_id": v})
            uniq, seen = [], set()
            for it in items:
                if it["item_id"] in seen:
                    continue
                seen.add(it["item_id"])
                if isinstance(pool_id, int):
                    it["pool_id"] = pool_id
                uniq.append(it)
            if not uniq:
                continue
            out_periods[per["period_id"]] = {"family": "典藏抽奖", "pool_ids": ([pool_id] if isinstance(pool_id, int) else []),
                                             "source": "super_fashion_lottery_conf_data.panel_show_item_ids+入口件",
                                             "items": uniq}
            by_fam["典藏抽奖"] += 1

    # ── D. 限定芯片：conf key → up_chips ∪ new_chips
    chip = T("special_chip_lottery_hd_conf_data")
    if chip:
        for key, row in chip.by_key.items():
            per = next((p for p in periods
                        if str(p.get("conf_key")) == str(key)
                        and "Chip" in str(p.get("family_key") or "")), None)
            if per is None:
                continue
            ids = jump_items(chip, row, "up_chips") + jump_items(chip, row, "new_chips")
            if not ids:
                continue
            uniq, seen = [], set()
            for x in ids:
                if x in seen:
                    continue
                seen.add(x)
                uniq.append({"slot": None, "item_id": x})
            out_periods[per["period_id"]] = {"family": "限定芯片抽奖", "pool_ids": [],
                                             "source": "special_chip_lottery_hd_conf_data.up/new_chips",
                                             "items": uniq}
            by_fam["限定芯片抽奖"] += 1

    # ── E. 建筑礼盒：conf key → lottery_pool_id + furniture_item_ids
    bv2 = T("building_lottery_v2_conf_data")
    if bv2:
        for key, row in bv2.by_key.items():
            per = next((p for p in periods
                        if str(p.get("conf_key")) == str(key)
                        and "BuildingObject" in str(p.get("family_key") or "")), None)
            if per is None:
                continue
            pool_id = row["values"].get("lottery_pool_id")
            ids = jump_items(bv2, row, "furniture_item_ids")
            if not ids:
                continue
            items = [{"slot": None, "item_id": x} for x in ids]
            out_periods[per["period_id"]] = {"family": "建筑礼盒", "pool_ids": ([pool_id] if isinstance(pool_id, int) else []),
                                             "source": "building_lottery_v2_conf_data.furniture_item_ids",
                                             "items": items}
            if isinstance(pool_id, int):
                pools[str(pool_id)] = {"table": "building_lottery_v2_conf_data",
                                       "family": "建筑礼盒", "items": items}
            by_fam["建筑礼盒"] += 1

    stats = {
        "periods_total": len(periods),
        "periods_with_members": len(out_periods),
        "items_total": sum(len(v["items"]) for v in out_periods.values()),
        "by_family": dict(by_fam),
        "pools": len(pools),
    }
    doc = {"generated": GEN, "tree": str(TREE), "stats": stats,
           "periods": out_periods, "pools": pools}
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"奖池成员_{GEN}.json"
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))
    print("写出:", p.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
