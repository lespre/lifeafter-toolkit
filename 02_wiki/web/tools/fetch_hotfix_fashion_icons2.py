# -*- coding: utf-8 -*-
"""正确解出热更新时装的 icons（0x27/0x05 帧里的 ui/item_icon 路径），再按路径取图。

比"按命名猜"可靠：路径直接来自表，男女两套都能拿到。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
import pc_fetch  # noqa: E402

NEW = sorted((ROOT / "01_索引与产物/30_分析/pc_hotfix_tables").glob("*"))[-1]
WEB = ROOT / "02_wiki/web"
OUT = WEB / "assets/fashion_posters/pc_hotfix"
REPORT = ROOT / "01_索引与产物/30_分析/pc_hotfix_new_fashion_imgs.json"


def uleb(b: bytes, q: int):
    v = 0
    s = 0
    while True:
        c = b[q]
        q += 1
        v |= (c & 0x7F) << s
        if not c & 0x80:
            return v, q
        s += 7


def load_rows():
    p = NEW / "fashion_data.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + n]
    cnt, _ = struct.unpack_from("<II", body, 0)
    blob = body[8 + 4 * cnt:]
    pool = parse_legacy_chs_pool((NEW / "fashion_data_chs.py").read_bytes())
    rows = json.loads((ROOT / "01_索引与产物/30_分析/pc_hotfix_new_fashion.json").read_text(encoding="utf-8"))
    out = []
    for r in rows:
        icons = str(r.get("icons") or "")
        paths = []
        if icons.startswith("jump:"):
            off = int(icons[5:])
            if blob[off] == 0x27:
                q = off + 2
                try:
                    num, q = uleb(blob, q)
                    for _ in range(num):
                        v, q = uleb(blob, q)
                        if v < len(pool) and "item_icon" in str(pool[v]):
                            paths.append(str(pool[v]))
                except Exception:                        # noqa: BLE001
                    pass
        out.append({**r, "icon_paths": paths})
    return out


def main() -> int:
    rows = load_rows()
    have = sum(1 for r in rows if r["icon_paths"])
    print("行 %d ｜ 解出 icons 的行 %d" % (len(rows), have))

    OUT.mkdir(parents=True, exist_ok=True)
    report, hit, miss = {}, 0, 0
    seen = set()
    for r in rows:
        name = str(r.get("name") or "")
        base_name = name.rsplit("-", 1)[0] if name.rsplit("-", 1)[-1].endswith("天") else name
        if not base_name or base_name in seen:
            continue
        seen.add(base_name)
        files = []
        for path in r["icon_paths"]:
            stem = path.rsplit("/", 1)[-1]
            dst = OUT / (stem + "_pc.png")
            if dst.is_file() and dst.stat().st_size > 1024:
                files.append(dst)
                continue
            for cand in (path, path + "_b", path + "_s"):
                if pc_fetch.export(cand, dst):
                    files.append(dst)
                    break
        if files:
            hit += 1
            report[base_name] = [str(f.relative_to(WEB)) for f in files]
        else:
            miss += 1
            report[base_name] = []
    print("套数 %d ｜ 有图 %d ｜ 无图 %d" % (len(seen), hit, miss))
    for k, v in report.items():
        print("   %-14s %s" % (k, v[:2] if v else "—"))
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
