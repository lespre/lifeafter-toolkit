# -*- coding: utf-8 -*-
"""（三）载具板深挖回填：魅力值 / 加速度 / 最大速度 / 加分项 / 等级属性。

背景（2026-10-29）
----------------
原 vehicle_full 板只用了 vehicle_ui_data（PE 测试服还原树）：卡面只有
ui_speed / ui_acc / ui_health 三个 UI 展示条（0~100 量级），既没有魅力值，
也没有真实加速度/最大速度。

本次新增数据源（两路，互不混用、逐条记 provenance）：
  A. 载具本体行 = all_equips（193000~196999 段）
     · 经典服 base : 源包 apk_20261002 安装基线（fid 1F8E9684E1B97CE0 / 94AB0B3FD057EF01）
     · 简单生存 kj1: 源包 pe_20261020（fid 3D123F2BEE73ED47 / 9B6BE39D902BD6D6）
     · 会员专享 yk : 源包 pe_20261020（fid 5790A7683EB6AAA8 / D1D2E03CF2901EBC）
     提取器：工具库/01_解码定位复原/表解码/载具板/vehicle_deep_extract.py
     冻结产物：01_索引与产物/30_分析/载具深挖_20261029/vehicle_core_*.json
     字段：charm_value / proto_id / navi_speed / navi_acc / navi_dec / navi_turn /
           field_navi_speed / ui_speed / ui_acc / nitrogen_*_addition /
           highway_road_*_addition / water_speed_ratio / attr_id / …
  B. 物理与阶梯（还原树 com/cdata，PE 测试服）
     · vehicle_proto_data.py  proto_id → acc / top_speed / driving_force /
       frictional_force / C_Mass（PhysX 车辆组件）
       ★ 已验证：acc == (driving_force − frictional_force) / C_Mass（逐行吻合）
     · vehicle_attr_data.py   attr_id + level → hp / car_rate / explode_rate /
       min_hurt_speed / max_hurt_speed / player_rate
     · vehicle_basic_conf.py  全局上限：max_speed=250 / max_acc=250 / ui_speed_ratio=0.7
     · vehicle_garage_upgrade_conf_data.py  车库等级 → need_charm_value
     · vehicle_modding_conf_data.py  改装等级 → charm_value

单位口径（诚实声明）
  · navi_speed / navi_acc 与全局 max_speed 250 同一量纲（引擎速度单位）
  · proto.top_speed / acc 为 PhysX 车辆组件内部量（top_speed 与 DDE_MaxOmega 成正比）
  · 表内没有给出单位换算字段，本板不换算成 km/h，只给原值 + 相对全局上限的百分比

只读源；写 data/boards/vehicle_full.{json,js}。

用法（统一入口）
  python la.py vehicle build --only params
或直接跑（等效，需 venv python）
  python 00_规范与工具/工具/工具库/01_解码定位复原/表解码/载具板/build_vehicle_params.py [--root DIR] [--frozen DIR] [--board FILE] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import defaultdict

# 项目根自动推断：向上找带 00_规范与工具/{治理,工具} 标记的目录
# （脚本已收编进 工具库/01_解码定位复原/表解码/载具板/，位置可挪，不数层级）
def _find_project_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for up in here.parents:
        if (up / "00_规范与工具/治理").is_dir() and (up / "00_规范与工具/工具").is_dir():
            return up
    return here.parents[6]  # 兜底：载具板/ 本文件向上 6 层 = 项目根

ROOT_DEFAULT = _find_project_root()

WEB = ROOT_DEFAULT / "02_wiki/web"
FROZEN = ROOT_DEFAULT / "01_索引与产物/30_分析/载具深挖_20261029"
BOARD = WEB / "data/boards/vehicle_full.json"


def configure(root: pathlib.Path, frozen: str | None = None,
              board: str | None = None) -> None:
    """按 CLI 参数落定路径（项目可整体搬迁，不依赖硬编码盘符）。"""
    global WEB, FROZEN, BOARD
    root = root.resolve()
    WEB = root / "02_wiki/web"
    FROZEN = pathlib.Path(frozen) if frozen else root / "01_索引与产物/30_分析/载具深挖_20261029"
    BOARD = pathlib.Path(board) if board else WEB / "data/boards/vehicle_full.json"

# 官方服名（server_types 表口径）：base=通用/经典服，kj1=简单生存，yk=会员专享（月卡服）
SERVERS = [
    ("classic", "经典服"),
    ("yk", "会员专享（月卡服）"),
    ("kj1", "简单生存服"),
]
CANON = "classic"  # 主口径服

PHYS_KEYS = [
    ("acc", "acc", "净加速度 acc =(driving_force−frictional_force)/C_Mass"),
    ("top_speed", "top_speed", "物理极速 top_speed（与 DDE_MaxOmega 成正比）"),
    ("driving_force", "driving_force", "驱动力"),
    ("frictional_force", "frictional_force", "摩擦阻力"),
    ("C_Mass", "mass", "质量 C_Mass"),
    ("DDE_PeakTorque", "peak_torque", "峰值扭矩"),
    ("DDE_MaxOmega", "max_omega", "引擎最高角速度"),
    ("DG_FinalRatio", "final_ratio", "主减速比"),
    ("KS_AccelRiseRate", "accel_rise", "油门上升速率"),
    ("KS_BrakeRiseRate", "brake_rise", "刹车上升速率"),
]


def load(name: str):
    return json.loads((FROZEN / name).read_text(encoding="utf-8"))


def rnd(x, nd=3):
    if isinstance(x, float):
        return round(x, nd)
    return x


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="build_vehicle_params",
        description="载具板回填 第一期：魅力值 / 加速度 / 最大速度 / 等级属性",
    )
    ap.add_argument("--root", default=str(ROOT_DEFAULT),
                    help="项目根（默认：从脚本所在位置推断，可整体搬迁）")
    ap.add_argument("--frozen", default=None,
                    help="第一期冻结产物目录（默认 <root>/01_索引与产物/30_分析/载具深挖_20261029）")
    ap.add_argument("--board", default=None,
                    help="板数据文件（默认 <root>/02_wiki/web/data/boards/vehicle_full.json）")
    ap.add_argument("--dry-run", action="store_true",
                    help="只算不写，打印将要产出的统计")
    a = ap.parse_args(argv)
    configure(pathlib.Path(a.root), a.frozen, a.board)
    if not BOARD.is_file():
        print("板数据不存在：", BOARD)
        return 2
    print("项目根 %s ｜ 冻结 %s ｜ 板 %s" % (pathlib.Path(a.root).resolve(), FROZEN, BOARD))

    cores = {t: {r["key"]: r for r in load(f"vehicle_core_{t}.json")["rows"]}
             for t, _lbl in SERVERS}
    phys = load("vehicle_proto_physics.json")["rows"]
    attr = load("vehicle_attr_levels.json")["rows"]
    garage = load("vehicle_garage_levels.json")["rows"]
    mod = load("vehicle_modding_charm.json")

    # attr_id → 按 level 升序的 [(level, hp, car_rate, explode_rate, min_h, max_h)]
    attr_curve: dict[int, list] = defaultdict(list)
    for _k, v in attr.items():
        aid = v.get("attr_id")
        if aid is None or v.get("level") is None:
            continue
        attr_curve[int(aid)].append((
            int(v["level"]), v.get("hp"), v.get("car_rate"), v.get("explode_rate"),
            v.get("min_hurt_speed"), v.get("max_hurt_speed"), v.get("player_rate"),
            v.get("hurt_reduction_rate"),
        ))
    for aid in attr_curve:
        attr_curve[aid].sort(key=lambda x: x[0])

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    meta = board.setdefault("meta", {})

    stats = {
        "cards": len(items),
        "cards_with_core_row": 0,
        "cards_with_charm": 0,
        "cards_with_proto": 0,
        "cards_with_proto_physics": 0,
        "cards_with_navi_speed": 0,
        "charm_values": defaultdict(int),
        "top_speed_min": None,
        "top_speed_max": None,
        "acc_min": None,
        "acc_max": None,
    }

    for it in items:
        vids = it.get("vehicle_ids") or ([it["vehicle_id"]] if it.get("vehicle_id") is not None else [])
        per_server = {}
        for tag, lbl in SERVERS:
            for vid in vids:
                r = cores[tag].get(vid)
                if r is not None:
                    per_server[lbl] = r
                    break
        if not per_server:
            it["params"] = None
            it["param_state"] = "all_equips 载具行无此编号（三服均无）"
            it["charm_value"] = None
            continue

        stats["cards_with_core_row"] += 1
        canon_row = per_server.get(dict(SERVERS)[CANON])
        src_lbl = dict(SERVERS)[CANON] if canon_row else next(iter(per_server))
        src = canon_row or per_server[src_lbl]
        v = src["raw_values"]

        charm = v.get("charm_value")
        charm_by_server = {lbl: (per_server[lbl]["raw_values"].get("charm_value") if lbl in per_server else None)
                           for _t, lbl in SERVERS}
        distinct = {c for c in charm_by_server.values() if c is not None}
        charm_note = None
        if len(distinct) > 1:
            charm_note = "分服不一致：" + " / ".join(
                f"{lbl} {charm_by_server[lbl]}" for _t, lbl in SERVERS
                if charm_by_server.get(lbl) is not None)

        proto_id = v.get("proto_id")
        p = phys.get(str(proto_id)) if proto_id is not None else None
        proto = None
        if p:
            proto = {out: rnd(p.get(src_key)) for src_key, out, _d in PHYS_KEYS if p.get(src_key) is not None}
            stats["cards_with_proto_physics"] += 1
            ts, ac = proto.get("top_speed"), proto.get("acc")
            if ts is not None:
                stats["top_speed_min"] = ts if stats["top_speed_min"] is None else min(stats["top_speed_min"], ts)
                stats["top_speed_max"] = ts if stats["top_speed_max"] is None else max(stats["top_speed_max"], ts)
            if ac is not None:
                stats["acc_min"] = ac if stats["acc_min"] is None else min(stats["acc_min"], ac)
                stats["acc_max"] = ac if stats["acc_max"] is None else max(stats["acc_max"], ac)
        if proto_id is not None:
            stats["cards_with_proto"] += 1

        def g(k):
            return rnd(v.get(k))

        navi = {k: g(k) for k in ("navi_speed", "navi_acc", "navi_dec", "navi_turn", "field_navi_speed")}
        if navi.get("navi_speed") is not None:
            stats["cards_with_navi_speed"] += 1
        adds = {k: g(k) for k in ("nitrogen_max_speed_addition", "nitrogen_acceleration_addition",
                                  "highway_road_max_speed_addition", "highway_road_acceleration_addition",
                                  "water_speed_ratio")}
        ui = {k: g(k) for k in ("ui_speed", "ui_acc", "ui_health")}

        aid = v.get("attr_id")
        curve = attr_curve.get(int(aid)) if aid is not None else None
        attr_block = None
        if curve:
            # ★ 完整 hp 曲线（每级 [level, hp]），不做降采样——
            #   游戏面板「生命」按载具当前等级取值（如天蝎座 lv8=352），
            #   降采样会丢失中间级；全量存储让任意等级都可查。
            attr_block = {
                "attr_id": int(aid),
                "levels_total": len(curve),
                "car_rate": curve[0][2],
                "explode_rate": curve[0][3],
                "min_hurt_speed": curve[0][4],
                "max_hurt_speed": curve[0][5],
                "player_rate": curve[0][6],
                "hp_curve": [[lv, hp] for lv, hp, *_ in curve],
            }

        it["charm_value"] = charm
        it["charm_by_server"] = charm_by_server
        if charm_note:
            it["charm_note"] = charm_note
        if charm is not None:
            stats["cards_with_charm"] += 1
            stats["charm_values"][charm] += 1
        it["proto_id"] = proto_id
        it["params"] = {
            "server": src_lbl,
            "servers_present": list(per_server.keys()),
            "proto_id": proto_id,
            "proto": proto,
            "navi": navi,
            "ui": ui,
            "adds": adds,
            "attr": attr_block,
            "raw_row_key": src["key"],
        }
        it["param_state"] = "已解出"

    # ---- meta ----
    caps = {
        "max_speed": 250, "max_acc": 250, "ui_speed_ratio": 0.7,
        "max_gasoline": 5000, "max_nitrogen": 10000.0,
        "source": "41_还原树/pe/配置/com/cdata/vehicle_basic_conf.py（0x56 单行字段字典，83 字段）",
        "note": "全局上限；navi_speed / navi_acc 与之同量纲。表内无单位换算字段，本板不换算 km/h。",
    }
    meta["params_meta"] = {
        "caps": caps,
        "charm_garage_ladder": [
            {"level": int(k), "need_charm_value": v.get("need_charm_value")}
            for k, v in sorted(garage.items(), key=lambda x: int(x[0]))
        ],
        "modding_charm_levels": sorted(
            {int(c) for c in mod["charm_by_level"].values() if isinstance(c, (int, float))}),
        "modding_note": "vehicle_modding_conf_data：改装等级 → charm_value（29/43 行带魅力值）；"
                        "载具↔改装等级的映射在 vehicle_modding_data 的 jump 组里（kind=0x0b 未解出），故只登记阶梯不做逐车归属。",
        "sources": [
            "all_equips 载具行（193000~196999）：charm_value / proto_id / navi_* / *_addition / attr_id",
            "41_还原树/pe/配置/com/cdata/vehicle_proto_data.py：acc / top_speed / driving_force / frictional_force / C_Mass",
            "41_还原树/pe/配置/com/cdata/vehicle_attr_data.py：attr_id+level → hp / car_rate / explode_rate / 撞击伤害速度区间",
            "41_还原树/pe/配置/com/cdata/vehicle_basic_conf.py：max_speed / max_acc / ui_speed_ratio",
            "41_还原树/pe/配置/com/cdata/vehicle_garage_upgrade_conf_data.py：车库等级 → need_charm_value",
            "41_还原树/pe/配置/com/cdata/vehicle_modding_conf_data.py：改装等级 → charm_value",
        ],
        "acc_formula": "acc == (driving_force − frictional_force) / C_Mass（vehicle_proto_data 逐行验证吻合）",
        "stats": {
            "cards": stats["cards"],
            "cards_with_core_row": stats["cards_with_core_row"],
            "cards_with_charm": stats["cards_with_charm"],
            "cards_with_proto": stats["cards_with_proto"],
            "cards_with_proto_physics": stats["cards_with_proto_physics"],
            "cards_with_navi_speed": stats["cards_with_navi_speed"],
            "charm_value_distribution": dict(sorted(stats["charm_values"].items(), key=lambda x: -x[1])),
            "top_speed_range": [stats["top_speed_min"], stats["top_speed_max"]],
            "acc_range": [stats["acc_min"], stats["acc_max"]],
        },
    }
    meta["generated"] = "2026-10-29"
    meta["source_server"] = (
        "PE 测试服 · 表 41_还原树/pe/配置/com/cdata（vehicle_ui_data.py、vehicle_brand_type_conf.py、"
        "vehicle_brand_data.py、vehicle_proto_data.py、vehicle_attr_data.py、vehicle_basic_conf.py）"
        " ＋ all_equips 载具行（经典服 apk_20261002 基线 / 简单生存 kj1 / 会员专享 yk，pe_20261020 快照）"
        " · 资源 41_还原树/pe/资源")
    # ★ 幂等追加：无条件拼接会让每次重跑都多一段 notes，产物噪声无界增长、
    #   幂等性永不成立（编排器 build_pipeline.py 重跑校验实测累积到 31 段 / 重复 8 次）。
    #   本脚本在工具库内、不能 import web/tools/notes_util.py，故内联等价实现。
    _note = ("2026-10-29 深挖回填：魅力值=all_equips.charm_value（分服分别登记，主口径经典服）；"
             "加速度=vehicle_proto_data.acc（=(驱动力−摩擦阻力)/质量）；"
             "最大速度=vehicle_proto_data.top_speed（物理极速）与 all_equips.navi_speed（巡航/导航速度，上限 250）双轨展示；"
             "氮气/公路加成、水中速度比、等级生命曲线一并入库。")
    _parts = [p for p in (meta.get("notes") or "").split(" ｜ ") if p.strip()]
    if _note not in _parts:
        _parts.append(_note)
        meta["notes"] = " ｜ ".join(_parts)

    print("卡片 %d｜有载具行 %d｜有魅力值 %d｜有 proto %d（命中物理表 %d）｜有巡航速度 %d"
          % (stats["cards"], stats["cards_with_core_row"], stats["cards_with_charm"],
             stats["cards_with_proto"], stats["cards_with_proto_physics"], stats["cards_with_navi_speed"]))
    print("魅力值分布:", dict(sorted(stats["charm_values"].items(), key=lambda x: -x[1])))
    print("top_speed 区间:", stats["top_speed_min"], "~", stats["top_speed_max"])
    print("acc 区间:", stats["acc_min"], "~", stats["acc_max"])

    if a.dry_run:
        print("[dry-run] 已算完，未写盘")
        return 0
    # 统一用 indent=1（与第二期回填器一致，保证 git diff 可读且两者不互相抖动格式）
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    js = WEB / "data/boards/vehicle_full.js"
    js.write_text("window.WIKI_BOARD_vehicle_full = " + json.dumps(board, ensure_ascii=False,
                                                                  separators=(",", ":")) + ";\n",
                  encoding="utf-8")
    print("wrote", BOARD)
    print("wrote", js)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
