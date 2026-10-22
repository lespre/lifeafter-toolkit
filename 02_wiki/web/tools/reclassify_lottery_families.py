# -*- coding: utf-8 -*-
r"""奖池板统一整理：按 huodong_conf 的 hd_class 重新归族 + 同名活动合并 + 期内去重。

hd_class → 家族：
  SuperFashionLotteryHD / DragonBlessingLotteryHD / BlessingsAlwaysLotteryHD / Scorpio* / Chitu* → 大版本奖池
  MultiOptionalLotteryHD / FashionDiyLotteryHD      → 自选保底奖池
  OnlyFashionLotteryHD                              → 不放回抽奖
  VehicleLotteryHD / NewVehicleLotteryHDV2          → 无人机奖池
  OptionalLotteryHD                                 → 宸世臻藏
  BeltChipSpecialLotteryHD                          → 限定芯片
  T1/T2 bobj                                        → 家具抽奖
  XiYangYang                                        → 羊狼寻宝
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import Counter

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CLASS_FAMILY = {
    "SuperFashionLotteryHD": "大版本奖池",
    "DragonBlessingLotteryHD": "大版本奖池",
    "BlessingsAlwaysLotteryHD": "大版本奖池",
    "ScorpioSuperLotteryHD": "大版本奖池",
    "ChituSuperLotteryHD": "大版本奖池",
    "MultiOptionalLotteryHD": "自选保底奖池",
    "FashionDiyLotteryHD": "自选保底奖池",
    "OnlyFashionLotteryHD": "不放回抽奖",
    "VehicleLotteryHD": "无人机奖池",
    "NewVehicleLotteryHDV2": "无人机奖池",
    "OptionalLotteryHD": "宸世臻藏",
    "BeltChipSpecialLotteryHD": "限定芯片",
    "XiYangYangLotteryHD": "羊狼寻宝",
    "T1BuildingObjectLotteryHD": "家具抽奖",
    "T2BuildingObjectLotteryHD": "家具抽奖",
}


def main() -> int:
    p = CD / "oversea/huodong_conf_data_auto_oversea_data_kj1.py"
    c = CD / "oversea/huodong_conf_data_auto_oversea_data_kj1_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=True)

    name2fam = {}
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        nm = str(f.get("name") or "").strip()
        cls = str(f.get("hd_class") or "")
        fam = CLASS_FAMILY.get(cls)
        if nm and fam:
            name2fam[nm] = fam

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    print("活动名→家族", len(name2fam))

    # 1) 重新归族
    re_fam = 0
    for per in d["periods"]:
        nm = str(per.get("activity_name") or "").strip()
        fam = name2fam.get(nm)
        if fam and per.get("family") != fam:
            per["family"] = fam
            re_fam += 1

    # 2) 同名活动合并期次
    by_name = {}
    for per in d["periods"]:
        nm = str(per.get("activity_name") or per.get("label") or "")
        by_name.setdefault((nm, per.get("family")), []).append(per)
    drop = set()
    remap = {}
    for (nm, fam), group in by_name.items():
        if len(group) < 2:
            continue
        group.sort(key=lambda x: (x.get("start") or "9999", x["period_id"]))
        keep = group[0]
        for other in group[1:]:
            drop.add(other["period_id"])
            remap[other["period_id"]] = keep["period_id"]
            keep["start"] = keep.get("start") or other.get("start") or ""
            keep["end"] = keep.get("end") or other.get("end") or ""
            if other.get("pool_size") and not keep.get("pool_size"):
                keep["pool_size"] = other["pool_size"]

    # 3) 迁移成员 + 期内去重
    items = []
    seen = set()
    moved = 0
    for it in d["items"]:
        pid = remap.get(it["period_id"], it["period_id"])
        it["period_id"] = pid
        key = (pid, str(it.get("item_id")))
        if key in seen:
            continue
        seen.add(key)
        items.append(it)
        if pid != it.get("period_id"):
            moved += 1

    d["periods"] = [x for x in d["periods"] if x["period_id"] not in drop]
    d["items"] = items
    for per in d["periods"]:
        per["member_count"] = sum(1 for i in d["items"] if i["period_id"] == per["period_id"])
    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("重新归族", re_fam, "｜合并期次", len(drop), "｜迁移成员", moved,
          "｜总期次", len(d["periods"]), "｜总成员", len(d["items"]))
    print("家族分布", Counter(p.get("family") for p in d["periods"]).most_common(12))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
