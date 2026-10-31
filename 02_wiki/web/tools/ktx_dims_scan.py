# -*- coding: utf-8 -*-
"""扫描 npk 内 KTX 纹理的尺寸分布（只读头部 128 B，不解压全量）。"""
from __future__ import annotations

import collections
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from la_unpack_core import NpkArchive  # noqa: E402

KTX_MAGIC = b"\xabKTX"


def main(argv: list[str]) -> int:
    pack = pathlib.Path(argv[0])
    a = NpkArchive(str(pack))
    print(pack.name, "条目", len(a._entries))
    dims = collections.Counter()
    ktx_rows = []
    with pack.open("rb") as f:
        for e in a._entries:
            f.seek(e.offset)
            head = f.read(80)
            if not head.startswith(KTX_MAGIC):
                continue
            try:
                w = struct.unpack_from("<I", head, 36)[0]
                h = struct.unpack_from("<I", head, 40)[0]
                fmt = struct.unpack_from("<I", head, 28)[0]
            except struct.error:
                continue
            dims[(w, h)] += 1
            ktx_rows.append((e.entry_index, w, h, fmt, e.packed))
    print("KTX 总数", len(ktx_rows))
    for (w, h), n in dims.most_common(12):
        print("   %4d×%-4d %5d" % (w, h, n))
    out = ROOT / "01_索引与产物/30_分析/ktx_dims_%s.json" % pack.stem.replace(".", "_")
    import json
    out.write_text(json.dumps(ktx_rows), encoding="utf-8")
    print("写出", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
