# -*- coding: utf-8 -*-
"""重建 1110188（一魂共鸣）的音效分组：射击 / 换弹 / 切枪 / 语音。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
ATT = ROOT / "02_wiki/web/data/weapon_skin_audio_attachments.json"
DIR = ROOT / "02_wiki/web/assets/audio/weapon_skin/asoul_1110188"

GROUPS = [
    ("射击音效", ["asoul_gun_fire_%02d" % i for i in range(1, 6)], "皮肤专属（asoul_gun_fire_*）"),
    ("换弹音效", ["reload_01", "reload_02", "reload_03"], "步枪通用底座（reload_0*）；该皮无专属换弹采样"),
    ("切枪音效", ["asoul_switch_01", "asoul_switch_02"], "皮肤专属（asoul_switch_*）"),
    ("语音", ["vo_gunreload_all", "vo_gunswitch_beila", "vo_gunswitch_jiaran", "vo_gunswitch_nailin"],
     "联动语音（换弹 / 切枪 · 贝拉 / 嘉然 / 乃琳）"),
]


def main() -> int:
    att = json.loads(ATT.read_text(encoding="utf-8"))
    groups = []
    missing = []
    for label, names, note in GROUPS:
        items = []
        for nm in names:
            if (DIR / (nm + ".wav")).is_file():
                items.append({"label": nm, "file": nm + ".wav"})
            else:
                missing.append(nm)
        if items:
            groups.append({"label": "%s（%s）" % (label, note), "items": items})
    rec = att["skins"].setdefault("1110188", {})
    rec.update({
        "name": "一魂共鸣", "dir": "asoul_1110188", "groups": groups,
        "evidence_kind": "专属音效 + 通用底座",
        "evidence": "射击/切枪为 asoul_* 专属样本；换弹无专属采样，取步枪通用 reload_0*；"
                    "语音取自同 bank 的 vo_gunreload_all / vo_gunswitch_*（0339.gpk）。",
    })
    ATT.write_text(json.dumps(att, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(len(g["items"]) for g in groups)
    print("1110188 分组 %d ｜ 条目 %d ｜ 缺失 %s" % (len(groups), total, missing or "无"))
    for g in groups:
        print("  ", g["label"], len(g["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
