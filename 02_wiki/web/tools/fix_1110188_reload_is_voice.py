# -*- coding: utf-8 -*-
"""一魂共鸣换弹音效=角色语音（vo_gunreload_all），移除误挂的步枪通用换弹底座。"""
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
    ("射击音效（皮肤专属 asoul_gun_fire_*）", ["asoul_gun_fire_%02d" % i for i in range(1, 6)]),
    ("换弹音效（角色语音 vo_gunreload_all）", ["vo_gunreload_all"]),
    ("切枪音效（皮肤专属 asoul_switch_*）", ["asoul_switch_01", "asoul_switch_02"]),
    ("切枪语音（贝拉 / 嘉然 / 乃琳）", ["vo_gunswitch_beila", "vo_gunswitch_jiaran", "vo_gunswitch_nailin"]),
]
DROP = ["reload_01", "reload_02", "reload_03"]


def main() -> int:
    att = json.loads(ATT.read_text(encoding="utf-8"))
    groups = []
    for label, names in GROUPS:
        items = [{"label": nm, "file": nm + ".wav"} for nm in names if (DIR / (nm + ".wav")).is_file()]
        if items:
            groups.append({"label": label, "items": items})
    rec = att["skins"]["1110188"]
    rec["groups"] = groups
    rec["evidence_kind"] = "皮肤专属音效（含联动语音）"
    rec["evidence"] = ("射击/切枪为 asoul_* 专属样本；换弹音效即角色语音 vo_gunreload_all；"
                       "切枪另有贝拉/嘉然/乃琳三条语音。全部取自 0339.gpk 同 bank。")
    ATT.write_text(json.dumps(att, ensure_ascii=False, indent=1), encoding="utf-8")
    removed = 0
    for nm in DROP:
        p = DIR / (nm + ".wav")
        if p.is_file():
            p.unlink()
            removed += 1
    total = sum(len(g["items"]) for g in groups)
    print("分组 %d ｜ 条目 %d ｜ 删除误挂 %d 条" % (len(groups), total, removed))
    for g in groups:
        print("  ", g["label"], len(g["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
