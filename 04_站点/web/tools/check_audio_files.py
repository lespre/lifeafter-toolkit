# -*- coding: utf-8 -*-
"""统计武器皮肤音效清单的文件命中率（按 basename 在全库 WAV 里找）。"""
from __future__ import annotations

import json
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(r"E:/la拆包项目")
WEB = ROOT / "04_站点/web"
SKIP_PARTS = {".venv", ".git", "41_还原树"}

# basename → 候选路径（优先级：audio_review > skin_audio_carved > skin_audio_all）
byname: dict[str, list[pathlib.Path]] = defaultdict(list)
for p in (ROOT / "03_执行").rglob("*.wav"):
    if any(part in SKIP_PARTS for part in p.parts):
        continue
    byname[p.name.lower()].append(p)


def rank(p: pathlib.Path) -> int:
    s = str(p).lower()
    if "audio_review" in s:
        return 0
    if "skin_audio_carved" in s:
        return 1
    if "skin_audio_all" in s:
        return 2
    return 3


for v in byname.values():
    v.sort(key=rank)

att = json.loads((WEB / "data/weapon_skin_audio_attachments.json").read_text(encoding="utf-8"))
skins = att["skins"]

total = hit = 0
miss_files = []
ok_skins = 0
detail = {}
for sid, rec in skins.items():
    s_hit = s_total = 0
    for g in rec.get("groups", []):
        for it in g.get("items", []):
            f = it.get("file")
            if not f:
                continue
            total += 1
            s_total += 1
            cand = byname.get(f.lower())
            if cand:
                hit += 1
                s_hit += 1
            else:
                miss_files.append(f)
    if s_total:
        detail[sid] = (rec.get("name"), s_hit, s_total)
        if s_hit == s_total:
            ok_skins += 1

print("WAV 库 %d 个 basename" % len(byname))
print("音效条目 %d ｜ 命中 %d ｜ 缺 %d ｜ 覆盖 %.1f%%" % (total, hit, total - hit, hit * 100.0 / max(total, 1)))
print("皮肤 %d 套 ｜ 全命中 %d 套" % (len(skins), ok_skins))
print("缺文件样例:", sorted(set(miss_files))[:8])
for sid, (nm, h, t) in list(detail.items())[:6]:
    print("  %s %s  %d/%d" % (sid, nm, h, t))
