# -*- coding: utf-8 -*-
"""标定参数数组描述符的偏移基准：file / blob / 组头偏移三种假设逐个打分。"""
from __future__ import annotations

import pathlib
import struct
import sys
from collections import Counter

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

P = pathlib.Path(r"E:/la拆包项目/01_索引与产物/41_还原树/pe_20261020/com/cdata/oversea/special_hurt_params_data_auto_oversea_data_kj1.py")
C = P.with_name(P.stem + "_chs.py")


def scan_groups(buf):
    g = {}
    for i in range(len(buf) - 3):
        if buf[i] != 0x27:
            continue
        t, n = buf[i + 1], buf[i + 2]
        if t not in (0x12, 0x22, 0x01, 0x0B) or not (1 <= n <= 64):
            continue
        pos, vals, ok = i + 3, [], True
        for _ in range(n):
            if t == 0x12:
                pos += 4
            elif t == 0x22:
                pos += 8
            else:
                try:
                    _, pos = BT.uleb(buf, pos, len(buf))
                except Exception:
                    ok = False
                    break
        if ok and pos <= len(buf):
            g[i] = (t, n)
    return g


def main() -> int:
    b = P.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    blob = b[at + 6: at + 6 + L]
    base_file = scan_groups(b)
    base_blob = scan_groups(blob)
    rows, _ = BT.decode_table_rows(blob, BT.parse_legacy_chs_pool(C.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    stats = Counter()
    samples = []
    for r in rows:
        for f in ("source_hurt_interval", "source_hurt_factor", "source_hurt_offset"):
            v = g(r, f)
            if not isinstance(v, str) or not v.startswith("jump:"):
                continue
            off = int(v.split(":")[1])
            # 描述符自身的整数（如 [689, 4, 704]）
            best = None
            for base_name, idx in (("file", base_file), ("blob", base_blob)):
                for d in range(0, 18):
                    o = off + d
                    if o in idx:
                        t, n = idx[o]
                        best = (base_name, d, t, n)
                        break
                if best:
                    break
            if best:
                stats[(best[0], best[1])] += 1
                if len(samples) < 8:
                    samples.append((r["key"], f, off, best))
            else:
                stats[("none", -1)] += 1

    print("命中分布（基准, 偏移差）→ 次数：")
    for k, v in stats.most_common(12):
        print("  %-6s +%-3d %d" % (k[0], k[1], v))
    print("\n样例：")
    for s in samples:
        print("  id %s %s off=%d → %s +%d type=%s n=%d" % s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
