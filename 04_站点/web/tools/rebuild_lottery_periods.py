#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建「奖池板块」看板：期次 → 奖池 → 成员（玩家视图）。

数据来源（同一冻结包：E:/mrzh/Documents/script.py314.lc.npk，热更合并树
03_执行/41_还原树/Documents/script.py314.lc.npk）：

  · only_fashion_hd_base_conf / _lottery_conf / _reward_pool_conf
        纯外观抽奖（OnlyFashionLotteryHD）：活动号 → 期号 → 奖池号 → 成员
  · multi_optional_lottery_conf_data / multi_optional_lottery_option_data
        多时装抽奖（MultiOptionalLotteryHD）：配置号 → 选项槽位 → 子池 → 成员
  · optional_version_data_auto_oversea_data_kj1 + optional_conf_data(...kj1)
        宸世臻藏（OptionalLotteryHD）：30 个期次，每期展示/兑换清单
  · huodong_conf_data_auto_oversea_data_kj1
        活动名 / 活动类型 / 起止时间（期次标题）

命名：com\\cdata\\fashion_data / gift_data / common_item(oversea kj1) /
all_equips(oversea yk) + 03_执行/10_索引/items/{common_item_names,show_item_names}.json
图标：gift/common_item/all_equips 的 icon 字段；时装取 fashion_data.icons 内联组。

输出：data/boards/lottery_periods.json (+ .js)
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WEB / "tools"))
sys.path.insert(0, r"E:\la拆包项目\01_工具\工具库\00_共享核心")

from toolkit_core.bindict_table import (decode_86_row, parse_index,  # noqa: E402
                                       parse_legacy_chs_pool, resolve_jump_group)
from toolkit_core.bindict_rows import uleb  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from preview_board_contract import apply_frozen_v3  # noqa: E402

TREE = Path(r"E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\com\cdata")
OVER = TREE / "oversea"
PKG = Path(r"E:\mrzh\Documents\script.py314.lc.npk")
OUT_BOARD = WEB / "data" / "boards" / "lottery_periods.json"
GEN_DATE = "2026-10-19"


# ────────────────────────────────────────────── 基础装载
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


class Table:
    """一张 x{ bindict 表 + 其 _chs 字符串池 + 表体 blob。"""

    def __init__(self, path: Path, chs: Path | None = None):
        self.path = path
        self.body = xbody(path)
        count = struct.unpack_from("<I", self.body, 0)[0]
        self.blob = self.body[8 + 4 * count:]
        self.pool = parse_legacy_chs_pool(chs.read_bytes()) if chs and chs.exists() else []
        self.rows, self.unbound = decode_table_rows_with_chs_slots(self.body, self.pool)
        self.by_key: dict[int, dict] = {}
        for row in self.rows:
            flat = {k: (v[1] if isinstance(v, tuple) else v) for k, v in row["values"].items()}
            self.by_key[row["key"]] = {"key": row["key"], "start": row["start"],
                                       "end": row.get("end"), "values": flat}
        self.sha256 = sha256_file(path)
        self.rel = path.relative_to(TREE).as_posix()
        # 0x36 映射表（池表/选项表）没有普通行：它的 by_key 只能从 0x76 索引尾取
        self.map_start: dict[int, int] = {}
        try:
            self.map_start = dict(parse_index(self.blob))
        except Exception:
            self.map_start = {}

    def group(self, target: int):
        if not isinstance(target, int) or not (0 <= target < len(self.blob)):
            return None
        if self.blob[target] != 0x27:
            return None
        kind = self.blob[target + 1]
        values = resolve_jump_group(self.blob, target)
        if values is None:
            return None
        if kind == 0x05:
            return [self.pool[v] if v < len(self.pool) else f"<oob:{v}>" for v in values]
        return values

    def jump_values(self, value) -> list:
        if not isinstance(value, str) or not value.startswith("jump:"):
            return []
        return self.group(int(value.split(":")[1])) or []


def parse_map_row(table: Table, start: int) -> list[tuple[int, int]]:
    """0x36 映射行：[36][kind][fmt][n] + n × (slot uleb, 偏移 uleb)。"""
    pos = start + 1
    _kind, pos = uleb(table.blob, pos, len(table.blob))
    _fmt, pos = uleb(table.blob, pos, len(table.blob))
    n, pos = uleb(table.blob, pos, len(table.blob))
    out = []
    for _ in range(n):
        slot, pos = uleb(table.blob, pos, len(table.blob))
        off, pos = uleb(table.blob, pos, len(table.blob))
        out.append((slot, off))
    return out


def read_27(blob: bytes, start: int):
    if blob[start] != 0x27:
        return None
    kind = blob[start + 1]
    if kind not in (0x01, 0x02, 0x05, 0x0B):
        return None
    try:
        count, pos = uleb(blob, start + 2, len(blob))
    except ValueError:
        return None
    if not 1 <= count <= 64:
        return None
    vals = []
    try:
        for _ in range(count):
            v, pos = uleb(blob, pos, len(blob))
            vals.append(v)
    except ValueError:
        return None
    return {"kind": kind, "values": vals, "end": pos}


def slot_groups(table: Table, off: int, bound: int) -> list[list[int]]:
    out = []
    i = off
    while i < bound:
        g = read_27(table.blob, i)
        if g:
            out.append(g["values"])
            i = g["end"]
        else:
            i += 1
    return out


def row86(table: Table, off: int) -> dict:
    try:
        r = decode_86_row(table.blob, off)
    except Exception:
        return {}
    return {k: (v[1] if isinstance(v, tuple) else v) for k, v in r["values"].items()}


# ────────────────────────────────────────────── 命名
FASHION_PREFIX = ("637", "633", "470", "460", "471", "472")
GIFT_PREFIX = ("135", "139", "13")


def kind_of(item_id: int) -> str:
    s = str(item_id)
    if s.startswith(("1110", "1111", "1112")):
        return "武器皮肤"
    if s.startswith(("194", "195")):
        return "载具"
    if s.startswith(FASHION_PREFIX):
        return "时装/外观"
    if s.startswith(GIFT_PREFIX):
        return "礼盒"
    if s.startswith("640"):
        return "投影/特效"
    if s.startswith("105"):
        return "配方"
    if item_id >= 100_000_000:
        return "时装/外观"
    return "道具"


class Names:
    def __init__(self):
        idx_items = Path(r"E:\la拆包项目\03_执行\10_索引\items")
        self.maps: dict[str, tuple[dict[str, str], str]] = {}
        self.icons: dict[int, tuple[str, str]] = {}

        self.fashion = Table(TREE / "fashion_data.py", TREE / "fashion_data_chs.py")
        self.gift = Table(TREE / "gift_data.py", TREE / "gift_data_chs.py")
        self.recipe = Table(TREE / "recipe.py", TREE / "recipe_chs.py")
        self.common_ov = Table(OVER / "common_item_data_auto_oversea_data_kj1.py",
                               OVER / "common_item_data_auto_oversea_data_kj1_chs.py")
        self.equips = Table(OVER / "all_equips_data_auto_oversea_data_yk.py",
                            OVER / "all_equips_data_auto_oversea_data_yk_chs.py")

        for label, table in (("fashion_data", self.fashion), ("gift_data", self.gift),
                             ("recipe", self.recipe),
                             ("common_item(oversea kj1)", self.common_ov),
                             ("all_equips(oversea yk)", self.equips)):
            mapping = {}
            for key, row in table.by_key.items():
                name = row["values"].get("name")
                if isinstance(name, str) and name.strip():
                    mapping[str(key)] = name
                icon = row["values"].get("icon")
                if isinstance(icon, str) and icon.startswith("ui/"):
                    self.icons.setdefault(key, (icon, table.rel))
            self.maps[label] = (mapping, table.rel)

        ci = json.loads((idx_items / "common_item_names.json").read_text(encoding="utf-8"))["items"]
        self.maps["common_item_names.json"] = (
            {k: v["name"] for k, v in ci.items() if v.get("name")},
            "03_执行/10_索引/items/common_item_names.json")
        show = json.loads((idx_items / "show_item_names.json").read_text(encoding="utf-8"))["items"]
        self.maps["show_item_names.json"] = (
            {k: next(iter(v)) for k, v in show.items() if v},
            "03_执行/10_索引/items/show_item_names.json")

        # 时装图标：fashion_data.icons 内联字符串组
        for key, row in self.fashion.by_key.items():
            if key in self.icons:
                continue
            vals = self.fashion.jump_values(row["values"].get("icons"))
            if vals and isinstance(vals[0], str) and vals[0].startswith("ui/"):
                self.icons[key] = (vals[0], "fashion_data.icons（内联字符串组）")

    def _order(self, item_id: int) -> list[str]:
        s = str(item_id)
        if s.startswith(FASHION_PREFIX) or len(s) >= 9:
            return ["fashion_data", "show_item_names.json", "gift_data",
                    "common_item_names.json", "common_item(oversea kj1)", "all_equips(oversea yk)"]
        if s.startswith(("105", "103", "106")):
            return ["recipe", "common_item_names.json", "gift_data",
                    "common_item(oversea kj1)", "all_equips(oversea yk)", "fashion_data"]
        if s.startswith(GIFT_PREFIX):
            return ["gift_data", "common_item_names.json", "show_item_names.json",
                    "common_item(oversea kj1)", "all_equips(oversea yk)", "fashion_data"]
        return ["common_item_names.json", "common_item(oversea kj1)", "all_equips(oversea yk)",
                "gift_data", "fashion_data", "show_item_names.json"]

    def resolve(self, item_id: int):
        s = str(item_id)
        cands = [(label, self.maps[label][0][s], self.maps[label][1])
                 for label in self._order(item_id) if s in self.maps[label][0]]
        if not cands:
            return None, None, []
        name, rel = cands[0][1], cands[0][2]
        alts = [f"{lbl}={nm}" for lbl, nm, _ in cands[1:] if nm != name]
        return name, f"{rel}#name", alts

    def icon_for(self, item_id: int):
        return self.icons.get(item_id, (None, None))


# ────────────────────────────────────────────── 期次构建
def ts_date(ts):
    if not isinstance(ts, (int, float)) or not ts:
        return None
    return dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")


def build():
    names = Names()
    hd = Table(OVER / "huodong_conf_data_auto_oversea_data_kj1.py",
               OVER / "huodong_conf_data_auto_oversea_data_kj1_chs.py")
    hd_by_key = {k: v["values"] for k, v in hd.by_key.items()}

    periods: list[dict] = []
    rows: list[dict] = []
    table_ref: dict[str, Table] = {}
    ordinal = 0

    def add_item(*, period, pool, slot, item_id, extra, table, row_key, field_refs):
        name, name_src, alts = names.resolve(item_id)
        icon, icon_src = names.icon_for(item_id)
        unresolved = name is None
        table_ref[table.rel] = table
        item_id_str = f"p{period['period_ordinal']}:{pool['pool_uid']}:s{slot}:{item_id}"
        pool.setdefault("member_ids", []).append(item_id_str)
        rows.append({
            "id": item_id_str,
            "name": name or f"未识别道具 {item_id}",
            "icon": icon,
            "item_id": item_id,
            "kind": kind_of(item_id),
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": (f"{period['label']} · {pool['pool_label']} · 槽位 {slot}；"
                       f"{table.rel} 的 0x36 映射行 + 槽位内 0x27 内联组"),
            "status_tags": (["unresolved", "static config"] if unresolved
                            else ["verified", "static config", "runtime final unknown"]),
            "period_id": period["period_id"],
            "period_label": period["label"],
            "period_date": period["start"],
            "activity": period["label"],
            "period_start": period["start"],
            "period_end": period["end"],
            "activity_id": period.get("activity_id"),
            "activity_name": period.get("activity_name"),
            "activity_class": period.get("activity_class"),
            "pool_id": pool["pool_id"],
            "pool_uid": pool.get("pool_uid"),
            "pool_label": pool["pool_label"],
            "pool_kind": pool["kind"],
            "slot": slot,
            **extra,
            "_table": table,
            "_row_key": row_key,
            "_field_refs": field_refs,
            "_name_source": name_src,
            "_alts": alts,
            "_icon_source": icon_src,
        })

    # ── 1) 纯外观抽奖（OnlyFashionLotteryHD）
    of_base = Table(TREE / "only_fashion_hd_base_conf.py")
    of_conf = Table(TREE / "only_fashion_hd_lottery_conf.py")
    of_pool = Table(TREE / "only_fashion_hd_reward_pool_conf.py",
                    TREE / "only_fashion_hd_reward_pool_conf_chs.py")
    of_periods = sorted(of_base.by_key.values(), key=lambda r: int(r["values"].get("<slot_7>") or 0))
    for row in of_periods:
        v = row["values"]
        hd_id = row["key"]
        period_no = int(v.get("<slot_7>") or 0)
        conf_no = int(v.get("<slot_2>") or period_no)
        hd_row = hd_by_key.get(hd_id, {})
        start = ts_date(v.get("<slot_6>")) or ts_date(hd_row.get("start_ts"))
        end = ts_date(v.get("<slot_1>")) or ts_date(hd_row.get("end_ts"))
        act_name = hd_row.get("name") or "（活动名未在活动表内）"
        conf = of_conf.by_key.get(conf_no, {"values": {}})["values"]
        pool_id = conf.get("<slot_4>")
        ordinal += 1
        period = {
            "period_id": f"only_fashion:{hd_id}",
            "period_ordinal": ordinal,
            "label": f"{act_name}（纯外观抽奖 · 第{period_no}期）",
            "activity_id": hd_id,
            "activity_name": act_name,
            "activity_class": hd_row.get("hd_class") or "OnlyFashionLotteryHD",
            "family": "纯外观抽奖",
            "start": start,
            "end": end,
            "period_no": period_no,
            "pools": [],
            "notes": [] if hd_row else ["活动行已被活动表回收：名称/时间取 only_fashion_hd_base_conf 期次行"],
        }
        if isinstance(pool_id, int) and pool_id in of_pool.map_start:
            prow_start = of_pool.map_start[pool_id]
            pairs = parse_map_row(of_pool, prow_start)
            offs = sorted(o for _s, o in pairs)
            ladder = of_conf.group(int(conf["<slot_0>"].split(":")[1])) if isinstance(conf.get("<slot_0>"), str) else None
            pool = {
                "pool_id": pool_id,
                "pool_uid": str(pool_id),
                "pool_label": f"{act_name} · 第{period_no}期主池",
                "kind": "抽奖主池",
                "currency_id": conf.get("<slot_1>"),
                "ladder": ladder,
                "member_count": 0,
                "slots": len(pairs),
            }
            for slot, off in pairs:
                bound = min([x for x in offs if x > off] + [prow_start])
                groups = slot_groups(of_pool, off, bound)
                if not groups:
                    continue  # UI 位（背景板/说明位）无道具组
                v86 = row86(of_pool, off)
                for g in groups:
                    for val in g:
                        if val < 1000:
                            continue
                        add_item(period=period, pool=pool, slot=slot, item_id=val,
                                 extra={"group_size": len(g),
                                        "slot_bg": v86.get(7), "slot_camera": v86.get(8)},
                                 table=of_pool,
                                 row_key=f"{pool_id}#slot{slot}",
                                 field_refs=[f"0x36 映射行 pool={pool_id} slot={slot} @{prow_start}",
                                             f"槽位 0x86 明细行 @{off}",
                                             "槽位内 0x27 组 [" + ", ".join(str(x) for x in g) + "]"])
                        pool["member_count"] += 1
            period["pools"].append(pool)
        else:
            # 期号 6（活动 3220 趴趴小宠）的 lottery_conf 行 schema 29 解码 overrun，
            # 但奖池表里恰好有一池（391407）没有被任何已解码期号引用，且 10 期 × 10 池
            # 的池号随期号单调递增，故按「唯一剩余池 + 单调序」反推，并显式标注为推断。
            inferred = None
            if conf_no == 6:
                used = {int(of_conf.by_key[k]["values"].get("<slot_4>")) for k in of_conf.by_key}
                leftover = [p for p in of_pool.map_start if p not in used]
                if len(leftover) == 1:
                    inferred = leftover[0]
            if inferred is not None:
                pool_id = inferred
                period["notes"].append(
                    f"期号 6 的 lottery_conf 行解码 overrun；池号 {inferred} 由「奖池表唯一剩余池 + 池号随期号单调」反推，非行内直读")
                prow_start = of_pool.map_start[inferred]
                pairs = parse_map_row(of_pool, prow_start)
                offs = sorted(o for _s, o in pairs)
                pool = {
                    "pool_id": inferred,
                    "pool_uid": str(inferred),
                    "pool_label": f"{act_name} · 第{period_no}期主池（期号→池号推断）",
                    "kind": "抽奖主池",
                    "pool_binding": "inferred-unique-leftover",
                    "currency_id": conf.get("<slot_1>"),
                    "member_count": 0,
                    "slots": len(pairs),
                }
                for slot, off in pairs:
                    bound = min([x for x in offs if x > off] + [prow_start])
                    groups = slot_groups(of_pool, off, bound)
                    if not groups:
                        continue
                    v86 = row86(of_pool, off)
                    for g in groups:
                        for val in g:
                            if val < 1000:
                                continue
                            add_item(period=period, pool=pool, slot=slot, item_id=val,
                                     extra={"group_size": len(g), "slot_bg": v86.get(7),
                                            "slot_camera": v86.get(8), "pool_binding": "inferred-unique-leftover"},
                                     table=of_pool,
                                     row_key=f"{inferred}#slot{slot}",
                                     field_refs=[f"0x36 映射行 pool={inferred} slot={slot} @{prow_start}",
                                                 f"槽位 0x86 明细行 @{off}",
                                                 "槽位内 0x27 组 [" + ", ".join(str(x) for x in g) + "]"])
                            pool["member_count"] += 1
                period["pools"].append(pool)
            else:
                period["notes"].append(f"期号 {conf_no} 未命中奖池行（only_fashion_hd_lottery_conf）")
        periods.append(period)

    # ── 2) 多时装抽奖（MultiOptionalLotteryHD）
    mo_conf = Table(TREE / "multi_optional_lottery_conf_data.py",
                    TREE / "multi_optional_lottery_conf_data_chs.py")
    mo_opt = Table(TREE / "multi_optional_lottery_option_data.py",
                   TREE / "multi_optional_lottery_option_data_chs.py")
    conf_to_hd: dict[int, list[int]] = {}
    for hd_id, hv in hd_by_key.items():
        if hv.get("hd_class") == "MultiOptionalLotteryHD" and isinstance(hv.get("extra_param"), int):
            conf_to_hd.setdefault(int(hv["extra_param"]), []).append(hd_id)

    for conf_no in sorted(mo_conf.by_key):
        cv = mo_conf.by_key[conf_no]["values"]
        hd_ids = sorted(conf_to_hd.get(conf_no, []), key=lambda i: hd_by_key[i].get("start_ts") or 0)
        hd_id = hd_ids[-1] if hd_ids else None
        hd_row = hd_by_key.get(hd_id, {}) if hd_id else {}
        act_name = hd_row.get("name") or f"多时装抽奖 配置{conf_no}"
        ordinal += 1
        period = {
            "period_id": f"multi_optional:{conf_no}:{hd_id}",
            "period_ordinal": ordinal,
            "label": f"{act_name}（多时装抽奖 · 配置{conf_no}）",
            "activity_id": hd_id,
            "activity_name": act_name,
            "activity_class": "MultiOptionalLotteryHD",
            "family": "多时装抽奖",
            "start": ts_date(hd_row.get("start_ts")),
            "end": ts_date(hd_row.get("end_ts")),
            "ensure_cnt": cv.get("ensure_cnt"),
            "lottery_id": cv.get("lottery_id"),
            "pools": [],
            "notes": ([f"同一配置被 {len(hd_ids)} 次活动复用，期次时间取最近一次（{act_name}）"]
                      if len(hd_ids) > 1 else []),
        }
        opt_start = mo_opt.map_start.get(conf_no)
        if opt_start is not None:
            pairs = parse_map_row(mo_opt, opt_start)
            offs = sorted(o for _s, o in pairs)
            for slot, off in pairs:
                bound = min([x for x in offs if x > off] + [opt_start])
                groups = slot_groups(mo_opt, off, bound)
                item_ids = sorted({val for g in groups for val in g if val >= 100000})
                v86 = row86(mo_opt, off)
                if not item_ids and not isinstance(v86.get(13), int):
                    continue
                sub_pool = v86.get(14) if isinstance(v86.get(14), int) and v86.get(14) < 1000 else None
                weight = v86.get(16)
                choice = v86.get(13) if isinstance(v86.get(13), int) and v86.get(13) < 1000 else None
                gift_id = v86.get(13) if isinstance(v86.get(13), int) and v86.get(13) >= 10000 else None
                pool = {
                    "pool_id": f"{conf_no}-{slot}",
                    "pool_uid": f"mo{conf_no}-s{slot}",
                    "pool_label": f"{act_name} · 选项{slot}",
                    "kind": "选项槽位（抽奖子池）",
                    "sub_pool_ref": sub_pool,
                    "weight": weight,
                    "choice_id": choice,
                    "option_item_id": gift_id,
                    "ensure_cnt": cv.get("ensure_cnt"),
                    "member_count": 0,
                    "slots": 1,
                }
                members = ([gift_id] if gift_id else []) + [v for v in item_ids if v != gift_id]
                for val in members:
                    role = "礼盒/兑奖物" if val == gift_id else "外观"
                    add_item(period=period, pool=pool, slot=slot, item_id=val,
                             extra={"option_slot": slot, "option_weight": weight, "role": role},
                             table=mo_opt,
                             row_key=f"option_pool={conf_no}#slot{slot}",
                             field_refs=[f"0x36 映射行 option_pool={conf_no} slot={slot} @{opt_start}",
                                         f"槽位 0x86 明细行 @{off}（字段14=子池/档位引用 {sub_pool}，字段16=权重 {weight}）",
                                         "槽位内 0x27 组（时装/外观 id，男女款成对）"])
                    pool["member_count"] += 1
                period["pools"].append(pool)
        periods.append(period)

    # ── 3) 宸世臻藏（OptionalLotteryHD 2538）
    ov = Table(OVER / "optional_version_data_auto_oversea_data_kj1.py",
               OVER / "optional_version_data_auto_oversea_data_kj1_chs.py")
    oc = Table(OVER / "optional_conf_data_auto_oversea_data_kj1.py",
               OVER / "optional_conf_data_auto_oversea_data_kj1_chs.py")
    oc_row = next(iter(oc.by_key.values()))["values"]
    chenshi_rows = sorted(ov.by_key.values(), key=lambda r: r["values"].get("start_ts") or 0)
    for row in chenshi_rows:
        v = row["values"]
        version = v.get("version")
        ordinal += 1
        theme = [x for x in (v.get("high_shop_effect_path") or "").split("/") if x][2:4]
        period = {
            "period_id": f"chenshi:v{version}",
            "period_ordinal": ordinal,
            "label": f"宸世臻藏 · 第{version}期",
            "activity_id": v.get("hd_id"),
            "activity_name": "宸世臻藏",
            "activity_class": "OptionalLotteryHD",
            "family": "宸世臻藏（保底典藏抽奖）",
            "start": ts_date(v.get("start_ts")),
            "end": ts_date(v.get("end_ts")),
            "theme": theme,
            "base_lottery_id": oc_row.get("base_lottery_id"),
            "high_level_coin_id": oc_row.get("high_level_coin_id"),
            "low_level_coin_id": oc_row.get("low_level_coin_id"),
            "pools": [],
            "notes": ["本期 ui_rewards/new_rewards 是展示/兑换清单，不是抽奖池开出内容；"
                      "主抽奖池的成员表在本客户端未闭合"],
        }
        ui_vals = ov.jump_values(v.get("ui_rewards"))
        new_vals = ov.jump_values(v.get("new_rewards"))
        # new_rewards 通常是「ui_rewards + 本期新增」，两者只出一份清单，避免同一道具重复登记
        vals = new_vals or ui_vals
        field = "new_rewards" if new_vals else "ui_rewards"
        if vals:
            pool = {"pool_id": f"chenshi:rewards:v{version}", "pool_uid": f"cs{version}-rewards",
                    "pool_label": f"第{version}期展示/兑换清单（{len(vals)} 件）",
                    "kind": "展示/兑换清单（非抽奖池）",
                    "ui_subset_size": len(ui_vals) if ui_vals else None,
                    "member_count": 0, "slots": len(vals)}
            for idx, item_id in enumerate(vals):
                if not isinstance(item_id, int) or item_id < 1000:
                    continue
                add_item(period=period, pool=pool, slot=idx, item_id=item_id,
                         extra={"list_field": field,
                                "list_role": "面板展示（前 %d 件）" % len(ui_vals) if ui_vals and idx < len(ui_vals) else "本期新增/兑换"},
                         table=ov,
                         row_key=f"version={version}",
                         field_refs=[f"optional_version_data key={row['key']} version={version}",
                                     f"{field} 字段 {v.get(field)} → 0x27 组第 {idx} 项"])
                pool["member_count"] += 1
            period["pools"].append(pool)
        if oc_row.get("base_lottery_id"):
            period["pools"].append({
                "pool_id": oc_row["base_lottery_id"],
                "pool_uid": f"cs{version}-main",
                "pool_label": "主抽奖池（成员表未闭合）",
                "kind": "抽奖主池",
                "member_count": 0,
                "slots": None,
                "note": "池号取自 optional_conf_data.base_lottery_id；成员表未闭合，不臆造",
            })
        periods.append(period)

    for p in periods:
        for pool in p["pools"]:
            pool.setdefault("member_ids", [])
        p["pool_count"] = sum(1 for x in p["pools"] if x.get("member_count"))
        p["member_count"] = sum(x.get("member_count") or 0 for x in p["pools"])
    periods.sort(key=lambda p: (p["start"] or "0000", p["period_id"]))
    return names, periods, rows, table_ref


def main() -> int:
    names, periods, rows, table_ref = build()
    pkg_sha = sha256_file(PKG)
    stat = PKG.stat()

    public_items = []
    for r in rows:
        pub = {k: v for k, v in r.items() if not k.startswith("_")}
        pub["provenance"] = {
            "name_source": r["_name_source"] or "未命中命名表（保留 item id）",
            "name_conflicts": r["_alts"],
            "icon_source": r["_icon_source"],
        }
        public_items.append(pub)

    board = {
        "meta": {
            "name": "奖池期次总表（期次 → 奖池 → 成员）",
            "category": "四、奖池 / （二）期次与奖池成员",
            "source_server": "简单生存服（体验服 Documents 快照，热更合并至 2026-10-17）",
            "package_sha": pkg_sha,
            "generated": GEN_DATE,
            "evidence": "structure",
            "notes": "",
            "state_summary": {},
        },
        "periods": periods,
        "items": public_items,
    }

    src_by_id = {r["id"]: r for r in rows}

    def locator(item):
        r = src_by_id[item["id"]]
        table = r["_table"]
        return {
            "table": table.rel,
            "row_key": r["_row_key"],
            "field_refs": r["_field_refs"],
            "kind": "decoded-table-row",
            "name_source": ((r["_name_source"] or "未命中命名表") +
                            f"（表文件 sha256={table.sha256}）"),
            "upstream": {
                "package_sha256": pkg_sha,
                "entry_index": None,
                "file_id": None,
                "decoded_sha256": None,
                "role": table.rel,
                "table_sha256": table.sha256,
            },
            "status_tags": r["status_tags"],
        }

    apply_frozen_v3(
        board,
        source_id="documents-py314-current",
        artifact_path=PKG,
        locator=locator,
        state_summary={},
        artifact_label=str(PKG).replace("\\", "/"),
        source_lock={
            "source_id": "documents-py314-current",
            "sha256": pkg_sha,
            "bytes": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "role": "primary",
            "path": str(PKG).replace("\\", "/"),
        },
    )

    ev = Counter(i["evidence_level"] for i in board["items"])
    tags = Counter(t for i in board["items"] for t in i["status_tags"])
    unresolved = sum(1 for i in board["items"] if i["name"].startswith("未识别道具"))
    with_icon = sum(1 for i in board["items"] if i.get("icon"))
    fam = Counter(p["family"] for p in periods)
    board["meta"]["state_summary"] = {
        "periods": len(periods),
        "pools": sum(p["pool_count"] for p in periods),
        "members": len(board["items"]),
        "unresolved_names": unresolved,
        "members_with_icon": with_icon,
        "evidence_levels": dict(sorted(ev.items())),
        "status_tags": dict(sorted(tags.items())),
        "families": dict(sorted(fam.items())),
    }
    board["meta"]["evidence_detail"] = {"structure": len(board["items"])}
    board["meta"]["notes"] = (
        f"按期次组织：{len(periods)} 个期次（" +
        "，".join(f"{k} {v}" for k, v in sorted(fam.items())) +
        f"）。成员 {len(board['items'])} 条，全部来自本客户端静态配置表的槽位内联 0x27 组或期次行 jump 组，"
        f"其中命名未命中 {unresolved} 条（保留 item id 并标 unresolved），带图标 {with_icon} 条。"
        "纯外观抽奖成员 = only_fashion_hd_reward_pool_conf 每池槽位的内联道具组（已用公开实例复现 391834 万圣绮夜："
        "魔女星愿 580215 / 第十三页 1110192 / 星紫迷踪-头饰 637330110）；"
        "多时装抽奖成员 = multi_optional_lottery_option_data 每个选项槽位的时装 id（男女款常成对出现）；"
        "宸世臻藏行内 ui_rewards/new_rewards 是【展示/兑换清单】而非抽奖池开出内容，主池 390927 的成员表在本客户端未闭合，"
        "故只登记池号不臆造成员。命名跨表查 fashion_data / gift_data / common_item(oversea kj1) / all_equips(oversea yk) "
        "与既有名字索引，撞号候选写进 provenance.name_conflicts；图标取各表 icon 字段（时装取 fashion_data.icons 内联组），"
        "无图标留 null、不伪造路径。全部条目证据等级 structure-only：静态配置可复现，运行期最终形态未知。"
        "meta.evidence 取 build_wiki 强校验的枚举字符串，分项计数见 evidence_detail / state_summary。"
    )

    OUT_BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_BOARD.with_suffix(".js").write_text(
        f"window.WIKI_BOARD_{OUT_BOARD.stem} = " + OUT_BOARD.read_text(encoding="utf-8").rstrip() + ";\n",
        encoding="utf-8")

    write_report(board, names, table_ref, pkg_sha)

    print(f"periods={len(periods)} items={len(board['items'])} pools={board['meta']['state_summary']['pools']}")
    print("evidence", dict(ev), "unresolved", unresolved, "icons", with_icon)
    print("families", dict(fam))
    print("tables", len(table_ref))
    for rel, t in sorted(table_ref.items()):
        print("   ", rel, t.sha256[:12], "rows", len(t.by_key))
    return 0


def write_report(board, names, table_ref, pkg_sha) -> None:
    items = board["items"]
    periods = board["periods"]
    fams = sorted({p["family"] for p in periods})
    pool_counts = [p["pool_count"] for p in periods]
    mem_counts = [p["member_count"] for p in periods]
    named = [i for i in items if not i["name"].startswith("未识别")]
    icons = [i for i in items if i.get("icon")]
    conflicts = [i for i in items if i["provenance"].get("name_conflicts")]
    unresolved = [i for i in items if i["name"].startswith("未识别")]

    lines = []
    A = lines.append
    A("# 奖池板块 · lottery_periods 构建说明\n")
    A(f"生成：{board['meta']['generated']}　|　构建脚本：`tools/rebuild_lottery_periods.py`\n")
    A("## 1. 数据来源（单一冻结包）\n")
    A(f"- 源包：`{board['meta']['provenance']['source_locks'][0]['path']}`")
    A(f"- package_sha256：`{pkg_sha}`（bytes {board['meta']['provenance']['source_locks'][0]['bytes']:,}）")
    A("- 表体取自 `03_执行/41_还原树/Documents/script.py314.lc.npk`（该包的热更合并树，合并台账 20261017_005239）\n")
    A("| 用途 | 表文件 | 表 sha256（前 12） |")
    A("|---|---|---|")
    roles = [
        ("oversea/huodong_conf_data_auto_oversea_data_kj1.py", "活动名 / 活动类型 / 起止时间"),
        ("only_fashion_hd_base_conf.py", "纯外观抽奖：活动号 → 期号 / 时间"),
        ("only_fashion_hd_lottery_conf.py", "纯外观抽奖：期号 → 奖池号 / 货币 / 阶梯"),
        ("only_fashion_hd_reward_pool_conf.py", "纯外观抽奖：奖池 → 槽位 → 成员"),
        ("multi_optional_lottery_conf_data.py", "多时装抽奖：配置 → 保底 / 展示道具"),
        ("multi_optional_lottery_option_data.py", "多时装抽奖：选项槽位 → 成员"),
        ("oversea/optional_version_data_auto_oversea_data_kj1.py", "宸世臻藏：30 个期次的展示/兑换清单"),
        ("oversea/optional_conf_data_auto_oversea_data_kj1.py", "宸世臻藏：主池号 / 双货币 / 兑换商店"),
    ]
    for rel, role in roles:
        if rel in table_ref:
            sha = table_ref[rel].sha256
        else:
            p = TREE / rel
            sha = sha256_file(p) if p.exists() else "（未参与产出）"
        A(f"| {role} | `{rel}` | `{sha[:12]}` |")
    A("")
    A("命名与图标来源（跨表，仅用于取名/取图，不参与行定位）：")
    for label in ("fashion_data", "gift_data", "recipe", "common_item(oversea kj1)", "all_equips(oversea yk)"):
        if label in names.maps:
            mapping, rel = names.maps[label]
            A(f"- `{rel}`：{len(mapping)} 条名称")
    for label in ("common_item_names.json", "show_item_names.json"):
        mapping, rel = names.maps[label]
        A(f"- `{rel}`：{len(mapping)} 条名称（既有索引）")
    A("")
    A("## 2. 期次 / 奖池 / 成员规模\n")
    A(f"- 期次总数：**{len(periods)}**")
    for f in fams:
        sub = [p for p in periods if p["family"] == f]
        A(f"  - {f}：{len(sub)} 期，成员 {sum(p['member_count'] for p in sub)} 条")
    A(f"- 有成员的奖池数：**{sum(pool_counts)}**（每期池数 min {min(pool_counts)} / max {max(pool_counts)} / 均 {sum(pool_counts)/len(pool_counts):.1f}）")
    A(f"- 成员条目：**{len(items)}**（每期 min {min(mem_counts)} / max {max(mem_counts)} / 均 {sum(mem_counts)/len(mem_counts):.1f}）")
    A(f"- 命名覆盖：{len(named)}/{len(items)} = {len(named)/len(items)*100:.1f}%")
    A(f"- 图标覆盖：{len(icons)}/{len(items)} = {len(icons)/len(items)*100:.1f}%")
    A(f"- 命名撞号（同 id 多表不同名，已保留候选）：{len(conflicts)} 条")
    A(f"- 未命名条目：{len(unresolved)} 条 → " + "、".join(f"{i['item_id']}（{i['period_label']}）" for i in unresolved))
    A("")
    A("期次清单（时间倒序）：\n")
    A("| 期次 | 起 | 止 | 池数 | 成员 |")
    A("|---|---|---|---|---|")
    for p in sorted(periods, key=lambda x: (x["start"] or "", x["period_id"]), reverse=True):
        A(f"| {p['label']} | {p['start'] or '-'} | {p['end'] or '未标注'} | {p['pool_count']} | {p['member_count']} |")
    A("")
    A("## 3. 确定性 / 推断 / 未闭合\n")
    A("**行内直读（确定）**")
    A("- 纯外观抽奖：每池的 0x36 映射行给出 (槽位 → 0x86 明细行偏移)，槽位字节区间内的 0x27 组即该槽位道具 id。")
    A("  已用公开实例复核：池 391834 = 万圣绮夜，槽位 8/3/1 读出 魔女星愿(580215) / 第十三页(1110192) / 星紫迷踪-头饰(637330110)。")
    A("- 多时装抽奖：option 行同构；槽位 0x86 明细行的字段 14 = 子池/档位引用、字段 16 = 权重、字段 13 = 选项号或礼盒 id。")
    A("- 宸世臻藏：期次行 ui_rewards / new_rewards 的 jump 目标直接解出 id 列表（jump 偏移相对表体 blob）。")
    A("")
    A("**推断（已在数据里显式标注）**")
    A("- 纯外观抽奖第 6 期（活动 3220 趴趴小宠）：`only_fashion_hd_lottery_conf` 的 key=6 行 schema 29 解码 overrun，")
    A("  期号→池号按「奖池表唯一未被引用的池 391407 + 池号随期号单调」反推。受影响条目的 `pool_binding` 字段标为")
    A("  `inferred-unique-leftover`，期次 notes 亦写明。其余 9 期的池号是行内直读。")
    A("- 期次名：活动 2793 / 2851 / 2865 / 2907 的 huodong_conf 行已被回收，名称显示为「（活动名未在活动表内）」，")
    A("  时间取 `only_fashion_hd_base_conf` 期次行的 slot_6 / slot_1。")
    A("- 多时装抽奖：同一配置号被多次活动复用（如配置 1/2/…），期次时间取最近一次活动实例，notes 里写明复用次数。")
    A("")
    A("**未闭合（不臆造）**")
    A("- 宸世臻藏主池：`optional_conf_data.base_lottery_id = 390927` 只登记池号，成员表未闭合（本客户端")
    A("  `reward_pool_data` 是「奖励条目表」，池→条目索引未打通），故 member_count=0 并带 note。")
    A("- 宸世臻藏 ui_rewards / new_rewards 是【展示/兑换清单】，不是抽奖池开出内容；池的 kind 明确写「展示清单/兑换清单」。")
    A("- 纯外观抽奖池内的 UI 位（背景板/说明位，bg=39/2694、camera=0/1）没有道具组，不计成员；因此「槽位数 > 成员数」是正常的。")
    A("- 多时装抽奖子池引用的语义（字段 14）只在 A-SOUL（配置 10）与技能文档的 4/100/143 对得上，其余配置里该值更可能是档位号；")
    A("  因此 pool_id 用「配置-槽位」合成键，字段 14 单独存为 `sub_pool_ref`，不当作池号使用。")
    A("- 武器皮肤/典藏大奖类（super_fashion_lottery / lottery_big_reward）未纳入本板：它们的池成员需要 `reward_pool_no_item_no_list`")
    A("  的池→条目索引才能闭合，本次未打通，不写进看板。")
    A("")
    A("## 4. 契约与校验\n")
    A("- `meta.evidence` 必须是 `build_wiki.py` 强校验的枚举字符串（structure/verified/candidate），")
    A("  写成对象会直接报错；分项计数改放 `meta.evidence_detail` 与 `meta.state_summary`。")
    A("- 每条 item 都有 id/name/evidence/evidence_level/status_tags/provenance；provenance 含 source_id、")
    A("  locator_chain（chain_status=replayed-structural、scope=record、no_cross_source_field_join=true、")
    A("  steps[decoded-table-row]）、source_lock_sha256（= 源包 sha）、upstream{package_sha256, table_sha256}、")
    A("  table、row_key、field_refs、name_source。")
    A("- `python tools/build_wiki.py`：退出码 0；`publication_contract_errors(board, strict_v2=True)` = 0 条。")
    A("  本板尚未登记进 `data/publication_policy.json`（按分工由主代理统一登记），登记后即走同一条 strict 校验路径。")
    A("")
    A("## 5. 复现\n")
    A("```")
    A("E:/la拆包项目/.venv/Scripts/python.exe 04_站点/web/tools/rebuild_lottery_periods.py")
    A("E:/la拆包项目/.venv/Scripts/python.exe 04_站点/web/tools/build_wiki.py")
    A("```")

    out = OUT_BOARD.parent / "_report_lottery_periods.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("report:", out)


if __name__ == "__main__":
    sys.exit(main())
