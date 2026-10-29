# -*- coding: utf-8 -*-
"""时装部位重定：以 desc 里的「 - 衣服（ / - 头饰（ / - 光源（」为准，不信 new_fashion_id_str。

背景：`扬帆远航` 有一条 light_3084_1_7，但 desc 明写「扬帆远航 - 衣服（7天）」——
说明 new_fashion_id_str 前缀在这种情况下是脏的，desc 才是真口径。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

T = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata/fashion_data.py"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
BAK = WEB / "data/boards/fashion_wardrobe.json.bak_merge"

CN = {"衣服": "衣服", "头饰": "头饰", "背包": "背包", "光源": "光源",
      "整套": "整套", "挂饰": "挂饰", "面饰": "面饰", "投影": "投影", "发饰": "发饰",
      "cloth": "衣服", "hat": "头饰", "bag": "背包", "light": "光源",
      "suit": "整套", "face": "面饰", "pendant": "挂饰", "proj": "投影"}
PAT = re.compile(r"-\s*(衣服|头饰|背包|光源|整套|挂饰|面饰|投影|发饰)\s*[（(]")
v = lambda x: x[1] if isinstance(x, tuple) else x


def desc_part() -> dict[str, str]:
    raw = T.read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = T.with_name("fashion_data_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes())
    rows = BT.decode_table_rows(raw[at + 6:at + 6 + L], pool,
                               resolve_jumps=False, lenient=True)[0]
    out = {}
    for r in rows:
        d = v(r["values"].get("desc"))
        if not isinstance(d, str):
            continue
        m = PAT.search(d)
        if m:
            out[str(r["key"])] = CN.get(m.group(1), m.group(1))
    return out


def main() -> int:
    src = BAK if BAK.exists() else BOARD
    d = json.loads(src.read_text(encoding="utf-8"))
    dp = desc_part()
    print("desc 可定部位的行", len(dp))

    fixed = 0
    for it in d["items"]:
        keys = [str(k) for k in (it.get("row_keys") or [])]
        if not keys:
            continue
        p = dp.get(keys[0])
        if p and p != it.get("part"):
            it["part_desc"] = p
            if p != it.get("part"):
                fixed += 1
    print("按 desc 修正的部位", fixed)

    # 合并同 name+model：部位取并集
    groups: dict[tuple, dict] = {}
    for it in d["items"]:
        mids = it.get("model_ids") or []
        key = (str(it.get("name") or ""), str(mids[0]) if mids else str(it.get("id")))
        part = it.get("part_desc") or it.get("part")
        g = groups.get(key)
        if g is None:
            it["parts_raw"] = [str(part)]
            it["part"] = str(part)
            it["part_bucket"] = [CN.get(str(part), str(part))]
            groups[key] = it
            continue
        if str(part) not in g["parts_raw"]:
            g["parts_raw"].append(str(part))
            cn = CN.get(str(part), str(part))
            if cn not in g["part_bucket"]:
                g["part_bucket"].append(cn)
        g["row_keys"] = sorted(set((g.get("row_keys") or []) + (it.get("row_keys") or [])))
        gimgs = (g.setdefault("_media", {}) or {}).get("images") or []
        for im in (it.get("_media") or {}).get("images") or []:
            if im not in gimgs:
                gimgs.append(im)
        g["_media"] = {"images": gimgs, "total": len(gimgs)}
        for f in ("charm_value", "level"):
            if g.get(f) in (None, 0) and it.get(f) not in (None, 0):
                g[f] = it[f]

    merged = list(groups.values())
    for it in merged:
        it["part"] = "/".join(it["parts_raw"])
        it["part_label"] = "+".join(it["part_bucket"])
    d["items"] = merged
    d["meta"]["notes"] = ((d["meta"].get("notes") or "")
                          + " ｜ 部位口径：desc 内「- 衣服（」等优先，new_fashion_id_str 仅兜底")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    from collections import Counter
    print("合并后", len(merged), "卡")
    print("部位分布", Counter(tuple(i["part_bucket"]) for i in merged).most_common(8))
    for i in merged:
        if i["name"] == "扬帆远航":
            print("扬帆远航 →", i["part_bucket"], i["parts_raw"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
