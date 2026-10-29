# -*- coding: utf-8 -*-
"""（三）载具板深挖 · 第二期回填：描述 / 特技 / 氮气 / 生命量 / 改装等级。

2026-10-30。依赖第一期 build_vehicle_params.py 已回填的 params（魅力值 + 速度/加速度），
本脚本在其之上追加，不覆盖第一期字段。

数据源（冻结产物 + 还原树，只读）
--------------------------------
  · 01_索引与产物/30_分析/载具深挖_20261030/vehicle_lore.json
      （提取器 03_执行/vehicle_lore_extract.py）
      - vehicle_ui_data            desc 载具描述（277/277 行全有）
      - vehicle_modding_function_conf_data  特技 116 行，81 行带 ref_vehicle_id
      - vehicle_modding_data       载具 → 改装等级 → func（11 行，0x0b 基址 28）
      - vehicle_garage_function_conf_data  车库功能 16 行（血量+ / 氮气上限+）
  · 01_索引与产物/30_分析/载具深挖_20261029/vehicle_core_classic.json
      （第一期冻结产物）max_nitrogen / acc_cost_nitrogen_per_second / restore_nitrogen_per_second …

回填字段
--------
  it.desc              载具描述（覆盖式补齐，空则不覆盖）
  it.brand_name        品牌系列（空则补）
  it.perks[]           特技：{name, desc, level, type, icon, via}（按 vehicle_ids 归并去重）
  it.modding_levels[]  改装等级 → 解锁特技（仅 11 辆车有，confidence=inferred）
  it.params.nitrogen   氮气全套
  it.params.health     生命量（UI 条 + 等级曲线 + 车库加成）
  meta.lore_meta       数据源、统计、口径声明

★ 口径声明
  · 车库加成（血量 +50 / 氮气上限 +500）为**全局功能**，非逐车配置，
    故挂在 params.nitrogen.garage_limit_bonus / params.health.garage_hp_bonus，
    数值取自 vehicle_garage_function_conf_data.func_desc 文本「#F(1)50」标记位
    （params 字段是 jump 组，帧族未解，故以游戏内显示的文本为准）。
  · 特技归属以 func.ref_vehicle_id 为准（显式字段）；vehicle_modding_data 的
    行↔块配平未经逐行自证，产物标 confidence="inferred"，仅作等级信息展示。

只读源；写 data/boards/vehicle_full.{json,js}。

用法（统一入口）
  python la.py vehicle build --only lore
或直接跑（等效，需 venv python；须先跑过第一期 build_vehicle_params）
  python tools/build_vehicle_lore.py [--root DIR] [--lore FILE] [--board FILE] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import defaultdict

# 项目根自动推断：本文件位于 <项目根>/02_wiki/web/tools/ 下
ROOT_DEFAULT = pathlib.Path(__file__).resolve().parents[3]

WEB = ROOT_DEFAULT / "02_wiki/web"
BOARD = WEB / "data/boards/vehicle_full.json"
LORE = ROOT_DEFAULT / "01_索引与产物/30_分析/载具深挖_20261030/vehicle_lore.json"
FROZEN1 = ROOT_DEFAULT / "01_索引与产物/30_分析/载具深挖_20261029"


def configure(root: pathlib.Path, lore: str | None = None,
              board: str | None = None) -> None:
    """按 CLI 参数落定路径（项目可整体搬迁，不依赖硬编码盘符）。"""
    global WEB, BOARD, LORE, FROZEN1
    root = root.resolve()
    WEB = root / "02_wiki/web"
    LORE = pathlib.Path(lore) if lore else root / "01_索引与产物/30_分析/载具深挖_20261030/vehicle_lore.json"
    BOARD = pathlib.Path(board) if board else WEB / "data/boards/vehicle_full.json"
    FROZEN1 = root / "01_索引与产物/30_分析/载具深挖_20261029"

# 氮气字段（all_equips 载具行 → 展示名）
NITRO_KEYS = [
    ("max_nitrogen", "max_nitrogen", "氮气容量上限（0 = 该载具无氮气）"),
    ("acc_cost_nitrogen_per_second", "cost_per_second", "加速时每秒消耗"),
    ("restore_nitrogen_per_second", "restore_per_second", "每秒自动回复"),
    ("in_navi_save_acc_cost_nitrogen_ratio", "navi_save_ratio", "导航状态消耗折扣"),
    ("nitrogen_phase_ratio", "phase_ratio", "氮气阶段系数"),
    ("nitrogen_air_impulse", "air_impulse", "空中氮气冲量"),
    ("impulse_ratio", "impulse_ratio", "冲量系数"),
]

# 车库功能：从 func_desc 的「#F(1)<数值>」标记位取加成
GARAGE_HP_RE = re.compile(r"血量增加#F\(1\)(\d+)")
GARAGE_NITRO_RE = re.compile(r"氮气容量上限提升#F\(1\)(\d+)")


def rnd(x, nd=3):
    return round(x, nd) if isinstance(x, float) else x


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="build_vehicle_lore",
        description="载具板回填 第二期：描述 / 特技 / 氮气 / 生命量 / 改装等级",
    )
    ap.add_argument("--root", default=str(ROOT_DEFAULT),
                    help="项目根（默认：从脚本所在位置推断，可整体搬迁）")
    ap.add_argument("--lore", default=None,
                    help="第二期冻结产物（默认 <root>/01_索引与产物/30_分析/载具深挖_20261030/vehicle_lore.json）")
    ap.add_argument("--board", default=None,
                    help="板数据文件（默认 <root>/02_wiki/web/data/boards/vehicle_full.json）")
    ap.add_argument("--dry-run", action="store_true",
                    help="只算不写，打印将要产出的统计")
    a = ap.parse_args(argv)
    configure(pathlib.Path(a.root), a.lore, a.board)
    for label, p in (("冻结产物", LORE), ("板数据", BOARD)):
        if not p.is_file():
            print("%s不存在：%s" % (label, p))
            return 2
    print("项目根 %s ｜ 冻结 %s ｜ 板 %s" % (pathlib.Path(a.root).resolve(), LORE, BOARD))

    lore = json.loads(LORE.read_text(encoding="utf-8"))
    ui = lore["ui"]
    perks_by_vehicle = lore.get("perks_by_vehicle") or {}
    tags_by_vehicle = lore.get("tags_by_vehicle") or {}
    vmod = lore.get("vehicle_modding") or {}
    garage_funcs = lore.get("garage_funcs") or {}

    # 第一期 core（经典服主口径）→ 氮气原值
    core = {r["key"]: r for r in
            json.loads((FROZEN1 / "vehicle_core_classic.json").read_text(encoding="utf-8"))["rows"]}

    # 车库加成（全局，非逐车）
    garage_hp_bonus = garage_nitro_bonus = None
    for _k, gf in garage_funcs.items():
        t = str(gf.get("func_desc") or "")
        m = GARAGE_HP_RE.search(t)
        if m:
            garage_hp_bonus = int(m.group(1))
        m = GARAGE_NITRO_RE.search(t)
        if m:
            garage_nitro_bonus = int(m.group(1))

    # vehicle_modding_data：块内 (level, func_id) → 按 func.ref_vehicle_id 归到载具
    # ★ 不用行序配平：实测按行序配平会把「古典绅士」串进「月舞风华」卡（2026-10-30 修正）。
    #   改用 func.ref_vehicle_id 反查，与 perks 口径一致，是表内显式字段。
    modding_by_vehicle: dict[str, list] = defaultdict(list)
    func_by_id = lore.get("func") or {}
    for b in vmod.get("blocks") or []:
        for lv in (b.get("levels") or []):
            fid = str(lv.get("func_id"))
            ref = (func_by_id.get(fid) or {}).get("ref_vehicle_id")
            if not ref:
                continue
            modding_by_vehicle[str(ref)].append({
                "level": lv.get("level"),
                "func_id": lv.get("func_id"),
                "func_name": lv.get("func_name"),
                "func_desc": lv.get("func_desc"),
            })

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    stats = {
        "cards": len(items),
        "cards_with_desc": 0,
        "cards_with_perks": 0,
        "cards_with_tags": 0,
        "cards_with_nitrogen": 0,
        "cards_with_health": 0,
        "cards_with_modding_levels": 0,
        "cards_with_ui_display": 0,
        "perk_total": 0,
        "perk_kinds": defaultdict(int),
    }

    for it in items:
        vids = [str(x) for x in (it.get("vehicle_ids")
                                 or ([it["vehicle_id"]] if it.get("vehicle_id") is not None else []))]

        # ---- 描述 / 品牌 -------------------------------------------------
        for vid in vids:
            row = ui.get(vid)
            if not row:
                continue
            if row.get("desc") and not it.get("desc"):
                it["desc"] = row["desc"]
            if row.get("brand_name") and not it.get("brand_name"):
                it["brand_name"] = row["brand_name"]
            break
        if it.get("desc"):
            stats["cards_with_desc"] += 1

        # ---- 特技（ref_vehicle_id 显式归属）------------------------------
        seen, perks = set(), []
        for vid in vids:
            for p in perks_by_vehicle.get(vid) or []:
                key = (p.get("func_id"), p.get("name"), p.get("desc"))
                if key in seen:
                    continue
                seen.add(key)
                rec = dict(p)
                rec["via"] = vid
                perks.append(rec)
                stats["perk_kinds"][p.get("name") or p.get("desc") or "?"] += 1
        if perks:
            it["perks"] = perks
            stats["cards_with_perks"] += 1
            stats["perk_total"] += len(perks)
        else:
            it.pop("perks", None)

        # ---- 特技标签（vehicle_ui_data.vehicle_garage_tags 跳转列表 → vehicle_tags_data）----
        # ★ 口径（2026-10-30 夜 用户纠错结案）：特技标签真实来源是 vehicle_garage_tags 跳转列表，
        #   跳转偏移加共享常量池基址 B=2716（全局一致性暴力搜唯一解，269/269 命中）。
        #   ★ 旧口径「special_function 位掩码 bit i→标签 i+1」是错的（曾错配天蝎座=水陆两栖/和平使者）。
        #   例：天蝎座 193031 → [1,4,10] = 电能驱动/智能导航/氮气漂浮。
        #   与 funcs（vehicle_modding_function_conf_data.ref_vehicle_id，改装专属功能）区分。
        seen_t, tags = set(), []
        for vid in vids:
            for t in tags_by_vehicle.get(vid) or []:
                key = (t.get("tag_id"), t.get("name"))
                if key in seen_t:
                    continue
                seen_t.add(key)
                tags.append({
                    "tag_id": t.get("tag_id"),
                    "name": t.get("name"),
                    "desc": t.get("desc"),
                    "icon": t.get("icon"),
                    "level": t.get("level"),
                })
        if tags:
            it["tags"] = tags
            stats["cards_with_tags"] += 1
        else:
            it.pop("tags", None)

        # ---- 改装等级（仅 11 辆车，inferred）-----------------------------
        lv, seen_lv = [], set()
        for vid in vids:
            for x in modding_by_vehicle.get(vid) or []:
                # 同一外观在多个部件组各有一份（如 func 20 与 24 都是「古典绅士-粉黛」），
                # 卡面按 等级+名称+描述 展示 → 以此去重，避免同条目重复出现
                key = (x.get("level"), x.get("func_name"), x.get("func_desc"))
                if key in seen_lv:
                    continue
                seen_lv.add(key)
                lv.append(x)
        if lv:
            it["modding_levels"] = sorted(lv, key=lambda x: (x.get("level") or 0))
            stats["cards_with_modding_levels"] += 1
        else:
            it.pop("modding_levels", None)

        # ---- 官方 UI 展示值：以 vehicle_ui_data 为唯一权威口径 -----------
        # ★ 校准依据（2026-10-30 游戏内「天蝎座」193031 面板实测）：
        #     速度 125(+15) / 加速度 140(+10) / 生命 352 / 氮气 2000
        #   四项与 vehicle_ui_data 193031 行逐项吻合；生命 352 = vehicle_attr_data
        #   attr_id 13 的 hp 曲线 lv8 值（面板按当前等级取，非固定值）。
        # ★ 为什么不用 all_equips：其 ui_acc 仅 25/258 行有值、ui_health 全无，
        #   且 32 辆车的 ui_speed 与 vehicle_ui_data 不一致。表名与覆盖率都表明
        #   vehicle_ui_data 才是游戏面板直接读取的表 → 覆盖式写入，不留旧口径。
        uirow = None
        for vid in vids:
            if ui.get(vid):
                uirow = ui[vid]
                break
        if uirow:
            for src in ("ui_speed", "ui_acc", "ui_health"):
                if uirow.get(src) is not None:
                    it[src] = rnd(uirow[src])
            stats["cards_with_ui_display"] += 1

        # ---- 氮气 / 生命量（挂到 params）---------------------------------
        cv = None
        for vid in vids:
            r = core.get(int(vid)) if vid.isdigit() else None
            if r is not None:
                cv = r["raw_values"]
                break
        p = it.get("params")
        if p is None:
            p = it["params"] = {}
        if cv is not None:
            # 只收数值；jump:xxxx 是未解指针，不入板（避免把指针串当参数展示）
            nit = {out: rnd(cv.get(src)) for src, out, _d in NITRO_KEYS
                   if cv.get(src) is not None and not isinstance(cv.get(src), str)}
            # UI 氮气加成（vehicle_ui_data）
            for vid in vids:
                row = ui.get(vid)
                if row:
                    if row.get("ui_nitrogen_acc_addition") is not None:
                        nit["ui_acc_addition"] = rnd(row["ui_nitrogen_acc_addition"])
                    if row.get("ui_nitrogen_speed_addition") is not None:
                        nit["ui_speed_addition"] = rnd(row["ui_nitrogen_speed_addition"])
                    break
            if garage_nitro_bonus is not None:
                nit["garage_limit_bonus"] = garage_nitro_bonus
            if nit:
                p["nitrogen"] = nit
                if nit.get("max_nitrogen"):
                    stats["cards_with_nitrogen"] += 1

            hp = {}
            if cv.get("ui_health") is not None:
                hp["ui_health"] = rnd(cv["ui_health"])
            if it.get("ui_health") is not None and "ui_health" not in hp:
                hp["ui_health"] = rnd(it["ui_health"])
            ab = p.get("attr") or {}
            if ab.get("hp_curve"):
                hp["hp_curve"] = ab["hp_curve"]
                hp["levels_total"] = ab.get("levels_total")
            if garage_hp_bonus is not None:
                hp["garage_hp_bonus"] = garage_hp_bonus
            if hp:
                p["health"] = hp
                stats["cards_with_health"] += 1
        # 同步顶层 ui_health，便于排序/筛选复用
        if p.get("health", {}).get("ui_health") is not None and it.get("ui_health") is None:
            it["ui_health"] = p["health"]["ui_health"]

    # ---- meta ------------------------------------------------------------
    meta = board.setdefault("meta", {})
    meta["lore_meta"] = {
        "generated": "2026-10-30",
        "extractor": "03_执行/vehicle_lore_extract.py",
        "backfiller": "02_wiki/web/tools/build_vehicle_lore.py",
        "frozen_input": str(LORE).replace("\\", "/"),
        "sources": {
            "desc": "vehicle_ui_data.desc（277/277 行全有）",
            "perks": "vehicle_modding_function_conf_data（116 行，81 行带 ref_vehicle_id）",
            "tags": "vehicle_ui_data.vehicle_garage_tags 跳转列表 → vehicle_tags_data"
                    "（跳转基址 B=2716 全局一致性暴力搜唯一解，269/269 命中 0 无效）",
            "nitrogen": "all_equips 载具行 max_nitrogen / acc_cost_nitrogen_per_second / "
                        "restore_nitrogen_per_second + vehicle_ui_data 氮气加成",
            "health": "vehicle_attr_data 等级曲线（按等级取 hp）+ 车库功能加成",
            "modding_levels": "vehicle_modding_data（11 行，0x0b 指针基址 28）",
            "ui_display": "★ 权威口径 = vehicle_ui_data（ui_speed / ui_acc / ui_health / "
                          "ui_nitrogen_*_addition），覆盖 277/277 行；"
                          "已覆盖第一期从 all_equips 取的 ui_* 值",
        },
        "official_calibration": {
            "date": "2026-10-30",
            "sample": "天蝎座 193031（游戏内载具面板截图）",
            "official_panel": {
                "速度": "125（氮气 +15）",
                "加速度": "140（氮气 +10）",
                "生命值": "352",
                "氮气储量": "2000",
            },
            "matched_fields": {
                "速度": "vehicle_ui_data.ui_speed = 125（一致）",
                "加速度": "vehicle_ui_data.ui_acc = 140（一致）",
                "速度氮气加成": "vehicle_ui_data.ui_nitrogen_speed_addition = 15（一致）",
                "加速度氮气加成": "vehicle_ui_data.ui_nitrogen_acc_addition = 10（一致）",
                "生命值": "vehicle_attr_data attr_id=13 hp 曲线 lv8 = 352（面板按当前等级取值）",
                "氮气储量": "all_equips.max_nitrogen = 2000（一致）",
            },
            "conclusion": "游戏面板四项全部来自 vehicle_ui_data + attr 曲线，"
                          "与 vehicle_proto_data 的物理量（top_speed 355.2 / acc 2618.7）不同量纲，"
                          "物理值不得当作面板速度展示",
        },
        "ptr_base": {
            "vehicle_modding_data": (vmod.get("jump_base")),
            "vehicle_garage_tags": 2716,
        },
        "caveats": [
            "车库加成（血量 +50 / 氮气上限 +500）是全局功能，非逐车配置，对所有生效载具同样适用",
            "车库加成数值取自 func_desc 文本「#F(1)<n>」标记位（params 字段为未解帧族）",
            "vehicle_modding_data 的行↔块归属无法自证（按行序配平会把古典绅士串进月舞风华，已弃用）"
            "→ 改装等级改用 func.ref_vehicle_id 反查，与特技同口径",
            "特技归属以 ref_vehicle_id 为准；同系列子型号共享主型号特技时 via 显示来源编号",
            "特技标签（it.tags）来自 vehicle_ui_data.vehicle_garage_tags 跳转列表（基址 2716），"
            "与 funcs（改装专属功能）区分；天蝎座 193031 → 电能驱动/智能导航/氮气漂浮。"
            "★ 旧口径「special_function 位掩码」是错的，已废弃（曾错配水陆两栖/和平使者）",
        ],
        "stats": {
            "cards": stats["cards"],
            "cards_with_desc": stats["cards_with_desc"],
            "cards_with_perks": stats["cards_with_perks"],
            "cards_with_tags": stats["cards_with_tags"],
            "cards_with_nitrogen": stats["cards_with_nitrogen"],
            "cards_with_health": stats["cards_with_health"],
            "cards_with_modding_levels": stats["cards_with_modding_levels"],
            "cards_with_ui_display": stats["cards_with_ui_display"],
            "perk_total": stats["perk_total"],
            "perk_kinds": dict(sorted(stats["perk_kinds"].items(), key=lambda x: -x[1])),
            "garage_hp_bonus": garage_hp_bonus,
            "garage_nitro_bonus": garage_nitro_bonus,
        },
    }

    print("回填统计：", json.dumps(meta["lore_meta"]["stats"], ensure_ascii=False)[:600])
    if a.dry_run:
        print("[dry-run] 已算完，未写盘")
        return 0
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    # .js 用紧凑分隔（与第一期回填器保持一致，避免两期轮流改写导致文件无谓抖动）
    (WEB / "data/boards/vehicle_full.js").write_text(
        "window.WIKI_BOARD_vehicle_full = " + json.dumps(board, ensure_ascii=False,
                                                         separators=(",", ":")) + ";\n",
        encoding="utf-8")
    print("wrote", BOARD)
    return 0


if __name__ == "__main__":
    sys.exit(main())
