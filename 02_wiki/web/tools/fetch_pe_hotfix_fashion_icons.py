# -*- coding: utf-8 -*-
"""用 PE 源（正源）导出热更新增时装的 2D 图：icons 帧 → ui/item_icon 路径 → pe_fetch。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
import pe_fetch  # noqa: E402

SRC = ROOT / "01_索引与产物/30_分析/hotfix_tables_pe_20261030"
WEB = ROOT / "02_wiki/web"
OUT = WEB / "assets/fashion_posters/pe_hotfix"
ROWS = ROOT / "01_索引与产物/30_分析/pc_hotfix_new_fashion.json"


def uleb(b, q):
    v = 0
    s = 0
    while True:
        c = b[q]; q += 1
        v |= (c & 0x7F) << s
        if not c & 0x80:
            return v, q
        s += 7


def main() -> int:
    p = SRC / "fashion_data.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + n]
    cnt, _ = struct.unpack_from("<II", body, 0)
    blob = body[8 + 4 * cnt:]
    pool = parse_legacy_chs_pool((SRC / "fashion_data_chs.py").read_bytes())

    rows = json.loads(ROWS.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    hit = 0
    for r in rows:
        name = str(r.get("name") or "")
        if not name:
            continue
        base_name = name.rsplit("-", 1)[0] if name.rsplit("-", 1)[-1].endswith("天") else name
        icons = str(r.get("icons") or "")
        if not icons.startswith("jump:"):
            continue
        off = int(icons[5:])
        paths = []
        if blob[off] == 0x27:
            q = off + 2
            try:
                num, q = uleb(blob, q)
                for _ in range(num):
                    v, q = uleb(blob, q)
                    if v < len(pool) and "item_icon" in str(pool[v]):
                        paths.append(str(pool[v]))
            except Exception:                            # noqa: BLE001
                pass
        files = []
        for path in paths:
            stem = path.rsplit("/", 1)[-1]
            dst = OUT / (stem + ".png")
            if dst.is_file() and dst.stat().st_size > 1024:
                files.append(dst)
                continue
            for cand in (path + "_b", path):
                if pe_fetch.export(cand, dst):
                    files.append(dst)
                    break
        if files:
            hit += 1
            report.setdefault(base_name, []).extend(str(f.relative_to(WEB)) for f in files)
    print("有图套数", hit, "／ 共", len(report))
    for k, v in list(report.items())[:8]:
        print("  ", k, v[:2])
    (ROOT / "01_索引与产物/30_分析/pe_hotfix_fashion_imgs.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
