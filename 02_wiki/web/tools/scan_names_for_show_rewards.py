# -*- coding: utf-8 -*-
r"""全表扫：给定 id 列表，在所有 base+_chs 成对的 cdata 表里找同名行，回填名字。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
CDATA = PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

WANT = {"489800", "489200", "492200", "154464", "1221067", "1221068", "1221069",
        "1221070", "1221071", "241894", "1221243", "1221241", "1221242", "1221244",
        "741480120", "741470120"}
NAME_KEYS = ("name", "item_name", "buff_item_name", "chip_name", "furniture_name",
             "show_name", "title", "desc_name")


def main() -> int:
    t0 = time.time()
    found = {}
    files = sorted(CDATA.rglob("*.py"))
    pairs = []
    for p in files:
        if p.stem.endswith("_chs"):
            continue
        c = p.with_name(p.stem + "_chs.py")
        if c.is_file() and p.stat().st_size < 3_000_000:
            pairs.append((p, c))
    print("成对表", len(pairs))
    for p, c in pairs:
        if len(found) >= len(WANT):
            break
        try:
            raw = p.read_bytes()
            at = raw.find(b"x{")
            if at < 0:
                continue
            L = struct.unpack_from("<I", raw, at + 2)[0]
            body = raw[at + 6: at + 6 + L]
            rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)
        except Exception:
            continue
        for r in rows:
            k = str(r["key"])
            if k not in WANT or k in found:
                continue
            f = {kk: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for kk, v in r["values"].items()}
            for nk in NAME_KEYS:
                if f.get(nk):
                    found[k] = (str(f[nk]).strip(), p.name)
                    break
        if time.time() - t0 > 480:
            print("超时，已扫到", len(found))
            break
    print("命中", len(found))
    for k, (n, src) in found.items():
        print("  ", k, "→", n, "|", src)

    if found:
        board_p = WEB / "data/boards/lottery_periods.json"
        d = json.loads(board_p.read_text(encoding="utf-8"))
        n = 0
        for it in d["items"]:
            if not str(it.get("name", "")).startswith("展示奖励"):
                continue
            hit = found.get(str(it.get("item_id")))
            if hit:
                it["name"] = hit[0]
                it["name_source"] = hit[1]
                n += 1
        board_p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        (WEB / "data/boards/lottery_periods.js").write_text(
            "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
            encoding="utf-8")
        print("回填", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
