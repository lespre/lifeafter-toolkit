# -*- coding: utf-8 -*-
r"""重建「自选保底奖池」期次：同一个活动可能返场多次，一次活动 = 一个期次。

来源 huodong_conf(kj1)：hd_class=MultiOptionalLotteryHD，extra_param = conf key。
命名：同名的第 1 次保留原名，第 2 次起标「（第N次 / 返场）」。
现成员按 conf key 迁移过来。
"""
from __future__ import annotations

import datetime
import json
import pathlib
import struct
import sys
from collections import defaultdict

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CLS = "MultiOptionalLotteryHD"


def day(ts):
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
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    runs = []
    for r in rows:
        if str(g(r, "hd_class")) != CLS:
            continue
        runs.append({
            "activity_id": r["key"],
            "name": str(g(r, "name") or "").strip(),
            "start": day(g(r, "start_ts")),
            "end": day(g(r, "end_ts")),
            "conf": str(g(r, "extra_param") or ""),
        })
    runs.sort(key=lambda x: (x["name"], x["start"] or "9999"))
    print("活动次数", len(runs))

    seen = defaultdict(int)
    for r in runs:
        seen[r["name"]] += 1
        r["ordinal"] = seen[r["name"]]

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    # 现有成员按 conf 分组
    items_by_conf = defaultdict(list)
    for it in d["items"]:
        if it.get("family_key") != "MultiOptional":
            continue
        ck = it["period_id"].split(":")[-1]
        items_by_conf[ck].append(it)
    d["items"] = [i for i in d["items"] if i.get("family_key") != "MultiOptional"]
    d["periods"] = [x for x in d["periods"] if x.get("family_key") != "MultiOptional"]

    added_p = added_i = 0
    for r in runs:
        pid = "MultiOptional:mo:%s" % r["activity_id"]
        label = r["name"] + ("（第%d次·返场）" % r["ordinal"] if r["ordinal"] > 1 else "")
        per = {
            "period_id": pid, "label": label, "activity_name": r["name"],
            "activity_id": r["activity_id"], "family": "自选保底奖池",
            "family_key": "MultiOptional", "server": "classic",
            "start": r["start"], "end": r["end"], "pool_count": 1, "member_count": 0,
            "conf_key": r["conf"],
            "note": "同活动多次返场，按活动号分期",
        }
        d["periods"].append(per)
        added_p += 1
        for it in items_by_conf.get(r["conf"], []):
            it["period_id"] = pid
            it["period_label"] = label
            it["period_start"] = r["start"]
            it["period_end"] = r["end"]
            d["items"].append(it)
            per["member_count"] += 1
            added_i += 1

    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("重建期次", added_p, "｜迁移成员", added_i)
    for per in d["periods"]:
        if per.get("family_key") == "MultiOptional":
            print("  ", per["period_id"], per["label"], per["start"], "→", per["end"], per["member_count"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
