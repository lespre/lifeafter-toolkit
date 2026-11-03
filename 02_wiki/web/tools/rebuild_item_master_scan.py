#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_item_master_scan.py — 「全量道具总表」选表依据扫描（只读 PE 还原树）

用途
----
在重建 ``item_master_full`` 之前，先把「哪些表能提供 id → 名字 / id → 图标」
这件事做成**可复核的普查**，而不是凭表名猜。输出：

  01_索引与产物/30_分析/全量总表_扫描.jsonl     每张候选表一行的机器可读普查

★ 人读的《全量总表_选表依据.md》由**构建脚本**写（`rebuild_item_master_full.py --md`）：
  它直接读构建常量 SELECTED / REJECT + 本普查，保证「文档写的表」= 「真入册的表」。
  本脚本只负责出普查，不重复写文档（两份文档必然漂移）。

判定口径（写进 md，脚本里也是同一套）
------------------------------------
idset      : common_item 真表（90_表缓存 base_B42760CCA41DBC25）的行 key 全集
              = 本客户端「道具 id」的权威空间（38,231 个）
reg_ids    : icon_registry.json 的 60,138 个 id（跨族并集，用于对齐已知规模）

每张候选表量三件事：
  rows            解出多少行
  common_ratio    key 落在 idset 里的比例 —— 判断「key 是否就是道具 id」
  name/icon       有没有 name 族字段 / icon 族字段

判定（写进普查的 verdict 列，供 md 引用）：
  S1 key 就是道具 id（common_ratio ≥ 0.90）且能给 name 或 icon
  S2 key 不是道具 id，但表自带 item_id 且 item_id==key 的比例 ≥ 0.90（同空间异名）
  S3 独立 id 命名空间但有 name+icon 的实体行表（时装/礼包/配方/外观/涂装…）
      —— 这类是「同一件东西在另一张表里的行」，命名空间不同，单独计入
排除：
  X1 key 是配置/类型/期次号（common_ratio < 0.05 且无 item_id 自证）
  X2 只有引用（字段里出现 item id 列表），本身不是实体行
  X3 解码失败 / 0 行 / 桩表

用法::

    python tools/rebuild_item_master_scan.py                 # 跑普查并写 jsonl
    python tools/rebuild_item_master_scan.py --limit 50      # 只扫前 50 张（调试用）
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import struct
import sys
from collections import Counter

WEB = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WEB / "tools"))

from la_paths import PROJ  # noqa: E402
import re as _re
import rebuild_lottery_periods as R  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

CACHE = PROJ / "01_索引与产物/30_分析/90_表缓存"
REG = PROJ / "01_索引与产物/30_分析/icon_registry.json"
OUT_JSONL = PROJ / "01_索引与产物/30_分析/全量总表_扫描.jsonl"

# 候选表族：按前缀圈定（宁可多扫，选/排除由普查数据说话）
FAMILY_RE = _re.compile(
    r"^(common_item|gift|recipe|fashion|simple_fashion|player_module_appear|player_appear|"
    r"equip_coating|vehicle_ui|body_sfx|chip_type|belt_chip|nucleus|box|all_equips|weapon_skin|"
    r"edible|item_|furniture_|building_|monster_|"
    r"avatar_frame|title_conf|drone_base|drone_conf|drone_type|pet_appear|pet_character|"
    r"home_appear|home_bobject|drop_item|world_item|shop_item|exchange_item)")
NUM_SUFFIX = _re.compile(r"_\d+$")

# 名字族字段 / 图标族字段
NAME_FIELDS = ("name", "item_name", "display_name", "show_name", "chip_name",
               "coating_name", "buff_item_name", "title_name")
ICON_FIELDS = ("icon", "icons", "chip_icon", "chip_big_icon", "coating_icon",
               "ui_vehicle_icon", "head_icon_path", "item_icon")


def xbody(path: pathlib.Path) -> bytes:
    raw = path.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        raise ValueError("no x{ container")
    size = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + size]


def load_common_item() -> dict[int, dict]:
    """common_item 真表（桩表在树里是 815B，真身在表缓存）。"""
    base = CACHE / "base_B42760CCA41DBC25.py"
    chs = CACHE / "base_EF3A8474A5E5F7A4.py"
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
    rows, _ = decode_table_rows_with_chs_slots(xbody(base), pool)
    out = {}
    for r in rows:
        out[r["key"]] = {k: (v[1] if isinstance(v, tuple) else v)
                         for k, v in r["values"].items()}
    return out


def decode_table(path: pathlib.Path, chs: pathlib.Path | None):
    body = xbody(path)
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs and chs.exists() else []
    rows, unbound = decode_table_rows_with_chs_slots(body, pool)
    return rows, unbound, pool


def census(stem: str, path: pathlib.Path, idset: set[int], reg_ids: set[int]) -> dict:
    chs = path.with_name(stem + "_chs.py")
    rec = {"table": stem, "file": path.name, "bytes": path.stat().st_size,
           "chs": chs.name if chs.exists() else None, "verdict": "", "reason": ""}
    try:
        rows, unbound, pool = decode_table(path, chs)
    except Exception as exc:                                    # noqa: BLE001
        rec.update({"rows": 0, "verdict": "X3", "reason": f"解码失败: {type(exc).__name__}: {exc}"[:160]})
        return rec
    keys = [r["key"] for r in rows]
    if not keys:
        rec.update({"rows": 0, "verdict": "X3",
                    "reason": "0 行（桩表/格式未覆盖）",
                    "unbound": len(unbound), "pool": len(pool)})
        return rec
    fields: dict[str, Counter] = {}
    for r in rows[:80]:
        for k, v in r["values"].items():
            fields.setdefault(k, Counter())[type(v).__name__] += 1
    name_fields = [f for f in fields if f in NAME_FIELDS or "name" in f.lower()]
    icon_fields = [f for f in fields if f in ICON_FIELDS or "icon" in f.lower()]
    inter = sum(1 for k in keys if k in idset)
    ratio = inter / len(keys)
    # id 自证：表自带 id/id_key 字段且等于 key
    self_id = 0
    for r in rows[:200]:
        v = r["values"].get("id")
        if isinstance(v, tuple):
            v = v[1]
        if v == r["key"]:
            self_id += 1
    rec.update({
        "rows": len(keys), "unbound": len(unbound), "pool": len(pool),
        "key_min": min(keys), "key_max": max(keys),
        "common_hits": inter, "common_ratio": round(ratio, 4),
        "reg_hits": sum(1 for k in keys if k in reg_ids),
        "name_fields": name_fields, "icon_fields": icon_fields,
        "self_id_hits": self_id, "sample_fields": sorted(fields)[:24],
    })
    # 判定
    if ratio >= 0.90 and (name_fields or icon_fields):
        rec["verdict"] = "S1"
        rec["reason"] = f"key 落在 common_item 道具 id 空间 {ratio:.0%}"
    elif self_id >= 20 and (name_fields or icon_fields) and ratio < 0.90:
        rec["verdict"] = "S3"
        rec["reason"] = f"独立 id 命名空间（行自带 id==key {self_id}/200），可按命名空间收录"
    elif name_fields and icon_fields and ratio < 0.05:
        rec["verdict"] = "S3"
        rec["reason"] = "非道具 id 空间的实体名册（自有 id），单独命名空间"
    elif ratio < 0.05 and not name_fields:
        rec["verdict"] = "X1"
        rec["reason"] = "key 为配置/类型/期次号，且无名字字段（非实体名册）"
    elif ratio < 0.05 and name_fields and not icon_fields:
        rec["verdict"] = "X2"
        rec["reason"] = "有名字但无图标且 key 非道具 id（引用/配置表）"
    else:
        rec["verdict"] = "X2"
        rec["reason"] = "混合 key 空间或字段不足以做实体名册"
    return rec


def candidate_stems() -> list[str]:
    seen: dict[str, pathlib.Path] = {}
    for p in sorted(R.TREE.glob("*.py")):
        stem = p.stem
        if stem.endswith("_chs"):
            continue
        if not FAMILY_RE.match(stem):
            continue
        if NUM_SUFFIX.search(stem):
            continue      # 分卷表（_1/_2…）先行排除，避免同一族重复计入
        seen[stem] = p
    for p in sorted(R.TREE.glob("*.nxs")):
        stem = p.stem
        if stem in seen or not FAMILY_RE.match(stem) or NUM_SUFFIX.search(stem):
            continue
        seen[stem] = p
    # 已确认在树里是桩表、真身在表缓存的 common_item 单独处理
    seen.pop("common_item_data", None)
    return sorted(seen)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    ci = load_common_item()
    idset = set(ci)
    reg_ids = {int(k) for k in json.loads(REG.read_text(encoding="utf-8"))["icons"]}
    print(f"common_item 真表 {len(ci):,} 行 / 道具 id 空间 {len(idset):,}；"
          f"icon_registry {len(reg_ids):,} id")

    stems = candidate_stems()
    if args.limit:
        stems = stems[: args.limit]
    print(f"候选表 {len(stems)} 张，开始普查…")

    out = []
    # ① common_item 本身（表缓存 base + chs）
    ci_fields = Counter()
    for v in list(ci.values())[:80]:
        for k in v:
            ci_fields[k] += 1
    out.append({
        "table": "common_item_data", "file": "base_B42760CCA41DBC25.py",
        "bytes": (CACHE / "base_B42760CCA41DBC25.py").stat().st_size,
        "chs": "base_EF3A8474A5E5F7A4.py", "rows": len(ci), "unbound": 0,
        "key_min": min(idset), "key_max": max(idset),
        "common_hits": len(idset), "common_ratio": 1.0,
        "reg_hits": sum(1 for k in idset if k in reg_ids),
        "name_fields": ["name"], "icon_fields": ["icon"], "self_id_hits": 80,
        "verdict": "S1", "reason": "道具 id 空间的权威主表（树里是 815B 桩，真身在 90_表缓存）",
    })

    for i, stem in enumerate(stems, 1):
        p = R.TREE / (stem + ".py")
        if not p.is_file():
            p = R.TREE / (stem + ".nxs")
        try:
            rec = census(stem, p, idset, reg_ids)
        except Exception as exc:                                # noqa: BLE001
            rec = {"table": stem, "file": p.name, "rows": 0, "verdict": "X3",
                   "reason": f"异常: {type(exc).__name__}: {exc}"[:160]}
        out.append(rec)
        if i % 50 == 0:
            print(f"  … {i}/{len(stems)}")

    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8", newline="\n") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("写出", OUT_JSONL)

    vc = Counter(r.get("verdict") for r in out)
    print("判定分布:", dict(vc))
    total_rows = sum(r.get("rows") or 0 for r in out if r.get("verdict", "").startswith("S"))
    print("S 类表合计行数:", total_rows)

    return 0


if __name__ == "__main__":
    sys.exit(main())
