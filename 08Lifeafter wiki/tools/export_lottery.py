#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出板块：限时主题抽奖奖池（已上线帝皇 = verified；未上线铠甲再临 = candidate/structure）

严格对齐 06 日志第四/九章：
- 帝皇铠甲已上线、用户可核验、同包闭环 -> verified；概率为配置原始值，未做归一化总和校验（notes 声明）。
- 铠甲再临未上线：本期“主池行/秘宝/福袋(未上线)” -> candidate；“关联/共享行”是跨活动旧池
  （潜龙濯月/星宿万象等）-> structure 且明确标注非本期，不得当新内容。
- 臻藏商店旧兑换表已被用户实机否定（作废），不在此导出。
用法: python tools/export_lottery.py
"""
import csv, json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CW = ROOT.parent / "03拆包产物" / "config_work"
BOARDS = ROOT / "data" / "boards"
DOC_SHA = "56def41376ed2e71f1901756cde1984a53e6a6b863767e982ffd1eac601bb224"
TODAY = datetime.date.today().isoformat()


def read_csv(name):
    p = CW / name
    with p.open("r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def pick_name(row, *keys):
    for k in keys:
        v = (row.get(k) or "").strip()
        if v and v != "待取名":
            return v
    for k in keys:
        v = (row.get(k) or "").strip()
        if v:
            return v
    return "(未命名)"


def to_prob(v):
    try:
        return round(float(v), 6)
    except Exception:
        return None


def server_hint(text):
    if "经典服" in text:
        return "经典服"
    if "生存服" in text:
        return "简单生存服"
    return ""


def export_dihuang():
    rows = read_csv("帝皇铠甲奖池_当前期全量_2026-08-31.csv")
    items, seen = [], set()
    for r in rows:
        pool, slot = r["池ID"].strip(), r["slot"].strip()
        uid = f"{pool}-{slot}"
        if uid in seen:
            continue
        seen.add(uid)
        name = pick_name(r, "发放物", "显示名")
        joined = " ".join(r.values())
        items.append({
            "id": uid,
            "name": name,
            "evidence": "verified",  # 已上线活动、同包闭环、用户可核验
            "source": f"Documents reward_pool 池{pool} slot{slot}；帝皇铠甲已上线",
            "tier": r["档位"].strip(),
            "pool_id": int(pool), "slot": int(slot),
            "item_id": r["发放物ID"].strip(),
            "prob": to_prob(r["概率"]),
            "config_exp": r["过期"].strip(),
            "server": server_hint(joined),
        })
    board = {
        "meta": {
            "name": "抽奖奖池·帝皇铠甲（已上线）",
            "category": "奖池类-限时主题",
            "source_server": "Documents 体验服（含经典服/生存服珍匣分支标注）",
            "package_sha": DOC_SHA, "generated": TODAY, "evidence": "verified",
            "notes": (
                f"共 {len(items)} 条当前期行，已上线、用户可核验，行级 verified。概率为配置原始值，"
                "未做按池归一化总和校验，引用时不要把跨池概率直接相加；config_exp 为配置内 expiration 原值"
                "（非截图倒计时）。含帝皇裁决/极光剑/极光盾/帝皇铠甲/帝皇铠骑等交易盒与涂装、核芯。"
            ),
        },
        "items": items,
    }
    (BOARDS / "lottery_dihuang.json").write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ lottery_dihuang: {len(items)} 条 verified")


def export_kaijia():
    # 【2026-09-01 废弃】二期铠甲再临已实装，旧“未上线预告层”导出会把板块打回 candidate。
    # 已由 export_kaijia_phase2.py（快照 BA8A239A，panel+左右大奖 verified）取代，此处不再生成。
    print("⏭ export_kaijia 已废弃：二期已实装，请运行 export_kaijia_phase2.py")
    return
    rows = read_csv("铠甲再临_刑天飞影_未上线预告层全量_2026-08-31.csv")
    items, seen = [], set()
    cnt = {"candidate": 0, "structure": 0}
    for r in rows:
        layer = r["层"].strip(); pool, slot = r["池ID"].strip(), r["slot"].strip()
        uid = f"{pool}-{slot}"
        if uid in seen:
            continue
        seen.add(uid)
        is_shared = layer.startswith("关联")
        ev = "structure" if is_shared else "candidate"
        cnt[ev] += 1
        name = pick_name(r, "发放物", "显示名", "name字段")
        items.append({
            "id": uid,
            "name": name,
            "evidence": ev,
            "source": (
                f"Documents reward_pool 池{pool} slot{slot}；层={layer}；"
                + ("跨活动共享旧行，非铠甲再临本期内容" if is_shared else "铠甲再临本期，活动未上线、待 real-pool 真值校准")
            ),
            "layer": layer,
            "pool_id": int(pool), "slot": int(slot),
            "item_id": r["发放物ID"].strip(),
            "prob": to_prob(r["概率"]),
            "config_exp": r["过期"].strip(),
            "broadcast": (r.get("活动") or "").strip(),
        })
    board = {
        "meta": {
            "name": "抽奖奖池·铠甲再临(刑天飞影)（未上线预告）",
            "category": "奖池类-限时主题",
            "source_server": "Documents 体验服（活动未上线，仅预告层）",
            "package_sha": DOC_SHA, "generated": TODAY, "evidence": "candidate",
            "notes": (
                f"共 {len(items)} 行：本期未上线主池/秘宝/福袋 {cnt['candidate']} 条 candidate（待 P1 real-pool "
                "用已上线活动真值校准后才可升 verified）；跨活动共享旧行 "
                f"{cnt['structure']} 条 structure（潜龙濯月/星宿万象等，明确非本期，仅因池共享被解出，勿当新内容）。"
                "含刑天/飞影铠甲、疾影枪、火刑电光炮(火刑裁决)、战神烈火剑、火刑战驱、刑天/飞影部件；概率为原始值。"
            ),
        },
        "items": items,
    }
    (BOARDS / "lottery_kaijiazailin.json").write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✅ lottery_kaijiazailin: {len(items)} 条 (candidate {cnt['candidate']} / 共享structure {cnt['structure']})")


if __name__ == "__main__":
    export_dihuang()
    export_kaijia()
