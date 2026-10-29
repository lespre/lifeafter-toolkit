# -*- coding: utf-8 -*-
r"""把「外观补充卡」（长编号）并入同名的时装主卡（短编号 + 魅力值）。

起因（2026-10-29 用户反馈）：
  板上出现成对的重名卡，例如
    fw_044f20cf5d  云兔衔光-头饰  model 3732     魅力 200   ← fashion_data 表
    fw_dbe26efc98  云兔衔光-头饰  model 3732001  魅力 —     ← player_appear_data 表
  短编号那张带品级/魅力/期限，长编号那张只有外观模型号，图还是同一张。
  玩家看到的是两张一样的卡，其中一张信息还缺一半。

合并规则（只合并能一一对上的）：
  ① 名字 + 部位完全一致 → 唯一主卡
  ② 名字一致且外观卡部位 ∈ 主卡 part_bucket（如「三周年纪念」两套外观卡 → 一张主卡）
  ③ 主卡 model_id 是长编号前缀（3732 → 3732001），对不上的不合并

合并后主卡：
  · model_ids     追加长编号（短号在前）
  · model_refs    新字段：外观编号（player_appear_data 的模型号）
  · appearance_merge  溯源（被并卡的 id / 部位 / 行键 / 表）
  · 主卡无图而外观卡有图时，把图搬过来
  · 被并的卡从 items 移除，条目存进顶层 merged_away 以便回滚

用法：
  python merge_appearance_cards.py --dry    # 只看会合哪些
  python merge_appearance_cards.py          # 落盘（同步 .js）
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import Counter, defaultdict

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
BOARD_JSON = BOARDS / "fashion_wardrobe.json"
BOARD_JS = BOARDS / "fashion_wardrobe.js"

AP = "appearance_extra"          # merged_from 标记：来自 player_appear_data 的外观补充卡


def load_board() -> dict:
    return json.loads(BOARD_JSON.read_text(encoding="utf-8"))


def save_board(d: dict) -> None:
    BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(d, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")


def is_ap(it: dict) -> bool:
    return it.get("merged_from") == AP


def main_card_for(ap: dict, mains: list) -> dict | None:
    """给外观卡找主卡：先按（名字+部位）精确，再按（名字+部位桶）。"""
    cand = [m for m in mains if m["name"] == ap["name"] and m.get("part") == ap.get("part")]
    if len(cand) == 1:
        return cand[0]
    bucket = ap.get("part_bucket") or []
    cand = [m for m in mains
            if m["name"] == ap["name"]
            and (ap.get("part") in (m.get("part_bucket") or [])
                 or (m.get("part") and m["part"] in bucket))]
    if len(cand) == 1:
        return cand[0]
    return None


def prefix_ok(main: dict, ap: dict) -> bool:
    """短编号必须是长编号的前缀（3732 → 3732001），否则视作不同款，不合。"""
    m = main.get("model_id")
    if m is None:
        return True
    return any(str(x).startswith(str(m)) for x in (ap.get("model_ids") or []))


def merge_one(main: dict, ap: dict) -> None:
    longs = [x for x in (ap.get("model_ids") or []) if isinstance(x, int)]
    ids = list(main.get("model_ids") or ([main["model_id"]] if main.get("model_id") is not None else []))
    for x in longs:
        if x not in ids:
            ids.append(x)
    main["model_ids"] = ids

    refs = list(main.get("model_refs") or [])
    for x in longs:
        if x not in refs:
            refs.append(x)
    if refs:
        main["model_refs"] = refs

    prov = ap.get("provenance") or {}
    rec = main.get("appearance_merge") or {"ids": [], "parts": [], "row_keys": []}
    rec["ids"].append(ap["id"])
    if ap.get("part") and ap["part"] not in rec["parts"]:
        rec["parts"].append(ap["part"])
    for rk in (ap.get("row_keys") or []):
        if rk not in rec["row_keys"]:
            rec["row_keys"].append(rk)
    rec["table"] = prov.get("table") or rec.get("table")
    rec["source_id"] = prov.get("source_id") or rec.get("source_id")
    rec["model_ids"] = refs
    main["appearance_merge"] = rec

    # 图：主卡没有、外观卡有时搬过来（同 base 不重复）
    mi = (main.get("_media") or {})
    ai = (ap.get("_media") or {})
    have = {str(x.get("png") or "") for x in (mi.get("images") or [])}
    haveb = {str(x.get("base") or "") for x in (mi.get("images") or [])}
    add = [x for x in (ai.get("images") or [])
           if x.get("png") and x["png"] not in have
           and pathlib.Path(WEB / x["png"]).is_file()
           and x.get("base") not in haveb]
    if add:
        mi.setdefault("images", []).extend(add)
        mi["total"] = len(mi["images"])
        main["_media"] = mi
        main["icon_count"] = len(mi["images"])
        main["icon_state"] = "有图"

    # 外观卡标了性别缺口、主卡没有时继承（别把已知缺口弄丢）
    if ai.get("missing") and not mi.get("missing"):
        mi["missing"] = ai["missing"]
        main["_media"] = mi

    main["card_kind"] = main.get("card_kind") or "fashion"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    d = load_board()
    items = d["items"]
    aps = [it for it in items if is_ap(it)]
    mains = [it for it in items if not is_ap(it)]
    stat = Counter()
    pairs = []

    for it in aps:
        m = main_card_for(it, mains)
        if not m:
            stat["找不到主卡"] += 1
            continue
        if not prefix_ok(m, it):
            stat["编号前缀不符"] += 1
            continue
        pairs.append((m, it))

    # 同一张主卡可能接多张外观卡（三周年纪念：头饰 + 衣服）
    by_main = {}          # main_id → (主卡, [外观卡])
    for m, it in pairs:
        by_main.setdefault(m["id"], (m, []))[1].append(it)

    for m, lst in by_main.values():
        for it in lst:
            if not a.dry:
                merge_one(m, it)
            stat["合并卡"] += 1
        print("%-16s %-14s 并入 %d 张：%s" % (
            m["id"], m["name"], len(lst),
            ", ".join("%s(%s→%s)" % (x["id"], x.get("part"), x.get("model_ids")) for x in lst)))

    gone = {x["id"] for _m, lst in by_main.values() for x in lst}
    if gone and not a.dry:
        d["items"] = [x for x in items if x["id"] not in gone]
        merged_away = d.get("merged_away") or []
        for it in items:
            if it["id"] in gone:
                merged_away.append({
                    "id": it["id"], "name": it["name"], "part": it.get("part"),
                    "model_ids": it.get("model_ids"),
                    "provenance": it.get("provenance"),
                    "into": next(m["id"] for m, lst in by_main.values() if it in lst),
                })
        d["merged_away"] = merged_away
        d["meta"]["merged_appearance_cards"] = len(merged_away)
        st = d["meta"].get("state_summary") or {}
        st["有图"] = sum(1 for x in d["items"] if x.get("icon_state") == "有图")
        st["无图"] = len(d["items"]) - st["有图"]
        d["meta"]["state_summary"] = st
        if isinstance(d["meta"].get("rebuild"), dict):
            d["meta"]["rebuild"]["cards"] = len(d["items"])
        d["meta"]["join_policy"] = (d["meta"].get("join_policy") or "") + \
            "；同名同部位的外观补充卡（player_appear_data，长编号）并入时装主卡，编号双写（model_ids / model_refs）"
        note = ("\n\n【外观补充卡合并（2026-10-29）】\n"
                "同名同部位的外观补充卡（player_appear_data，长编号 model 如 3732001）已并入时装主卡"
                "（fashion_data，短编号 3732 + 魅力值），共 %d 张：%s。\n"
                "主卡 model_ids / model_refs 同时保留短编号与外观编号，卡面显示「model 3732 · 3732001」"
                "（多编号时 +N，悬停看全部）；技术详情新增「外观编号」「合并来源」两栏；"
                "被并条目完整存于顶层 merged_away，可回滚。\n"
                "注：本段以上计数为 2026-10-24 重建时的快照，此后增删以 state_summary 为准。") % (
                    len(gone), "、".join(sorted({x["name"] for _m, lst in by_main.values() for x in lst})))
        d["meta"]["notes"] = (d["meta"].get("notes") or "") + note

    print("=== 结果 ===")
    for k, v in stat.most_common():
        print("  %-12s %4d" % (k, v))
    print("  cards %d → %d" % (len(items), len(items) - len(gone)))
    if a.dry:
        print("（dry-run，未写盘）")
    else:
        save_board(d)
        print("已写回", BOARD_JSON.name, "与", BOARD_JS.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
