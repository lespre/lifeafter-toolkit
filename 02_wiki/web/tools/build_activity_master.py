# -*- coding: utf-8 -*-
r"""活动总表：huodong_conf(kj1) 一行一个活动。

字段：名称 / 类型（hd_class 中文）/ 起止 / 状态 / 排序。
类型中文映射只覆盖已知类；未识别的统一显示「其他活动」，原始类名放技术详情。
"""
from __future__ import annotations

import datetime
import json
import pathlib
import re
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
from _src import cdata_dir
CD = cdata_dir("oversea")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

TODAY = datetime.date.today()

CLASS_CN = {
    "FashionSaleHD": "时装商城", "LotteryTeamHD": "返利小队",
    "AnniversarySignInHD": "周年签到", "BeltChipSpecialLotteryHD": "限定芯片抽奖",
    "SuperFashionLotteryHD": "大版本奖池", "NewTokenExchangeHD": "代币兑换",
    "InviteMissionHuodong": "邀请任务", "RouletteLotteryHD": "转盘抽奖",
    "GiftStoreHD": "礼包商店", "StoreLuckyBoxHDV2": "商店幸运箱",
    "AccumulateGiftLotteryHD": "累充抽奖", "SecretFashionHD": "秘藏时装",
    "GetRewardHD": "领奖活动", "BuildingObjectLotteryHD": "家具抽奖",
    "T1BuildingObjectLotteryHDV2": "家具抽奖", "WelfareJumpHuoDong": "福利跳转",
    "NucleusLotteryHD": "核芯抽奖", "ClimbTowerHuoDong": "爬塔",
    "FashionBoxLotteryHD": "时装盒抽奖", "PigeonWishHDV2": "许愿池",
    "MultiOptionalLotteryHD": "自选保底抽奖", "RadiationFundHD": "辐射基金",
    "DoubleClimbTowerSummaryHD": "双塔总结", "DiscountMarketHD": "折扣商店",
    "NucleusHD": "核芯活动", "JigsawHD": "拼图", "ChainGiftHD": "连充礼包",
    "BlessingsAlwaysLotteryHD": "福运常在抽奖", "WishFashionHDV2": "许愿时装",
    "MinesweeperHD": "扫雷", "SigninBattlepassHDV2": "签到通行证",
    "ChristmasGiftHuoDong": "圣诞礼包", "CheapSubscribeHD": "特惠订阅",
    "ScorpioSuperLotteryHD": "天蝎座奖池", "FashionSuitLotteryHD": "套装抽奖",
    "OnlyFashionLotteryHD": "不放回抽奖", "FirstPayHD": "首充",
    "LotteryTeamHD": "返利小队", "AsoulHalloweenHD": "A-SOUL 联动",
    "ClimbTowerV2HD": "通行证", "WeaponRebirthPlanHD": "武器重生计划",
    "TransformPartyHD": "变身派对", "CombineExchangeHuoDong": "收集兑换",
    "VehicleLotteryHD": "载具抽奖", "NewVehicleLotteryHDV2": "载具抽奖",
    "FashionDiyLotteryHD": "时装 DIY 抽奖", "OptionalLotteryHD": "自选奖池",
    "DragonBlessingLotteryHD": "龙祈福袋",
}

# 归类规则：先看是否命中已知中文名，否则按类名词根归大类
RULES = [
    ("Lottery", "抽奖"),
    ("SignIn|Signin", "签到"),
    ("Exchange|Token", "兑换"),
    ("Mission|Task", "任务"),
    ("Store|Market|Sale|Subscribe|Pay|Fund|Pass", "商城付费"),
    ("Welfare|Reward|Gift|Fund", "福利礼包"),
    ("ClimbTower|Battle|Boss|Challenge|Rank|Pvp|PVP", "挑战排行"),
    ("Invite|Team|Social|Friend", "社交组队"),
    ("Fashion|Appear|Suit", "时装外观"),
    ("Jigsaw|Minesweeper|Puzzle|Bingo|Scratch|Card|Collect", "收集小游戏"),
    ("RedEnvelope|ManJian|Duty|Discount|Pumpkin|SnowMan|Christmas|Halloween", "节日福利"),
    ("HuoDong", "常规活动"),
]


def _perm(st: str, en: str) -> str:
    """常开 = 无结束时间且已开超过 90 天；新开/未开始但缺结束时间仍算限时。"""
    if en:
        return "限时"
    if not st:
        return "限时"
    days = (TODAY - datetime.date.fromisoformat(st)).days
    return "常开" if days > 90 else "限时"


def classify(cls: str) -> str:
    if cls in CLASS_CN:
        return CLASS_CN[cls]
    for pat, cn in RULES:
        if re.search(pat, cls, re.I):
            return cn if cn.endswith("活动") else "%s类活动" % cn
    return "常规活动"


def day(ts) -> str:
    if not isinstance(ts, (int, float)) or ts < 1e9:
        return ""
    return datetime.datetime.fromtimestamp(ts + 8 * 3600, datetime.UTC).strftime("%Y-%m-%d")


def _prov(tpl: dict, row_key: int, cls: str, hd_type: str, ui_class: str) -> dict:
    import copy
    pr = copy.deepcopy(tpl)
    pr["table"] = "huodong_conf_data_auto_oversea_data_kj1"
    pr["row_key"] = row_key
    pr["field_refs"] = ["name", "hd_class", "start_ts", "end_ts"]
    ch = copy.deepcopy(pr.get("locator_chain") or {})
    ch["steps"] = [{"kind": "decoded-table-row",
                    "source_id": pr.get("source_id", "documents-py314-current"),
                    "table": pr["table"], "row_key": row_key,
                    "field_refs": ["name", "hd_class", "start_ts", "end_ts"]}]
    ch["chain_status"] = "replayed-structural"
    ch["scope"] = "record"
    ch["no_cross_source_field_join"] = True
    pr["locator_chain"] = ch
    pr["tech"] = {"hd_class": cls, "hd_type": hd_type, "ui_class": ui_class}
    return pr


def main() -> int:
    p = CD / "huodong_conf_data_auto_oversea_data_kj1.py"
    c = CD / "huodong_conf_data_auto_oversea_data_kj1_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    rows, _ = BT.decode_table_rows(raw[at + 6: at + 6 + L],
                                   BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    ref_board = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    tpl_prov = ref_board["items"][0]["provenance"]

    items = []
    for r in rows:
        name = str(g(r, "name") or "").strip()
        if not name:
            continue
        cls = str(g(r, "hd_class") or "")
        st, en = day(g(r, "start_ts")), day(g(r, "end_ts"))
        if st:
            if TODAY < datetime.date.fromisoformat(st):
                status, sk = "未开始", "upcoming"
            elif en and TODAY > datetime.date.fromisoformat(en):
                status, sk = "已结束", "ended"
            else:
                status, sk = "进行中", "on"
        else:
            status, sk = "无时间", "unknown"
        items.append({
            "id": "act_%s" % r["key"],
            "item_id": r["key"],
            "name": name,
            "kind": "活动",
            "activity_type": classify(cls),
            "sub_title": str(g(r, "sub_title") or "").strip(),
            "month": (st[:7] if st else ""),
            "permanent": _perm(st, en),
            "first_level_tab": str(g(r, "first_level_tab") or "").strip(),
            "tab_name": str(g(r, "tab_name") or "").strip(),
            "start": st, "end": en, "activity_status": status,
            "family": status, "family_key": "Activity",
            "_media": {"images": [], "total": 0},
            "evidence": "structure", "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "source": "huodong_conf_data_auto_oversea_data_kj1",
            "provenance": _prov(tpl_prov, r["key"], cls,
                                 str(g(r, "hd_type") or ""), str(g(r, "ui_class") or "")),
        })

    # 来源锁用现有板块的
    ref = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    lock = (ref["meta"].get("provenance") or {}).get("source_locks", [{}])[0]
    for it in items:
        it["provenance"]["source_lock_sha256"] = lock.get("sha256", "")

    # 倒序：新的在前；无时间的排最后
    items.sort(key=lambda i: (i["start"] or "0000-00-00"), reverse=True)
    items.sort(key=lambda i: 0 if i["start"] else 1)

    stats = {}
    for it in items:
        stats[it["family"]] = stats.get(it["family"], 0) + 1

    board = {
        "meta": {
            "name": "活动总表 · 全部活动与起止时间",
            "category": "三、活动类 / （零）活动总表",
            "source_server": "简单生存服（huodong_conf kj1）",
            "generated": TODAY.isoformat(),
            "evidence": "structure",
            "card_mode": "roster",
            "filters": [{"key": "activity_status", "label": "状态"},
                        {"key": "month", "label": "月份"},
                        {"key": "permanent", "label": "常开"},
                        {"key": "first_level_tab", "label": "页签"}],
            "filter_defaults": {"permanent": "限时"},
            "card_summary": [["name", "活动"], ["sub_title", "子标题"], ["activity_type", "类型"],
                             ["start", "开始"], ["end", "结束"], ["activity_status", "状态"]],
            "field_labels": {"item_id": "活动ID", "kind": "类别", "family": "状态",
                             "sub_title": "子标题", "first_level_tab": "页签", "tab_name": "页签名",
                             "hd_class": "原始类名", "hd_type": "活动子类型", "ui_class": "界面类"},
            "state_summary": stats,
            "provenance": {"source_locks": [lock]},
            "notes": "一行 = huodong_conf 里一个活动；状态按今天计算。类型未识别时显示「其他活动」，原始类名在技术详情。",
        },
        "periods": [],
        "items": items,
    }
    out = WEB / "data/boards/activity_master.json"
    out.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/activity_master.js").write_text(
        "window.WIKI_BOARD_activity_master = " + json.dumps(board, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("活动", len(items), stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
