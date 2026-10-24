# -*- coding: utf-8 -*-
"""全面拆 factor：把参数表里所有 0x27 组建索引，再核对每个描述符指向什么。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import Counter

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

OV = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata/oversea")
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/伤害系统逆向")
P = OV / "special_hurt_params_data_auto_oversea_data_kj1.py"
C = OV / "special_hurt_params_data_auto_oversea_data_kj1_chs.py"


def groups(blob):
    out = {}
    for i in range(len(blob) - 3):
        if blob[i] != 0x27:
            continue
        t, n = blob[i + 1], blob[i + 2]
        if t not in (0x12, 0x22, 0x01, 0x0B) or n == 0 or n > 64:
            continue
        pos, vals, ok = i + 3, [], True
        for _ in range(n):
            if t == 0x12:
                if pos + 4 > len(blob):
                    ok = False
                    break
                vals.append(round(struct.unpack_from("<f", blob, pos)[0], 4)); pos += 4
            elif t == 0x22:
                if pos + 8 > len(blob):
                    ok = False
                    break
                vals.append(round(struct.unpack_from("<d", blob, pos)[0], 4)); pos += 8
            else:
                try:
                    v, pos = BT.uleb(blob, pos, len(blob))
                except Exception:
                    ok = False
                    break
                vals.append(v)
        if ok:
            out[i] = (t, vals, pos - i)
    return out


def main() -> int:
    b = P.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    blob = b[at + 6: at + 6 + L]
    gs = groups(blob)
    print("blob", len(blob), "组", len(gs),
          "类型分布", Counter(t for t, _, _ in gs.values()).most_common())

    rows, _ = BT.decode_table_rows(blob, BT.parse_legacy_chs_pool(C.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    FIELDS = ["source_hurt_interval", "source_hurt_factor", "source_hurt_offset"]
    stat = Counter()
    samples = []
    for r in rows:
        rec = {"id": r["key"]}
        for f in FIELDS:
            v = g(r, f)
            if not (isinstance(v, str) and v.startswith("jump:")):
                rec[f] = None
                continue
            off = int(v.split(":")[1])
            # 找该偏移之后最近的组
            cand = [(o, gs[o]) for o in sorted(gs) if off <= o <= off + 24]
            if cand:
                o, (t, vals, size) = cand[0]
                rec[f] = {"off": off, "group_at": o, "delta": o - off, "type": t, "vals": vals}
                stat[(f, t)] += 1
            else:
                rec[f] = {"off": off, "group_at": None}
                stat[(f, "none")] += 1
        samples.append(rec)

    (OUT / "hurt_params_factor_probe.json").write_text(
        json.dumps({"stat": {str(k): v for k, v in stat.items()}, "rows": samples},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n字段×组类型命中统计：")
    for k, v in stat.most_common():
        print("  %-34s %-6s %d" % (k[0], k[1], v))

    print("\n样例（前 3 行）：")
    for rec in samples[:3]:
        print(" id", rec["id"])
        for f in FIELDS:
            print("   %-22s %s" % (f, rec[f]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
