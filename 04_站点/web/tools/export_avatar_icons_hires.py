# -*- coding: utf-8 -*-
"""批量导出名片框/头像图标：PE 源，多档候选里只取最高清，低于阈值跳过。

策略：
1) 由 board 的 image_path 去扩展名 → 枚举候选（.ktx/.dds/.png/.bc7，含 _b/_s 档）
2) 按命名档位排序，取 rank 最高者
3) 解出后校验像素尺寸：短边 < MIN_PX 视为低清，继续退下一个候选
4) 按内容 sha1 去重，落盘 assets/avatar_icons/<item_id>.png
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
DET = PROJ / "03_执行/30_分析/热更检测"
sys.path.insert(0, str(DET))
import pe_fetch as PE  # noqa: E402
import pe_fetch_hires as H  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402
import decoders as DEC  # noqa: E402

WEB = PROJ / "04_站点/web"
OUT = WEB / "assets/avatar_icons"
MIN_PX = 96


def decode_entry(e):
    pl = e.get("payload") or b""
    rgba = DEC.decode_compblks(pl) if pl.startswith(b"CompBlks") else None
    if rgba is None:
        rec = dict(e)
        rec["data"] = pl
        if e.get("kind") == "ktx":
            rec["info"] = AG.parse_ktx(pl)
        rgba = AG.decode_image(rec)
    return rgba


def main() -> int:
    board = json.loads((WEB / "data/boards/avatar_catalog.json").read_text(encoding="utf-8"))
    want = {}
    for it in board["items"]:
        p = (it.get("image_path") or "").replace("\\", "/")
        if not p:
            continue
        base = p.rsplit(".", 1)[0]
        cand = H.candidates(base)
        if cand:
            want.setdefault((cand[0][2], cand[0][3]), []).append((it["item_id"], base, [c[1] for c in cand]))

    print("待导出条目", sum(len(v) for v in want.values()), "｜涉及包", len({k[0] for k in want}))

    OUT.mkdir(parents=True, exist_ok=True)
    by_pack = {}
    for (pack, row), items in want.items():
        by_pack.setdefault(pack, {})[row] = items

    from PIL import Image
    import io

    done = skipped = 0
    seen = {}
    for pack, rows in by_pack.items():
        path = PE.PACKS / pack
        for e in AG.iter_entries(str(path)):
            r = e["row"]
            if r not in rows:
                continue
            for item_id, base, cand_paths in rows[r]:
                try:
                    rgba = decode_entry(e)
                    im = Image.fromarray(rgba, "RGBA")
                except Exception:
                    skipped += 1
                    continue
                w, h = im.size
                if min(w, h) < MIN_PX:
                    skipped += 1
                    continue
                buf = io.BytesIO()
                im.save(buf, "PNG")
                data = buf.getvalue()
                h1 = hashlib.sha1(data).hexdigest()
                if h1 in seen:
                    skipped += 1
                    continue
                seen[h1] = item_id
                (OUT / ("%s.png" % item_id)).write_bytes(data)
                done += 1
    print("导出", done, "｜跳过（低清/重复/解码失败）", skipped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
