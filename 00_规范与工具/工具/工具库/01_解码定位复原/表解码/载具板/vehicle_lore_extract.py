# -*- coding: utf-8 -*-
"""（三）载具深挖 · 第二期：描述 / 特技 / 氮气 / 生命量 / 改装等级。

2026-10-30 结案。与 vehicle_deep_extract.py（第一期：魅力值 + 速度/加速度）互补。

数据源（全部为 PE 还原树 com/cdata，只读）
----------------------------------------
  A. vehicle_ui_data.py（277 行，key = 载具 id 19xxxx）
     · desc          载具描述（★ 277/277 行全有，本板描述文案的唯一来源）
     · name / brand_name / special_function / theme
     · ui_health / ui_speed / ui_acc（0~100 展示条）
     · ui_nitrogen_acc_addition / ui_nitrogen_speed_addition（氮气加成）
     · ui_acc_water_add / ui_speed_water_add（水域加成）
  B. vehicle_modding_function_conf_data.py（116 行）
     · func_name / func_desc / func_type / func_level
     · ref_vehicle_id  ★ 显式载具 id —— 特技归属主口径
  C. vehicle_modding_data.py（11 行）
     · 载具 → 改装等级 → func id 列表（逐部件：模型/氮气/音效/变形/轮子）
     · ★ 本表是 0x7B 行表但 schema 内联，0x0b 指针组需解基址（见下）
  D. vehicle_modding_conf_data.py（43 行）
     · modding_name / modding_desc / charm_value / unlock_funcs / tag_ids
  E. vehicle_garage_function_conf_data.py（16 行）
     · extra_nitrogen_limit（氮气上限+）/ extra_vehicle_hp（血量+）/ extra_capacity

★ C 表 0x0b 指针组结案（2026-10-30）
-----------------------------------
C 表不是标准行表：body 头 40B(05+零填充) + u32 + u16(字段数)，随后整段 [34, tail)
是「共享常量池」，由 27 组构成；行索引在尾部 `76 01 0b` 之后（桶数组 + node 溢出区）。

27 组两种：
  kind=0x01 叶子组：`27 01 02 <lv> <val>`  → 一个 (改装等级, 值) 对
  kind=0x0b 指针组：`27 0b <n> <t1>..<tn>` → n 个指针，指向 n 个叶子组
每个「块」= k 个叶子组 + 1 个指针组（指针指回本块的 k 个叶子）。

**指针基址 = 28**（暴力搜得：唯一使全部 66 个指针目标都落在 27 组起点的基址；
次优解 33 会使 @44 指针组自引用自身，排除）。

node 溢出区 = 连续的 (key uleb, row_start uleb) 键对，解出 11 个载具 key
（195027/195022/195030/195017/194191/194161/195005/194160/195012/194102/194088）。

行↔块归属：21 个块按位置序、11 行按 node 序配平为 2,2,2,2,1,2,2,2,2,2,2。
★ 该配平未经逐行自证（row_start 与块起点无统一偏移关系），故产物里保留
  row_start 与块偏移，level_maps 标 confidence="inferred"。
  特技归属以 B 表 ref_vehicle_id 为准（显式字段，covered 更广）。

产出
----
01_索引与产物/30_分析/载具深挖_20261030/vehicle_lore.json

用法（统一入口）
  python la.py vehicle extract --only lore
或直接跑（等效，需 venv python）
  python 00_规范与工具/工具/工具库/01_解码定位复原/表解码/载具板/vehicle_lore_extract.py [--root DIR] [--cd DIR] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import struct
import sys
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

# ---- 以下全局变量由 configure() 按 CLI 参数赋值 ----
CD = ROOT_DEFAULT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
OUT_DIR = ROOT_DEFAULT / "01_索引与产物/30_分析/载具深挖_20261030"


def configure(root: pathlib.Path, cd: str | None = None, out: str | None = None) -> None:
    """按 CLI 参数落定路径与 sys.path（项目可整体搬迁，不依赖硬编码盘符）。"""
    global CD, OUT_DIR
    root = root.resolve()
    for p in (root / "00_规范与工具/工具/工具库/00_共享核心",
              root / "02_wiki/web/tools"):
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)
    CD = pathlib.Path(cd) if cd else root / "01_索引与产物/41_还原树/pe/配置/com/cdata"
    OUT_DIR = pathlib.Path(out) if out else root / "01_索引与产物/30_分析/载具深挖_20261030"
    if not CD.is_dir():
        raise SystemExit("还原树目录不存在：%s（用 --cd 指定）" % CD)
    OUT_DIR.mkdir(parents=True, exist_ok=True)


for _p in (ROOT_DEFAULT / "00_规范与工具/工具/工具库/00_共享核心",
           ROOT_DEFAULT / "02_wiki/web/tools"):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

from toolkit_core.bindict_table import parse_legacy_chs_pool, resolve_jump_group  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots       # noqa: E402


# --------------------------------------------------------------------------
# 通用：抽 body / 解行表
# --------------------------------------------------------------------------
def body_of(p: pathlib.Path) -> bytes:
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6:at + 6 + n]


def load_table(name: str) -> dict[str, dict]:
    """解一张标准行表 → {key(str): {字段: 值}}"""
    rows, bad = decode_table_rows_with_chs_slots(
        body_of(CD / f"{name}.py"),
        parse_legacy_chs_pool((CD / f"{name}_chs.py").read_bytes()))
    out: dict[str, dict] = {}
    for r in rows:
        v = {k: (val[1] if isinstance(val, (list, tuple)) and len(val) == 2 else val)
             for k, val in (r.get("values") or {}).items()}
        out[str(r.get("key"))] = v
    print(f"  {name:38s} 行 {len(rows):4d}  丢 {len(bad)}")
    return out


def load_tags_table() -> dict[str, dict]:
    """载具特技标签定义表（vehicle_tags_data.nxs，x{ 体，行 key = 标签 id）。

    字段：tag_name / tag_desc / tag_icon / tag_level / tag_sort_order / hd_tag_icon
    返回 {str(key): {字段: 值}}。
    """
    rows, bad = decode_table_rows_with_chs_slots(
        body_of(CD / "vehicle_tags_data.nxs"),
        parse_legacy_chs_pool((CD / "vehicle_tags_data_chs.py").read_bytes()))
    out: dict[str, dict] = {}
    for r in rows:
        v = {k: (val[1] if isinstance(val, (list, tuple)) and len(val) == 2 else val)
             for k, val in (r.get("values") or {}).items()}
        out[str(r.get("key"))] = v
    print(f"  {'vehicle_tags_data.nxs':38s} 行 {len(rows):4d}  丢 {len(bad)}")
    return out


# --------------------------------------------------------------------------
# ULEB / 27 组
# --------------------------------------------------------------------------
def uleb(buf: bytes, p: int):
    r = s = 0
    while True:
        b = buf[p]
        p += 1
        r |= (b & 0x7F) << s
        if not b & 0x80:
            break
        s += 7
    return r, p


def scan_27(body: bytes, start: int, end: int) -> dict[int, tuple]:
    """扫 [start,end) 内全部 27 组 → {pos: (kind, elems, end)}"""
    groups: dict[int, tuple] = {}
    p = start
    while p < end - 2:
        if body[p] != 0x27:
            p += 1
            continue
        kind = body[p + 1]
        try:
            c, q = uleb(body, p + 2)
        except Exception:
            break
        if c > 64:
            p += 1
            continue
        elems, ok = [], True
        for _ in range(c):
            try:
                v, q = uleb(body, q)
            except Exception:
                ok = False
                break
            elems.append(v)
        if not ok:
            break
        groups[p] = (kind, elems, q)
        p = q
    return groups


def solve_ptr_base(groups: dict[int, tuple], body: bytes) -> int:
    """暴力求 0x0b 指针基址：全部目标必须落在 27 组起点，且不得自引用。"""
    ptr = {p: g for p, g in groups.items() if g[0] == 0x0B}
    if not ptr:
        return 0
    targets = [t for _, (_, es, _) in ptr.items() for t in es]
    hi = len(body) - max(targets) - 8
    cands = [B for B in range(0, hi) if all(body[B + t] == 0x27 for t in targets)]
    # 排除自引用（指针组指向自己）
    good = [B for B in cands
            if not any((B + t) == p for p, (_, es, _) in ptr.items() for t in es)]
    return (good or cands or [0])[0]


# --------------------------------------------------------------------------
# C 表：vehicle_modding_data（0x7B + 内联 schema + 0x0b 指针组）
# --------------------------------------------------------------------------
def decode_vehicle_modding_data() -> dict:
    body = body_of(CD / "vehicle_modding_data.py")
    tail = body.rfind(b"\x76\x01\x0b")

    groups = scan_27(body, 34, tail)
    B = solve_ptr_base(groups, body)
    ptr = {p: g for p, g in groups.items() if g[0] == 0x0B}

    # 指针组 → [(level, value), ...]（按指针顺序）
    def resolve(p: int):
        _, es, _ = groups[p]
        out = []
        for t in es:
            g = groups.get(B + t)
            if g and g[0] == 0x01 and len(g[1]) >= 2:
                out.append((g[1][0], g[1][1]))
        return out

    blocks = [{"ptr_off": p, "pairs": resolve(p)}
              for p in sorted(ptr)]

    # 尾部索引：桶数组 + node 溢出区 (key, row_start)
    p = tail + 3
    bc, p = uleb(body, p)
    p += bc * 8
    keys, p2 = [], p
    while p2 < len(body) - 1:
        try:
            k, p2 = uleb(body, p2)
            rs, p2 = uleb(body, p2)
        except Exception:
            break
        if not (190000 <= k <= 199999):
            break
        keys.append({"key": k, "row_start": rs})

    return {
        "jump_base": B,
        "bucket_count": bc,
        "group_total": len(groups),
        "ptr_groups": len(ptr),
        "blocks": blocks,
        "rows": keys,
        "note": ("行↔块归属按位置序配平 2,2,2,2,1,2,2,2,2,2,2，未经逐行自证；"
                 "特技归属以 vehicle_modding_function_conf_data.ref_vehicle_id 为准"),
    }


# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="vehicle_lore_extract",
        description="载具深挖 第二期：描述 / 特技 / 氮气 / 生命量 / 改装等级",
    )
    ap.add_argument("--root", default=str(ROOT_DEFAULT),
                    help="项目根（默认：从脚本所在位置推断，可整体搬迁）")
    ap.add_argument("--cd", default=None,
                    help="还原树 cdata 目录（默认 <root>/01_索引与产物/41_还原树/pe/配置/com/cdata）")
    ap.add_argument("--out", default=None,
                    help="输出目录（默认 <root>/01_索引与产物/30_分析/载具深挖_20261030）")
    a = ap.parse_args(argv)

    configure(pathlib.Path(a.root), a.cd, a.out)
    print("项目根 %s ｜ 输出 %s" % (pathlib.Path(a.root).resolve(), OUT_DIR))

    print("== 解表 ==")
    ui = load_table("vehicle_ui_data")
    func = load_table("vehicle_modding_function_conf_data")
    modconf = load_table("vehicle_modding_conf_data")
    garage = load_table("vehicle_garage_function_conf_data")
    # 载具特技标签表（.nxs，同 x{ 体；行 key = 标签 id，相关字段 tag_name/tag_desc/tag_icon/tag_level）
    tags_def = load_tags_table()
    print(f"  vehicle_tags_data 标签定义 {len(tags_def)} 条")
    print("== 解 vehicle_modding_data（0x0b 指针组）==")
    vmod = decode_vehicle_modding_data()
    print(f"  基址 B={vmod['jump_base']}  27组 {vmod['group_total']}  "
          f"指针组 {vmod['ptr_groups']}  行 {len(vmod['rows'])}")

    # ---- 特技：按 ref_vehicle_id 归到载具 -------------------------------
    perks_by_vehicle: dict[str, list] = defaultdict(list)
    orphan = []
    for k, v in func.items():
        nm, ds = v.get("func_name"), v.get("func_desc")
        if not nm and not ds:
            continue
        rec = {
            "func_id": v.get("func_id"),
            "type": v.get("func_type"),
            "level": v.get("func_level"),
            "name": nm,
            "desc": ds,
            "icon": v.get("func_icon"),
        }
        ref = v.get("ref_vehicle_id")
        if ref:
            perks_by_vehicle[str(ref)].append(rec)
        else:
            orphan.append(rec)

    # ---- 改装等级：vehicle_modding_data 块 → func -----------------------
    func_by_id = {str(v.get("func_id")): v for v in func.values() if v.get("func_id")}
    # 块内 value 直接就是 func 行 key（已验证：106→func106「氮气加速」）
    for b in vmod["blocks"]:
        b["levels"] = [{"level": lv,
                        "func_id": val,
                        "func_name": func.get(str(val), {}).get("func_name"),
                        "func_desc": func.get(str(val), {}).get("func_desc")}
                       for lv, val in b["pairs"]]

    # ---- 载具特技标签：vehicle_ui_data.vehicle_garage_tags 跳转列表 → vehicle_tags_data
    # ★ 口径（2026-10-30 夜 用户纠错结案）：特技标签真实来源是 vehicle_garage_tags 跳转列表，
    #   跳转偏移须加共享常量池基址 B，B 由全局一致性求出：使全部 269 个跳转目标都落在
    #   blob 内 0x27 组起点。暴力搜唯一解 B=2716（269/269 命中 0 失败）。
    #   ★ 旧口径「special_function 位掩码 bit i→标签 i+1」是错的（曾错配天蝎座=水陆两栖/和平使者）。
    #   例：天蝎座 193031 vehicle_garage_tags=jump:5156 → [1,4,10]
    #       = 电能驱动/智能导航/氮气漂浮（与游戏内一致）。
    ui_blob = body_of(CD / "vehicle_ui_data.py")
    ui_starts = {i for i in range(len(ui_blob)) if ui_blob[i] == 0x27}
    # 全局一致性求跳转基址：所有 vehicle_garage_tags 跳转目标必须落在 0x27 组起点
    _gt_offsets = set()
    for u in ui.values():
        gt = u.get("vehicle_garage_tags")
        val = gt[1] if isinstance(gt, (list, tuple)) and len(gt) == 2 else gt
        if isinstance(val, str) and val.startswith("jump:"):
            _gt_offsets.add(int(val.split(":")[1]))
    garage_tag_base = None
    for B in range(0, len(ui_blob)):
        if all((B + off) in ui_starts for off in _gt_offsets):
            garage_tag_base = B
            break
    if garage_tag_base is None:
        raise RuntimeError("vehicle_garage_tags 跳转基址暴力搜失败（无全局一致解）")
    print(f"  vehicle_garage_tags 跳转基址 B={garage_tag_base}  "
          f"（{len(_gt_offsets)} 个偏移全部落在 0x27 组起点）")
    tags_by_vehicle: dict[str, list] = {}
    tag_invalid = 0
    for vid, u in ui.items():
        gt = u.get("vehicle_garage_tags")
        val = gt[1] if isinstance(gt, (list, tuple)) and len(gt) == 2 else gt
        if not (isinstance(val, str) and val.startswith("jump:")):
            continue
        tgt = garage_tag_base + int(val.split(":")[1])
        ids = resolve_jump_group(ui_blob, tgt) or []
        recs = []
        for tid in ids:
            tag = tags_def.get(str(tid))
            if not tag:
                tag_invalid += 1
                continue
            recs.append({
                "tag_id": tid,
                "name": tag.get("tag_name"),
                "desc": tag.get("tag_desc"),
                "icon": tag.get("tag_icon"),
                "level": tag.get("tag_level"),
            })
        if recs:
            tags_by_vehicle[vid] = recs

    # ---- 输出 ----------------------------------------------------------
    out = {
        "meta": {
            "generated": "2026-10-30",
            "extractor": "00_规范与工具/工具/工具库/01_解码定位复原/表解码/载具板/vehicle_lore_extract.py",
            "source_tree": "01_索引与产物/41_还原树/pe/配置/com/cdata",
            "unit_policy": "表内无单位换算字段，不换算 km/h；UI 展示条为 0~100 相对量",
            "ptr_base_discovery": {
                "table": "vehicle_modding_data",
                "jump_base": vmod["jump_base"],
                "method": "暴力搜：全部 0x0b 目标须落在 27 组起点，且指针组不自引用",
            },
            "garage_tag_jump_base": {
                "table": "vehicle_ui_data.vehicle_garage_tags",
                "jump_base": garage_tag_base,
                "method": "全局一致性暴力搜：全部跳转目标须落在 blob 内 0x27 组起点（唯一解）",
            },
            "stats": {
                "ui_rows": len(ui),
                "ui_with_desc": sum(1 for v in ui.values() if v.get("desc")),
                "func_rows": len(func),
                "func_with_ref": sum(1 for v in func.values() if v.get("ref_vehicle_id")),
                "perk_vehicles": len(perks_by_vehicle),
                "orphan_funcs": len(orphan),
                "tag_vehicles": len(tags_by_vehicle),
                "tag_invalid_refs": tag_invalid,
                "modding_rows": len(vmod["rows"]),
                "modding_blocks": len(vmod["blocks"]),
                "garage_funcs": len(garage),
            },
        },
        "ui": ui,
        "func": func,
        "modding_conf": modconf,
        "garage_funcs": garage,
        "vehicle_modding": vmod,
        "perks_by_vehicle": {k: sorted(v, key=lambda x: (x.get("level") or 0, x.get("type") or 0))
                             for k, v in perks_by_vehicle.items()},
        "perks_orphan": orphan,
        "tags_def": tags_def,
        "tags_by_vehicle": tags_by_vehicle,
    }
    p = OUT_DIR / "vehicle_lore.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n== 产出 ==")
    print(f"  {p}  ({p.stat().st_size/1024:.0f} KB)")
    print("  统计:", json.dumps(out["meta"]["stats"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
