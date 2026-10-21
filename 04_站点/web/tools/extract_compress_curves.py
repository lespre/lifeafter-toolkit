# -*- coding: utf-8 -*-
"""抽取 compressed_attr_data 的折线端点（base + kj1），输出 JSON。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/01_工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT  # noqa: E402

CD = pathlib.Path(r"E:/la拆包项目/03_执行/41_还原树/pe_20261020/com/cdata")
OUT = pathlib.Path(r"E:/la拆包项目/04_站点/web/analysis")
OUT.mkdir(parents=True, exist_ok=True)


def rows_of(path: pathlib.Path, chs: pathlib.Path | None = None):
    b = path.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs and chs.is_file() else {}
    rows, _ = BT.decode_table_rows(b[at + 6:at + 6 + L], pool, resolve_jumps=False)
    return b[at + 6:at + 6 + L], rows


def grp(blob, off):
    if off >= len(blob) or blob[off] != 0x27:
        return None
    t, n = blob[off + 1], blob[off + 2]
    pos = off + 3
    out = []
    for _ in range(n):
        if t == 0x12:
            out.append(round(struct.unpack_from("<f", blob, pos)[0], 4))
            pos += 4
        elif t == 0x22:
            out.append(round(struct.unpack_from("<d", blob, pos)[0], 4))
            pos += 8
        elif t in (0x01, 0x0B):
            v, pos = BT.uleb(blob, pos, len(blob))
            out.append(v)
        else:
            return None
    return t, out


def find(blob, off, span=12):
    for d in range(span):
        g = grp(blob, off + d)
        if g:
            return g
    return None


def arrays(blob, row):
    """按槽位顺序取出所有数组（float 数组保留，int 数组标记 skip）。"""
    out = []
    for k in sorted(row["values"], key=lambda x: int(x.strip("<>slot_"))):
        v = row["values"][k]
        val = v[1] if isinstance(v, tuple) else v
        if not (isinstance(val, str) and val.startswith("jump:")):
            continue
        g = find(blob, int(val.split(":")[1]))
        out.append(g)
    return out


def curves(path, chs=None):
    blob, rows = rows_of(path, chs)
    res = {}
    for r in rows:
        aid = int(r["key"])
        arrs = [a for a in arrays(blob, r) if a and a[0] in (0x12, 0x22)]
        floats = [a[1] for a in arrs if len(a[1]) >= 2]
        # 取前两组长���相同的浮点数组作为 (x, y)
        for i in range(0, len(floats) - 1):
            x, y = floats[i], floats[i + 1]
            if len(x) == len(y) and len(x) >= 2:
                if all(x[j] <= x[j + 1] for j in range(len(x) - 1)):
                    res.setdefault(aid, []).append({"x": x, "y": y})
                    break
    return res, len(rows)


def main() -> int:
    names_blob, name_rows = rows_of(CD / "attribute_data.py", CD / "attribute_data_chs.py")

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    name = {int(r["key"]): str(g(r, "name") or "") for r in name_rows}

    base, nb = curves(CD / "compressed_attr_data.py")
    kj1, nk = curves(CD / "oversea/compressed_attr_data_auto_oversea_data_kj1.py")

    out = {
        "base": {"rows": nb, "curves": [dict(id=k, name=name.get(k, ""), segs=v) for k, v in sorted(base.items())]},
        "kj1": {"rows": nk, "curves": [dict(id=k, name=name.get(k, ""), segs=v) for k, v in sorted(kj1.items())]},
    }
    (OUT / "attr_compress_curves.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("base %d 行 → %d 条曲线" % (nb, len(base)))
    print("kj1  %d 行 → %d 条曲线" % (nk, len(kj1)))
    for c in out["kj1"]["curves"][:5]:
        print("  kj1", c["id"], c["name"], c["segs"][0]["x"], "→", c["segs"][0]["y"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
