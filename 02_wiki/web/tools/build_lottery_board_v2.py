# -*- coding: utf-8 -*-
r"""把 lottery_inventory + lottery_server_variants 合并成奖池板 v2。

- 期次卡：family × period_key
- 成员：每槽一条，带 kind（奖励类型）、server（服型集合）
- 图标：沿用现有板里同 item_id 的 _media；其余留空待补
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
DET = PROJ / "01_索引与产物/10_索引/热更检测"

FAMILY_CN = {
    "SuperFashion": "幻彩典藏",
    "SuperFashionDragonPray": "龙祈福袋",
    "OnlyFashion": "纯外观抽奖",
    "MultiOptional": "多时装抽奖",
    "OptionalChenshi": "宸世臻藏",
    "BeltChipSpecialLottery": "限定芯片",
    "LotteryTeam": "组队抽奖",
    "T1BuildingObjectLotteryV2": "建筑抽奖 T1",
    "T2BuildingObjectLottery": "家具抽奖 T2",
    "T2FurnitureBox": "家具盒",
    "NucleusLottery": "核芯抽奖",
    "PigeonWish": "许愿池",
    "FurnitureReturnLottery": "家具返场",
    "VehicleLottery": "载具抽奖",
    "XiYangYang": "羊狼寻宝",
    "LotteryBigReward": "大奖池",
    "CommonLottery": "通用抽奖",
}


def main() -> int:
    import hashlib
    INV_BYTES = (DET / "lottery_inventory.json").read_bytes()
    INV_SHA = hashlib.sha256(INV_BYTES).hexdigest()
    inv = json.loads(INV_BYTES.decode("utf-8"))
    var = json.loads((DET / "lottery_server_variants.json").read_text(encoding="utf-8"))
    old = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))

    # 旧板 item_id → _media
    lock = (old["meta"]["provenance"].get("source_locks") or [{}])[0]
    LOCK_ID = lock.get("source_id")
    LOCK_SHA = lock.get("sha256")

    media_by_item = {}
    for it in old["items"]:
        ims = ((it.get("_media") or {}).get("images") or [])
        if ims and ims[0].get("png") and it.get("item_id"):
            media_by_item[str(it["item_id"])] = ims[0]

    # 期次索引：family → period_key → period
    pidx = {}
    for fam in inv["families"]:
        pidx[fam["family"]] = {p["period_key"]: p for p in (fam.get("periods") or [])}

    rewards = var.get("rewards") or {}
    svars = var.get("server_variants") or {}

    periods, items = [], []
    for fam_key, pools in rewards.items():
        cn = FAMILY_CN.get(fam_key, fam_key)
        per_src = pidx.get(fam_key, {})
        by_period = {}
        for pool in pools:
            pk = pool.get("period_key") or "?"
            by_period.setdefault(pk, []).append(pool)
        for pk, plist in by_period.items():
            src = per_src.get(pk) or {}
            label = src.get("activity_name") or plist[0].get("activity_name") or pk
            pid = "%s:%s" % (fam_key, pk)
            states = var.get("families", {}).get(fam_key, {})
            periods.append({
                "period_id": pid,
                "label": label,
                "activity_name": label,
                "family": cn,
                "family_key": fam_key,
                "start": src.get("start") or "",
                "end": src.get("end") or "",
                "server": "classic",
                "pool_count": len(plist),
                "member_count": sum(p.get("member_count") or len(p.get("members") or []) for p in plist),
            })
            for pool in plist:
                plabel = "%s · %s" % (label, pool.get("pool_kind") or "池")
                for m in (pool.get("members") or []):
                    iid = m.get("item_id")
                    if not iid:
                        continue
                    key = str(iid)
                    md = media_by_item.get(key)
                    n = len(items) + 1
                    items.append({
                        "id": "%s:%s:%s:%s" % (fam_key, pk, pool.get("pool_id"), m.get("item_id")),
                        "name": m.get("name") or ("道具 %s" % iid),
                        "item_id": iid,
                        "kind": m.get("kind") or "其他",
                        "kind_evidence": m.get("kind_evidence"),
                        "slot": m.get("slot"),
                        "period_id": pid,
                        "period_label": label,
                        "period_start": src.get("start") or "",
                        "period_end": src.get("end") or "",
                        "pool_id": pool.get("pool_id"),
                        "pool_label": plabel,
                        "pool_kind": pool.get("pool_kind"),
                        "family": cn,
                        "server": "classic",
                        "source": "%s · %s · pool %s · slot %s" % (fam_key, pool.get("evidence_table") or "-", pool.get("pool_id"), m.get("slot")),
                        "evidence": "structure",
                        "evidence_level": "structure-only",
                        "status_tags": ["verified", "static config"],
                        "icon": m.get("icon"),
                        "icon_state": "有图" if md else "未下发",
                        "_media": {"images": [md], "total": 1} if md else {"images": [], "total": 0},
                        "provenance": {
                            "source_id": LOCK_ID,
                            "source_lock_sha256": LOCK_SHA,
                            "table": pool.get("evidence_table") or fam_key,
                            "row_key": pool.get("row_key") or pool.get("pool_id"),
                            "field_refs": ["item_id", "name", "slot", "kind"],
                            "name_source": m.get("name_source") or "inventory",
                            "upstream": {"package_sha256": LOCK_SHA, "role": pool.get("evidence_table") or fam_key},
                            "locator_chain": {
                                "chain_status": "replayed-structural",
                                "scope": "record",
                                "no_cross_source_field_join": True,
                                "steps": [{"kind": "decoded-table-row",
                                           "source_id": LOCK_ID,
                                           "table": pool.get("evidence_table") or fam_key,
                                           "row_key": pool.get("row_key") or pool.get("pool_id"),
                                           "field_refs": ["item_id", "name", "slot", "kind"]}],
                            },
                        },
                    })

    print("期次", len(periods), "｜成员", len(items))
    import collections
    print("家族期次", collections.Counter(p["family"] for p in periods).most_common())
    print("类型", collections.Counter(i["kind"] for i in items).most_common(8))

    meta = old["meta"]
    meta.update({
        "name": "当期&历史每期抽奖奖池",
        "category": "三、活动类 / （一）限时主题类 / 1、当期&历史每期抽奖奖池",
        "evidence": "structure",
        "card_mode": "period",
        "card_summary": [],
        "state_summary": {
            "期次": len(periods),
            "奖池": sum(p["pool_count"] for p in periods),
            "成员": len(items),
            "有图": sum(1 for i in items if i["icon_state"] == "有图"),
            "家族": len({p["family"] for p in periods}),
        },
    })
    meta["notes"] = ("数据源：lottery_inventory.json（17 家族）+ lottery_server_variants.json（服型/类型）。"
                     "服型：base=经典服；kj1/kjxq=简单生存；yk=会员专享。"
                     "成员为静态配置槽位，运行时最终结果以服务端下发为准。")
    out = {"meta": meta, "periods": periods, "items": items}
    p = WEB / "data/boards/lottery_periods.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("写入", p, p.stat().st_size // 1024, "KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
