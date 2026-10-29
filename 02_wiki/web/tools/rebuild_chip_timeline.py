# -*- coding: utf-8 -*-
r"""重建限定芯片的 37 期时间线（来自 huodong_conf），保留已确认的芯片锚点。"""
from __future__ import annotations

import datetime
import json
import pathlib
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

FAM = "BeltChipSpecialLottery"


def day(ts) -> str:
    if not isinstance(ts, (int, float)) or ts < 1e9:
        return ""
    return datetime.datetime.fromtimestamp(ts + 8 * 3600, datetime.UTC).strftime("%Y-%m-%d")


def main() -> int:
    p = CD / "oversea/huodong_conf_data_auto_oversea_data_kj1.py"
    c = CD / "oversea/huodong_conf_data_auto_oversea_data_kj1_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    pool = BT.parse_legacy_chs_pool(c.read_bytes())
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=True)

    acts = []
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        if str(f.get("hd_class")) != "BeltChipSpecialLotteryHD":
            continue
        acts.append({
            "activity_id": r["key"],
            "name": f.get("name") or "限定芯片自选",
            "start": day(f.get("start_ts")),
            "end": day(f.get("end_ts")),
            "extra": f.get("extra_param"),
        })
    acts.sort(key=lambda x: (x["start"] or "9999", x["activity_id"]))
    print("芯片活动", len(acts))

    bp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(bp.read_text(encoding="utf-8"))
    anchors = {}
    for it in d["items"]:
        if it.get("family_key") == FAM:
            anchors.setdefault(it["period_id"], []).append(it)
    print("保留锚点", {k: len(v) for k, v in anchors.items()})

    d["items"] = [i for i in d["items"] if i.get("family_key") != FAM]
    d["periods"] = [x for x in d["periods"] if x.get("family_key") != FAM]

    for idx, a in enumerate(acts, 1):
        pid = "chip:%s" % a["extra"]
        per = {
            "period_id": pid,
            "label": "%s · 第%s期" % (a["name"], a["extra"]),
            "activity_name": a["name"],
            "activity_id": a["activity_id"],
            "family": "限定芯片",
            "family_key": FAM,
            "server": "classic",
            "start": a["start"],
            "end": a["end"],
            "pool_count": 1,
            "member_count": 0,
            "note": "期次时间来自活动表；芯片内容客户端无映射，仅已确认期展示",
        }
        d["periods"].append(per)
        for it in anchors.get(pid, []):
            it["period_label"] = per["label"]
            it["period_start"] = per["start"]
            it["period_end"] = per["end"]
            d["items"].append(it)
            per["member_count"] += 1

    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("重建期次", len(acts), "｜成员", len(d["items"]))
    for x in d["periods"]:
        if x.get("family_key") == FAM:
            print("   ", x["period_id"], x["label"], x["start"], "→", x["end"], "| 成员", x["member_count"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
