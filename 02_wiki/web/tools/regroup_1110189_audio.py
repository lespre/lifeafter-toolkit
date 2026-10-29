# -*- coding: utf-8 -*-
"""1110189：把音效分成「本体音 / 通用开火 / 通用补充」，并去掉与 lp1 完全相同的 lp2。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
ATT = ROOT / "02_wiki/web/data/weapon_skin_audio_attachments.json"
DIR = ROOT / "02_wiki/web/assets/audio/weapon_skin/penhuoqi_base"

GROUPS = [
    ("本体音（weapon_1013_10：循环 / 单发）", ["weapon_1013_10_lp1", "weapon_1013_10_oneshot"]),
    ("通用开火（喷火器 penhuoqi_fire_*）",
     ["penhuoqi_fire_start_01", "penhuoqi_fire_loop_01",
      "penhuoqi_fire_random_01", "penhuoqi_fire_random_02", "penhuoqi_fire_random_03"]),
    ("通用补充（燃料 / 换弹 penhuoqi_*）",
     ["penhuoqi_gas_01", "penhuoqi_gas_02", "penhuoqi_gas_03", "penhuoqi_gas_04",
      "penhuoqi_huandan_01"]),
]
DROP = ["weapon_1013_10_lp2"]


def main() -> int:
    att = json.loads(ATT.read_text(encoding="utf-8"))
    groups, missing = [], []
    for label, names in GROUPS:
        items = []
        for nm in names:
            if (DIR / (nm + ".wav")).is_file():
                items.append({"label": nm, "file": nm + ".wav"})
            else:
                missing.append(nm)
        if items:
            groups.append({"label": label, "items": items})
    rec = att["skins"]["1110189"]
    rec["groups"] = groups
    rec["evidence"] = ("本体音 weapon_1013_10_*（lp1 与 lp2 逐字节相同，只留 lp1）；"
                       "通用开火取喷火器 penhuoqi_fire_start/loop/random；燃料与换弹取 penhuoqi_gas_*/huandan。"
                       "该皮自身 skin_1013_010 资源未进包，故无专属音。")
    ATT.write_text(json.dumps(att, ensure_ascii=False, indent=1), encoding="utf-8")
    removed = 0
    for nm in DROP:
        p = DIR / (nm + ".wav")
        if p.is_file():
            p.unlink()
            removed += 1
    print("分组 %d ｜ 条目 %d ｜ 删除重复 %d ｜ 缺 %s"
          % (len(groups), sum(len(g["items"]) for g in groups), removed, missing or "无"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
