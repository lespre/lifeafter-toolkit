# -*- coding: utf-8 -*-
"""把皮肤音效按页面约定补到 assets/audio/weapon_skin/<dir>/<file>。

board.html 的 renderSkinAudio 读的就是这个路径；缺一条就是 404 静音。
来源：01_索引与产物 全库 WAV（按 basename 匹配）。
"""
from __future__ import annotations
import sys

import json
import pathlib
import shutil
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
WEB = ROOT / "02_wiki/web"
DST = WEB / "assets/audio/weapon_skin"
SKIP = {"00_规范与工具/环境/venv", ".git", "41_还原树"}

byname: dict[str, list[pathlib.Path]] = defaultdict(list)
for p in (ROOT / "01_索引与产物").rglob("*.wav"):
    if any(part in SKIP for part in p.parts):
        continue
    byname[p.name.lower()].append(p)


def rank(p: pathlib.Path) -> int:
    s = str(p).lower()
    return 0 if "audio_review" in s else (1 if "skin_audio_carved" in s else (2 if "skin_audio_all" in s else 3))


for v in byname.values():
    v.sort(key=rank)

att = json.loads((WEB / "data/weapon_skin_audio_attachments.json").read_text(encoding="utf-8"))
skins = att["skins"]

copied = already = missing = total = 0
miss_by_skin = {}
for sid, rec in skins.items():
    d = rec.get("dir") or sid
    outdir = DST / d
    m = 0
    for g in rec.get("groups", []):
        for it in g.get("items", []):
            f = it.get("file")
            if not f:
                continue
            total += 1
            dst = outdir / f
            if dst.is_file():
                already += 1
                continue
            src = byname.get(f.lower())
            if not src:
                missing += 1
                m += 1
                continue
            outdir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src[0], dst)
            copied += 1
    if m:
        miss_by_skin[rec.get("name") or sid] = m

print("条目 %d ｜ 已有 %d ｜ 本次补 %d ｜ 仍缺 %d ｜ 覆盖 %.1f%%"
      % (total, already, copied, missing, (already + copied) * 100.0 / max(total, 1)))
top = sorted(miss_by_skin.items(), key=lambda kv: -kv[1])[:6]
print("缺口最多的皮肤:", top)
