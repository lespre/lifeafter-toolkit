# -*- coding: utf-8 -*-
"""1110189（传世·喷火器）音频：改用新式喷火器底座 weapon_1013_10_*，并保留通用补充。"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path("E:/la拆包项目")
ATT = ROOT / "02_wiki/web/data/weapon_skin_audio_attachments.json"
DIR = ROOT / "02_wiki/web/assets/audio/weapon_skin/penhuoqi_base"

GROUPS = [
    ("喷火底座（新式喷火器 weapon_1013_10_*）",
     ["weapon_1013_10_lp1", "weapon_1013_10_lp2", "weapon_1013_10_oneshot"]),
    ("通用补充（喷火器基础 penhuoqi_*）",
     ["penhuoqi_fire_start_01", "penhuoqi_fire_loop_01", "penhuoqi_fire_random_01",
      "penhuoqi_fire_random_02", "penhuoqi_fire_random_03", "penhuoqi_gas_01",
      "penhuoqi_gas_02", "penhuoqi_gas_03", "penhuoqi_gas_04", "penhuoqi_huandan_01"]),
]


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
    rec["dir"] = "penhuoqi_base"
    rec["groups"] = groups
    rec["evidence_kind"] = "底座音效（皮肤自身资源未进包）"
    rec["evidence"] = ("该皮只有行为资源行（skin_1013_010 的 kh/sj/jisha 特效路径），无主表父行、无道具名、"
                       "资源未进本地包；喷火主音取新式喷火器底座 weapon_1013_10_lp1/lp2/oneshot（0188.gpk），"
                       "起手/换弹/燃料等取喷火器通用 penhuoqi_*（0187.gpk）。")
    ATT.write_text(json.dumps(att, ensure_ascii=False, indent=1), encoding="utf-8")
    print("1110189 分组 %d ｜ 缺失 %s" % (len(groups), missing or "无"))
    for g in groups:
        print("  ", g["label"], len(g["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
