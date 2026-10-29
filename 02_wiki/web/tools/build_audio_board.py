# -*- coding: utf-8 -*-
"""构建武器皮肤音效板：把能定位到的 WAV 复制进站点，生成 audio_catalog 板块。

口径：
  · 清单来源 weapon_skin_audio_attachments.json（35 套皮肤 / 404 条）
  · 文件按 basename 在 01_索引与产物 全库 WAV 里找，命中才复制
  · 找不到的条目仍保留在板上，标 available=False（不隐藏，方便后续补）
"""
from __future__ import annotations
import sys

import hashlib
import json
import pathlib
import shutil
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
WEB = ROOT / "02_wiki/web"
OUT = WEB / "assets/audio"
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

items, copied, seen = [], 0, {}
OUT.mkdir(parents=True, exist_ok=True)

for sid, rec in skins.items():
    name = rec.get("name") or sid
    for gi, g in enumerate(rec.get("groups", [])):
        gname = g.get("label") or ("组 %d" % (gi + 1))
        for it in g.get("items", []):
            f = it.get("file")
            if not f:
                continue
            src = byname.get(f.lower())
            url = ""
            available = False
            if src:
                sp = src[0]
                h = hashlib.sha1(sp.read_bytes()).hexdigest()[:12]
                if h in seen:
                    url = seen[h]
                else:
                    dst = OUT / sid / sp.name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if not dst.is_file():
                        shutil.copy2(sp, dst)
                        copied += 1
                    url = "assets/audio/%s/%s" % (sid, sp.name)
                    seen[h] = url
                available = True
            items.append({
                "id": "%s_%s_%d" % (sid, it.get("label", "x"), len(items)),
                "item_id": sid,
                "name": "%s · %s" % (name, it.get("label") or f),
                "skin": name,
                "skin_id": sid,
                "group": gname,
                "label": it.get("label") or "",
                "file": f,
                "url": url,
                "available": available,
                "kind": "皮肤音效",
                "evidence": "structure",
                "evidence_level": "static/candidate" if available else "candidate",
                "status_tags": ["static config"] + ([] if available else ["file-missing"]),
                "source": "weapon_skin_audio_attachments.json",
            })

avail = sum(1 for i in items if i["available"])
board = {
    "meta": {
        "name": "武器皮肤音效",
        "category": "二、时装类 / （七）武器皮肤",
        "source_server": "体验服 Documents 快照 + 人工听辨",
        "generated": "2026-10-22",
        "id_label": "音效",
        "hide_media": False,
        "evidence": "structure",
        "card_mode": "roster",
        "package_sha": "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523",
        "total": len(items),
        "available": avail,
        "note": "文件按 basename 在本地 WAV 库匹配；未命中的保留条目并标 file-missing",
    },
    "items": items,
}

dst_json = WEB / "data/boards/audio_catalog.json"
dst_js = WEB / "data/boards/audio_catalog.js"
dst_json.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
dst_js.write_text("window.WIKI_BOARD_audio_catalog = " + json.dumps(board, ensure_ascii=False) + ";\n",
                  encoding="utf-8")
print("条目 %d ｜ 可播放 %d (%.1f%%) ｜ 复制 %d 个文件" % (len(items), avail, avail * 100.0 / len(items), copied))
print("缺文件 %d 条" % (len(items) - avail))
