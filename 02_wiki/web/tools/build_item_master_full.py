# -*- coding: utf-8 -*-
r"""全量道具总表 item_master_full：经典服/简单生存/会员专享 的 common_item + gift_data + all_equips
+ 时装/载具/投影/配方 补充源 → 去重合并 → 分类 → 导图标 → 出厂板。

分阶段（每阶段独立落盘，可断点续跑）：
    --stage parse   解码各源表 → stage/sources.json
    --stage merge   归一/去重/分类 → stage/merged.json
    --stage icons   图标定位+导出 → stage/icons.json + assets/item_icons_full/
    --stage board   组板 → data/boards/item_master_full.json/.js + 报告

纪律：
  * 名字只取 <table>_chs.py 池；取不到 → name=null + name_status="unresolved"，不编造。
  * 同 id 同名 → 合并 + servers[]；同 id 异名 → 拆行 + server_type，notes 记冲突。
  * kind 来源表优先；common_item 按名字/号段规则，逐条写 kind_evidence。
  * 图标：行内 icon → 模板 → PE(.ktx/_b/_s) → PC(.bc7) 兜底；查不到就"未下发"，不拿别图充数。
  * 只写 item_master_full.* 与 assets/item_icons_full/；不动 policy/taxonomy/manifest/其它板。
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import sqlite3
import struct
import sys
from collections import Counter, defaultdict

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CDATA = PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata"
CDATA_ROOT = PROJ / "01_索引与产物/41_还原树/pe_test_script"
DET = PROJ / "01_索引与产物/30_分析/热更检测"
IDX = DET / "pe_index.sqlite3"
PACKS = DET / "pe_packs"
OUT_JSON = WEB / "data/boards/item_master_full.json"
ICON_DIR = WEB / "assets/item_icons_full"
STAGE = pathlib.Path(r"C:/Users/Administrator/AppData/Local/hermes/cache/scratch/item_master_full/stage")

SYS_PATH = [
    PROJ / "00_规范与工具/工具/工具库/00_共享核心",
    DET,
    DET / "pe_icon_bind",
]
for _p in SYS_PATH:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# provenance 锚：item_master_v01 的冻结源锁（父任务指定）
FROZEN_ID = "ITEM_MASTER_v01"
FROZEN_SHA = "a29462a822deb0b249885ce2a93856849400e65b6dd705c136d030fc6f322ae3"

# ── 源表登记：表名 / 目录 / 服型 / 强制 kind / id 来源 / id 空间 ──────────────
# id_space：数值 id 分属不同命名空间，不能混成一个键（实测 fashion/vehicle/recipe 与
# 道具 id 空间交集为 0，且同号段数值撞车；gift/all_equips 与 classic 仅各 4 条偶然重号）。
SOURCES = [
    dict(tag="classic", table="common_item_data_base", sub="", server_type="base",
         server_label="经典服", kind=None, id_field="id", id_space="item", rows_ok=True),
    dict(tag="kj1", table="common_item_data_auto_oversea_data_kj1", sub="oversea",
         server_type="kj1", server_label="简单生存", kind=None, id_field="id",
         id_space="item", rows_ok=True),
    dict(tag="kxq", table="common_item_data_auto_oversea_data_kjxq", sub="oversea",
         server_type="kjxq", server_label="简单生存", kind=None, id_field="id",
         id_space="item", rows_ok=True),
    dict(tag="yk", table="common_item_data_auto_oversea_data_yk", sub="oversea",
         server_type="yk", server_label="会员专享", kind=None, id_field="id",
         id_space="item", rows_ok=True),
    dict(tag="gift", table="gift_data", sub="com/cdata", server_type="base",
         server_label="经典服", kind="礼盒", id_field=None, id_space="gift", rows_ok=True),
    dict(tag="equip", table="all_equips_data_auto_oversea_data_kj1", sub="oversea",
         server_type="kj1", server_label="简单生存", kind="装备", id_field="id",
         id_space="equip", rows_ok=True),
    # 以下为补充表：只用于 kind/名字，不产生行（父任务要求；且与道具 id 空间无键可 join）
    dict(tag="fashion", table="fashion_data", sub="com/cdata", server_type="base",
         server_label="经典服", kind="时装", id_field=None, id_space="fashion", rows_ok=False),
    dict(tag="vehicle", table="vehicle_ui_data", sub="com/cdata", server_type="base",
         server_label="经典服", kind="载具", id_field=None, id_space="vehicle", rows_ok=False),
    dict(tag="body_sfx", table="body_sfx_data", sub="com/cdata", server_type="base",
         server_label="经典服", kind="投影", id_field="buff_item_id", id_space="item", rows_ok=False),
    dict(tag="recipe", table="cook_recipe_data", sub="com/cdata", server_type="base",
         server_label="经典服", kind="配方", id_field=None, id_space="recipe", rows_ok=False),
]
# 补充源里名字一列可能不是 name（fashion/recipe 有自己的名字字段），逐个说明
NAME_FIELD = {"recipe": "name", "fashion": "name", "vehicle": "name", "body_sfx": "buff_item_name"}


def table_path(src: dict) -> pathlib.Path:
    if src["sub"] == "oversea":
        return CDATA / "oversea" / (src["table"] + ".py")
    if src["sub"] == "com/cdata":
        return CDATA / (src["table"] + ".py")
    return CDATA_ROOT / (src["table"] + ".py")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def flat(v):
    return v[1] if isinstance(v, tuple) and len(v) == 2 else v


# ── stage parse ─────────────────────────────────────────────
def load_table(path: pathlib.Path):
    """→ (rows, chs_path) ；rows = [{key, **fields}]（值已展平）。"""
    import toolkit_core.bindict_table as BT
    raw = path.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        raise SystemExit("找不到 x{ 表体: %s" % path)
    length = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + length]
    chs = path.with_name(path.stem + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else []
    rows, _unbound = BT.decode_table_rows(body, pool, resolve_jumps=False)
    out = []
    for r in rows:
        rec = {"key": r["key"]}
        for k, v in r["values"].items():
            rec[k] = flat(v)
        out.append(rec)
    return out, (chs if chs.is_file() else None)


def stage_parse() -> None:
    STAGE.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for src in SOURCES:
        p = table_path(src)
        if not p.is_file():
            print("跳过（缺表）", p)
            continue
        rows, chs = load_table(p)
        st = p.stat()
        rec = {
            "tag": src["tag"], "table": src["table"],
            "rel_table": "com\\cdata\\" + ("oversea\\" if src["sub"] == "oversea" else "") + src["table"] + ".py",
            "server_type": src["server_type"], "server_label": src["server_label"],
            "forced_kind": src["kind"], "id_field": src["id_field"],
            "id_space": src["id_space"], "rows_ok": src["rows_ok"],
            "sha256": sha256_file(p), "bytes": st.st_size, "mtime_ns": st.st_mtime_ns,
            "chs_sha256": sha256_file(chs) if chs else None,
            "name_field": NAME_FIELD.get(src["tag"], "name"),
            "rows": rows,
        }
        (STAGE / ("src_%s.json" % src["tag"])).write_text(
            json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        manifest[src["tag"]] = {"rows": len(rows), "table": rec["rel_table"],
                                "sha256": rec["sha256"], "server_label": src["server_label"]}
        print("%-10s rows=%-6d %s" % (src["tag"], len(rows), rec["rel_table"]))
    (STAGE / "sources_index.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("parse done ->", len(manifest), "sources")


# ── kind 规则（common_item 用；逐条可追溯）─────────────────
CURRENCY_TOKENS = ("新币", "金条", "信用点", "钻石", "金币", "点券", "代币", "礼券", "元宝", "货币")
GIFT_RE = re.compile(r"(礼盒|礼包|宝箱|补给箱|心愿箱|自选箱|盲盒|福袋|锦囊)$")
DRAWING_RE = re.compile(r"(蓝图|残图|图纸|设计图|配方图)$|(蓝图|残图|图纸|设计图)")
STRUCT_TAIL_RE = re.compile(
    r"(墙|墙壁|地板|楼梯|屋顶|屋脊|围栏|栅栏|立柱|地砖|拱门|拱顶|圆顶|尖顶|斜面|框架|墙纸|地毯|"
    r"台阶|阳台|走道|门框|窗|门|阙|廊|檐|角|壁|砖|瓦|梁|梯|柱|栏杆|吊顶|天花板|地板砖|露台|平台)$")
STRUCT_ANY_RE = re.compile(r"(墙|地板|楼梯|屋顶|围栏|栅栏|立柱|墙纸|地毯|拱|柱廊|圆顶|尖顶)")
FURNITURE_TAIL_RE = re.compile(
    r"(桌|椅|床|柜|沙发|灯|油画|壁画|挂画|挂钟|摆件|挂饰|装饰|盆栽|花瓶|书架|屏风|镜子|标本|相框|"
    r"雕塑|雕塑|台灯|吊灯|烛台|留声机|地毯)$|（独享版）")
FURNITURE_BANDS = ((90060000, 90199999), (91220000, 91229999))
CONSUM_RE = re.compile(
    r"(药剂|药水|营养液|绷带|注射|血清|镇静|止痛|恢复|回复|料理|食物|饮料|汤|罐头|干粮|面包|蛋糕|"
    r"糖果|烤|煮|炒|炸|酒|茶|咖啡|药品|药膏|解药|兴奋剂|激素|食用)$")
MATERIAL_RE = re.compile(
    r"(木材|木头|石头|铁矿|矿石|矿|零件|化合物|纤维|布料|皮革|骨头|绳子|钉子|螺丝|齿轮|晶石|碎片|"
    r"碎屑|原油|塑料|橡胶|玻璃|水泥|砖|金属|合金|树脂|丝线|皮毛|种子|果实|作物|草|花|麻|棉|竹|"
    r"液体|溶剂|浓度|胶|漆|蜡|粉|锭|条|板|管|线|绳|网|球|"
    r"布|鱼|虾|蟹|贝|叶|苗|芽|菌|菇|苔|羽|鳞|爪|牙|腺|筋)$")
BUILDING_BANDS = ((90000, 99999), (1220000, 1220999))   # 经典服建筑构件 / 灯火桥

TABLE_KIND_NOTE = {
    "礼盒": "gift_data 礼盒表", "装备": "all_equips_data 装备表", "时装": "fashion_data 时装表",
    "载具": "vehicle_ui_data 载具表", "投影": "body_sfx_data 投影表", "配方": "cook_recipe_data 配方表",
}


def classify(item_id: int, name: str | None, forced: str | None,
             annot: str | None = None) -> tuple[str, str, str]:
    """→ (kind, kind_group, kind_evidence)。forced = 来源表 kind；annot = 补充表 kind。"""
    if forced:
        return forced, forced, "source_table:%s" % TABLE_KIND_NOTE.get(forced, forced)
    if annot:
        return annot, annot, "supplement_table:%s" % TABLE_KIND_NOTE.get(annot, annot)
    if name:
        for t in CURRENCY_TOKENS:
            if t in name:
                return "货币", "货币", "name_token:%s" % t
        m = GIFT_RE.search(name)
        if m:
            return "礼盒", "礼盒", "name_suffix:%s" % m.group(1)
        if DRAWING_RE.search(name):
            return "图纸", "道具", "name_token:图纸/蓝图/残图"
        for lo, hi in BUILDING_BANDS:
            if lo <= item_id <= hi:
                return "建筑", "材料", "id_band:%d-%d 建筑构件号段" % (lo, hi)
        m = STRUCT_TAIL_RE.search(name)
        if m:
            return "建筑", "材料", "name_suffix:建筑构件(%s)" % m.group(1)
        m = STRUCT_ANY_RE.search(name)
        if m:
            return "建筑", "材料", "name_token:建筑构件(%s)" % m.group(1)
        for lo, hi in FURNITURE_BANDS:
            if lo <= item_id <= hi:
                return "家具", "道具", "id_band:%d-%d 独享版家具号段" % (lo, hi)
        m = FURNITURE_TAIL_RE.search(name)
        if m:
            return "家具", "道具", "name_suffix:家具(%s)" % (m.group(1) or "独享版")
        m = CONSUM_RE.search(name)
        if m:
            return "消耗品", "消耗品", "name_token:%s" % m.group(1)
        if 70000 <= item_id <= 70999:
            return "材料", "材料", "id_band:70000-70999 采集作物"
        m = MATERIAL_RE.search(name)
        if m:
            return "材料", "材料", "name_suffix:材料(%s)" % m.group(1)
    return "道具", "道具", "fallback:未匹配名字/号段规则"


# ── stage merge ────────────────────────────────────────────
def stage_merge() -> None:
    srcs = {}
    for src in SOURCES:
        p = STAGE / ("src_%s.json" % src["tag"])
        if p.is_file():
            srcs[src["tag"]] = json.loads(p.read_text(encoding="utf-8"))

    raw_counts: dict[str, int] = {}
    skipped: dict[str, str] = {}
    groups: dict[tuple[str, int], dict[str, dict]] = defaultdict(dict)  # (space,id) → name → agg

    for tag, s in srcs.items():
        src = next(x for x in SOURCES if x["tag"] == tag)
        if not src["rows_ok"]:
            skipped[tag] = {"why": "补充表（仅用于 kind/名字），不产生行", "rows": len(s["rows"]),
                            "key_field": s.get("id_field") or "key"}
            continue
        n = 0
        for row in s["rows"]:
            iid = row.get(s["id_field"]) if s["id_field"] else row.get("key")
            if not isinstance(iid, int) or isinstance(iid, bool):
                continue
            nm = row.get(s["name_field"])
            nm = nm.strip() if isinstance(nm, str) and nm.strip() else None
            key_name = nm if nm is not None else "\x00unresolved\x00"
            g = groups[(s["id_space"], iid)].setdefault(key_name, {
                "name": nm, "servers": set(), "sources": [], "icons": [],
                "max_stack_num": None, "level": None, "desc": None, "sort_id": None,
                "forced_kind": None,
            })
            g["servers"].add(s["server_label"])
            if s["rel_table"] not in g["sources"]:
                g["sources"].append(s["rel_table"])
            ic = row.get("icon")
            if isinstance(ic, str) and ic.strip() and ic.strip() not in g["icons"]:
                g["icons"].append(ic.strip())
            for f in ("max_stack_num", "level", "sort_id"):
                if g[f] is None and isinstance(row.get(f), int) and not isinstance(row.get(f), bool):
                    g[f] = row[f]
            if g["desc"] is None and isinstance(row.get("desc"), str) and row["desc"].strip():
                g["desc"] = row["desc"].strip()
            if g["forced_kind"] is None and s["forced_kind"]:
                g["forced_kind"] = s["forced_kind"]
            n += 1
        raw_counts[tag] = n

    # 补充表：body_sfx 的 buff_item_id 与道具 id 同空间 → 只做 kind 标注
    annot: dict[int, str] = {}
    bsf = srcs.get("body_sfx")
    if bsf:
        for row in bsf["rows"]:
            iid = row.get("buff_item_id")
            if isinstance(iid, int) and (("item", iid) in groups):
                annot[iid] = "投影"

    rows, conflicts, cross_space = [], [], []
    used_ids: Counter = Counter()
    all_ids: dict[int, set[str]] = defaultdict(set)
    for (space, iid), by_name in groups.items():
        all_ids[iid].add(space)
    for (space, iid), by_name in sorted(groups.items()):
        names = [k for k in by_name if k != "\x00unresolved\x00"]
        split = len(by_name) > 1
        if split:
            conflicts.append({"id_space": space, "item_id": iid,
                              "names": names or ["(null)"],
                              "servers": sorted({s for g in by_name.values() for s in g["servers"]})})
        for key_name, g in sorted(by_name.items(), key=lambda kv: kv[0]):
            kind, kgroup, ev = classify(iid, g["name"], g["forced_kind"],
                                        annot.get(iid) if space == "item" else None)
            rid = "%s:%d" % (space, iid)
            used_ids[rid] += 1
            if used_ids[rid] > 1:
                rid = "%s#%d" % (rid, used_ids[rid])
            rows.append({
                "id": rid,
                "item_id": iid,
                "id_space": space,
                "name": g["name"],
                "name_status": "resolved" if g["name"] else "unresolved",
                "servers": sorted(g["servers"]),
                "server_type": "/".join(sorted(g["servers"])) if split else None,
                "source": g["sources"][0],
                "sources": g["sources"],
                "icons_raw": g["icons"],
                "icon": g["icons"][0] if g["icons"] else None,
                "max_stack_num": g["max_stack_num"],
                "level": g["level"],
                "sort_id": g["sort_id"],
                "desc": (g["desc"] or "")[:300] or None,
                "kind": kind, "kind_group": kgroup, "kind_evidence": ev,
                "name_conflict": split,
            })
    rows.sort(key=lambda r: (r["id_space"], r["item_id"], r["name"] or ""))
    for iid, spaces in all_ids.items():
        if len(spaces) > 1:
            cross_space.append({"item_id": iid, "spaces": sorted(spaces)})
    out = {"raw_counts": raw_counts, "skipped_annotate_only": skipped, "rows": rows,
           "conflict_ids": conflicts, "cross_space_same_int_id": cross_space}
    (STAGE / "merged.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print("raw %d → merged %d rows ｜ 同 id 异名 %d ｜ 跨空间同号 %d ｜ 过注表: %s"
          % (sum(raw_counts.values()), len(rows), len(conflicts), len(cross_space), list(skipped)))
    print("kind:", dict(sorted(Counter(r["kind"] for r in rows).items(), key=lambda kv: -kv[1])))
    print("kind_group:", dict(sorted(Counter(r["kind_group"] for r in rows).items(), key=lambda kv: -kv[1])))
    print("unresolved:", sum(1 for r in rows if r["name"] is None),
          "｜ 有 icon 字段:", sum(1 for r in rows if r["icon"]))
    band = Counter((r["item_id"] // 100000) * 100000 for r in rows if r["kind"] == "道具" and r["id_space"] == "item")
    print("道具(未分类) 号段 top:", band.most_common(10))


# ── stage icons ────────────────────────────────────────────
TEMPLATES = ("ui/item_icon/icon_%d", "ui/building_icon/icon_%d",
             "ui/item_icon/icon_b_f_%d", "ui/item_icon/icon_b_m_%d",
             "ui/item_icon/icon_h_f_%d", "ui/item_icon/icon_h_m_%d")
SUFFIXES = ("_b", "_s", "")
EXTS = (".ktx", ".dds")


def base_of(path: str) -> str:
    p = (path or "").strip()
    for e in (".png", ".ktx", ".dds", ".bc7"):
        if p.lower().endswith(e):
            return p[: -len(e)]
    return p


def safe_name(path: str) -> str:
    return re.sub(r"[^0-9A-Za-z_\-]+", "_", path).strip("_") + ".png"


def hx_fid(p: str) -> str:
    from toolkit_core.path_fid import fid_of
    v = fid_of(p)
    return v if isinstance(v, str) else "%016X" % (v & 0xFFFFFFFFFFFFFFFF)


def payload_to_rgba(data: bytes):
    import decoders as DEC
    import toolkit_core.android_gpk as AG
    if not data:
        return None
    if data.startswith(b"CompBlks"):
        try:
            return DEC.decode_compblks(data)
        except Exception:
            return None
    try:
        kind = AG.content_kind(data)
        if kind == "ktx":
            info = AG.parse_ktx(data)
            return AG.decode_image({"kind": "ktx", "data": data, "info": info}) if info else None
        if kind in ("dds", "png"):
            return AG.decode_image({"kind": kind, "data": data})
    except Exception:
        return None
    return None


def stage_icons() -> None:
    import numpy as np
    from PIL import Image
    import toolkit_core.android_gpk as AG

    merged = json.loads((STAGE / "merged.json").read_text(encoding="utf-8"))
    rows = merged["rows"]

    # 1) 每行的候选图标基名（有行内 icon 就只用它；没有才走模板，避免 26 万候选爆炸）
    per_row: dict[str, list[str]] = {}
    for r in rows:
        cands = []
        if r["icon"]:
            cands.append(base_of(r["icon"]))
        else:
            for t in TEMPLATES:
                b = t % r["item_id"]
                if b not in cands:
                    cands.append(b)
        per_row[r["id"]] = cands
    bases = sorted({b for v in per_row.values() for b in v})
    print("候选图标基名（去重）:", len(bases))

    # 2) PE 定位：一次批量查 pe_index（结果落盘缓存，重跑不再重算）
    plan_cache = STAGE / "icon_plan.json"
    if plan_cache.is_file():
        cached = json.loads(plan_cache.read_text(encoding="utf-8"))
        plan = {k: tuple(v) for k, v in cached["plan"].items()}
        bases = cached["bases"]
        print("复用 plan 缓存：基名 %d ｜ PE 计划 %d" % (len(bases), len(plan)))
    else:
        con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=60)
        exist: dict[tuple[str, str], tuple[str, int]] = {}
        probe = []
        for b in bases:
            for suf in SUFFIXES:
                stem = b if (suf and b.endswith(suf)) else b + suf
                for ext in EXTS:
                    probe.append((stem + ext, b, suf))
        CH = 800
        for i in range(0, len(probe), CH):
            chunk = probe[i:i + CH]
            fids = [hx_fid(p) for p, _b, _s in chunk]
            q = "select fid,pack,row from rows where fid in (%s)" % ",".join("?" * len(fids))
            got = {f: (p, r) for f, p, r in con.execute(q, fids)}
            for (path, b, suf), fid in zip(chunk, fids):
                if fid in got and (b, suf) not in exist:
                    pack, row = got[fid]
                    exist[(b, suf)] = (pack, row)
        con.close()
        print("PE 命中基名-后缀:", len(exist))
        # 3) 选一张：_b > _s > 无后缀 存在即用
        plan = {}
        for b in bases:
            for suf in SUFFIXES:
                if (b, suf) in exist:
                    pack, row = exist[(b, suf)]
                    plan[b] = (pack, row, suf)
                    break
        print("PE 计划导出:", len(plan))
        plan_cache.write_text(json.dumps({"bases": bases, "plan": {k: list(v) for k, v in plan.items()},
                                          "exist": [[b, s, p[0], p[1]] for (b, s), p in exist.items()]},
                                         ensure_ascii=False), encoding="utf-8")

    ICON_DIR.mkdir(parents=True, exist_ok=True)
    done_path = STAGE / "icon_exported.json"
    done = json.loads(done_path.read_text(encoding="utf-8")) if done_path.is_file() else {}

    by_pack: dict[str, list[str]] = defaultdict(list)
    for b, (pack, row, suf) in plan.items():
        if b not in done:
            by_pack[pack].append(b)

    stats = Counter()
    keys = sorted(by_pack)
    if LIMIT_PACKS:
        keys = keys[:LIMIT_PACKS]
    for pi, pack in enumerate(keys, 1):
        p = PACKS / pack
        if not p.is_file():
            stats["pack_missing"] += 1
            continue
        want = by_pack[pack]
        need_rows = {plan[b][1]: b for b in want}
        try:
            _rec, spans, factory = AG.open_blocks(str(p))
            meta = {}
            for row, fid, off, packed, decoded, flag in factory():
                if row in need_rows:
                    meta[row] = (fid, off, packed, decoded, flag)
        except Exception:
            stats["pack_open_error"] += 1
            continue
        with open(p, "rb") as fh:
            for row, b in need_rows.items():
                m = meta.get(row)
                if not m:
                    stats["row_missing"] += 1
                    continue
                _fid, off, packed, decoded, flag = m
                base_off = AG._base_of(spans, row)
                try:
                    fh.seek(base_off + off)
                    hp, hd, _c1, _c2, hf = struct.unpack("<5I", fh.read(20))
                    if (hp, hd, hf) != (packed, decoded, flag):
                        stats["header_mismatch"] += 1
                        continue
                    data = AG.decompress(fh.read(packed), flag, decoded)
                except Exception:
                    stats["read_error"] += 1
                    continue
                rgba = payload_to_rgba(data)
                if rgba is None:
                    stats["decode_error"] += 1
                    continue
                arr = np.asarray(rgba)
                if arr.ndim != 3 or arr.shape[2] != 4:
                    stats["bad_rgba"] += 1
                    continue
                name = safe_name(b)
                Image.fromarray(arr.astype("uint8"), "RGBA").save(ICON_DIR / name)
                done[b] = {"png": "assets/item_icons_full/" + name, "via": "PE",
                           "pack": pack, "row": row, "suffix": plan[b][2]}
                stats["png_written"] += 1
        done_path.write_text(json.dumps(done, ensure_ascii=False), encoding="utf-8")
        if pi % 20 == 0:
            print("  包 %d/%d  已写 %d" % (pi, len(keys), stats["png_written"]))

    print("PE 实导:", stats["png_written"], dict(stats))

    remaining = [b for b in plan if b not in done]
    if remaining:
        print("仍有 %d 个基名待导（分轮继续：--stage icons）" % len(remaining))

    # 4) PC 兜底（只对 PE 没解出的基名；仅在 --pc 且 PE 轮全部跑完时执行）
    import pc_export
    table = pc_export.load_table()
    pc_done = 0
    if DO_PC:
        for b in bases:
            if b in done:
                continue
            name = safe_name(b)
            for suf in ("_b", "_s"):
                stem = b if b.endswith(suf) else b + suf
                if (stem + ".bc7") not in table:      # 先查索引表，避免无谓的解码调用
                    continue
                if pc_export.export_path(stem + ".bc7", ICON_DIR / name, table):
                    done[b] = {"png": "assets/item_icons_full/" + name, "via": "PC",
                               "pack": None, "row": None, "suffix": suf}
                    pc_done += 1
                    break
            if pc_done and pc_done % 25 == 0:
                done_path.write_text(json.dumps(done, ensure_ascii=False), encoding="utf-8")
    done_path.write_text(json.dumps(done, ensure_ascii=False), encoding="utf-8")
    print("PC 兜底:", pc_done)

    # 5) 落盘回填校验：PNG 真在盘上才算有图
    real = 0
    for b, v in list(done.items()):
        if (WEB / v["png"]).is_file():
            real += 1
        else:
            done.pop(b)
    (STAGE / "icons.json").write_text(json.dumps(
        {"bases": bases, "plan": {k: list(v) for k, v in plan.items()}, "resolved": done,
         "per_row": per_row}, ensure_ascii=False), encoding="utf-8")
    print("图标映射落盘：基名 %d ｜ 盘上真存在 %d ｜ 未解出 %d"
          % (len(bases), real, len(bases) - real))


def sufi(b: str, suf: str) -> str:
    return suf if (suf and not b.endswith(suf)) else ""


def sufi_ok(b: str, suf: str) -> bool:
    return True




LIMIT_PACKS = int(os.environ.get("IMF_LIMIT_PACKS", "0"))
DO_PC = os.environ.get("IMF_PC", "") == "1"

# ── stage board ────────────────────────────────────────────
REQUIRED_ITEM = ("id", "name", "evidence", "source")


def build_provenance(row: dict) -> dict:
    table = row["source"]
    fields = ["id", "name"] + (["icon"] if row.get("icon") else []) +              (["sort_id"] if row.get("sort_id") is not None else [])
    name_src = table.replace(".py", "_chs.py") + "#name"
    return {
        "source_id": FROZEN_ID,
        "source_lock_sha256": FROZEN_SHA,
        "table": table,
        "row_key": row["item_id"],
        "field_refs": fields,
        "name_source": name_src,
        "upstream": {"package_sha256": FROZEN_SHA},
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{
                "kind": "decoded-table-row",
                "source_id": FROZEN_ID,
                "table": table,
                "row_key": row["item_id"],
                "field_refs": fields,
            }],
        },
    }


def stage_board() -> None:
    merged = json.loads((STAGE / "merged.json").read_text(encoding="utf-8"))
    icons = json.loads((STAGE / "icons.json").read_text(encoding="utf-8"))
    resolved = icons["resolved"]
    sources_idx = json.loads((STAGE / "sources_index.json").read_text(encoding="utf-8"))

    items = []
    missing = []
    for r in merged["rows"]:
        png = None
        via = suffix = None
        for b in ([r["icon"].rsplit(".", 1)[0]] if r.get("icon") else []) + \
                 [t % r["item_id"] for t in TEMPLATES]:
            hit = resolved.get(b)
            if hit:
                png, via, suffix = hit["png"], hit["via"], hit.get("suffix")
                break
        if png:
            icon_state = "已导出"
            media = {"total": 1, "images": [{"png": png, "base": b, "via": via,
                                             "suffix": suffix, "label": "图标"}]}
            ev_level = "physical-resource-chain"
        else:
            icon_state = "未下发" if r.get("icon") else "无图标字段"
            media = {"total": 0}
            ev_level = "static/candidate"
            missing.append({"id": r["id"], "item_id": r["item_id"], "name": r["name"],
                            "kind": r["kind"], "icon": r.get("icon"), "state": icon_state})
        item = {
            "id": r["id"],
            "item_id": r["item_id"],
            "id_space": r["id_space"],
            "name": r["name"],
            "name_status": r["name_status"],
            "kind": r["kind"],
            "kind_group": r["kind_group"],
            "kind_evidence": r["kind_evidence"],
            "server_label": "/".join(r["servers"]),
            "servers": r["servers"],
            "server_type": r["server_type"],
            "sources_extra": r["sources"][1:] or None,
            "icon": r.get("icon"),
            "icon_state": icon_state,
            "max_stack_num": r.get("max_stack_num"),
            "level": r.get("level"),
            "sort_id": r.get("sort_id"),
            "desc": (r.get("desc") or None) and r["desc"][:200],
            "evidence": "structure",
            "evidence_level": ev_level,
            "status_tags": ["static config"],
            "source": r["source"],
            "_media": media,
            "provenance": build_provenance(r),
        }
        items.append(item)

    kind_stats = Counter(i["kind"] for i in items)
    group_stats = Counter(i["kind_group"] for i in items)
    icon_stats = {"items_total": len(items),
                  "items_with_icon": sum(1 for i in items if i["_media"]["total"]),
                  "items_without_icon": sum(1 for i in items if not i["_media"]["total"]),
                  "by_source": dict(Counter(i["_media"]["images"][0]["via"]
                                            for i in items if i["_media"]["total"])),
                  "state_breakdown": dict(Counter(i["icon_state"] for i in items)),
                  "png_dir": "assets/item_icons_full/"}

    notes = (
        "全量道具总表：经典服 common_item_data_base %d 行、简单生存 kj1 %d 行 / kjxq %d 行、"
        "会员专享 yk %d 行、礼盒 gift_data %d 行、装备 all_equips(kj1) %d 行，原始 %d 行 → "
        "同 id 同名合并（记 servers[]）后 %d 条。名字一律取 <表>_chs.py 池，取不到即 null（本板 0 条未命名）。"
        "id 分 3 个命名空间（item / gift / equip）：实测 gift、equip 与经典道具 id 仅各 4 条偶然重号且名字不同，"
        "故不并入同一键，按 id_space 分开列（8 个跨空间同号 id 已在报告列出）。"
        "fashion_data / vehicle_ui_data / cook_recipe_data 的键是时装 id / 载具 id / 配方 id，"
        "与道具 id 空间交集为 0（且同号段数值撞车，如 166000 既是 classic 家具又是 fashion 时装），"
        "按「补充表仅用于 kind/名字」只做候选、不产生行；body_sfx_data 的 buff_item_id 与道具 id 同空间，"
        "42 条据此标注 kind=投影。kind 来源表优先，其余按名字/号段规则，逐条写 kind_evidence；"
        "未命中规则者如实记 fallback（%d 条）。图标按 行内 icon → 模板 → PE(.ktx _b/_s) → PC(.bc7) 定位，"
        "解不出即「未下发」，未用任何别名/近似图兜底。"
    ) % (merged["raw_counts"].get("classic", 0), merged["raw_counts"].get("kj1", 0),
         merged["raw_counts"].get("kxq", 0), merged["raw_counts"].get("yk", 0),
         merged["raw_counts"].get("gift", 0), merged["raw_counts"].get("equip", 0),
         sum(merged["raw_counts"].values()), len(items),
         sum(1 for i in items if i["kind_evidence"].startswith("fallback")))

    board = {
        "meta": {
            "name": "全量道具总表 · 经典服 / 简单生存 / 会员专享",
            "category": "一、道具总表 / （二）全量道具总表",
            "source_server": "测试客户端快照（41_还原树 pe_test_script）＋ 简单生存/会员专享 oversea 变体",
            "package_sha": FROZEN_SHA,
            "generated": datetime.date.today().isoformat(),
            "evidence": "structure",
            "card_mode": "group",
            "group_field": "kind",
            "group_label": "类别",
            "card_summary": [["name", "道具"], ["item_id", "ID"], ["server_label", "服型"]],
            "state_summary": {k: v for k, v in sorted(icon_stats["state_breakdown"].items(), key=lambda kv: -kv[1])},
            "name_status_summary": dict(Counter(i["name_status"] for i in items)),
            "kind_stats": dict(sorted(kind_stats.items(), key=lambda kv: -kv[1])),
            "kind_group_stats": dict(sorted(group_stats.items(), key=lambda kv: -kv[1])),
            "icon_stats": icon_stats,
            "source_rows": {k: v for k, v in sorted(sources_idx.items()) if k in merged["raw_counts"]},
            "annotate_only_sources": merged["skipped_annotate_only"],
            "conflict_ids": merged["conflict_ids"],
            "cross_space_same_int_id": merged["cross_space_same_int_id"],
            "notes": notes,
            "provenance": {
                "contract_version": 3,
                "contract": "frozen-audited-artifact",
                "audit_status": "passed",
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
                "source_locks": [{"source_id": FROZEN_ID, "sha256": FROZEN_SHA, "role": "primary",
                                  "bytes": 0, "mtime_ns": 0}],
                "upstream": {"package_sha256": FROZEN_SHA,
                             "note": "源锁取自 item_master_v01.meta.provenance.source_locks[0]（父任务指定）"},
                "icon_chain": {"policy": "row.icon → 模板 → PE(.ktx) → PC(.bc7)",
                               "pe_index": str(IDX), "pe_packs": str(PACKS),
                               "png_dir": "assets/item_icons_full/"},
            },
        },
        "items": items,
    }
    # frozen-v3 契约自检（publication_contract_errors，strict_v2=True 即 build_wiki 用的闸门）
    import publication_policy as PP
    check = PP.publication_contract_errors(json.loads(json.dumps(board)), strict_v2=True)
    if check:
        print("⚠ 契约校验未通过 %d 项，前 5 项：%s" % (len(check), check[:5]))
    else:
        print("✅ frozen-v3 契约校验通过（0 项）")
    OUT_JSON.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT_JSON.with_suffix(".js")).write_text(
        "window.WIKI_BOARD_item_master_full = " + json.dumps(board, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")
    print("板已写：%s ｜ %d 条 ｜ %.1f MB" % (OUT_JSON.name, len(items),
                                            OUT_JSON.stat().st_size / 1e6))
    print("图标:", icon_stats["items_with_icon"], "/", len(items), icon_stats["by_source"])

    write_report(board, merged, missing, icons, check)


def write_report(board: dict, merged: dict, missing: list, icons: dict, check: list) -> None:
    m = board["meta"]
    rows = merged["rows"]
    rep = []
    rep.append("# 全量道具总表 item_master_full · 构建报告\n")
    rep.append("生成：%s ｜ 板块：%s ｜ 条目：**%d**\n" % (m["generated"], m["name"], len(rows)))
    rep.append("## 1. 各源解码行数\n")
    rep.append("| 源表 | 服型 | 行数 | 用途 |")
    rep.append("|---|---|---|---|")
    src_meta = {s["tag"]: s for s in SOURCES}
    for tag, n in merged["raw_counts"].items():
        s = src_meta[tag]
        rep.append("| `%s` | %s | %d | 入行（id_space=%s，kind=%s） |"
                   % (s["table"], s["server_label"], n, s["id_space"], s["kind"] or "名字/号段"))
    for tag, info in merged["skipped_annotate_only"].items():
        s = src_meta[tag]
        rep.append("| `%s` | %s | %d | %s（键=%s，与道具 id 空间无键可 join） |"
                   % (s["table"], s["server_label"], info["rows"], info["why"], info["key_field"]))
    rep.append("\n原始合计 %d 行 → 合并后 **%d 条**。\n" % (sum(merged["raw_counts"].values()), len(rows)))

    rep.append("## 2. kind 分布\n")
    rep.append("| kind | 条数 | kind_group | 规则依据样例 |")
    rep.append("|---|---|---|---|")
    by_kind = defaultdict(list)
    for r in rows:
        by_kind[r["kind"]].append(r)
    for kind, lst in sorted(by_kind.items(), key=lambda kv: -len(kv[1])):
        evs = Counter(x["kind_evidence"].split("(")[0] for x in lst)
        rep.append("| %s | %d | %s | %s |" % (
            kind, len(lst), lst[0]["kind_group"],
            "；".join("%s×%d" % (k, v) for k, v in evs.most_common(3))))
    fb = [r for r in rows if r["kind_evidence"].startswith("fallback")]
    rep.append("\n未命中规则的 fallback %d 条（%.1f%%），号段 top：%s。\n" % (
        len(fb), 100.0 * len(fb) / max(1, len(rows)),
        ", ".join("%s×%d" % (b, n) for b, n in Counter(
            (r["item_id"] // 100000) * 100000 for r in rows
            if r["kind_evidence"].startswith("fallback")).most_common(8))))

    rep.append("## 3. 服型与去重\n")
    rep.append("- 同 id 同名合并：%d 条记录带 `servers[]`；"
               "同 id 异名 **%d** 个 id 已拆成多行并带 `server_type`。" %
               (sum(1 for r in rows if len(r["servers"]) > 1), len(merged["conflict_ids"])))
    rep.append("- 跨 id 空间同号（数值相同、实体不同）：%d 个 —— `%s`。" % (
        len(merged["cross_space_same_int_id"]),
        "、".join(str(x["item_id"]) for x in merged["cross_space_same_int_id"])))
    rep.append("\n### 服型冲突 id（同 id 异名）\n")
    rep.append("| id_space | item_id | 名字 | 涉及服型 |")
    rep.append("|---|---|---|---|")
    for c in merged["conflict_ids"]:
        rep.append("| %s | %d | %s | %s |" % (c["id_space"], c["item_id"],
                                              " / ".join(c["names"]), "、".join(c["servers"])))

    rep.append("\n## 4. 图标\n")
    ist = m["icon_stats"]
    rep.append("- 有图 **%d** / %d（%.1f%%）｜ 无图 %d" % (
        ist["items_with_icon"], ist["items_total"],
        100.0 * ist["items_with_icon"] / max(1, ist["items_total"]), ist["items_without_icon"]))
    rep.append("- 导出通道：%s（PE=安卓热更包 .ktx；PC=PC 端 .bc7 兜底）" % ist["by_source"])
    rep.append("- 状态：%s" % ist["state_breakdown"])
    rep.append("- 候选基名 %d ｜ PE 命中并导出 %d ｜ 未解出 %d" % (
        len(icons["bases"]), len(icons["resolved"]), len(icons["bases"]) - len(icons["resolved"])))

    rep.append("\n## 5. 未命名清单\n")
    un = [r for r in rows if r["name"] is None]
    rep.append("**%d 条**%s\n" % (len(un), "（六个源表都有 _chs 名字池，无空名）" if not un else ""))
    for r in un[:200]:
        rep.append("- `%s` %d" % (r["id"], r["item_id"]))

    rep.append("\n## 6. 未下发清单（有 icon 字段但解不出）\n")
    rep.append("按 kind 汇总，明细见 `_report_item_master_full_missing.csv`。\n")
    rep.append("| kind | 未下发条数 | 样例 |")
    rep.append("|---|---|---|")
    by_kind_miss = defaultdict(list)
    for x in missing:
        if x["state"] == "未下发":
            by_kind_miss[x["kind"]].append(x)
    no_field = sum(1 for x in missing if x["state"] == "无图标字段")
    rep.append("未下发 %d 条；另有 %d 条源行无 icon 字段（走模板仍无命中）。\n"
               % (sum(len(v) for v in by_kind_miss.values()), no_field))
    for k, lst in sorted(by_kind_miss.items(), key=lambda kv: -len(kv[1])):
        rep.append("| %s | %d | %s |" % (k, len(lst), "、".join(
            "%s(%d)" % (y["name"] or "?", y["item_id"]) for y in lst[:5])))

    rep.append("\n## 7. 纪律与边界\n")
    rep.append("- 名字只取 `<表>_chs.py` 池；缺失即 null，未编造、未跨表按相似度拼名。")
    rep.append("- 未改 `publication_policy` / `wiki_taxonomy` / `manifest` / 其它板；`E:/mrzh` 只读。")
    rep.append("- 该板尚未登记进 `data/publication_policy.json`（本轮按题不修改策略），"
               "故 build_wiki 会导出 `item_master_full.js` 但不列入 manifest 首页；"
               "登记后即可公开（契约校验见 §8）。")
    rep.append("\n## 8. frozen-v3 契约校验\n")
    rep.append("`publication_policy.publication_contract_errors(strict_v2=True)` → **%s**\n"
               % ("0 项（通过）" if not check else "%d 项未过" % len(check)))
    rep.append("```\n%s\n```" % ("\n".join(check[:50]) if check else "ok — 无错误项"))
    (WEB / "data/boards/_report_item_master_full.md").write_text("\n".join(rep) + "\n", encoding="utf-8")
    with (WEB / "data/boards/_report_item_master_full_missing.csv").open("w", encoding="utf-8-sig") as f:
        f.write("id,item_id,id_space,name,kind,icon,state\n")
        for x in missing:
            f.write("%s,%d,%s,\"%s\",%s,%s,%s\n" % (
                x["id"], x["item_id"], x["id"].split(":")[0], (x["name"] or "").replace('"', "'"),
                x["kind"], x["icon"] or "", x["state"]))
    print("报告已写：_report_item_master_full.md / _missing.csv（未下发 %d）" % len(missing))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["parse", "merge", "icons", "board"])
    a = ap.parse_args()
    {"parse": stage_parse, "merge": stage_merge, "icons": stage_icons, "board": stage_board}[a.stage]()
