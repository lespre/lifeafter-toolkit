# -*- coding: utf-8 -*-
"""解 special_hurt_params_data（伤害加成真正的分段参数表）。"""
import json
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

OV = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置/com/cdata/oversea")
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/伤害系统逆向")
KEYS = [
    "scene_id", "min_attack", "min_building_attack", "reduce_hurt_value",
    "min_hurt_additional_rate", "max_hurt_additional_rate", "p2d_min_hurt_additional_rate",
    "source_hurt_interval", "source_hurt_factor", "source_hurt_offset",
    "p2p_a_class_hurt_additional_rate_interval", "p2p_a_class_hurt_additional_rate_factor",
    "p2p_a_class_hurt_additional_rate_offset",
    "d2p_a_class_hurt_additional_rate_interval", "d2p_a_class_hurt_additional_rate_factor",
    "d2p_a_class_hurt_additional_rate_offset",
    "m2p_a_class_hurt_additional_rate_interval", "m2p_a_class_hurt_additional_rate_factor",
    "m2p_a_class_hurt_additional_rate_offset",
]


def grp(blob, off):
    if off >= len(blob) or blob[off] != 0x27:
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
    return out


def find(blob, off, span=12):
    """优先返回浮点数组（0x12/0x22），没有再退回整数数组。"""
    best = None
    for d in range(span):
        if off + d >= len(blob) or blob[off + d] != 0x27:
            continue
        g = grp(blob, off + d)
        if not g:
            continue
        if blob[off + d + 1] in (0x12, 0x22):
            return g
        if best is None:
            best = g
    return best


def main() -> int:
    p = OV / "special_hurt_params_data_auto_oversea_data_kj1.py"
    c = OV / "special_hurt_params_data_auto_oversea_data_kj1_chs.py"
    b = p.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    blob = b[at + 6: at + 6 + L]
    pool = BT.parse_legacy_chs_pool(c.read_bytes())
    rows, _ = BT.decode_table_rows(blob, pool, resolve_jumps=False)

    def val(r, k):
        v = r["values"].get(k)
        if not v:
            return None
        x = v[1] if isinstance(v, tuple) else v
        if isinstance(x, str) and x.startswith("jump:"):
            return find(blob, int(x.split(":")[1]))
        return x

    out = []
    for r in rows:
        rec = {"id": r["key"]}
        for k in KEYS:
            rec[k] = val(r, k)
        out.append(rec)
    (OUT / "hurt_additional_rate_params_kj1.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("行", len(out), "→", OUT / "hurt_additional_rate_params_kj1.json")
    witharr = [r for r in out if r.get("p2p_a_class_hurt_additional_rate_interval") or r.get("p2p_a_class_hurt_additional_rate_factor")]
    print("带 a_class 分段参数的行", len(witharr))
    for rec in witharr[:5]:
        print(" id", rec["id"])
        for k in KEYS:
            if rec[k] is not None:
                print("   %-42s %s" % (k, rec[k]))
    for rec in out[:3]:
        print(" id", rec["id"])
        for k in KEYS:
            if rec[k] is not None:
                print("   %-42s %s" % (k, rec[k]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
