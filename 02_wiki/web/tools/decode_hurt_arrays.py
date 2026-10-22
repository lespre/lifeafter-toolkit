# -*- coding: utf-8 -*-
"""正确解析 special_hurt_params 的数组描述符：值起点 = 0x27 组头 +1。

实测：描述符 [689,4,704] 对应 blob[688] = 27 12 05 → 5 个 float32 从 689 开始。
之前只向后扫 0x27，漏掉了「组头在描述符前 1 字节」这种排列。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

OV = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe_20261020/com/cdata/oversea")
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/伤害系统逆向")
FIELDS = ["source_hurt_interval", "source_hurt_factor", "source_hurt_offset",
          "p2p_a_class_hurt_additional_rate_interval", "p2p_a_class_hurt_additional_rate_factor",
          "p2p_a_class_hurt_additional_rate_offset"]


def group(blob, off):
    if off < 0 or off >= len(blob) or blob[off] != 0x27:
        return None
    t, n = blob[off + 1], blob[off + 2]
    pos, out = off + 3, []
    for _ in range(n):
        if t == 0x12:
            out.append(round(struct.unpack_from("<f", blob, pos)[0], 4)); pos += 4
        elif t == 0x22:
            out.append(round(struct.unpack_from("<d", blob, pos)[0], 4)); pos += 8
        elif t in (0x01, 0x0B):
            v, pos = BT.uleb(blob, pos, len(blob)); out.append(v)
        else:
            return None
    return t, out


def resolve(blob, off):
    """描述符指向某个 0x27 组头之前若干字节，组头位置不固定 → 向后扫 14 字节取第一个组。"""
    for d in range(0, 15):
        g = group(blob, off + d)
        if g:
            return g[1], d
    return None, None


def main() -> int:
    p = OV / "special_hurt_params_data_auto_oversea_data_kj1.py"
    c = OV / "special_hurt_params_data_auto_oversea_data_kj1_chs.py"
    b = p.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    blob = b[at + 6: at + 6 + L]
    rows, _ = BT.decode_table_rows(blob, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    out = []
    for r in rows:
        rec = {"id": r["key"], "scene_id": g(r, "scene_id"), "K": g(r, "K"), "M": g(r, "M"),
               "min_attack": g(r, "min_attack"), "max_rate": g(r, "max_hurt_additional_rate")}
        for f in FIELDS:
            v = g(r, f)
            if isinstance(v, str) and v.startswith("jump:"):
                arr, shift = resolve(blob, int(v.split(":")[1]))
                rec[f] = arr
                rec[f + "__shift"] = shift
            else:
                rec[f] = v
        out.append(rec)

    (OUT / "hurt_params_arrays_kj1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for r in out if r["source_hurt_interval"] and r["source_hurt_offset"])
    print("行", len(out), "区间+偏移都解出", ok)
    for r in out[:4]:
        print(" id", r["id"], "scene", r["scene_id"], "M", r["M"], "min_atk", r["min_attack"])
        print("   interval", r["source_hurt_interval"], "shift", r["source_hurt_interval__shift"])
        print("   factor  ", r["source_hurt_factor"])
        print("   offset  ", r["source_hurt_offset"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
