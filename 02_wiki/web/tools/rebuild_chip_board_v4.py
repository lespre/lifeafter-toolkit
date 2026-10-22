# -*- coding: utf-8 -*-
r"""重建「限定芯片」期次与成员（schema 解码版）。

huodong(kj1) hd_class=BeltChipSpecialLotteryHD → 一行一期（期名/时间/conf）
special_chip_lottery_hd_conf_data(kj1) → up_chips / new_chips（jump:<off> 解 0x27 组）
名字/图标 → _cache_official_icons.json
"""
from __future__ import annotations

import copy
import datetime
import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CLS = "BeltChipSpecialLotteryHD"
ANCHORS = {"31": ("330112", "以攻为守"), "32": ("330132", "处变不惊")}


def day(ts):
    if not isinstance(ts, (int, float)) or ts < 1e9:
        return ""
    return datetime.datetime.fromtimestamp(ts + 8 * 3600, datetime.UTC).strftime("%Y-%m-%d")


def uleb(b, i):
    r = s = 0
    while True:
        x = b[i]
        i += 1
        r |= (x & 0x7F) << s
        s += 7
        if x < 0x80:
            return r, i


def load_conf_chips(body, blob, pool):
    """conf key → {'up': [...], 'new': [...]}"""
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

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

    res = {}
    for r in rows:
        conv = lambda v: int(str(v).split(":")[1]) if v else None
        res[r["key"]] = {"up": grp(conv(g(r, "up_chips"))), "new": grp(conv(g(r, "new_chips")))}
    return res


def main() -> int:
    cache = json.loads((WEB / "_cache_official_icons.json").read_text(encoding="utf-8"))
    names, icons = cache["names"], cache["icons"]

    cp = CD / "oversea/special_chip_lottery_hd_conf_data_auto_oversea_data_kj1.py"
    raw = cp.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    conf_body = raw[at + 6: at + 6 + L]
    cnt = struct.unpack_from("<I", conf_body, 0)[0]
    conf_blob = conf_body[8 + 4 * cnt:]
    chips = load_conf_chips(conf_body, conf_blob, BT.parse_legacy_chs_pool((CD / "oversea/special_chip_lottery_hd_conf_data_auto_oversea_data_kj1_chs.py").read_bytes()))
    print("conf", len(chips), "｜有 up_chips", sum(1 for v in chips.values() if v["up"]))

    hp = CD / "oversea/huodong_conf_data_auto_oversea_data_kj1.py"
    hc = CD / "oversea/huodong_conf_data_auto_oversea_data_kj1_chs.py"
    hraw = hp.read_bytes()
    hat = hraw.find(b"x{")
    hL = struct.unpack_from("<I", hraw, hat + 2)[0]
    hbody = hraw[hat + 6: hat + 6 + hL]
    rows, _ = BT.decode_table_rows(hbody, BT.parse_legacy_chs_pool(hc.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    runs = [{"activity_id": r["key"], "name": str(g(r, "name") or "").strip(),
             "start": day(g(r, "start_ts")), "end": day(g(r, "end_ts")),
             "conf": str(g(r, "extra_param") or "")}
            for r in rows if str(g(r, "hd_class")) == CLS]
    runs.sort(key=lambda x: (x["start"], x["activity_id"]))

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    d["items"] = [x for x in d["items"] if x.get("family_key") != "BeltChipSpecialLottery"]
    d["periods"] = [x for x in d["periods"] if x.get("family_key") != "BeltChipSpecialLottery"]

    tpl = copy.deepcopy(d["items"][0]["provenance"]) if d["items"] and d["items"][0].get("provenance") else {}

    np_ = ni = named = 0
    for n, r in enumerate(runs, 1):
        pid = "chip:%s" % r["activity_id"]
        per = {"period_id": pid, "label": "%s · 第%d期" % (r["name"] or "限定芯片自选", n),
               "activity_name": r["name"], "family": "限定芯片", "family_key": "BeltChipSpecialLottery",
               "server": "classic", "start": r["start"], "end": r["end"],
               "conf_key": r["conf"], "member_count": 0}
        cid = int(r["conf"]) if r["conf"].isdigit() else None
        info = chips.get(cid) or {"up": [], "new": []}
        ids = []
        for x in info["up"] + info["new"]:
            if x not in ids:
                ids.append(x)
        per["up_chips"] = info["up"]
        per["new_chips"] = info["new"]
        d["periods"].append(per)
        np_ += 1
        for sid_int in ids:
            sid = str(sid_int)
            nm = names.get(sid) or "芯片 %s" % sid
            named += 1 if sid in names else 0
            prov = copy.deepcopy(tpl)
            prov["table"] = "special_chip_lottery_hd_conf_data"
            prov["row_key"] = cid
            ch = dict(copy.deepcopy((tpl or {}).get("locator_chain") or {}))
            step = dict((((tpl or {}).get("locator_chain") or {}).get("steps") or [{}])[0])
            step.update({"kind": "decoded-table-row",
                         "source_id": (tpl or {}).get("source_id", "documents-py314-current"),
                         "table": "special_chip_lottery_hd_conf_data",
                         "row_key": cid, "field_refs": ["up_chips", "new_chips"]})
            ch.update({"chain_status": "replayed-structural", "scope": "record",
                       "no_cross_source_field_join": True, "steps": [step]})
            prov["locator_chain"] = ch
            it = {"id": "%s_%s" % (pid, sid), "period_id": pid, "period_label": per["label"],
                  "period_start": r["start"], "period_end": r["end"],
                  "family": "限定芯片", "family_key": "BeltChipSpecialLottery",
                  "name": nm, "item_id": sid, "kind": "芯片",
                  "evidence": "structure", "evidence_level": "structure-only",
                  "status_tags": ["verified", "static config"],
                  "icon_state": "未下发",
                  "source": "special_chip_lottery_hd_conf_data(kj1) conf %s" % r["conf"],
                  "provenance": prov}
            ic = icons.get(sid)
            if ic:
                base = ic[:-4] if ic.lower().endswith((".png", ".ktx", ".dds")) else ic
                f = WEB / "assets/lottery_icons" / (sid + ".png")
                it["_media"] = {"images": [{"png": "assets/lottery_icons/" + f.name, "label": "图标"}], "total": 1}
                it["icon_state"] = "有图"
            d["items"].append(it)
            per["member_count"] += 1
            ni += 1
        a = ANCHORS.get(str(n))
        if a:
            per["note"] = "大奖芯片：%s（%s）" % (a[1], a[0])

    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    empty = [p for p in d["periods"] if p.get("family_key") == "BeltChipSpecialLottery" and not p["member_count"]]
    print("期次", np_, "｜成员", ni, "｜有名", named, "｜空期", len(empty))
    for p in d["periods"]:
        if p.get("family_key") == "BeltChipSpecialLottery" and p.get("new_chips"):
            print("  ", p["label"], "new", p["new_chips"], "up", p["up_chips"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
