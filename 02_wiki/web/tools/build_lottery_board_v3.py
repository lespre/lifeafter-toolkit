# -*- coding: utf-8 -*-
r"""奖池板 v3：严格按活动表重建。

规范：
  一行 huodong(kj1) 里 hd_class 属抽奖类 = 一期，**不合并、不按名字猜**。
  成员只挂结构可证的：SuperFashion → panel_show_item_ids(+588)；芯片 → up_chips/new_chips。
  其余期次成员为空，不编造。
"""
from __future__ import annotations

import copy
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
DET = PROJ / "01_索引与产物/10_索引/热更检测"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

TODAY = datetime.date.today()
LOTTERY_RE = re.compile(r"Lottery|Roulette|PigeonWish|BuildingObject|FashionSuit|SecretFashion|WishFashion")

CLASS_CN = {
    "SuperFashionLotteryHD": "大版本奖池", "MultiOptionalLotteryHD": "自选保底抽奖",
    "OnlyFashionLotteryHD": "不放回抽奖", "BuildingObjectLotteryHD": "家具抽奖",
    "T1BuildingObjectLotteryHDV2": "家具抽奖", "BeltChipSpecialLotteryHD": "限定芯片抽奖",
    "LotteryTeamHD": "返利小队", "RouletteLotteryHD": "转盘抽奖",
    "NucleusLotteryHD": "核芯抽奖", "FashionBoxLotteryHD": "时装盒抽奖",
    "PigeonWishHDV2": "许愿池", "PigeonWishHD": "许愿池",
    "AccumulateGiftLotteryHD": "累充抽奖", "ScorpioSuperLotteryHD": "天蝎座奖池",
    "FashionSuitLotteryHD": "套装抽奖", "SecretFashionHD": "秘藏时装",
    "DragonBlessingLotteryHD": "龙祈福袋", "BlessingsAlwaysLotteryHD": "福运常在抽奖",
    "VehicleLotteryHD": "载具抽奖", "NewVehicleLotteryHDV2": "载具抽奖",
    "OptionalLotteryHD": "自选奖池", "FashionDiyLotteryHD": "时装 DIY 抽奖",
}


def day(ts):
    if not isinstance(ts, (int, float)) or ts < 1e9:
        return ""
    return datetime.datetime.fromtimestamp(ts + 8 * 3600, datetime.UTC).strftime("%Y-%m-%d")


def status_of(st: str, en: str):
    if not st:
        return "无时间"
    if TODAY < datetime.date.fromisoformat(st):
        return "未开始"
    if en and TODAY > datetime.date.fromisoformat(en):
        return "已结束"
    return "进行中"


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

    preview = {int(x["conf_key"]): x.get("preview_ids") or []
               for x in json.loads((DET / "superfashion_preview.json").read_text(encoding="utf-8"))}

    # 名称表
    im = json.loads((WEB / "data/boards/item_master_full.json").read_text(encoding="utf-8"))
    names = {str(i.get("item_id")): i.get("name") for i in im["items"] if i.get("name")}

    # 芯片：conf → chips
    cp = CD / "special_chip_lottery_hd_conf_data_auto_oversea_data_kj1.py"
    chips = {}
    if cp.is_file():
        craw = cp.read_bytes()
        cat = craw.find(b"x{")
        cL = struct.unpack_from("<I", craw, cat + 2)[0]
        cbody = craw[cat + 6: cat + 6 + cL]
        cnt = struct.unpack_from("<I", cbody, 0)[0]
        blob = cbody[8 + 4 * cnt:]
        pools = BT.parse_legacy_chs_pool((CD / "special_chip_lottery_hd_conf_data_auto_oversea_data_kj1_chs.py").read_bytes())
        crows, _ = BT.decode_table_rows(cbody, pools, resolve_jumps=False)

        def uleb(b, i):
            r = s = 0
            while True:
                x = b[i]
                i += 1
                r |= (x & 0x7F) << s
                s += 7
                if x < 0x80:
                    return r, i

        def grp(off):
            if not off or blob[off] != 0x27:
                return []
            n = blob[off + 2]
            j = off + 3
            out = []
            for _ in range(n):
                v, j = uleb(blob, j)
                out.append(v)
            return out

        for r in crows:
            def conv(v):
                return int(str(v).split(":")[1]) if v else None
            ids = grp(conv(g(r, "up_chips"))) + grp(conv(g(r, "new_chips")))
            chips[r["key"]] = list(dict.fromkeys(ids))

    # 活动展示表：key=活动 id → show_item_ids（结构可证）
    show_map = {}
    sp = (PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata/common_hd_show_reward_data.py")
    sc = sp.with_name("common_hd_show_reward_data_chs.py")
    if sp.is_file():
        sraw = sp.read_bytes()
        sat = sraw.find(b"x{")
        sL = struct.unpack_from("<I", sraw, sat + 2)[0]
        sbody = sraw[sat + 6: sat + 6 + sL]
        scnt = struct.unpack_from("<I", sbody, 0)[0]
        sblob = sbody[8 + 4 * scnt:]
        srows, _ = BT.decode_table_rows(sbody, BT.parse_legacy_chs_pool(sc.read_bytes()) if sc.is_file() else {}, resolve_jumps=False)

        def uleb2(b, i):
            r = s = 0
            while True:
                x = b[i]
                i += 1
                r |= (x & 0x7F) << s
                s += 7
                if x < 0x80:
                    return r, i

        def grp2(off):
            if not off or sblob[off] != 0x27:
                return []
            n = sblob[off + 2]
            j = off + 3
            out = []
            for _ in range(n):
                v, j = uleb2(sblob, j)
                out.append(v)
            return out

        for r in srows:
            v = r["values"].get("show_item_ids")
            v = (v[1] if isinstance(v, tuple) else v) if v else None
            if not v:
                continue
            show_map[str(r["key"])] = grp2(int(str(v).split(":")[1]))

    old = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    tpl_period = old["periods"][0]
    tpl_prov = old["items"][0]["provenance"]

    periods, items = [], []
    for r in rows:
        cls = str(g(r, "hd_class") or "")
        if not LOTTERY_RE.search(cls):
            continue
        conf = str(g(r, "extra_param") or "")
        st, en = day(g(r, "start_ts")), day(g(r, "end_ts"))
        stt = status_of(st, en)
        pid = "lp_%s" % r["key"]
        fam = CLASS_CN.get(cls, "抽奖活动")
        per = {"period_id": pid, "label": str(g(r, "name") or r["key"]),
                    "activity_name": str(g(r, "name") or ""), "activity_id": r["key"],
                    "family": fam, "family_key": cls, "start": st, "end": en,
                    "status": stt, "conf_key": conf, "member_count": 0,
                    "pool_count": 1, "pool_size": 0}
        periods.append(per)

        ids = []
        if cls == "SuperFashionLotteryHD" and conf.isdigit():
            ids = list(preview.get(int(conf), []))
        elif cls == "BeltChipSpecialLotteryHD" and conf.isdigit():
            ids = list(chips.get(int(conf), []))
        if not ids:
            ids = list(show_map.get(str(r["key"]), []))

        for k, iid in enumerate(dict.fromkeys(ids)):
            sid = str(iid)
            prov = copy.deepcopy(tpl_prov)
            prov["table"] = cls
            prov["row_key"] = r["key"]
            ch = copy.deepcopy(prov.get("locator_chain") or {})
            ch["steps"] = [{"kind": "decoded-table-row",
                            "source_id": prov.get("source_id", "documents-py314-current"),
                            "table": cls, "row_key": r["key"],
                            "field_refs": ["extra_param"]}]
            prov["locator_chain"] = ch
            items.append({
                "id": "%s_%d" % (pid, k), "period_id": pid, "period_label": per["label"],
                "period_start": st, "period_end": en, "family": fam, "family_key": cls,
                "name": names.get(sid) or ("道具 %s" % sid), "item_id": sid, "kind": "奖池奖励",
                "evidence": "structure", "evidence_level": "static/candidate",
                "status_tags": ["static config"],
                "_media": {"images": [], "total": 0}, "icon_state": "未下发",
                "source": "huodong_conf(%s) conf %s" % (cls, conf),
                "provenance": prov,
            })
            icon_png = WEB / "assets/lottery_icons" / (re.sub(r"[^0-9A-Za-z_.-]+", "_", sid) + ".png")
            if icon_png.is_file():
                items[-1]["_media"] = {"images": [{"png": "assets/lottery_icons/" + icon_png.name,
                                                   "label": "图标"}], "total": 1}
                items[-1]["icon_state"] = "有图"
            per["member_count"] += 1

    # ── 候选层：从归档旧板按「活动名 + 最接近的开始日」取成员，单列证据候选
    arc_path = WEB / "data/boards/_archive_lottery_20261020.json"
    if arc_path.is_file():
        arc = json.loads(arc_path.read_text(encoding="utf-8"))
        old_by_period = {}
        for it in arc["items"]:
            old_by_period.setdefault(it.get("period_id"), []).append(it)
        old_periods = [x for x in arc["periods"] if (old_by_period.get(x["period_id"]))]

        def dnum(s):
            try:
                return datetime.date.fromisoformat(s).toordinal()
            except Exception:
                return None

        cand_total = 0
        for per in periods:
            have = {str(i["item_id"]) for i in items if i["period_id"] == per["period_id"]}
            nm = per.get("activity_name") or ""
            dn = dnum(per.get("start") or "")
            best, bestd = None, None
            for op in old_periods:
                if (op.get("activity_name") or op.get("label") or "") != nm:
                    continue
                od = dnum(op.get("start") or "")
                dist = abs(od - dn) if (od and dn) else 10**6
                if bestd is None or dist < bestd:
                    best, bestd = op, dist
            if not best:
                continue
            for oi in old_by_period.get(best["period_id"], []):
                sid = str(oi.get("item_id"))
                if not sid or sid in have:
                    continue
                have.add(sid)
                prov = copy.deepcopy(tpl_prov)
                prov["table"] = "lottery_periods(archive)"
                prov["row_key"] = per["activity_id"]
                items.append({
                    "id": "%s_c%s" % (per["period_id"], sid), "period_id": per["period_id"],
                    "period_label": per["label"], "period_start": per.get("start"),
                    "period_end": per.get("end"), "family": per["family"],
                    "family_key": per["family_key"],
                    "name": (names.get(sid) if str(oi.get("name") or "") in ("", "待命名", "未知", "None") else oi.get("name")) or ("道具 %s" % sid),
                    "item_id": sid, "kind": "奖池奖励（候选）",
                    "evidence": "candidate", "evidence_level": "static/candidate",
                    "status_tags": ["static config"], "_media": oi.get("_media") or {"images": [], "total": 0},
                    "icon_state": oi.get("icon_state") or "未下发",
                    "source": "归档旧板按活动名匹配（候选）", "provenance": prov,
                })
                per["member_count"] += 1
                cand_total += 1
        print("候选成员", cand_total)

    order = {"进行中": 0, "未开始": 1, "已结束": 2, "无时间": 3}
    periods.sort(key=lambda x: (order.get(x["status"], 9), x["start"] or ""))

    meta = copy.deepcopy(old["meta"])
    meta["name"] = "当期&历史每期抽奖奖池（按活动表重建）"
    meta["generated"] = TODAY.isoformat()
    meta["state_summary"] = {"期次": len(periods), "成员": len(items),
                             "候选成员": sum(1 for i in items if i.get("evidence") == "candidate"),
                             "有成员期次": sum(1 for p_ in periods if p_["member_count"]),
                             "进行中": sum(1 for p_ in periods if p_["status"] == "进行中"),
                             "未开始": sum(1 for p_ in periods if p_["status"] == "未开始")}
    meta["notes"] = ("一期 = 活动表里一条抽奖活动，不合并同名活动。"
                     "成员仅挂结构可证的（大版本奖池=面板预览，限定芯片=up/new chips），其余期次不编成员。")

    out = {"meta": meta, "periods": periods, "items": items}
    (WEB / "data/boards/lottery_periods.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("期次", len(periods), "｜成员", len(items), "｜", meta["state_summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
