# -*- coding: utf-8 -*-
"""解析 special_attr_params_data 的加成压缩曲线（0x27 帧 + 0x12/0x22/0x01 元素）。

帧格式（实测）：
  [0x27][elem_type][uleb count][count × 元素]
  元素类型 0x12=f32, 0x22=f64, 0x01=u32
jump:N 的 N 是相对 blob 起点的字节偏移，blob = base_body[8 + 4*count:]。

输出：01_索引与产物/30_分析/伤害加成曲线.json
"""
from __future__ import annotations

import json
import struct
import sys
import pathlib


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import ANALYSIS_ROOT, TOOLKIT_CORE, WEB  # noqa: E402
sys.path.insert(0, str(TOOLKIT_CORE))
sys.path.insert(0, str(WEB / "tools"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

OUT = pathlib.Path(ANALYSIS_ROOT / "伤害加成曲线.json")
TABLE = "special_attr_params_data"


def uleb(b: bytes, p: int) -> tuple[int, int]:
    v = 0
    s = 0
    while True:
        c = b[p]
        v |= (c & 0x7F) << s
        p += 1
        if not c & 0x80:
            return v, p
        s += 7


def read_frame(blob: bytes, off: int):
    if blob[off] != 0x27:
        return None
    et = blob[off + 1]
    cnt, p = uleb(blob, off + 2)
    out = []
    for _ in range(cnt):
        if et == 0x12:
            out.append(struct.unpack_from("<f", blob, p)[0]); p += 4
        elif et == 0x22:
            out.append(struct.unpack_from("<d", blob, p)[0]); p += 8
        elif et == 0x01:
            out.append(struct.unpack_from("<I", blob, p)[0]); p += 4
        else:
            return None
    return {"elem_type": hex(et), "values": [round(v, 6) for v in out]}


def main() -> int:
    CD = cdata_dir()
    raw = (CD / (TABLE + ".py")).read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    base = raw[at + 6: at + 6 + n]
    count, _res = struct.unpack_from("<II", base, 0)
    blob = base[8 + 4 * count:]

    chs = CD / (TABLE + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
    rows, _ = decode_table_rows(base, pool, resolve_jumps=False, lenient=True)

    out = {}
    for r in rows:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
        rec = {}
        for k, val in v.items():
            if isinstance(val, str) and val.startswith("jump:"):
                f = read_frame(blob, int(val[5:]))
                if f:
                    rec[k] = f["values"]
        if rec:
            out[str(r["key"])] = rec

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("行 %d ｜ 解出曲线的行 %d ｜ 写出 %s" % (len(rows), len(out), OUT))
    k0 = next(iter(out))
    for name in ("hc_body_part_addition_interval", "hc_body_part_addition_factor",
                 "hc_body_part_addition_offset", "hc_head_part_addition_interval",
                 "hc_critical_hurt_addition_interval", "hc_critical_rate_interval"):
        if name in out[k0]:
            print("  ", name, out[k0][name])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
