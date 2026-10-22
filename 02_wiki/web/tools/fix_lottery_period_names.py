# -*- coding: utf-8 -*-
r"""把「典藏抽奖 配置N」这类占位期次换成真活动名 + 起止时间。

桥：huodong_conf.extra_param == super_fashion_lottery_conf_data 的 key。
同一 conf 被多次活动复用时取**最近一次**（start 最大），并记录复用次数。
"""
from __future__ import annotations

import datetime
import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

SF_CLASSES = ("SuperFashionLotteryHD", "DragonBlessingLotteryHD", "BlessingsAlwaysLotteryHD",
              "ScorpioSuperLotteryHD", "ChituSuperLotteryHD")


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
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=True)

    def g(f, k):
        v = f.get(k)
        return (v[1] if isinstance(v, tuple) and len(v) == 2 else v)

    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    o2 = raw.find(b"x{")  # 占位，保持变量名一致
    _at2 = raw.find(b"x{")
    _L2 = struct.unpack_from("<I", raw, _at2 + 2)[0]
    _b2 = raw[_at2 + 6:_at2 + 6 + _L2]
    count2 = struct.unpack_from("<I", _b2, 0)[0]
    blob2 = _b2[8 + 4 * count2:]

    def resolve_jump(v):
        if isinstance(v, str) and v.startswith("jump:"):
            n = int(v.split(":")[1])
            for base in (blob, body):
                for d in range(0, 25):
                    grp = BT.resolve_jump_group(base, n + d)
                    if grp:
                        return grp
            return []
        return [v] if isinstance(v, int) else []

    # conf_key → 最近一次活动
    best = {}
    for r in rows:
        f = {k: g({k: v}, k) for k, v in r["values"].items()}
        if str(f.get("hd_class")) not in SF_CLASSES:
            continue
        keys = resolve_jump(f.get("extra_param"))
        if not keys:
            continue
        start = f.get("start_ts") or 0
        for ck in keys:
            cur = best.get(str(ck))
            if cur is None or start > cur["start_ts"]:
                best[str(ck)] = {
                    "name": str(f.get("name") or ""),
                    "start_ts": start,
                    "start": day(start),
                    "end": day(f.get("end_ts")),
                    "activity_id": r["key"],
                    "sub": str(f.get("sub_title") or ""),
                }
    print("conf_key 命中活动", len(best))

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    n = 0
    for per in d["periods"]:
        pid = per.get("period_id", "")
        if not pid.startswith("SuperFashion:sf:"):
            continue
        ck = pid.split(":")[-1]
        hit = best.get(ck)
        if not hit or not hit["name"]:
            continue
        # 只在当前是占位名或名字更短时替换
        cur = str(per.get("activity_name") or "")
        if "配置" in str(per.get("label")) or len(hit["name"]) >= len(cur):
            per["activity_name"] = hit["name"]
            per["label"] = "%s（配置%s）" % (hit["name"], ck)
            if hit["start"]:
                per["start"] = hit["start"]
            if hit["end"]:
                per["end"] = hit["end"]
            per["activity_id"] = hit["activity_id"]
            if hit["sub"]:
                per["sub_title"] = hit["sub"]
            n += 1

    # 兜底：conf 行的 left_item_desc（如「典藏_幻夜神谕」）
    cp = CD / "super_fashion_lottery_conf_data.py"
    cc = CD / "super_fashion_lottery_conf_data_chs.py"
    craw = cp.read_bytes()
    cat = craw.find(b"x{")
    cL = struct.unpack_from("<I", craw, cat + 2)[0]
    cbody = craw[cat + 6: cat + 6 + cL]
    crows, _ = BT.decode_table_rows(cbody, BT.parse_legacy_chs_pool(cc.read_bytes()), resolve_jumps=False)
    desc = {}
    for r in crows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        if f.get("left_item_desc"):
            desc[str(r["key"])] = str(f["left_item_desc"]).strip()
    n2 = 0
    for per in d["periods"]:
        pid = per.get("period_id", "")
        if not pid.startswith("SuperFashion:sf:") or "配置" not in str(per.get("label")):
            continue
        ck = pid.split(":")[-1]
        nm = desc.get(ck)
        if not nm:
            continue
        nm = nm.replace("典藏_", "").replace("典藏", "").strip()
        if not nm:
            continue
        per["activity_name"] = nm
        per["label"] = "%s（配置%s）" % (nm, ck)
        n2 += 1
    print("left_item_desc 兜底命名", n2)
    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("替换占位期次", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
