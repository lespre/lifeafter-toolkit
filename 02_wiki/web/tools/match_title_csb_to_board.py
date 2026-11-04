# -*- coding: utf-8 -*-
"""把 PE 里捞到的称号 csb 按贴图路径对到 title_catalog 条目，报告覆盖率。"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
CSB_DIR = PROJ / "01_索引与产物/30_分析/title_csb_pe/gpk_all"
STR_RE = re.compile(rb"[ -~]{6,140}")


def main() -> int:
    idx = json.loads((CSB_DIR / "index.json").read_text(encoding="utf-8"))
    csbs = []
    for it in idx:
        b = (CSB_DIR / it["file"]).read_bytes()
        tex = sorted({s.decode("ascii", "ignore") for s in STR_RE.findall(b) if b"chenghao/" in s})
        csbs.append({"file": it["file"], "pack": it["pack"], "row": it["row"],
                     "bytes": len(b), "textures": tex})
    board = json.loads((WEB / "data/boards/title_catalog.json").read_text(encoding="utf-8"))
    hits = 0
    for it in board["items"]:
        csb = str(it.get("anim_csb") or "")
        if not csb:
            continue
        stem = csb.replace("\\", "/").rsplit("/", 1)[-1].removesuffix(".csb")
        tokens = [t for t in re.split(r"[_]+", stem) if len(t) >= 5 and t not in ("main", "chenghao", "xuancai")]
        m = next((c for c in csbs if any(tok in " ".join(c["textures"]) for tok in tokens)), None)
        if m:
            hits += 1
    print("有 anim_csb 的条目", sum(1 for i in board["items"] if i.get("anim_csb")))
    print("可对上 PE csb 的条目", hits)
    print("PE csb 总数", len(csbs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
