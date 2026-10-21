# -*- coding: utf-8 -*-
"""在 PE 树里找带 scene id 的表，并尝试取名字。"""
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/01_工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

CD = pathlib.Path(r"E:/la拆包项目/03_执行/41_还原树/pe_20261020/com/cdata")
WANT = {580, 750, 799, 754, 724}


def main() -> int:
    cands = [p for p in CD.glob("*scene*.py") if "_chs" not in p.name]
    cands += [p for p in CD.glob("*map*.py") if "_chs" not in p.name]
    print("候选", len(cands))
    for p in cands:
        b = p.read_bytes()
        at = b.find(b"x{")
        if at < 0:
            continue
        L = struct.unpack_from("<I", b, at + 2)[0]
        chs = CD / (p.stem + "_chs.py")
        pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else {}
        try:
            rows, _ = BT.decode_table_rows(b[at + 6:at + 6 + L], pool, resolve_jumps=False)
        except Exception:
            continue
        keys = set()
        for r in rows:
            try:
                keys.add(int(r["key"]))
            except Exception:
                pass
        hit = sorted(WANT.intersection(keys))
        if hit:
            print("%-46s 行%-5d 命中%s" % (p.name, len(rows), hit))

            def g(r, k):
                v = r["values"].get(k)
                return (v[1] if isinstance(v, tuple) else v) if v else None

            for r in rows:
                try:
                    k = int(r["key"])
                except Exception:
                    continue
                if k in hit:
                    vals = {kk: str(g(r, kk))[:26] for kk in list(r["values"])[:6]}
                    print("    ", k, vals)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
