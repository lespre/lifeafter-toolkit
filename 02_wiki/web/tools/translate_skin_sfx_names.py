# -*- coding: utf-8 -*-
"""把武器皮肤音效的内部真名翻译成中文短标签（内部名保留，中文并列展示）。

规则：按 _ 切词直译；武器词前置（reload_rifle → 步枪换弹）；ride_horse 合并为「骑乘」；
纯数字保留；未收录词原样保留，不臆造。
"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"

ACTION = {
    "shoot": "射击", "reload": "换弹", "attack": "攻击", "hit": "命中", "impact": "命中",
    "draw": "拉弓", "bolt": "上膛", "start": "起手", "idle": "待机", "loop": "循环",
    "spell": "施法", "magic": "魔法", "switch": "切换", "charge": "蓄力",
}
WEAPON = {
    "rifle": "步枪", "pistol": "手枪", "shotgun": "霰弹枪", "bow": "弓", "arrow": "箭",
    "nucleus": "核芯", "shield": "护盾", "liandao": "镰刀",
    "huojianqiang": "火箭枪", "huojiantong": "火箭筒",
}
MOD = {"ride": "骑乘", "horse": "", "crouch": "蹲伏", "coruch": "蹲伏", "jump": "跳跃",
       "heng": "横", "shu": "竖", "left": "左", "right": "右",
       "l": "左", "r": "右", "u": "上", "b": "后", "f": "前", "d": "下",
       "long": "长", "short": "短", "weaponskin": "皮肤", "fire": "开火", "gun": "枪"}
CODEWORDS = {"hqj", "hjq", "hd", "dj", "zl", "zx", "yk", "js"}


def translate(name: str) -> str:
    toks = [t for t in name.split("_") if t]
    mods, weapons, actions, nums, others = [], [], [], [], []
    for raw in toks:
        t = raw.lower()
        if t.isdigit():
            nums.append(t)
        elif t in ("ride", "horse"):
            if "骑乘" not in mods:
                mods.append("骑乘")
        elif t in ACTION:
            actions.append(ACTION[t])
        elif t in WEAPON:
            weapons.append(WEAPON[t])
        elif t in MOD:
            if MOD[t] and MOD[t] not in mods:
                mods.append(MOD[t])
        elif t in CODEWORDS:
            others.append(t)
        else:
            others.append(raw)

    DIRS = {'左','右','上','后','前','下','横','竖'}
    body_mods=[m for m in mods if m not in DIRS]
    tail_mods=[m for m in mods if m in DIRS]
    head = list(weapons)
    if weapons and weapons[0] in ("步枪", "手枪", "霰弹枪") and "换弹" in actions:
        actions = [a for a in actions if a != "换弹"] + ["换弹"]
    head += body_mods
    head += others
    head += actions
    head += tail_mods
    return " ".join(head + nums).strip()


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    n = 0
    for it in d["items"]:
        names = it.get("sfx_real_names") or []
        if not names:
            continue
        it["sfx_real_names_cn"] = {nm: translate(nm) for nm in names}
        n += 1
    d.setdefault("meta", {})["sfx_real_names_cn_note"] = (
        "内部真名按固定词表逐词直译（shoot→射击、reload→换弹、ride_horse→骑乘、nucleus→核芯），"
        "武器词前置（reload_rifle→步枪换弹）；数字与代号原样保留，未收录词不臆造。")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("翻译 %d 卡" % n)
    for nm in ("ride_horse_shoot_02_r", "nucleus_attack_04_01", "reload_rifle_01",
               "crouch_shoot_03_heng", "shoot_07", "asoul_gun_fire_01",
               "penhuoqi_fire_loop_01", "huojianqiang_long_01"):
        print("  %-24s → %s" % (nm, translate(nm)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
