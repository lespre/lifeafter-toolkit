# -*- coding: utf-8 -*-
r"""把 assets/skin_posters/<skin_id>.png 挂到武器皮肤媒体库里（用户提供的官方/实机图）。

为什么单独写：媒体库由 tools/rebuild_weapon_skin_media.py 从 3D 预览目录重建，
本身不看这个目录 —— 这里做「重建后补齐」，同时给 rebuild 工具加了同一段合并逻辑，
两边口径一致，下次重建不会把海报冲掉。
"""
from __future__ import annotations

import json
import pathlib
import shutil
import datetime

WEB = pathlib.Path(r"E:/la拆包项目/04_站点/web")
MEDIA_JS = WEB / "data/media/weapon_skin_media.js"
POSTERS = WEB / "assets/skin_posters"
PREFIX = "window.WEAPON_SKIN_MEDIA = "

text = MEDIA_JS.read_text(encoding="utf-8")
assert text.startswith(PREFIX), "媒体库文件格式不符合预期"
payload = json.loads(text[len(PREFIX):].rstrip().rstrip(";"))
skins = payload.setdefault("skins", {})

stamp = datetime.datetime.now().strftime("%Y%m%d")
shutil.copy2(MEDIA_JS, MEDIA_JS.with_suffix(".js.bak_posters_%s" % stamp))

n = 0
for png in sorted(POSTERS.glob("*.png")):
    sid = png.stem
    rec = skins.setdefault(sid, {"skin_id": sid})
    rec["poster"] = {"src": "assets/skin_posters/%s" % png.name}
    rec["poster_source"] = "user_supplied"
    rec["poster_note"] = "用户提供（2026-10-18），官方皮肤 2D 图（白底 UI 图标）"
    rec.pop("poster_kind", None)          # 这是正式海报，不是素材底图
    n += 1
    print("挂图:", sid, "→", rec["poster"]["src"])

payload["posters_merged_at"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
MEDIA_JS.write_text(PREFIX + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
                    encoding="utf-8")
# ★ 2026-10-18：媒体库是 .js/.json 双胞胎，页面读 .js，审计/工具读 .json —— 必须同步写，
#   只写一份会让两边条目数对不上（本脚本此前只写 .js）。
MEDIA_JSON = WEB / "data/media/weapon_skin_media.json"
if MEDIA_JSON.is_file():
    shutil.copy2(MEDIA_JSON, MEDIA_JSON.with_suffix(".json.bak_posters_%s" % stamp))
MEDIA_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("挂图 %d 条 ｜ 媒体库条目 %d ｜ 已同步 %s" % (n, len(skins), MEDIA_JSON.name))
