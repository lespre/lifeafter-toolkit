# -*- coding: utf-8 -*-
"""给刚补的两张典藏/传世卡补证据标注，并把音频说明落到 attachments。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
ATT = ROOT / "02_wiki/web/data/weapon_skin_audio_attachments.json"

EVID = {
    "1110188": {
        "name": "一魂共鸣",
        "kind": "专属音效",
        "note": "配置表该皮 SFX 行 sfx_params=ASoul；样本 asoul_gun_fire_01..05 / asoul_switch_01..02 全库唯一命中，取自 0339.gpk。",
    },
    "1110189": {
        "name": "未命名皮肤 · ID 1110189",
        "kind": "底座音效",
        "note": "该皮无独立音效配置行，模型仅由特效路径 skin_1013_010 推定；使用喷火器通用底座 penhuoqi_*（0187.gpk），非其它皮肤专属。",
    },
}


def main() -> int:
    att = json.loads(ATT.read_text(encoding="utf-8"))
    for sid, ev in EVID.items():
        rec = att["skins"].get(sid)
        if not rec:
            print("缺记录", sid)
            continue
        rec["evidence_kind"] = ev["kind"]
        rec["evidence"] = ev["note"]
        if rec.get("name") in (None, "", "None"):
            rec["name"] = ev["name"]
        print(sid, ev["kind"], len(rec["groups"][0]["items"]), "条")
    ATT.write_text(json.dumps(att, ensure_ascii=False, indent=1), encoding="utf-8")
    print("attachments 卡数", len(att["skins"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
