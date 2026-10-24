# -*- coding: utf-8 -*-
"""用 appear_ids 定每套时装的性别（男/女/男/女/未知）。

口径：
  fashion_data.appear_ids（0x0b 跳转组）→ player_appear_data 的 key
  player_appear_data.model_name 含 _f_ / _m_ → 女 / 男
  一套里两种都有 → 男/女；只有一种 → 单性别；都没有 → 未知
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import Counter

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
v = lambda x: x[1] if isinstance(x, tuple) else x


def load(path):
    raw = path.read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = path.with_name(path.stem + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    return rows, pool, body[8 + 4 * cnt:]


def main() -> int:
    ap, _, _ = load(CD / "player_appear_data.py")
    gend = {}
    for r in ap:
        mn = v(r["values"].get("model_name"))
        if isinstance(mn, str):
            g = "女" if "_f_" in mn else ("男" if "_m_" in mn else None)
            if g:
                gend[str(r["key"])] = g

    fd, pool, blob = load(CD / "fashion_data.py")
    row_gender = {}
    icon_gender = {}
    for r in fd:
        a = r["values"].get("appear_ids")
        if not isinstance(a, tuple):
            continue
        try:
            off = int(str(a[1]).split(":")[1])
        except Exception:
            continue
        g = BT.read_27_group(blob, off)
        if not g:
            continue
        gs = {gend.get(str(i)) for i in g[1]}
        gs.discard(None)
        # 图标兜底：icon_light_f_xxx / icon_light_m_xxx 带性别标记
        ic = r["values"].get("icons")
        if not gs and isinstance(ic, tuple):
            try:
                ig = BT.read_27_group(blob, int(str(ic[1]).split(":")[1]))
                paths = " ".join(pool[i] for i in ig[1] if i < len(pool)) if ig else ""
                if "_f_" in paths:
                    gs.add("女")
                if "_m_" in paths:
                    gs.add("男")
            except Exception:
                pass
        if gs:
            row_gender[str(r["key"])] = "/".join(sorted(gs))

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    for it in d["items"]:
        gs = set()
        for k in (it.get("row_keys") or []):
            g = row_gender.get(str(k))
            if g:
                gs |= set(g.split("/"))
        it["gender"] = "/".join(x for x in ("女", "男") if x in gs) if gs else ""
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    c = Counter(i.get("gender") or "未知" for i in d["items"])
    print("行级性别映射", len(row_gender), "｜ 卡片分布", c.most_common())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
