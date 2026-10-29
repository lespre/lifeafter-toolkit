# -*- coding: utf-8 -*-
"""把「音效真名（内部名）」写进武器皮肤板的每张卡。

来源：weapon_skin_sfx_function_data(skin_id → 行 key)
      → weapon_skin_sound_data_for_query 行内联 <key, 真名> 对
      （如 1120380 → nucleus_attack_04_01 / shoot_02 / reload_rifle_01）
"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
MAP = ROOT / "01_索引与产物/30_分析/weapon_skin_sfx_real_names.json"
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"
ATT = ROOT / "02_wiki/web/data/weapon_skin_audio_attachments.json"


def main() -> int:
    m = json.loads(MAP.read_text(encoding="utf-8"))
    att = json.loads(ATT.read_text(encoding="utf-8"))
    have_audio = set(att.get("skins") or {})
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    n_names = n_audio = 0
    for it in d["items"]:
        sid = str(it.get("skin_id") or it.get("id"))
        rec = m.get(sid) or {}
        names = rec.get("real_names") or []
        if names:
            it["sfx_real_names"] = names
            it["sfx_real_source"] = "weapon_skin_sound_data_for_query 内联键值对（绑定该皮肤的 SFX 配置行 %d 条）" % len(rec.get("sfx_keys") or [])
            n_names += 1
        if sid in have_audio:
            n_audio += 1
            it["sfx_audio_state"] = "已提取"
        elif names:
            it["sfx_audio_state"] = "真名已确认 · 音频未提取"
    d.setdefault("meta", {})["sfx_real_names_note"] = (
        "音效真名取自带内联键值对的音效查询表：皮肤表 skin_id 行 → SFX 配置行 key → 查询表同 key 的内联名。"
        "内部名原样保留，不做翻译；有真名不等于音频已提取，两者分列展示。")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("写入真名 %d 卡 ｜ 已提取音频 %d 卡 / 共 %d" % (n_names, n_audio, len(d["items"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
