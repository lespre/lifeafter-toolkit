# -*- coding: utf-8 -*-
r"""重建「限定芯片」期次与成员（按 huodong 活动一行一期）。

数据：
  huodong_conf(kj1) hd_class=BeltChipSpecialLotteryHD → 期名 / 时间 / conf
  special_chip_lottery_hd_conf_data(kj1) conf → 8 个研发池芯片 id（0x27 组）
名字/图标：_cache_official_icons.json（common_item + gift + recipe 合并）
锚点：add_chip_anchors.py 补的两期大奖芯片，保留在 note 里
"""
from __future__ import annotations

import datetime
import json
import pathlib
import re
import struct
import sys
from collections import defaultdict

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "04_站点/web"
CD = PROJ / "03_执行/41_还原树/pe_test_script/com/cdata"
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CLS = "BeltChipSpecialLotteryHD"


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


def decode_conf_chips():
    p = CD / "oversea/special_chip_lottery_hd_conf_data_auto_oversea_data_kj1.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    idx = sorted(BT.parse_index(blob))
    out = {}
    for pos, (k, off) in enumerate(idx):
        end = min(len(blob), off + 200)
        i = off
        best = []
        while i < end - 3:
            if blob[i] == 0x27:
                try:
                    n = blob[i + 2]
                    if 1 <= n <= 32:
                        j = i + 3
                        items = []
                        for _ in range(n):
                            v, j = uleb(blob, j)
                            items.append(v)
                        if j <= end:
                            chips = [x for x in items if 329000 <= x <= 333000]
                            if len(chips) >= 4 and len(chips) > len(best):
                                best = chips
                            i = j
                            continue
                except Exception:
                    pass
            i += 1
        out[k] = best
    return out


def main() -> int:
    cache = json.loads((WEB / "_cache_official_icons.json").read_text(encoding="utf-8"))
    names, icons = cache["names"], cache["icons"]

    p = CD / "oversea/huodong_conf_data_auto_oversea_data_kj1.py"
    c = CD / "oversea/huodong_conf_data_auto_oversea_data_kj1_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    runs = []
    for r in rows:
        if str(g(r, "hd_class")) != CLS:
            continue
        runs.append({"activity_id": r["key"], "name": str(g(r, "name") or "").strip(),
                     "start": day(g(r, "start_ts")), "end": day(g(r, "end_ts")),
                     "conf": str(g(r, "extra_param") or "")})
    runs.sort(key=lambda x: (x["start"], x["activity_id"]))
    chips_by_conf = decode_conf_chips()
    print("芯片活动", len(runs), "｜解出 conf", sum(1 for v in chips_by_conf.values() if v))

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    keep = [x for x in d["items"] if x.get("family_key") != "BeltChipSpecialLottery"]
    d["items"] = keep
    d["periods"] = [x for x in d["periods"] if x.get("family_key") != "BeltChipSpecialLottery"]

    lot_meta = (d["meta"].get("provenance") or {}).get("source_locks", [{}])[0]
    LOCK = {"source_id": lot_meta.get("source_id", "documents-py314-current"),
            "source_lock_source_id": lot_meta.get("source_id", "documents-py314-current"),
            "source_lock_sha256": lot_meta.get("sha256", "")}
    LOCK_STEP = {"source_id": LOCK["source_id"], "kind": "decoded-table-row",
                 "field_refs": ["panel_show_item_ids"]}
    import copy
    TEMPLATE = copy.deepcopy(d["items"][0]["provenance"]) if d["items"] and d["items"][0].get("provenance") else {}
    anchors = {"31": ("330112", "以攻为守"), "32": ("330132", "处变不惊")}
    np_ = ni = named = 0
    for n, r in enumerate(runs, 1):
        pid = "chip:%s" % r["activity_id"]
        per = {"period_id": pid, "label": "%s · 第%d期" % (r["name"] or "限定芯片自选", n),
               "activity_name": r["name"], "family": "限定芯片", "family_key": "BeltChipSpecialLottery",
               "server": "classic", "start": r["start"], "end": r["end"],
               "conf_key": r["conf"], "member_count": 0}
        d["periods"].append(per)
        np_ += 1
        chips = chips_by_conf.get(int(r["conf"])) if r["conf"].isdigit() else None
        for cid in (chips or []):
            sid = str(cid)
            nm = names.get(sid) or "芯片 %s" % sid
            if sid in names:
                named += 1
            it = {"id": "%s_%s" % (pid, sid), "period_id": pid, "period_label": per["label"],
                  "period_start": r["start"], "period_end": r["end"],
                  "family": "限定芯片", "family_key": "BeltChipSpecialLottery",
                  "name": nm, "item_id": sid, "kind": "芯片", "evidence": "structure",
                  "evidence_level": "structure-only",
                  "status_tags": ["verified", "static config"], "icon_state": "未下发",
                  "source": "special_chip_lottery_hd_conf_data(kj1) conf %s" % r["conf"],
                  "provenance": dict(copy.deepcopy(TEMPLATE),
                                     table="special_chip_lottery_hd_conf_data",
                                     row_key=int(r["conf"]),
                                     locator_chain=dict(copy.deepcopy((TEMPLATE or {}).get("locator_chain") or {}),
                                                        chain_status="replayed-structural",
                                                        scope="record",
                                                        no_cross_source_field_join=True,
                                                        steps=[dict((((TEMPLATE or {}).get("locator_chain") or {}).get("steps") or [{}])[0],
                                                                    kind="decoded-table-row",
                                                                    source_id=(TEMPLATE or {}).get("source_id", "documents-py314-current"),
                                                                    table="special_chip_lottery_hd_conf_data",
                                                                    row_key=int(r["conf"]),
                                                                    field_refs=["extra_param", "chip_ids"])])),
                  "source": "special_chip_lottery_hd_conf_data(kj1) conf %s" % r["conf"]}
            ic = icons.get(sid)
            if ic:
                base = ic[:-4] if ic.lower().endswith((".png", ".ktx", ".dds")) else ic
                f = WEB / "assets/lottery_icons" / (re.sub(r"[^0-9A-Za-z_.-]+", "_", sid) + ".png")
                it["_media"] = {"images": [{"png": "assets/lottery_icons/" + f.name, "label": "图标"}], "total": 1}
                it["icon_state"] = "有图"
            d["items"].append(it)
            per["member_count"] += 1
            ni += 1
        a = anchors.get(str(n))
        if a:
            per["note"] = "大奖芯片：%s（%s）" % (a[1], a[0])
    print("重建期次", np_, "｜成员", ni, "｜有名字", named)
    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    for per in d["periods"]:
        if per.get("family_key") == "BeltChipSpecialLottery" and per["member_count"]:
            print("  ", per["label"], per["start"], "成员", per["member_count"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
