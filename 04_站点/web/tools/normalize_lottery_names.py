# -*- coding: utf-8 -*-
r"""把广播表的内部简称换成正式名，并按 item_id 去重。

优先级：时装/道具/载具/投影/配方表 > 板上非广播来源的名字 > 广播 note。
被替换掉的广播简称写进 `alias`，不丢信息。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "04_站点/web"
CD = PROJ / "03_执行/41_还原树/pe_test_script/com/cdata"
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

TABLES = ["fashion_data", "oversea/common_item_data_auto_oversea_data_kj1",
          "vehicle_ui_data", "body_sfx_data", "recipe", "gift_data",
          "oversea/all_equips_data_auto_oversea_data_kj1"]


def load_names(nm: str):
    p = CD / (nm + ".py")
    c = CD / (nm + "_chs.py")
    if not p.is_file() or not c.is_file():
        return {}
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return {}
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    try:
        rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)
    except Exception:
        return {}
    out = {}
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        for nk in ("name", "item_name", "buff_item_name", "chip_name"):
            if f.get(nk):
                out[str(r["key"])] = str(f[nk]).strip()
                break
    return out


def main() -> int:
    nm = {}
    for t in TABLES:
        got = load_names(t)
        if got:
            print("  %-48s 名字 %d" % (t, len(got)))
        for k, v in got.items():
            nm.setdefault(k, v)

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    # 板上非广播来源的名字优先
    for it in d["items"]:
        if it.get("via_broadcast") or it.get("via_show_reward"):
            continue
        iid = it.get("item_id")
        if iid and it.get("name"):
            nm.setdefault(str(iid), it["name"])

    replaced = 0
    for it in d["items"]:
        if not it.get("via_broadcast"):
            continue
        iid = str(it.get("item_id"))
        good = nm.get(iid)
        if good and good != it.get("name"):
            it.setdefault("alias", it.get("name"))
            it["name"] = good
            it["name_source"] = "正式表名字优先（广播简称存 alias）"
            replaced += 1

    # 同期同 id 去重，保留有图/非广播的那条
    seen = {}
    out = []
    dropped = 0
    for it in d["items"]:
        key = (it["period_id"], str(it.get("item_id")))
        if key in seen:
            a = seen[key]
            better = it if ((((it.get("_media") or {}).get("images") or [{}])[0] or {}).get("png")
                            and not (((a.get("_media") or {}).get("images") or [{}])[0] or {}).get("png")) else a
            if better is it:
                if a.get("alias") and not it.get("alias"):
                    it["alias"] = a["alias"]
                out[out.index(a)] = it
                seen[key] = it
            elif a.get("alias") and not a.get("alias_merged"):
                a["alias_merged"] = True
            dropped += 1
            continue
        seen[key] = it
        out.append(it)
    d["items"] = out
    for per in d["periods"]:
        per["member_count"] = sum(1 for i in d["items"] if i["period_id"] == per["period_id"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("换正式名", replaced, "｜同期去重", dropped, "｜总成员", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
