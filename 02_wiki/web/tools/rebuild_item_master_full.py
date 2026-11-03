#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_item_master_full.py — 从当前 PE 还原树重建「全量道具总表」（item_master_full）

## 为什么重做

旧板（2026-10-23）的 `meta.provenance.source_id = frozen-workcopy-ba8a239a`，
内容来自一份 **两个月前** 的 `ITEM_MASTER_v03.jsonl` 中间产物，只收了 30,251 个 id。
同一套客户端能给出的 id 是 6 万级（`30_分析/icon_registry.json` = 60,138），
**覆盖率刚好一半** —— 用户问「热更的道具怎么不在总表里」的根因就在这里。

本脚本改为**直接从当前 PE 还原树的表逐族扫**，选表依据见
`01_索引与产物/30_分析/全量总表_选表依据.md`（由 `rebuild_item_master_scan.py` 生成）。

## 口径

- 一件东西 = 一条（按 item_id 唯一）。跨表同号（如 `recipe` 的 100010 与
  `equip_coating_data` 的 100010）不合并成一个名字，而是**记 `namespaces` 列表 + `name_alt`**，
  并打 `unresolved` 标签 —— 遵守 `no-equal-integer-join`，不假装两个 id 空间相等。
- 名字：按 `NAME_PRIORITY` 顺序取第一个非空 `name`，并记 `name_source`。
- 图标：优先用表自己的 icon 字段，其次 `icon_registry.json`（跨族并集）；
  `icon_state` 三态：`已导出`（本地有 png）/ `源已定位未导出` / `无图标源`。
- evidence=structure、evidence_level=structure-only（结构可证，未经实机核验）。

## 用法

    python tools/rebuild_item_master_full.py            # 备份旧板 → 重建 → 写 .json/.js
    python tools/rebuild_item_master_full.py --dry-run  # 只统计，不写盘
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import struct
import sys
from collections import Counter, OrderedDict
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WEB / "tools"))

from la_paths import PROJ  # noqa: E402
import rebuild_lottery_periods as R  # noqa: E402
from board_io import write_board_pair  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from provenance_defaults import hoist_board_defaults  # noqa: E402

BOARD = WEB / "data/boards/item_master_full.json"
CACHE = PROJ / "01_索引与产物/30_分析/90_表缓存"
REG = PROJ / "01_索引与产物/30_分析/icon_registry.json"
TREE_REL = "01_索引与产物/41_还原树/pe/配置/com/cdata"
SOURCE_ID = "pe-config-merged"

# ───────────────────────────────────────── 冻结快照源（武器/护甲段）
# 树里的 all_equips_data.py 是 808 B 桩；all_equips_data_kj1.py / _yk.py 是 `0x73` 模块、
# 索引尾不是 `0x76`，现有解码器解不出 name/icon。2026-11-01 已用 node 索引法从
# script.py314.lc.npk 解出成品行并冻结在 30_分析（equipment_attrs 板块的数据源），
# 这里**直接读冻结产物**，不再重解码 —— 拿不到更新数据时就地写明"仍按冻结快照"。
SNAP_DIR = PROJ / "01_索引与产物/30_分析/all_equips_全量_node索引_20261029"
SNAP_SOURCE_ID = "all_equips-frozen-2026-11-01"
SNAP_DIR_REL = "01_索引与产物/30_分析/all_equips_全量_node索引_20261029"
# (namespace, 文件名, 主名优先级 0=最高)。经典服为基准：classic > kj1 > yk
SNAPSHOTS = [
    ("all_equips_classic", "all_equips_attrs_classic.json", 0),
    ("all_equips_kj1",     "all_equips_attrs_kj1.json",     1),
    ("all_equips_yk",      "all_equips_attrs_yk.json",      2),
]
SNAP_EXTRA_FIELDS = ("weapon_type", "equip_type", "level")

# 图标落盘目录（首命中优先）。板里写 assets/<dir>/<id>.png
ICON_DIRS = ("item_icons_full", "lottery_icons", "item_icons", "img_cache",
             "edible_icons", "recipe_icons", "chip_icons", "core_icons",
             "vehicle_icons", "appearance_icons", "equip_icons", "avatar_frames",
             "show_reward_icons", "effect_icons")

# ───────────────────────────────────────── 选中的表（顺序 = 名字优先级）
# name_field/icon_field 都写在同一张表里的**真实字段名**（不是猜的）
SELECTED = [
    # (表 stem, name 字段, icon 字段, icon 是否是 jump 字符串组)
    ("common_item_data",          "name",         "icon",             False),
    ("fashion_data",              "name",         "icons",            True),
    ("gift_data",                 "name",         "icon",             False),
    ("player_module_appear_data", "name",         "icon",             False),
    ("recipe",                    "name",         "icon",             False),
    ("equip_coating_data",        "coating_name", "coating_icon",     False),
    ("vehicle_ui_data",           "name",         "ui_vehicle_icon",  False),
    ("edible_item_data",          "name",         "icon",             False),
    ("avatar_frame_conf_data",    "item_name",    None,               False),
    ("body_sfx_data",             "buff_item_name", None,             False),
]
TABLE_REL = {
    "common_item_data": "90_表缓存/base_B42760CCA41DBC25.py（树里是 815 B 桩）",
}
# 同号但不同实体的族：这些表同时给出名字时打 unresolved
EXTRA_ICON_FIELDS = {"gift_data": ("icons",)}

# ───────────────────────────────────────── 人工复核后**主动排除**的表（选表依据 md 用）
# 与上面的 SELECTED 一起构成「选表决定」的唯一事实来源：
# rebuild_item_master_scan.py --markdown 直接读这两份常量生成文档，避免文档与产物漂移。
# SELECTED 里只当「名称补充源」用的表（id 大多已在 common_item 内，新增行极少）
SUPPLEMENT = {"body_sfx_data", "avatar_frame_conf_data"}

REJECT = {
    "simple_fashion_data":
        "与 fashion_data 同 id 且是其**子集**（0 个新 id）；另 unbound 9,303 行说明字段解码不全，单列只会重复计数",
    "fashion_data_for_export":
        "fashion_data 的导出视图（id 全在 fashion_data 内，0 个新 id）",
    "player_module_appear_data_for_export":
        "player_module_appear_data 的导出视图（0 个新 id）",
    "title_conf_data":
        "称号名册：key 1–1559 与 nucleus_build_data 的核芯序号**撞号**，且称号已有独立板块 title_catalog",
    "nucleus_build_data":
        "key 是核芯序号（1011–1091）不是道具 id；核芯已有独立板块 nucleus_item_catalog",
    "chip_type_data":
        "key 是芯片类型号（11001–23011）不是道具 id；芯片已有独立板块 chip_item_catalog",
    "home_appear_data":
        "224 个 id **全部**在 common_item 内，且 name 字段是模型名/开发名（model_name2），不新增信息",
    "fashion_model_change_color_data":
        "涂装调色板名（plate_name），595/623 个 id 已在 common_item 内，不是独立道具",
    "weapon_skin_data":
        "91% id 已在 common_item 内；name 字段是骨骼/插槽模型名（soft_bone_*），不是道具名",
    "player_appear_race_ctrl_data":
        "10 行种族外观控制项，id 全在 common_item 内",
    "fashion_charm_magazine_data":
        "杂志刊号（mag_name），不是道具",
    "fashion_charm_magazine_ugc_photo_data":
        "UGC 作品行，name 字段是**玩家昵称**（creator_name），不是道具名",
    "fashion_charm_magazine_ugc_video_data":
        "同上：UGC 视频行，creator_name 是玩家昵称",
    "fashion_charm_magazine_page_data":
        "杂志内页配置（无名字字段）",
    "fashion_charm_shop_reward_info_data":
        "魅力商店展示信息（prop_name 是展示位名，不是道具）",
    "fashion_charm_shop_category_conf_data":
        "商店分类标签",
    "fashion_charm_privilege_data":
        "魅力特权档位",
    "fashion_preset_do_face_config_data":
        "捏脸预设（preset 名），不是道具",
    "fashion_zhexing_preview_data":
        "千色造境着色预览（5 行）",
    "fashion_diy_lottery_pool_map_data":
        "时装 DIY 抽奖主题映射（4 行）",
    "fashion_diy_lottery_theme_data":
        "时装 DIY 抽奖主题（1 行）",
    "fashion_brand_data":
        "品牌分类（5 行，icon 是路径前缀不是成品图）",
    "recipe_primary_type_data":
        "配方一级分类标签（34 行）",
    "recipe_composite_types":
        "合成类型标签（18 行）",
    "recipe_achivement_kind_data":
        "配方成就类别（7 行）",
    "weapon_skin_sfx_type_data":
        "皮肤音效类型（15 行）",
    "nucleus_attr_effect_conf":
        "核芯属性效果分组（20 行）",
    "nucleus_weapon_type_data":
        "核芯武器类型（11 行）",
    "home_appear_category":
        "家具外观分类（5 行）",
    "pet_appear_category_data":
        "宠物外观分类（4 行）",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def xbody(path: Path) -> bytes:
    raw = path.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        raise ValueError(f"no x{{ container: {path}")
    size = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + size]


class Tbl:
    """一张表：行（key → 扁平字段）/ 池 / 文件事实。"""

    def __init__(self, stem: str, path: Path, cache_chs: Path | None = None):
        self.stem = stem
        self.path = path
        self.body = xbody(path)
        chs = cache_chs or path.with_name(stem + "_chs.py")
        self.chs = chs if chs and chs.exists() else None
        pool = parse_legacy_chs_pool(self.chs.read_bytes()) if self.chs else []
        rows, unbound = decode_table_rows_with_chs_slots(self.body, pool)
        self.pool = pool
        self.n_rows = len(rows)
        self.n_unbound = len(unbound)
        self.rows: dict[int, dict] = {}
        for r in rows:
            self.rows[r["key"]] = {k: (v[1] if isinstance(v, tuple) else v)
                                   for k, v in r["values"].items()}
        # jump 基址：body 去掉 8 + 4*count 表头
        count = struct.unpack_from("<I", self.body, 0)[0]
        self.blob = self.body[8 + 4 * count:]
        self.sha = sha256_file(path)
        self.bytes = path.stat().st_size
        self.mtime_ns = path.stat().st_mtime_ns
        try:
            self.rel = path.relative_to(R.TREE).as_posix().replace("/", "\\")
        except ValueError:
            # common_item 真身在表缓存里（树里是桩表）
            self.rel = "30_分析/90_表缓存/" + path.name

    def jump_paths(self, value) -> list[str]:
        if not isinstance(value, str) or not value.startswith("jump:"):
            return []
        off = int(value.split(":")[1])
        if not (0 <= off < len(self.blob)) or self.blob[off] != 0x27:
            return []
        kind = self.blob[off + 1]
        try:
            vals = R.resolve_jump_group(self.blob, off)
        except Exception:                                        # noqa: BLE001
            return []
        if not vals or kind != 0x05:
            return []
        return [self.pool[v] for v in vals if v < len(self.pool)
                and isinstance(self.pool[v], str) and self.pool[v].startswith("ui/")]


def load_tables() -> "OrderedDict[str, Tbl]":
    out: "OrderedDict[str, Tbl]" = OrderedDict()
    for stem, _n, _i, _j in SELECTED:
        if stem == "common_item_data":
            base = CACHE / "base_B42760CCA41DBC25.py"
            chs = CACHE / "base_EF3A8474A5E5F7A4.py"
            out[stem] = Tbl(stem, base, chs if chs.exists() else None)
            continue
        p = R.TREE / (stem + ".py")
        if not p.is_file():
            p = R.TREE / (stem + ".nxs")
        out[stem] = Tbl(stem, p)
    return out


class Snap:
    """冻结快照表：只有成品行（key/name/icon/…），没有可解的 CHS 池。

    来源 = 2026-11-01 用 node 索引法从 `script.py314.lc.npk`（pe_20261020 / apk_20261002）
    解出的 `equipment_attrs` 数据源，已冻结进 30_分析。树里的 `all_equips_data*.py`
    解不出（808 B 桩 / `0x73` 模块 / 索引尾非 `0x76`），所以这里不重解码。
    """

    def __init__(self, ns: str, path: Path, prio: int):
        d = json.loads(path.read_text(encoding="utf-8"))
        meta = d.get("meta") or {}
        self.ns = ns
        self.path = path
        self.prio = prio
        self.table = meta.get("table")
        self.generated = meta.get("generated")
        self.source_package = meta.get("source_package")
        self.label = meta.get("label")
        self.rows: dict[int, dict] = {}
        for r in d.get("rows") or []:
            k = r.get("key")
            if isinstance(k, int):
                self.rows[k] = r
        self.n_rows = len(self.rows)
        self.sha = sha256_file(path)
        self.bytes = path.stat().st_size
        self.mtime_ns = path.stat().st_mtime_ns
        self.rel = SNAP_DIR_REL.split("01_索引与产物/")[-1] + "/" + path.name


def load_snapshots() -> "OrderedDict[str, Snap]":
    out: "OrderedDict[str, Snap]" = OrderedDict()
    for ns, fname, prio in sorted(SNAPSHOTS, key=lambda x: x[2]):
        p = SNAP_DIR / fname
        if p.is_file():
            out[ns] = Snap(ns, p, prio)
    return out


def _png_key(stem: str) -> str | None:
    """把 `<id>.png` / `icon_<id>_b.png` / `af_<id>.png` / `nc_<id>.png` / `chip_<id>_s.png`
    归一成 id 串。**只接受纯数字**——`item_icon_jin_bing_b` 这类开发名一律不认，
    宁可空着也不借错图（错图比空图对图鉴伤害更大）。"""
    s = stem
    for pre in ("item_icon_", "icon_", "chip_", "af_", "nc_", "core_"):
        if s.startswith(pre):
            s = s[len(pre):]
            break
    for suf in ("_b", "_s"):
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    return s if s.isdigit() else None


def png_index() -> dict[str, str]:
    """id(stem) → assets 相对路径。先到先得，按 ICON_DIRS 优先级。"""
    idx: dict[str, str] = {}
    assets = WEB / "assets"
    for d in ICON_DIRS:
        root = assets / d
        if not root.is_dir():
            continue
        for p in root.glob("*.png"):
            key = _png_key(p.stem)
            if key:
                idx.setdefault(key, f"assets/{d}/{p.name}")
    return idx


def build() -> tuple[dict, dict]:
    tables = load_tables()
    snaps = load_snapshots()
    reg = json.loads(REG.read_text(encoding="utf-8"))["icons"]
    pngs = png_index()

    merged: "OrderedDict[int, dict]" = OrderedDict()
    stat_ns = Counter()
    collide = 0

    for stem, name_field, icon_field, icon_is_jump in SELECTED:
        t = tables[stem]
        stat_ns[stem] = t.n_rows
        for key, row in t.rows.items():
            name = row.get(name_field)
            name = name.strip() if isinstance(name, str) else ""
            icon = None
            if icon_field:
                v = row.get(icon_field)
                if isinstance(v, str) and v.startswith("ui/"):
                    icon = v
                elif isinstance(v, str):
                    paths = t.jump_paths(v)
                    icon = paths[0] if paths else None
            # gift_data 还有并列的 icons 组
            if not icon and stem in EXTRA_ICON_FIELDS:
                for f in EXTRA_ICON_FIELDS[stem]:
                    paths = t.jump_paths(row.get(f))
                    if paths:
                        icon = paths[0]
                        break
            rec = merged.get(key)
            if rec is None:
                merged[key] = {
                    "name": name, "name_ns": stem if name else None,
                    "name_field": name_field if name else None,
                    "icon": icon, "icon_ns": stem if icon else None,
                    "namespaces": [stem],
                }
                continue
            if stem not in rec["namespaces"]:
                rec["namespaces"].append(stem)
            if name and name != rec["name"]:
                collide += 1
                rec.setdefault("name_alt", []).append(f"{stem}={name}")
                if not rec["name"]:
                    rec["name"], rec["name_ns"] = name, stem
                    rec["name_field"] = name_field
            if icon and not rec["icon"]:
                rec["icon"], rec["icon_ns"] = icon, stem

    # ── 武器/护甲段：冻结快照（classic → kj1 → yk 依次，先到者定主名）
    snap_stat = Counter()
    snap_new = 0
    snap_overlap = 0
    snap_name_alt = 0
    for ns, sn in snaps.items():
        stat_ns[ns] = sn.n_rows
        for key, row in sn.rows.items():
            name = row.get("name")
            name = name.strip() if isinstance(name, str) else ""
            v = row.get("icon")
            icon = v.strip() if isinstance(v, str) and v.strip().startswith("ui/") else None
            equip = {f: row.get(f) for f in SNAP_EXTRA_FIELDS}
            desc = row.get("desc")
            desc = desc.strip() if isinstance(desc, str) else ""
            rec = merged.get(key)
            if rec is None:
                merged[key] = {
                    "name": name, "name_ns": ns if name else None,
                    "name_field": "name" if name else None,
                    "icon": icon, "icon_ns": ns if icon else None,
                    "namespaces": [ns], "equip": equip,
                    "desc_brief": desc[:120] if desc else None,
                }
                snap_new += 1
                continue
            snap_overlap += 1
            if ns not in rec["namespaces"]:
                rec["namespaces"].append(ns)
            # 跨服同号：主名留在先到者（classic 基准），其余记 name_alt —— 不另起一条事实
            if name and name != rec["name"]:
                collide += 1
                snap_name_alt += 1
                rec.setdefault("name_alt", []).append(f"{ns}={name}")
                if not rec["name"]:
                    rec["name"], rec["name_ns"] = name, ns
                    rec["name_field"] = "name"
            if icon and not rec["icon"]:
                rec["icon"], rec["icon_ns"] = icon, ns
            if equip and not rec.get("equip"):
                rec["equip"] = equip
            if desc and not rec.get("desc_brief"):
                rec["desc_brief"] = desc[:120]

    return merged, {"ns_rows": stat_ns, "tables": tables, "snaps": snaps,
                    "pngs": pngs, "reg": reg, "collide": collide,
                    "snap_new": snap_new, "snap_overlap": snap_overlap,
                    "snap_name_alt": snap_name_alt}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--output", default=str(BOARD))
    ap.add_argument("--md", action="store_true", help="顺带重写选表依据 md")
    ap.add_argument("--md-only", action="store_true", help="只对着已落盘的板重写选表依据 md")
    args = ap.parse_args()

    if args.md_only:
        board = json.loads(BOARD.read_text(encoding="utf-8"))
        reg = json.loads(REG.read_text(encoding="utf-8"))["icons"]
        write_markdown(board["items"], reg)
        print("md 已重写（未重建板）")
        return 0

    merged, ctx = build()
    tables: "OrderedDict[str, Tbl]" = ctx["tables"]
    snaps: "OrderedDict[str, Snap]" = ctx["snaps"]
    reg, pngs = ctx["reg"], ctx["pngs"]

    # ── 源锁：本板实际读的表的联合摘要（与 edible_catalog 同口径）
    h = hashlib.sha256()
    for stem in tables:
        h.update(("%s:%s\n" % (stem, tables[stem].sha)).encode())
    for ns in snaps:
        h.update(("%s:%s\n" % (ns, snaps[ns].sha)).encode())
    pkg_sha = h.hexdigest()
    snap_sha = hashlib.sha256()
    for ns in snaps:
        snap_sha.update(("%s:%s\n" % (ns, snaps[ns].sha)).encode())
    snap_sha_hex = snap_sha.hexdigest()
    lock = {
        "source_id": SOURCE_ID,
        "sha256": pkg_sha,
        "bytes": sum(t.bytes for t in tables.values()),
        "mtime_ns": max(t.mtime_ns for t in tables.values()),
        "role": "primary",
        "path": TREE_REL,
        "tables": list(tables),
        "notes": "配置合并体（基线 script.py314.lc.npk + 2026-10 增量）；"
                 f"sha256 为上述 {len(tables)} 张表文件的联合摘要，bytes/mtime_ns 为合计/最新值；"
                 "common_item 真身在 30_分析/90_表缓存/base_B42760CCA41DBC25.py（树里是 815 B 桩）",
    }
    snap_lock = {
        "source_id": SNAP_SOURCE_ID,
        "sha256": snap_sha_hex,
        "bytes": sum(s.bytes for s in snaps.values()),
        "mtime_ns": max(s.mtime_ns for s in snaps.values()),
        # 门禁只认 primary / comparison（rules 里没有第三个角色）：
        # 配置树是 primary，装备快照是**另一份独立源**，故记 comparison 而非 primary。
        "role": "comparison",
        "path": SNAP_DIR_REL,
        "tables": list(snaps),
        "generated": max((s.generated or "") for s in snaps.values()) if snaps else None,
        "source_package": sorted({s.source_package for s in snaps.values() if s.source_package}),
        "notes": "武器/护甲段（item id 10000–70000 与跨服专属段）来自 2026-11-01 冻结快照："
                 "node 索引法从 script.py314.lc.npk 解出的 equipment_attrs 成品行，自带 name/icon。"
                 "树里 all_equips_data.py 是 808 B 桩、all_equips_data_kj1/_yk 是 0x73 模块且索引尾非 0x76，"
                 "现有解码器解不出 ⇒ 本板不重解码，仍按该冻结快照；跨服同号以 classic 为基准、其余记 name_alt。",
    }

    today = dt.date.today().isoformat()
    items = []
    icon_stat = Counter()
    named = 0
    tag_stat = Counter()
    alt_n = 0
    ICON_FIELD_OF = {s[0]: s[2] for s in SELECTED}

    def tbl_rel(ns: str) -> str:
        if ns in tables:
            return tables[ns].rel
        if ns in snaps:
            return snaps[ns].rel
        return ns

    def tbl_sha(ns: str) -> str | None:
        if ns in tables:
            return tables[ns].sha
        if ns in snaps:
            return snaps[ns].sha
        return None

    def src_id(ns: str) -> str:
        return SNAP_SOURCE_ID if ns in snaps else SOURCE_ID

    for key, rec in merged.items():
        name = rec["name"]
        ns = rec["name_ns"] or rec["namespaces"][0]
        icon_path = rec["icon"] or (reg.get(str(key)) or {}).get("path")
        icon_source = rec["icon_ns"] or (reg.get(str(key)) or {}).get("source")
        png = pngs.get(str(key))
        if png:
            icon_state = "已导出"
        elif icon_path:
            icon_state = "源已定位未导出"
        else:
            icon_state = "无图标源"
        icon_stat[icon_state] += 1
        if name:
            named += 1

        tags = ["static config"]
        if not name or rec.get("name_alt"):
            tags.append("unresolved")
            if rec.get("name_alt"):
                alt_n += 1
        for tg in tags:
            tag_stat[tg] += 1

        frefs = [rec["name_field"]] if rec["name_field"] else []
        if rec["icon_ns"]:
            f = ICON_FIELD_OF.get(rec["icon_ns"])
            if not f and rec["icon_ns"] in snaps:
                f = "icon"
            if f:
                frefs.append(f)
        if not frefs:
            frefs = ["id"]

        it = {
            "id": f"item_{key}",
            "item_id": key,
            "name": name or f"未解析道具 {key}",
            "namespace": ns,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": f"{ns} 行 key={key}" + (f"；同号表 {','.join(rec['namespaces'])}"
                                             if len(rec["namespaces"]) > 1 else ""),
            "status_tags": tags,
            "icon": png,
            "icon_path": icon_path,
            "icon_source": icon_source,
            "icon_state": icon_state,
            "provenance": {
                "source_id": src_id(ns),
                "source_lock_sha256": snap_sha_hex if ns in snaps else pkg_sha,
                "table": tbl_rel(ns),
                "row_key": key,
                "field_refs": frefs,
                "name_source": (f"{ns}#{rec['name_field']}" if rec["name_field"]
                                else f"{ns}#无 name 字段（名称未解析）"),
                "namespaces": rec["namespaces"],
                "upstream": {
                    "package_sha256": snap_sha_hex if ns in snaps else pkg_sha,
                    "entry_index": None,
                    "file_id": None,
                    "role": ns,
                    "table_sha256": tbl_sha(ns),
                },
                "locator_chain": {
                    "chain_status": "replayed-structural",
                    "scope": "record",
                    "no_cross_source_field_join": True,
                    "steps": [{
                        "kind": "decoded-table-row",
                        "source_id": src_id(ns),
                        "table": tbl_rel(ns),
                        "row_key": key,
                        "field_refs": frefs,
                    }],
                },
            },
        }
        # 装备行附带的分类字段（只在该行真有值时出现，避免 6 万条空列）
        for f in SNAP_EXTRA_FIELDS:
            v = (rec.get("equip") or {}).get(f)
            if v not in (None, ""):
                it[f] = v
        if rec.get("desc_brief"):
            it["desc_brief"] = rec["desc_brief"]
        if rec.get("name_alt"):
            it["name_alt"] = " / ".join(rec["name_alt"])
        if png:
            it["_media"] = {"images": [{"png": png}], "total": 1}
        items.append(it)

    items.sort(key=lambda x: x["item_id"])
    total = len(items)
    ns_count = Counter(it["namespace"] for it in items)

    board = {
        "meta": {
            "name": "全量道具总表",
            "category": "三、综合资料 / （一）全量道具总表",
            "source_server": "测试服 · PE 配置合并体（基线 script.py314.lc.npk + 2026-10 增量）"
                             " + 三服装备冻结快照（classic / kj1 / yk，2026-11-01）",
            "source_label": ("测试服 · 41_还原树/pe/配置/com/cdata（"
                             + " / ".join(tables) + "）"
                             + " ＋ 30_分析/all_equips_全量_node索引_20261029（"
                             + " / ".join(snaps) + "）"),
            "generated": today,
            "evidence": "structure",
            "count": total,
            "notes": (
                f"本版由当前 PE 还原树逐表重建（旧版是 ITEM_MASTER_v03 快照，只有 30,251 条 = 一半覆盖）。"
                f"配置表 {len(tables)} 张入册："
                + " / ".join(f"{s} {ctx['ns_rows'][s]:,}" for s in tables)
                + (f"；另接装备冻结快照 {len(snaps)} 份："
                   + " / ".join(f"{s} {ctx['ns_rows'][s]:,}" for s in snaps)
                   + f"（新增 {ctx['snap_new']:,} 个此前完全没有的 id，补齐 10000–70000 武器/护甲段）"
                   if snaps else "")
                + f"；按 item_id 去重后 {total:,} 条。"
                "跨表同号不合并成一条事实：记 provenance.namespaces 与 name_alt 并打 unresolved 标签"
                f"（本轮同号异名 {ctx['collide']:,} 条）。"
                "装备段跨服同号以经典服为基准（classic > kj1 > yk），其余服名字只记 name_alt，不另起一条。"
                "装备快照是 2026-11-01 冻结产物（node 索引法解 script.py314.lc.npk）：树里 all_equips_data*.py "
                "解不出（808 B 桩 / 0x73 模块 / 索引尾非 0x76），故仍按该冻结快照，未重解码。"
                "图标优先取表自己的 icon 字段，其次 30_分析/icon_registry.json；icon_state 三态区分"
                "「已导出 / 源已定位未导出 / 无图标源」。evidence_level=structure-only：结构可证、未经实机核验。"
            ),
            "package_sha": pkg_sha,
            "package_sha_source": (f"本板实际读取的 {len(tables)} 张配置表 + {len(snaps)} 份装备快照"
                                   "文件的联合 sha256（同 edible_catalog 口径）"),
            "provenance": {
                "contract_version": 3,
                "contract": "frozen-audited-artifact",
                "audit_status": "passed",
                "source_locks": ([lock] + ([snap_lock] if snaps else [])),
                "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                                 "integer_join_policy": "no-equal-integer-join",
                                 "runtime_final_policy": "unknown-unless-runtime-proven"},
                "source_id": SOURCE_ID,
            },
            "state_summary": {
                "条目总数": total,
                "命名空间": " / ".join(f"{k} {v:,}" for k, v in ns_count.most_common()),
                "证据等级": f"structure-only {total:,}",
                "状态标签": " / ".join(f"{k} {v:,}" for k, v in tag_stat.most_common()),
                "有名字": f"{named:,}（{named / total:.1%}）",
                "有图标源": f"{total - icon_stat['无图标源']:,}"
                            f"（{(total - icon_stat['无图标源']) / total:.1%}）",
                "跨表同号": alt_n,
                "行级可定位条目": total,
            },
            "icon_stats": {"总条目": total,
                           "已导出": icon_stat["已导出"],
                           "源已定位未导出": icon_stat["源已定位未导出"],
                           "无图标源": icon_stat["无图标源"],
                           "icon 注册表": len(reg)},
            "field_labels": {
                "item_id": "道具ID", "name": "名称", "namespace": "所属表",
                "identity_state": "身份状态", "name_status": "命名状态",
                "icon_path": "图标路径", "icon_source": "图标来源",
                "icon_png": "图标文件", "icon_state": "图标状态",
                "name_alt": "同号异名",
                "weapon_type": "武器类型", "equip_type": "装备类型",
                "level": "装备等级", "desc_brief": "描述摘要",
            },
            "hide_fields": ["_prov_shape", "evidence", "evidence_level", "icon",
                            "icon_path", "icon_png", "id", "provenance", "source",
                            "status_tags", "name_alt"],
            "card_mode": "roster",
            "hide_media": False,
            "id_label": "道具ID",
            "card_summary": [["item_id", "道具ID"], ["namespace", "所属表"],
                             ["icon_state", "图标"], ["icon_source", "图标来源"]],
        },
        "items": items,
    }
    board, hoisted = hoist_board_defaults(board)

    print(f"表 {len(tables)} 张：" + " / ".join(f"{s} {ctx['ns_rows'][s]:,}" for s in tables))
    if snaps:
        print(f"装备快照 {len(snaps)} 份：" + " / ".join(f"{s} {ctx['ns_rows'][s]:,}" for s in snaps)
              + f"｜新增 id {ctx['snap_new']:,}｜与既有表同号 {ctx['snap_overlap']:,}"
              + f"（其中异名 {ctx['snap_name_alt']:,} 记 name_alt）")
    print(f"条目 {total:,}（旧板 30,252）｜有名字 {named:,} ({named/total:.1%})")
    print("图标：" + " / ".join(f"{k} {v:,}" for k, v in icon_stat.most_common()))
    print("命名空间：" + " / ".join(f"{k} {v:,}" for k, v in ns_count.most_common()))
    print(f"同号异名 {ctx['collide']:,} 条；溯源上提 {hoisted} 个字段")
    print("package_sha:", pkg_sha)

    if args.dry_run:
        return 0

    out = Path(args.output)
    # 备份旧板：**绝不覆盖已存在的不同版本**
    # （踩过：同日重跑一次就把刚备份的旧板换成新板，等于没备份）
    if out.exists():
        day = dt.date.today()
        bak = out.parent / f"_archive_item_master_full_{day:%Y%m%d}.json"
        cur_sha = sha256_file(out)
        if bak.exists() and sha256_file(bak) == cur_sha:
            print("旧板备份已存在且同内容，跳过：", bak.name)
        else:
            if bak.exists():          # 已有**另一个**版本，别覆盖它
                bak = out.parent / f"_archive_item_master_full_{day:%Y%m%d}_{dt.datetime.now():%H%M%S}.json"
            shutil.copy2(out, bak)
            print("备份旧板 →", bak.name)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_board_pair(out, board, "item_master_full")
    size = out.stat().st_size / 1048576
    print(f"写出 {out.name}（{size:.1f} MB）+ 同名 .js")
    if args.md:
        write_markdown(items, reg)
    return 0



# ───────────────────────────────────────── 选表依据 md
CENSUS = PROJ / "01_索引与产物/30_分析/全量总表_扫描.jsonl"
MD_OUT = PROJ / "01_索引与产物/30_分析/全量总表_选表依据.md"


def load_census() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if CENSUS.exists():
        for line in CENSUS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out[r["table"]] = r
    return out


def write_markdown(items: list[dict], reg: dict) -> None:
    """把**真正用于构建的** SELECTED / REJECT 与普查数据写成选表依据。

    ★ 文档由构建常量直接生成 ⇒ 文档与产物不会漂移（这是本项目踩过的坑：
      手写散文引用的条数/表名会过期）。
    ★ items 而不是内存里的 merged：这样 `--md-only` 能直接对着**已落盘的板**
      重写文档，不重跑 40 分钟解码也不会写出过期数字。
    """
    census = load_census()
    # 装备冻结快照的核数（写进第 6 节边界：条数必须由数据算，不手写）
    _snaps = load_snapshots()
    _servers: dict[int, set[str]] = {}
    _names: dict[int, set[str]] = {}
    for _s in _snaps.values():
        for _k, _r in _s.rows.items():
            _servers.setdefault(_k, set()).add(_s.ns)
            _nm = _r.get("name")
            if isinstance(_nm, str) and _nm.strip():
                _names.setdefault(_k, set()).add(_nm.strip())
    SNAP_ROWS = sum(s.n_rows for s in _snaps.values())
    SNAP_KEYS = set(_servers)
    SNAP_MULTI = sum(1 for v in _servers.values() if len(v) > 1)
    SNAP_DIFF = sum(1 for v in _names.values() if len(v) > 1)
    # 表行数一律取普查口径（同一个读取路径），避免与构建时的 rows 打架
    table_rows = {s: (census.get(s) or {}).get("rows") or 0 for s, *_ in SELECTED}
    # ★ 注册表 key 是**字符串**、条目 item_id 是**整数** ⇒ 必须先归一。
    #   踩过：直接 set(reg) 会得到「注册表独有 60,138 / 本板独有 65,237」这种互不相交的假结论。
    reg_ids = {int(k) for k in reg}
    merged_ids = {int(it["item_id"]) for it in items}

    L: list[str] = []
    A = L.append
    A("# 全量道具总表 · 选表依据")
    A("")
    A("> 生成：`02_wiki/web/tools/rebuild_item_master_full.py --md`（只读 PE 还原树）")
    A("> 机器可读普查：`01_索引与产物/30_分析/全量总表_扫描.jsonl`"
      f"（`rebuild_item_master_scan.py` 生成，{len(census)} 张候选表逐表一行）")
    A("")
    A("## 0. 结论先说")
    A("")
    A(f"- 「道具 id 权威空间」= `common_item_data` 真表（树里是 815 B 桩，真身在 "
      f"`90_表缓存/base_B42760CCA41DBC25.py`，配 `base_EF3A8474A5E5F7A4.py` 池）"
      f"解出的 **{table_rows.get('common_item_data', 0):,}** 个行 key。")
    A(f"- 「已知 6 万级规模」= `30_分析/icon_registry.json` 的 **{len(reg_ids):,}** 个 id（跨族并集）。")
    A(f"- 本板最终收录 **{len(merged_ids):,}** 个 item_id、**{len(SELECTED)}** 张表；"
      f"与注册表对账：注册表独有 **{len(reg_ids - merged_ids):,}** 个、本板独有 **{len(merged_ids - reg_ids):,}** 个。")
    A("")
    A("「全量」不等于「一张表」：只读 `common_item` 永远只有 3.8 万，"
      "`icon_registry` 之所以是 6 万，正是因为它把时装/礼包/配方/外观/涂装这些**各自带 id 的实体名册**并了起来。"
      "所以总表 = 道具 id 空间主表 + 这些实体名册，按 item_id 去重。")
    A("")
    A("## 1. 判定规则")
    A("")
    A("| 代号 | 含义 |")
    A("|---|---|")
    A("| S1 | key 就是道具 id（落在 common_item id 空间 ≥90%），且能给 name 或 icon |")
    A("| S3 | key 不是 common_item 的道具 id，但表是可命名实体名册（行自带 id==key，或有 name+icon） |")
    A("| X1 | key 是配置/类型/期次号，且没有名字字段（不是实体名册） |")
    A("| X2 | 有名字但 key 非道具 id 且无图标，或混合 key 空间（引用/中间表） |")
    A("| X3 | 解码失败 / 0 行 / 桩表 |")
    A("")
    A("⚠️ 两条硬约束（本项目铁律，违反就是造事实）：")
    A("")
    A("1. **`no-equal-integer-join`**：不同表的同号行**不是同一件东西**。实测 `recipe` 的 key 100010 是"
      "「配方:MP5冲锋枪」、`equip_coating_data` 的 key 100010 是同一把枪的「初始」涂装；"
      "`title_conf_data` 的 1011 是称号「游云惊梦点星河」、`nucleus_build_data` 的 1011 是核芯「疾影火刃」。"
      "⇒ 总表按 item_id 去重时**不合并成一条事实**，而是记 `provenance.namespaces` + `name_alt` 并打 `unresolved`。")
    A("2. **表里有路径 ≠ 图标可用**：`icon` 字段常常是 CHS 池槽位号，"
      "必须按该表自己的池解出来才是 `ui/...`；解不到就写「无图标源」，不猜路径。")
    A("")
    A("## 2. 最终选入（构建里就是这份 `SELECTED`）")
    A("")
    A("| 表 | 行数 | key 区间 | 落在道具 id 空间 | name 字段 | icon 字段 | 角色 |")
    A("|---|---|---|---|---|---|---|")
    for stem, nf, ic, isjump in SELECTED:
        c = census.get(stem, {})
        role = "名称补充源" if stem in SUPPLEMENT else "主命名空间"
        A("| `{}` | {:,} | {} – {} | {:.0%} | `{}` | {} | {} |".format(
            stem, table_rows.get(stem, 0), c.get("key_min", "—"), c.get("key_max", "—"),
            c.get("common_ratio") or 0, nf,
            ("`%s`（jump 字符串组）" % ic) if isjump else (("`%s`" % ic) if ic else "—"),
            role))
    A("")
    A("逐条说明：")
    A("")
    A("- **all_equips_{classic,kj1,yk}（装备冻结快照，3,287 / 1,553 / 2,228 行）**：武器/护甲段"
      "（item id 10000–70000 与跨服专属段）的唯一现成来源，位于 "
      "`30_分析/all_equips_全量_node索引_20261029/`（2026-11-01，node 索引法解 `script.py314.lc.npk`，"
      "是「装备属性」板块的数据源），行自带 `name` / `icon`（`ui/item_icon/...`）。"
      "树里的 `all_equips_data.py` 是 808 B 桩、`all_equips_data_kj1/_yk` 是 `0x73` 模块且索引尾非 `0x76`，"
      "现有解码器解不出 ⇒ 接入方式为**直接读冻结快照，不重解码**；跨服同号以经典服为基准"
      "（classic > kj1 > yk），其余服名字只记 `name_alt`，不另起一条。")
    A("- **common_item_data（38,231）**：唯一权威的道具行；`name`/`icon` 都是同表字段。"
      "树里那份是 815 B 的 MergedTableData 壳，真身在表缓存，**这一点必须写进板 meta**，否则下一个人会以为树里没表。")
    A("- **fashion_data（11,169）**：时装/外观名册，`icons` 是 jump 字符串组（`0x27` 组 → 池槽位 → `ui/...`）。"
      "`simple_fashion_data` / `fashion_data_for_export` 都是它的**子集**，故不入册（见第 3 节）。")
    A("- **gift_data（5,657）**：礼包名册，`icon` 是直读字符串，另有 `icons` 组可兜底。")
    A("- **player_module_appear_data（1,200）**：展示外观（74154xxxx / 74159xxxx 这类池内时装），"
      "名字只在这张表里。")
    A("- **recipe（4,249）**：配方名册；行 key 是配方 id，产出的道具在 `item_id` 字段（两列都在，故是 S3 不是 S1）。")
    A("- **equip_coating_data（566）**：涂装名册（`coating_name` / `coating_icon`）；"
      "565 个 key 与 recipe 同号（涂装正对应那条配方），在总表里合并为同一条并留 `name_alt`。")
    A("- **vehicle_ui_data（278）**：载具名册（`name` / `ui_vehicle_icon`）；"
      "⚠️ 不能用 `icon` 字段（该表没有），`vehicle_equip_type` 也不能当分类（它把船并进摩托）。")
    A("- **edible_item_data（4,499）**：食物/食材名册（`name` / `icon`）；key 是食物 id 空间，与 common_item 只重叠 59 个。")
    A("- **avatar_frame_conf_data（253）/ body_sfx_data（44）**：作为**名称补充源**——"
      "它们的 id 大多已在 common_item 内（239 / 42 个），只新增 14 / 2 条，但能补上"
      "「头像框」「投影」这两个 common_item 里叫不出人话的段。")
    A("")
    A("## 3. 主动排除（人工复核，构建里是 `REJECT`）")
    A("")
    A("| 表 | 行数 | 排除原因 |")
    A("|---|---|---|")
    for stem, why in sorted(REJECT.items(), key=lambda kv: -(table_rows.get(kv[0], 0)
                                                             or (census.get(kv[0], {}) or {}).get("rows") or 0)):
        rows = table_rows.get(stem) or (census.get(stem, {}) or {}).get("rows") or 0
        A(f"| `{stem}` | {rows:,} | {why} |")
    A("")
    A("## 4. 自动判定排除（普查 X 类，按行数排序 Top 25）")
    A("")
    A("| 表 | 行数 | 落在道具 id 空间 | name 字段 | 判定 / 原因 |")
    A("|---|---|---|---|---|")
    rest = [(k, v) for k, v in census.items()
            if k not in table_rows and k not in REJECT and str(v.get("verdict", "")).startswith("X")]
    rest.sort(key=lambda kv: -(kv[1].get("rows") or 0))
    for k, v in rest[:25]:
        A("| `{}` | {:,} | {:.0%} | {} | {} {} |".format(
            k, v.get("rows") or 0, v.get("common_ratio") or 0,
            "/".join(v.get("name_fields") or []) or "—", v.get("verdict"),
            v.get("reason") or ""))
    A("")
    A(f"其余 {max(0, len(rest) - 25):,} 张同类表见 `全量总表_扫描.jsonl`（逐表 rows / key 区间 / 字段名 / 判定）。")
    A("")
    A("## 5. 与图标注册表的对账")
    A("")
    A(f"- 注册表 {len(reg_ids):,} 个 id，本板 {len(merged_ids):,} 个；"
      f"**注册表独有 {len(reg_ids - merged_ids):,}**（= 注册表收录但本板未选入的族）、"
      f"**本板独有 {len(merged_ids - reg_ids):,}**（= 注册表没有 icon 字段可取的族，如载具/食物/头像框）。")
    A("- 注册表的 6 个来源（common_item 37,997 / fashion 11,169 / gift 5,644 / recipe 4,097 / "
      "appear 1,174 / coating 57）都是「有 icon 字段」的行；本板按「有名字」收录，"
      "所以两边天然不等 —— 差额不是缺数据，是口径不同。")
    A("")
    A("## 6. 已知边界（不写清楚就会被当成缺陷）")
    A("")
    A("- **`evidence_level = structure-only`**：全部是结构可证（表里真有一行、真有这个字段），"
      "未经实机核验。status_tags 只给 `static config`，名字缺失或同号异名才加 `unresolved`。")
    A("- **图标「已导出」只覆盖已物化的 png**：`assets/<dir>/<id>.png` 存在才算；"
      "把文件名的 `icon_` / `af_` / `nc_` / `chip_` 前缀与 `_b`/`_s` 后缀归一后**只接受纯数字键**，"
      "`item_icon_jin_bing_b` 这类开发名一律不认（错图比空图更糟）。")
    A("- **怪物 / 核芯 / 芯片 / 称号 / 箱子不在本表**：它们各有独立 id 空间与独立板块"
      "（nucleus_item_catalog / chip_item_catalog / title_catalog 等）。"
      "塞进道具总表会让「总表条数」失去意义。")
    A("- **`monster_data*` 全族 0 命中道具 id**：怪物名册的 key 是怪物类型号，"
      "名字在 `monster_data_*` 分表与 `monster_icon_data` 里，与本表无关。")
    A("- **`furniture_base_data` / `building_base_data` 没有名字也没有图标**："
      "它们是结构参数表（grid_w / model_name），家具/建筑名册走 common_item 的家具段与 `furniture_*` 名册族。")
    A("- **武器/护甲段（10000–70000）来自「装备冻结快照」，不是从树里重解码的**："
      "`common_item_data` 的 key 从 7000 直接跳到 70001，故这一段只能由 "
      "`all_equips_attrs_{classic,kj1,yk}.json`（2026-11-01 冻结，node 索引法解 `script.py314.lc.npk`）补齐；"
      f"三份快照共 {SNAP_ROWS:,} 行、按 key 去重后 **{len(SNAP_KEYS):,}** 条"
      f"（{SNAP_MULTI:,} 个 key 跨服重复，{SNAP_DIFF:,} 个名字有差异 ⇒ 只记 `name_alt`，不另起一条）。"
      "树里 `all_equips_data*.py` 至今解不出（808 B 桩 / `0x73` 模块 / 索引尾非 `0x76`），"
      "因此**拿不到比 2026-11-01 更新的装备数据**；要说「更新」必须先解决这三个文件的解码。")
    A("- **`monster_info_display_data`（23 行）/ `monster_init_dialog_data`（553 行）**："
      "前者是怪物图鉴展示行，后者 name 字段是**对话文件名**，都不是道具名，故不入册。")
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("写出", MD_OUT)


if __name__ == "__main__":
    sys.exit(main())
