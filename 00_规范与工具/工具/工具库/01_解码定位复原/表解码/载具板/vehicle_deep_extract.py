# -*- coding: utf-8 -*-
"""载具深挖：all_equips 载具行全字段 + vehicle_proto_data 物理参数 join。

背景（2026-10-29）
----------------
（三）载具板（vehicle_full）现只有 vehicle_ui_data 的 UI 展示值（ui_speed/ui_acc/ui_health，
均为 0~100 的条状展示分），没有魅力值、也没有真实加速度/最大速度。
经查：
  * 载具本体行在 all_equips（193000~196999 段），字段含 charm_value / proto_id /
    ui_speed / ui_acc / ui_health / nitrogen_max_speed_addition /
    nitrogen_acceleration_addition / highway_road_*_addition / water_speed_ratio …
    但既有 all_equips_full_extract.py 只保留了 key/name/equip_type/weapon_type/attrs，
    载具行 attrs 为空 → 整类数据被漏掉。
  * 真实物理参数在还原树 com/cdata/vehicle_proto_data.py（86 行，proto_id 主键）：
    acc（驱动力相关加速度参数）/ top_speed（最大速度）/ driving_force / frictional_force /
    C_Mass（质量）/ …（PhysX 车辆组件全套）。
  * 载具等级属性在 vehicle_attr_data.py（attr_id+level → hp / car_rate / explode_rate /
    min_hurt_speed / max_hurt_speed / player_rate / hurt_reduction_rate）。
  * 改装魅力在 vehicle_modding_conf_data.py（modding 等级 → charm_value）。

数据源（沿用 2026-10-29 结案的 node 索引法与已冻结 fid）
  经典服 base : 01_索引与产物/源包/apk_20261002/mumu_5.0.679/assets/script.py314.lc.npk
                fid 1F8E9684E1B97CE0 行表 + 94AB0B3FD057EF01 池
  简单生存 kj1: 01_索引与产物/源包/pe_20261020/script.py314.lc.npk
                fid 3D123F2BEE73ED47 + 9B6BE39D902BD6D6
  悠客服   yk : 同上包 fid 5790A7683EB6AAA8 + D1D2E03CF2901EBC
  物理/改装/等级表：01_索引与产物/41_还原树/pe/配置/com/cdata/*.py（PE 测试服还原树）

输出：01_索引与产物/30_分析/载具深挖_20261029/
  vehicle_core_{classic,kj1,yk}.json   每服载具行全字段（含魅力值/原型 id/UI 值）
  vehicle_proto_physics.json           还原树 vehicle_proto_data 物理参数
  vehicle_attr_levels.json             还原树 vehicle_attr_data 等级属性
  vehicle_modding_charm.json           还原树 vehicle_modding_conf_data 改装魅力

用法（统一入口）
  python la.py vehicle extract --only deep
或直接跑（等效，需 venv python）
  python 00_规范与工具/工具/工具库/01_解码定位复原/表解码/载具板/vehicle_deep_extract.py [--root DIR] [--cd DIR] [--out DIR] [--server classic|kj1|yk]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import struct
import sys

# 项目根自动推断：向上找带 00_规范与工具/{治理,工具} 标记的目录
# （脚本已收编进 工具库/01_解码定位复原/表解码/载具板/，位置可挪，不数层级）
def _find_project_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for up in here.parents:
        if (up / "00_规范与工具/治理").is_dir() and (up / "00_规范与工具/工具").is_dir():
            return up
    return here.parents[6]  # 兜底：载具板/ 本文件向上 6 层 = 项目根

ROOT_DEFAULT = _find_project_root()

# ---- 以下全局变量由 configure() 按 CLI 参数赋值 ----
PROJ = ROOT_DEFAULT
PACK_APK = PACK_PE20 = OUT_DIR = CD = None  # type: ignore[assignment]

TABLE_FIDS = {
    "classic": {
        "pack": "APK", "fid_rows": "1F8E9684E1B97CE0", "fid_pool": "94AB0B3FD057EF01",
        "label": "经典服 all_equips_data（apk_20261002 安装基线）",
        "server": "经典服", "channel": "base",
    },
    "kj1": {
        "pack": "PE20", "fid_rows": "3D123F2BEE73ED47", "fid_pool": "9B6BE39D902BD6D6",
        "label": "简单生存服 oversea_data_kj1（pe_20261020 快照）",
        "server": "简单生存服", "channel": "kj1",
    },
    "yk": {
        "pack": "PE20", "fid_rows": "5790A7683EB6AAA8", "fid_pool": "D1D2E03CF2901EBC",
        "label": "悠客服 oversea_data_yk（pe_20261020 快照）",
        "server": "悠客服", "channel": "yk",
    },
}


def configure(root: pathlib.Path, cd: str | None = None, out: str | None = None) -> None:
    """按 CLI 参数落定路径与 sys.path（项目可整体搬迁，不依赖硬编码盘符）。"""
    global PROJ, PACK_APK, PACK_PE20, OUT_DIR, CD
    PROJ = root.resolve()
    for p in (
        PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描",
        PROJ / "00_规范与工具/工具/工具库/00_共享核心",
        PROJ / "02_wiki/web/tools",
    ):
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)
    PACK_APK = PROJ / "01_索引与产物/源包/apk_20261002/mumu_5.0.679/assets/script.py314.lc.npk"
    PACK_PE20 = PROJ / "01_索引与产物/源包/pe_20261020/script.py314.lc.npk"
    CD = pathlib.Path(cd) if cd else PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
    OUT_DIR = pathlib.Path(out) if out else PROJ / "01_索引与产物/30_分析/载具深挖_20261029"
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def tables() -> dict:
    """构造分服配置（须在 configure() 之后调用）。"""
    packs = {"APK": PACK_APK, "PE20": PACK_PE20}
    return {tag: dict(c, pack=packs[c["pack"]]) for tag, c in TABLE_FIDS.items()}


# ---- 工具库导入（依赖 configure() 之前的默认 sys.path；--root 指向别处时 configure 会前置补路）----
for _p in (
    ROOT_DEFAULT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描",
    ROOT_DEFAULT / "00_规范与工具/工具/工具库/00_共享核心",
    ROOT_DEFAULT / "02_wiki/web/tools",
):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

import la_unpack_core as L  # noqa: E402
from toolkit_core.bindict_table import (  # noqa: E402
    decode_table_rows, parse_legacy_chs_pool,
)
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

# 载具 id 段（vehicle_ui_data 实测 193000~196017）
VEH_MIN, VEH_MAX = 193000, 196999

# 关心的字段（其余字段仍全量保留在 raw_values）
FOCUS = [
    "name", "desc", "icon", "charm_value", "proto_id", "vehicle_equip_type",
    "vehicle_type", "ui_speed", "ui_acc", "ui_health",
    "nitrogen_max_speed_addition", "nitrogen_acceleration_addition",
    "highway_road_max_speed_addition", "highway_road_acceleration_addition",
    "water_speed_ratio", "max_hp_addition", "durability", "level",
    "sale_id", "price", "quality", "equip_type", "weapon_type",
]


def sections(raw: bytes):
    out, i = [], 0
    while i < len(raw) - 9:
        if raw[i] != 0x7B:
            i += 1
            continue
        bl = struct.unpack_from("<I", raw, i + 1)[0]
        if bl < 16 or i + 5 + bl > len(raw):
            i += 1
            continue
        cnt, res = struct.unpack_from("<II", raw, i + 5)
        if res == 0 and cnt < 200000 and 8 + 4 * cnt < bl:
            out.append((i, bl, cnt))
        i += 5 + bl
    return out


def uleb(b: bytes, p: int):
    r, s = 0, 0
    while True:
        x = b[p]
        p += 1
        r |= (x & 0x7F) << s
        if not x & 0x80:
            return r, p
        s += 7


def node_index(blob: bytes):
    de = struct.unpack_from("<I", blob, 0)[0]
    tail = blob[de:]
    if not (len(tail) >= 4 and tail[0] == 0x76 and tail[1] == 0x01 and tail[2] == 0x0B):
        raise ValueError("index tail head not 76 01 0b: %s" % tail[:4].hex())
    bc, p = uleb(tail, 3)
    arr_end = p + 8 * bc
    if arr_end > len(tail):
        raise ValueError("bucket array out of tail")
    pairs, q = [], arr_end
    while q < len(tail):
        k, q = uleb(tail, q)
        v, q = uleb(tail, q)
        pairs.append((k, v))
    return bc, pairs


def tree_body(name: str) -> bytes:
    raw = (CD / f"{name}.py").read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def tree_pool(name: str):
    p = CD / f"{name}_chs.py"
    if not p.exists():
        return []
    try:
        return parse_legacy_chs_pool(p.read_bytes())
    except Exception:
        return []


def scalar(v):
    """取值：[(type, val)] → val；jump: 目标原样保留。"""
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return v[1]
    return v


def decode_tree_table(name: str):
    rows, bad = decode_table_rows_with_chs_slots(tree_body(name), tree_pool(name))
    out = {}
    for r in rows:
        vals = r.get("values") or {}
        out[r.get("key")] = {k: scalar(v) for k, v in vals.items()}
    return out, len(bad)


def extract(tag: str, cfg: dict) -> dict:
    a = L.NpkArchive(str(cfg["pack"]))
    got = {}
    for ent in a.iter_entries():
        fid = "%016X" % ent.file_id
        if fid in (cfg["fid_rows"], cfg["fid_pool"]):
            got[fid] = a.read_entry(entry_index=ent.entry_index)
    raw_rows, raw_pool = got[cfg["fid_rows"]], got[cfg["fid_pool"]]

    soff, sbl, scnt = sections(raw_rows)[0]
    body = raw_rows[soff + 5: soff + 5 + sbl]
    _bc, pairs = node_index(body[8 + 4 * scnt:])

    psoff, psbl, _pcnt = sections(raw_pool)[0]
    pool = parse_legacy_chs_pool(raw_pool[psoff: psoff + 5 + psbl])

    rows, unbound = decode_table_rows(body, pool, index_rows=pairs, lenient=True)

    veh = []
    for r in rows:
        k = r.get("key")
        if not (isinstance(k, int) and VEH_MIN <= k <= VEH_MAX):
            continue
        vals = r.get("values") or {}
        flat = {fk: scalar(fv) for fk, fv in vals.items()}
        if "charm_value" not in flat and "proto_id" not in flat and "ui_speed" not in flat:
            continue  # 非载具行（19 段里的武器/道具）剔除
        rec = {"key": k, "server": cfg["server"], "channel": cfg["channel"]}
        for f in FOCUS:
            if f in flat:
                rec[f] = flat[f]
        rec["raw_values"] = flat
        veh.append(rec)
    veh.sort(key=lambda x: x["key"])

    payload = {
        "meta": {
            "generated": "2026-10-29",
            "tag": tag,
            "label": cfg["label"],
            "server": cfg["server"],
            "channel": cfg["channel"],
            "source_package": str(cfg["pack"]).replace("\\", "/"),
            "rows_fid": cfg["fid_rows"],
            "pool_fid": cfg["fid_pool"],
            "decode": "node 索引法（2026-10-29 结案）+ lenient=True",
            "slots_declared": scnt,
            "rows_decoded": len(rows),
            "unbound": len(unbound),
            "vehicle_rows": len(veh),
        },
        "rows": veh,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    p = OUT_DIR / f"vehicle_core_{tag}.json"
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{tag}: 解码 {len(rows)} 行，载具行 {len(veh)} → {p}")
    return payload


PHYS_FIELDS = ["acc", "top_speed", "driving_force", "frictional_force", "C_Mass",
               "C_MOI", "C_LinearDamping", "C_AngularDamping", "DDE_PeakTorque",
               "DDE_MaxOmega", "DG_FinalRatio", "KS_AccelRiseRate", "KS_BrakeRiseRate",
               "SR_Speed", "SR_SteerRatio", "DC_Strength"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="vehicle_deep_extract",
        description="载具深挖 第一期：all_equips 载具行全字段 + vehicle_proto_data 物理参数",
    )
    ap.add_argument("--root", default=str(ROOT_DEFAULT),
                    help="项目根（默认：从脚本所在位置推断，可整体搬迁）")
    ap.add_argument("--cd", default=None,
                    help="还原树 cdata 目录（默认 <root>/01_索引与产物/41_还原树/pe/配置/com/cdata）")
    ap.add_argument("--out", default=None,
                    help="输出目录（默认 <root>/01_索引与产物/30_分析/载具深挖_20261029）")
    ap.add_argument("--server", action="append", choices=sorted(TABLE_FIDS),
                    help="只跑指定分服，可重复传；默认 classic/kj1/yk 全跑")
    a = ap.parse_args(argv)

    configure(pathlib.Path(a.root), a.cd, a.out)
    tbl = tables()
    sel = a.server or sorted(TABLE_FIDS)
    missing = [t for t in sel if not tbl[t]["pack"].is_file()]
    if missing:
        print("源包缺失：%s" % ", ".join("%s→%s" % (t, tbl[t]["pack"]) for t in missing))
        print("  先确认 01_索引与产物/源包/ 下的 apk_20261002 与 pe_20261020 快照")
        return 2
    print("项目根 %s ｜ 输出 %s ｜ 分服 %s" % (PROJ, OUT_DIR, "/".join(sel)))

    cores = {t: extract(t, tbl[t]) for t in sel}

    # ---- 还原树物理参数 ----
    proto, pbad = decode_tree_table("vehicle_proto_data")
    phys = {}
    for k, v in proto.items():
        phys[k] = {f: v.get(f) for f in PHYS_FIELDS if f in v}
    (OUT_DIR / "vehicle_proto_physics.json").write_text(json.dumps({
        "meta": {"source": "41_还原树/pe/配置/com/cdata/vehicle_proto_data.py",
                 "rows": len(proto), "unbound": pbad,
                 "fields": PHYS_FIELDS,
                 "note": "PhysX 车辆组件参数；acc=加速度参数，top_speed=最大速度（引擎单位 cm/s 量级）"},
        "rows": phys,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("vehicle_proto_data 物理参数:", len(phys), "行")

    # ---- 等级属性 ----
    attr, abad = decode_tree_table("vehicle_attr_data")
    (OUT_DIR / "vehicle_attr_levels.json").write_text(json.dumps({
        "meta": {"source": "41_还原树/pe/配置/com/cdata/vehicle_attr_data.py",
                 "rows": len(attr), "unbound": abad,
                 "note": "行主键=level；attr_id 分组。hp/car_rate/explode_rate/min_max_hurt_speed/player_rate"},
        "rows": attr,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("vehicle_attr_data:", len(attr), "行")

    # ---- 改装魅力 ----
    mod, mbad = decode_tree_table("vehicle_modding_conf_data")
    charm = {k: v.get("charm_value") for k, v in mod.items() if "charm_value" in v}
    (OUT_DIR / "vehicle_modding_charm.json").write_text(json.dumps({
        "meta": {"source": "41_还原树/pe/配置/com/cdata/vehicle_modding_conf_data.py",
                 "rows": len(mod), "with_charm": len(charm),
                 "note": "改装等级 → charm_value（魅力值）"},
        "rows": mod,
        "charm_by_level": charm,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("vehicle_modding_conf_data:", len(mod), "行，含魅力", len(charm))

    # ---- 车库等级魅力门槛 ----
    gu, gbad = decode_tree_table("vehicle_garage_upgrade_conf_data")
    (OUT_DIR / "vehicle_garage_levels.json").write_text(json.dumps({
        "meta": {"source": "41_还原树/pe/配置/com/cdata/vehicle_garage_upgrade_conf_data.py",
                 "rows": len(gu), "unbound": gbad,
                 "note": "车库等级 → need_charm_value（魅力门槛）"},
        "rows": gu,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("vehicle_garage_upgrade_conf_data:", len(gu), "行")

    # ---- 汇总 ----
    summ = {}
    for t, c in cores.items():
        rows = c["rows"]
        summ[t] = {
            "server": c["meta"]["server"],
            "vehicle_rows": len(rows),
            "with_charm": sum(1 for r in rows if r.get("charm_value") is not None),
            "with_proto": sum(1 for r in rows if r.get("proto_id") is not None),
            "with_ui_speed": sum(1 for r in rows if r.get("ui_speed") is not None),
            "with_ui_acc": sum(1 for r in rows if r.get("ui_acc") is not None),
            "with_nitrogen": sum(1 for r in rows if r.get("nitrogen_max_speed_addition") is not None),
            "proto_hit_physics": sum(1 for r in rows
                                     if r.get("proto_id") in phys),
        }
    (OUT_DIR / "_summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
    print(json.dumps(summ, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
