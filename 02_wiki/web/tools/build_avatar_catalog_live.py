#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_avatar_catalog_live.py — 从 PE 活树重建「头像 / 头像框 / 名片框」板。

数据源（只读，禁碰 E:/mrzh、E:/LifeAfter、禁 APK）：
  01_索引与产物/41_还原树/pe/配置/com/cdata/
    dynamic_avatar_conf_data(+_chs)                      → 头像   da_<item_id>
    avatar_frame_conf_data(+_chs)                        → 头像框 af_<item_id>
    business_card_scheme_data(+_chs)                     → 名片框 bc_<item_id>
    oversea/<表名>_auto_oversea_data_<服>.py(+_chs)      → 分服变体
  01_索引与产物/10_索引/items/common_item_names.json     → 名片框名字（表里没有 item_name）

合并规则（可复核）：
  · 主表优先；分服变体只补主表里**不存在**的主键（按 key 并集去重，不跨源拼字段）。
    —— 实测 avatar_frame_conf_data 主表 253 行，yk 变体独有的 410188（赤色誓约）在旧板里
       也只有这一条是主表没有的，正是它把头像框从 253 抬到 254。
  · 字段映射：头像/头像框 image_path←image_path；名片框 image_path←frame_img_path。
  · 名字：表内 item_name 优先，名片框回落到 common_item_names.json，再回落「（无名称）」。

媒体与排序口径（不重生成图，不删旧图）：
  · _media 按同 id 从旧板整块沿用；旧板没有的新 id 留空（报告里统计无图条数）。
  · order 沿用旧板（旧板的 order 是三表混排的展示序号，无法从表内重算）；
    新 id 按类型顺序接在尾部。

幂等：读旧板 → 重建 → 用 board_io 写 .json/.js，同日重复运行字节一致。

用法：
  python 02_wiki/web/tools/build_avatar_catalog_live.py            # 写板
  python 02_wiki/web/tools/build_avatar_catalog_live.py --dry-run  # 只统计
  python 02_wiki/web/tools/build_avatar_catalog_live.py --allow-fewer  # 允许低于 681
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent
PROJ = WEB.parent.parent          # 02_wiki/web → 项目根
TOOLS = WEB / "tools"
BOARD = WEB / "data/boards/avatar_catalog.json"

sys.path.insert(0, str(TOOLS))

import rebuild_lottery_periods as R  # noqa: E402  复用 Table 解码（PE marshal）
from board_io import write_board_pair  # noqa: E402

TREE = Path(R.TREE)
NAME_INDEX = PROJ / "01_索引与产物/10_索引/items/common_item_names.json"

# (kind, id 前缀, 主表名, 图标字段)
SPECS = [
    ("头像", "da", "dynamic_avatar_conf_data", "image_path"),
    ("头像框", "af", "avatar_frame_conf_data", "image_path"),
    ("名片框", "bc", "business_card_scheme_data", "frame_img_path"),
]

MIN_ITEMS = 681


# ───────────────────────────────────────────── 读表
def _load(table_file: Path):
    """Table + 同名 _chs 池；缺文件返回空表（不抛）。"""
    chs = table_file.with_name(table_file.stem + "_chs.py")
    return R._opt_table(table_file, chs if chs.is_file() else None)


def _variants(table_name: str) -> list[Path]:
    """分服变体（排除 _chs），按文件名排序保证顺序稳定。"""
    out = [p for p in sorted((TREE / "oversea").glob(table_name + "_auto_oversea_data_*.py"))
           if not p.stem.endswith("_chs")]
    return out


def collect(table_name: str) -> tuple[dict[str, dict], dict]:
    """主表 + 分服变体 → {key: {'values':…, 'table': 实际来源表}}，主表优先。"""
    rows: dict[str, dict] = {}
    stats = {"base": 0, "variant_only": 0, "per_variant": {}}

    base = _load(TREE / (table_name + ".py"))
    for key, rec in base.by_key.items():
        rows[str(key)] = {"values": dict(rec.get("values") or {}), "table": table_name}
    stats["base"] = len(rows)

    for path in _variants(table_name):
        t = _load(path)
        added = 0
        for key, rec in t.by_key.items():
            k = str(key)
            if k in rows:            # 主表优先，不覆盖、不拼字段
                continue
            rows[k] = {"values": dict(rec.get("values") or {}), "table": path.stem}
            added += 1
        stats["per_variant"][path.stem] = {"rows": len(t.by_key), "added": added}
        stats["variant_only"] += added
    return rows, stats


def load_names() -> dict[str, str]:
    if not NAME_INDEX.is_file():
        return {}
    try:
        d = json.loads(NAME_INDEX.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out = {}
    for k, v in (d.get("items") or {}).items():
        nm = v.get("name") if isinstance(v, dict) else None
        if nm:
            out[str(k)] = nm
    return out


# ───────────────────────────────────────────── 组装
def _s(v) -> str:
    return (v or "").strip().replace("\\", "/") if isinstance(v, str) else ""


def _sha(path: Path) -> dict:
    raw = path.read_bytes()
    st = path.stat()
    return {
        "source_id": "pe-restore-tree-cdata",
        "role": "primary",
        "path": str(path).replace("\\", "/"),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": st.st_size,
        "mtime_ns": st.st_mtime_ns,
    }


def build_board() -> tuple[dict, dict]:
    old = json.loads(BOARD.read_text(encoding="utf-8"))
    old_items = {i["id"]: i for i in old.get("items", [])}
    names = load_names()

    items: list[dict] = []
    report = {"before": len(old.get("items", [])), "by_kind": {}, "tables": {}}
    seq = {kind: 0 for kind, *_ in SPECS}

    for kind, prefix, table_name, icon_field in SPECS:
        rows, tstats = collect(table_name)
        report["tables"][table_name] = tstats
        seq[kind] = max([int(i.get("order") or 0) for i in old.get("items", [])
                         if i.get("kind") == kind] + [0])

        for key in sorted(rows, key=lambda x: int(x) if x.isdigit() else 0):
            rec = rows[key]
            v = rec["values"]
            iid = "%s_%s" % (prefix, key)

            name = _s(v.get("item_name")) or names.get(key, "") or "（无名称）"
            item = {
                "id": iid,
                "item_id": key,
                "name": name,
                "kind": kind,
                "image_path": _s(v.get(icon_field)),
                "spine_path": _s(v.get("spine_path")),
                "resource_path": _s(v.get("resource_path")),
                "detail_bg": _s(v.get("detail_bg")),
                "evidence": "structure",
                "evidence_level": "static/candidate",
                "status_tags": ["static config"],
                "source": rec["table"],
            }

            prev = old_items.get(iid)
            if prev:
                # 展示序号沿用旧板（三表混排序号没法从表内重算）
                item["order"] = prev.get("order", v.get("order") or 0)
                if prev.get("_media"):
                    item["_media"] = copy.deepcopy(prev["_media"])
                if prev.get("status_tags"):
                    item["status_tags"] = copy.deepcopy(prev["status_tags"])
                if prev.get("status_note"):
                    item["status_note"] = prev["status_note"]
                prov = copy.deepcopy(prev.get("provenance") or {})
                if prov:
                    # 只校准「这行到底来自哪张表」，其余溯源字段沿用旧板
                    prov["table"] = rec["table"]
                    prov["table_raw"] = rec["table"]
                    item["provenance"] = prov
            else:
                seq[kind] += 1
                item["order"] = seq[kind]

            if "provenance" not in item:
                refs = [f for f in (icon_field, "item_name", "order") if f]
                item["provenance"] = {
                    "source_id": "pe-restore-tree-cdata",
                    "table": rec["table"],
                    "row_key": key,
                    "field_refs": refs,
                    "name_source": "inventory" if _s(v.get("item_name")) or names.get(key) else "unresolved",
                    "no_cross_source_field_join": True,
                }

            items.append(item)

        report["by_kind"][kind] = sum(1 for i in items if i["kind"] == kind)

    total = len(items)
    report["after"] = total
    report["missing_ids"] = sorted(set(old_items) - {i["id"] for i in items})
    report["no_media"] = sum(1 for i in items if not i.get("_media"))
    report["no_image_path"] = sum(1 for i in items if not i["image_path"])

    # ── meta：沿用旧板，只更新总数/统计/日期/来源锁
    meta = copy.deepcopy(old.get("meta") or {})
    has_img = sum(1 for i in items if (i.get("_media") or {}).get("images"))
    has_anim = sum(1 for i in items if (i.get("_media") or {}).get("anim"))
    meta["total"] = total
    meta["icon_hit"] = has_img
    meta["generated"] = dt.date.today().isoformat()
    meta["source_server"] = "PE 活树 · 41_还原树/pe/配置/com/cdata（%s）" % "、".join(
        s[2] for s in SPECS)
    meta["note"] = (
        "三张主表 + 分服变体按主键并集去重（主表优先，不跨源拼字段）；"
        "头像 da_、头像框 af_、名片框 bc_；名片框名字取 common_item_names 索引；"
        "_media 与 order 沿用旧板（媒体未重生成，图未新增/删除）"
        " ｜ 动态头像由 spine_path 的 Spine 资源预渲染为 APNG（卡面默认静态图，悬停/开详情播放）"
        " ｜ 个性化时装不分服，条目不带服别字段"
    )
    meta["state_summary"] = {**report["by_kind"], "有图": has_img,
                             "缺图": total - has_img, "有动画": has_anim}
    meta.setdefault("sort_by_code", True)          # id 数字升序即条目序，保留旧板口径
    # 来源标签：旧板记的是 Documents 快照口径，这里改成活树口径，历史值留在 *_prev（幂等）
    PE_LABEL = "PE 活树 · 41_还原树/pe/配置/com/cdata · 三主表 + 分服变体并集"
    prev = meta.get("source_label_prev")
    if not prev or prev == PE_LABEL:
        prev = meta.get("source_label")
    if not prev or prev == PE_LABEL:
        prev = "Documents 快照 script.py314 · dynamic_avatar_conf_data · 简单生存服"
    meta["source_label_prev"] = prev
    meta["source_label"] = PE_LABEL

    prov = copy.deepcopy(meta.get("provenance") or {})
    prov.setdefault("contract_version", 3)
    prov.setdefault("audit_status", "passed")
    prov.setdefault("contract", "frozen-audited-artifact")
    prov["source_locks"] = [_sha(TREE / (s[2] + ".py")) for s in SPECS]
    prov.setdefault("source_scope", {
        "cross_source_policy": "no-cross-source-field-join",
        "integer_join_policy": "no-equal-integer-join",
        "runtime_final_policy": "unknown-unless-runtime-proven",
    })
    meta["provenance"] = prov
    meta["package_sha"] = "bundle:" + hashlib.sha256(
        "".join(_sha(TREE / (s[2] + ".py"))["sha256"] for s in SPECS).encode()).hexdigest()

    board = {k: v for k, v in old.items() if k not in ("meta", "items")}
    board["meta"] = meta
    board["items"] = items
    return board, report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-fewer", action="store_true")
    a = ap.parse_args(argv)

    board, rep = build_board()

    print("旧板：%d 条" % rep["before"])
    for kind, n in rep["by_kind"].items():
        print("  %s %d" % (kind, n))
    for t, st in rep["tables"].items():
        print("  表 %s：主表 %d，变体独有 %d %s" % (t, st["base"], st["variant_only"],
                                                 {k: v["added"] for k, v in st["per_variant"].items() if v["added"]}))
    print("合计 %d；无图 %d；无 image_path %d；旧板有而新板缺 %d"
          % (rep["after"], rep["no_media"], rep["no_image_path"], len(rep["missing_ids"])))

    if rep["after"] < MIN_ITEMS and not a.allow_fewer:
        print("!! 条目数 %d 低于硬要求 %d，拒绝写板（--allow-fewer 可强制）" % (rep["after"], MIN_ITEMS))
        return 2
    if rep["missing_ids"]:
        print("!! 相对旧板缺失 id：", rep["missing_ids"][:20])

    if a.dry_run:
        print("dry-run：未写文件")
        return 0

    write_board_pair(BOARD, board, "avatar_catalog")
    print("已写：%s(.json/.js)" % BOARD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
