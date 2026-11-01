#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""奖池「池 → 道具」全量映射构建（当前还原树口径）。

产物（只读配置，不写板）：
  01_索引与产物/30_分析/奖池映射_<date>.json
  01_索引与产物/30_分析/奖池映射_<date>.md

三层：
  ① pools      池号 → 成员（来自映射表 0x36 / 行内 0x27 组 / 行字段 jumper）
  ② bindings   配置键 → 池号（来自各家族 conf 表的 lottery_id / reward_pool_id / pool_id…）
  ③ periods    期次（活动表）→ 配置键 → 池号 → 成员，用于写板

证据口径全部标 structure；解不出的池只登记池号与来源，不编成员。
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))

import rebuild_lottery_periods as R  # noqa: E402

TREE = R.TREE
OUT_DIR = Path(r"E:\la拆包项目\01_索引与产物\30_分析")
GEN = dt.date.today().strftime("%Y%m%d")

ID_LO, ID_HI = 10000, 3_000_000_000

# 映射表：key = 池号 / 选项号 / 礼盒号，slot → 0x86 明细行 → 行内 0x27 组 = 成员
MAP_TABLES = [
    ("only_fashion_hd_reward_pool_conf", "纯外观抽奖"),
    ("multi_optional_lottery_option_data", "多时装抽奖"),
    ("falcon_reward_pool_data", "猎鹰寻宝"),
    ("home_dream_hd_reward_pool_conf", "家园梦"),
    ("dance_party_lottery_data", "舞会"),
    ("box_lottery_data", "宝箱抽奖"),
    ("building_obj_lottery_conf", "建筑抽奖"),
    ("roulette_lottery_share_data", "转盘分享"),
    ("weekly_lottery_conf_data", "周常抽奖"),
    ("vehicle_lottery_exchange_shop_data", "载具兑换"),
    ("vehicle_lottery_decompose_data", "载具分解"),
    ("super_fashion_lottery_exchange_shop_data", "典藏兑换"),
    ("fashion_diy_lottery_item_show_data", "配饰盲盒"),
    ("T1_bobj_lottery_v2_model_preview_conf_data", "家具T1预览"),
]

# conf 表：key → 池号（字段从一个到多个，取第一个命中的）
CONF_POOL_FIELDS = [
    "reward_pool_id", "lottery_pool_id", "lottery_id", "pool_id",
    "reward_pools_id", "a_lottery_id", "b_lottery_id", "base_lottery_id",
    "option_pool_id", "lottery_conf_ids",
]

# hd_class → conf 表（用于把期次绑到配置键）
FAMILY_CONF = {
    "SuperFashionLotteryHD": "super_fashion_lottery_conf_data",
    "BlessingsAlwaysLotteryHD": "super_fashion_lottery_conf_data",
    "DragonBlessingLotteryHD": "super_fashion_lottery_conf_data",
    "MultiOptionalLotteryHD": "multi_optional_lottery_conf_data",
    "BeltChipSpecialLotteryHD": "special_chip_lottery_hd_conf_data",
    "NewServerBeltChipSpecialLotteryHD": "special_chip_lottery_hd_conf_data",
    "BuildingObjectLotteryHD": "building_lottery_v2_conf_data",
    "T1BuildingObjectLotteryHDV2": "T1_bobj_lottery_v2_base_conf_data",
    "T2BuildingObjectLotteryHD": "T2_bobj_lottery_reward_conf_data",
    "OnlyFashionLotteryHD": "only_fashion_hd_lottery_conf",
    "XiYangYangLotteryHD": "xi_yang_yang_lottery_conf_data",
    "RouletteLotteryHD": "roulette_lottery_conf_data",
    "NucleusLotteryHD": "nucleus_lottery_conf_data",
    "LotteryTeamHD": "lottery_team_hd_conf_data",
}


def looks_item(v) -> bool:
    return isinstance(v, int) and ID_LO <= v <= ID_HI and not (1_500_000_000 < v < 2_000_000_000)


def open_table(name: str):
    p = TREE / f"{name}.py"
    if not p.exists():
        return None
    chs = p.with_name(p.stem + "_chs.py")
    try:
        return R.Table(p, chs if chs.exists() else None)
    except Exception as exc:
        print(f"  ! {name} 打不开: {exc}")
        return None


def scan_map_table(name: str, family: str) -> tuple[dict, dict]:
    t = open_table(name)
    if not t or not t.map_start:
        return {}, {}
    pools, meta = {}, {"table": name, "family": family, "keys": len(t.map_start), "with_items": 0}
    for key, off in sorted(t.map_start.items()):
        try:
            slots = R.parse_map_row(t, off)
        except Exception:
            continue
        nxt = None
        ids = []
        for i, (slot, soff) in enumerate(slots):
            # 每个槽位只取「紧邻明细行起点的第一个 0x27 组」——再往后就是邻槽/历史期的组，
            # 大窗口会把别人的成员算进来（实测单池会从 3 件涨到 60+ 件）。
            grp = None
            j = soff
            limit = min(soff + 32, len(t.blob))
            while j < limit:
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
        if ids:
            # 同一个 id 在多个槽位重复出现 → 多半是 UI/背景位；最多容忍 2 个槽位
            rep = Counter(x for _s, x in ids)
            uniq, seen = [], set()
            for slot, x in sorted(ids):
                if rep[x] > 2 or x in seen:
                    continue
                seen.add(x)
                uniq.append({"slot": slot, "item_id": x})
            pools[str(key)] = {"pool_id": key, "family": family, "source_table": name,
                               "evidence": "structure", "items": uniq}
            meta["with_items"] += 1
    return pools, meta


def scan_conf_bindings() -> dict:
    """conf 表 key → 池号。"""
    out = {}
    for fname in sorted(set(FAMILY_CONF.values())):
        t = open_table(fname)
        if not t:
            continue
        for key, row in t.by_key.items():
            vals = row["values"]
            pools = []
            for f in CONF_POOL_FIELDS:
                v = vals.get(f)
                if isinstance(v, str) and v.startswith("jump:"):
                    pools += [x for x in t.jump_values(v) if 300000 <= x <= 500000]
                elif isinstance(v, int) and 300000 <= v <= 500000:
                    pools.append(v)
            if pools:
                out.setdefault(fname, {})[key] = sorted(set(pools))
    return out


def main() -> int:
    print("还原树:", TREE)
    pools, metas = {}, []
    for name, family in MAP_TABLES:
        p, m = scan_map_table(name, family)
        pools.update(p)
        if m:
            metas.append(m)
            print(f"  {name:52s} 键 {m['keys']:>4}  有道具 {m['with_items']:>4}")
    bindings = scan_conf_bindings()
    print("\nconf 绑定表:", {k: len(v) for k, v in bindings.items()})

    # 期次侧：读现有板（period_id / family_key / conf_key）
    board = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    periods = board["periods"]
    bound, unbound = 0, 0
    period_bind = {}
    for per in periods:
        cls = str(per.get("family_key") or "")
        conf_key = per.get("conf_key")
        try:
            ck = int(conf_key)
        except (TypeError, ValueError):
            ck = None
        table = FAMILY_CONF.get(cls)
        ids = []
        if table and ck is not None:
            ids = bindings.get(table, {}).get(ck, [])
        if ids:
            bound += 1
            period_bind[per["period_id"]] = {"conf_table": table, "conf_key": ck, "pools": ids,
                                             "members": sum(len(pools.get(str(i), {}).get("items", []))
                                                            for i in ids)}
        else:
            unbound += 1

    stats = {
        "pools_with_members": len(pools),
        "member_total": sum(len(p["items"]) for p in pools.values()),
        "by_family": dict(Counter(p["family"] for p in pools.values()).most_common()),
        "periods": len(periods),
        "periods_bound": bound,
        "periods_unbound": unbound,
    }
    print("\n池带成员:", stats["pools_with_members"], "| 成员条:", stats["member_total"])
    print("期次:", stats["periods"], "| 绑上池:", bound, "| 未绑:", unbound)

    doc = {"generated": GEN, "tree": str(TREE), "stats": stats,
           "map_tables": metas, "pools": pools, "period_bindings": period_bind}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jp = OUT_DIR / f"奖池映射_{GEN}.json"
    jp.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = [f"# 奖池映射（{GEN}）", "",
             f"- 带成员的池：**{stats['pools_with_members']}**，成员条目 **{stats['member_total']}**",
             f"- 期次 {stats['periods']}：已绑池 **{bound}**，未绑 {unbound}", "",
             "## 按家族", "", "| 家族 | 池数 |", "|---|---|"]
    for fam, n in stats["by_family"].items():
        lines.append(f"| {fam} | {n} |")
    lines += ["", "## 映射表", "", "| 表 | 键数 | 有道具 |", "|---|---|---|"]
    for m in metas:
        lines.append(f"| `{m['table']}` | {m['keys']} | {m['with_items']} |")
    mp = OUT_DIR / f"奖池映射_{GEN}.md"
    mp.write_text("\n".join(lines), encoding="utf-8")
    print("写出:", jp.name, "/", mp.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
