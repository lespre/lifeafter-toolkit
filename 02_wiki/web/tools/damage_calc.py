# -*- coding: utf-8 -*-
"""伤害计算器：武器攻击力 × 场景加成区间 × (1 − 目标减伤)。

口径来源（都有据可查，不臆造）：
  武器/护甲属性   data/boards/equipment_attrs.json（all_equips attrs，0xC6/0x86 帧解出）
  场景加成区间    data/boards/scene_balance.json（special_hurt_params_data，按服型分档）
  结算结构        伤害 = 基础 × (1 + Σ加成) × (1 − Σ减免) × 部位 × 暴击
                  （见 01_索引与产物/30_分析/伤害系统逆向/伤害计算逆向_结论.md）

刻意不做的事：
  · 不猜「攻击力 vs 护甲」到区间内哪个点（游戏是分段曲线，规则未证）
  · 不乘部位/暴击系数（默认取 1，需要时显式给 --part / --crit）

用法：
  python tools/damage_calc.py --weapon AK47 --target 白衣骑士 --scene 夏尔镇
  python tools/damage_calc.py --weapon 10001 --target 30019 --scene 329 --server 测试服·经典服源
"""
from __future__ import annotations

import argparse
import json
import pathlib

WEB = pathlib.Path(__file__).resolve().parents[1]
EQ = WEB / "data/boards/equipment_attrs.json"
SCENE = WEB / "data/boards/scene_balance.json"


def load_equip() -> list[dict]:
    return json.loads(EQ.read_text(encoding="utf-8"))["items"]


def pick(items: list[dict], q: str) -> dict | None:
    q = str(q).strip()
    for it in items:
        if str(it.get("row_key")) == q or str(it.get("id")) == q:
            return it
    for it in items:
        if q and q in str(it.get("name") or ""):
            return it
    return None


def attr_of(item: dict, *names: str) -> float:
    """从 属性 文本里取某个属性的数值（文本形如 '攻击力 85 ｜ 武器火力 1.4'）。"""
    text = str(item.get("属性") or "")
    for seg in text.split("｜"):
        seg = seg.strip()
        for n in names:
            if seg.startswith(n):
                tail = seg[len(n):].strip()
                try:
                    return float(tail)
                except ValueError:
                    return 0.0
    return 0.0


def scene_range(items: list[dict], q: str, server: str | None) -> tuple[str, float, float, dict]:
    cands = []
    for it in items:
        if server and it.get("server_type") != server:
            continue
        if str(it.get("scene_id")) == str(q) or (q and q in str(it.get("name") or "")):
            cands.append(it)
    if not cands:
        raise SystemExit("没找到场景：%s（可先看 scene_balance 板）" % q)
    it = cands[0]
    return it.get("name"), float(it.get("lower") or 0), float(it.get("upper") or 0), it


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weapon", required=True, help="武器名/row_key，如 AK47 / 10001")
    ap.add_argument("--target", default="", help="目标护甲名/row_key（取减伤率与护甲值）")
    ap.add_argument("--scene", required=True, help="场景名/scene_id")
    ap.add_argument("--server", default=None, help="服型：测试服·经典服源 / 测试服·简单生存服源")
    ap.add_argument("--part", type=float, default=1.0, help="部位系数，默认 1")
    ap.add_argument("--crit", type=float, default=1.0, help="暴击系数，默认 1")
    a = ap.parse_args()

    eq = load_equip()
    w = pick(eq, a.weapon)
    if not w:
        raise SystemExit("没找到武器：%s" % a.weapon)
    hurt = attr_of(w, "攻击力", "伤害", "hurt")
    power = attr_of(w, "武器火力", "功率", "power")

    reduce = 0.0
    armor = 0.0
    tname = "-"
    if a.target:
        t = pick(eq, a.target)
        if not t:
            raise SystemExit("没找到护甲：%s" % a.target)
        tname = t.get("name")
        reduce = attr_of(t, "伤害减免百分比", "减伤率", "hurt_reduction_rate")
        armor = attr_of(t, "护甲值", "护甲", "armor")

    sname, lo, hi, srow = scene_range(json.loads(SCENE.read_text(encoding="utf-8"))["items"],
                                      a.scene, a.server)

    def dmg(mult: float) -> float:
        return hurt * (1 + mult) * (1 - reduce) * a.part * a.crit

    print("武器      %s（攻击力 %g ｜ 武器火力 %g）" % (w.get("name"), hurt, power))
    print("目标      %s（护甲值 %g ｜ 减伤率 %g）" % (tname, armor, reduce))
    print("场景      %s ｜ %s ｜ 加成区间 %.2f ~ %.2f ｜ %s" %
          (sname, srow.get("server_type"), lo, hi, srow.get("source_kind")))
    print("部位/暴击 %g / %g" % (a.part, a.crit))
    print("-" * 56)
    print("伤害区间  %.1f ~ %.1f（区间内具体值取决于攻击力/护甲分段曲线，未证，不取点值）" %
          (dmg(lo), dmg(hi)))
    print("不暴击基准 %.1f ｜ 满加成 %.1f" % (dmg(lo), dmg(hi)))
    print()
    print("口径：伤害 = 攻击力 × (1 + 场景加成) × (1 − 减伤率) × 部位 × 暴击")
    print("依据：equipment_attrs（all_equips attrs） + scene_balance（special_hurt_params_data） + 伤害逆向结论")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
