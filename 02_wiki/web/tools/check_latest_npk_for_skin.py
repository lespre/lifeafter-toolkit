# -*- coding: utf-8 -*-
"""从最新 PE 测试服 script npk 直接取表，检查目标 id 是否已进最新数据。"""
from __future__ import annotations

import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
NPK = ROOT / "01_索引与产物/源包/pe_20261020/script.py314.lc.npk"
sys.path.insert(0, str(ROOT / "02_wiki/web/tools"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
import live_npk_reader as L  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402

TABLES = [
    "com/cdata/weapon_skin_data.py",
    "com/cdata/weapon_skin_behavior_res_data.py",
    "com/cdata/oversea/all_equips_data_auto_oversea_data_yk.py",
    "com/cdata/oversea/all_equips_data_auto_oversea_data_kj1.py",
    "com/cdata/common_item_data_base.py",
]
WANT = sys.argv[1:] or ["1110189"]


def body(raw: bytes):
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n] if 0 < n and at + 6 + n <= len(raw) else None


def get(reader, by_fid, path: str):
    try:
        fid = fid_of(path) & 0xFFFFFFFFFFFFFFFF
    except Exception:  # noqa: BLE001
        return None
    e = by_fid.get(fid)
    if not e:
        return None
    return L._unpack_entry(e.packed, e.declared_size, e.flag)


def main() -> int:
    r = L.LiveNpkReader(NPK, "playertest")
    by_fid = {e.file_id: e for e in r._entries}
    print("npk 条目", len(by_fid))
    for t in TABLES:
        raw = get(r, by_fid, t)
        if raw is None:
            print("  缺表", t)
            continue
        chs_raw = get(r, by_fid, t.replace(".py", "_chs.py"))
        pool = []
        if chs_raw:
            try:
                pool = parse_legacy_chs_pool(chs_raw)
            except Exception:  # noqa: BLE001
                pool = []
        b = body(raw)
        if not b:
            print("  %-52s 无 x{ 容器（%d B）" % (t.split("/")[-1], len(raw)))
            continue
        try:
            rows, _ = decode_table_rows(b, pool, resolve_jumps=False, lenient=True)
        except Exception as exc:  # noqa: BLE001
            print("  %-52s 解码失败 %s" % (t.split("/")[-1], str(exc)[:40]))
            continue
        keys = {str(x.get("key")) for x in rows}
        hit = [w for w in WANT if w in keys]
        print("  %-52s rows %5d | 命中 %s" % (t.split("/")[-1], len(rows), hit or "无"))
        if hit:
            for x in rows:
                if str(x.get("key")) in hit:
                    v = {k: (y[1] if isinstance(y, tuple) else y) for k, y in (x.get("values") or {}).items()}
                    print("     key", x["key"], {k: v[k] for k in list(v)[:10]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
