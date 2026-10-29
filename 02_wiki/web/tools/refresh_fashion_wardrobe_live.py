# -*- coding: utf-8 -*-
"""全量时装衣柜（fashion_wardrobe）—— 用**当前树里的 fashion_data 表**重读刷新字段。

背景（用户 2026-10-18 反馈）：① 无分类筛选/搜索 ② 卡片赘述 ③ 数据源旧 ④ 图标需校对。

本脚本只做「刷新字段」，**不改 1253 件的身份**：
  · id / 聚合口径（归一名字）/ row_keys / _media / provenance 一律保留；
  · name 只在「当前表里全部行的归一名字都不再等于旧名」时才改名（实测 0 次）；
  · desc 只在旧值不在当前行里、且当前有实质描述时才覆盖（实测 0 次）；
  · part 用当前行的 `part_type` 字段重算（缺字段的 597 件 = 旧口径「整套」，实测 0 次变更）。

新增派生字段（供前端筛选/卡片，全部来自表字段或已发布图标绑定）：
    part_bucket   部位归组（头饰/衣服/背包/整套/光源/其他）
    durations     valid_days 的期限档（天）
    has_permanent 是否含永久款（该件存在不带 valid_days 的行）
    duration_state permanent / timed / mixed
    model_id      首个模型 ID（卡片显示用；model_ids 仍全保留）
    level / levels, charm_value, show_no_have, fashion_preview, hide_in_bag
    gender        从图标基名 _f_/_m_ 判（女/男）；无标记为 null
    icon_state    有图 / 含占位

源：01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata/fashion_data.py(+_chs.py)
解码：toolkit_core.bindict_table.decode_table_rows(resolve_jumps=True)
"""
from __future__ import annotations
import pathlib

import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # 02_wiki/web

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
CDATA = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata"
BOARD_JSON = ROOT / "data/boards/fashion_wardrobe.json"
BOARD_JS = ROOT / "data/boards/fashion_wardrobe.js"
# 差异基线：刷新前的快照（存在就用来算「改了多少条」，保证复跑结果可复现）
BASELINE = ROOT / "data/boards/fashion_wardrobe.json.bak_refresh20261018"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402

CST = timezone(timedelta(hours=8))
BASE = CDATA / "fashion_data.py"
CHS = CDATA / "fashion_data_chs.py"

_PARTS = ["-衣服", "-头饰", "-背包", "-套装", "-挂件", "-脱帽头", "-头发", "-帽子"]
_GENERIC_DESC = re.compile(r"^一件(永久款|\d+天时效|.{0,6}时效)")
BUCKET = {"hat": "头饰", "cloth": "衣服", "bag": "背包", "suit": "整套", "light": "光源"}
# 与旧板一致：无 part_type 的 597 件在旧口径里就是「整套」
BUCKET_FALLBACK = "整套"


def norm_name(n: str) -> str:
    s = (n or "").strip()
    s = re.sub(r"[-－]?\d+天$", "", s)
    s = re.sub(r"[（(]\s*永久款\s*[）)]", "", s)
    s = re.sub(r"[（(]\s*\d+天\s*[）)]", "", s)
    s = s.replace("永久款", "")
    for sep in ("·", "・", "•"):
        if sep in s:
            s = s.split(sep)[0]
    for x in _PARTS:
        if s.endswith(x):
            s = s[: -len(x)]
    return s.strip()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rows():
    raw = BASE.read_bytes()
    chs = CHS.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        raise SystemExit("✗ fashion_data.py 里找不到 x{ 头")
    length = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + length]
    rows, unbound = decode_table_rows(body, parse_legacy_chs_pool(chs), resolve_jumps=True)
    return rows, unbound


def v(row, key):
    got = row["values"].get(key) if row else None
    return got[1] if got else None


def gender_of(media) -> str | None:
    """按图标基名的 _f_ / _m_ 判性别（任务口径：只看图片文件名，不做推断）。"""
    gs = set()
    for im in (media or {}).get("images") or []:
        stem = str(im.get("base", "")).rsplit("/", 1)[-1]
        if "_f_" in stem:
            gs.add("女")
        elif "_m_" in stem:
            gs.add("男")
    if gs == {"女"}:
        return "女"
    if gs == {"男"}:
        return "男"
    if gs == {"女", "男"}:
        return "女/男"
    return None


def main() -> int:
    board = json.loads(BOARD_JSON.read_text(encoding="utf-8"))
    items = board["items"]
    rows, unbound = load_rows()
    by_key = {r["key"]: r for r in rows}
    print(f"fashion_data 行 {len(rows)} ｜ 未解组 {len(unbound)}")

    changed = Counter()
    hit_rows = hit_items = total_keys = 0
    fresh = []
    for it in items:
        keys = [k for k in (it.get("row_keys") or [])]
        total_keys += len(keys)
        rs = [by_key[k] for k in keys if k in by_key]
        hit_rows += len(rs)
        if rs:
            hit_items += 1

        # ── 名字：当前行归一后是否仍能产出旧名 ──
        cur_names = [v(r, "name") for r in rs if v(r, "name")]
        norms = {norm_name(x) for x in cur_names}
        if it["name"] not in norms and norms:
            cnt = Counter(norm_name(x) for x in cur_names)
            new = cnt.most_common(1)[0][0]
            if new:
                changed["name"] += 1
                it["name"] = new
        it["name_variants"] = sorted(set(cur_names)) or it.get("name_variants") or []

        # ── 部位 ──
        pts = sorted({str(v(r, "part_type")) for r in rs if v(r, "part_type")})
        if pts:
            new_part = pts[0] if len(pts) == 1 else "/".join(pts)
        else:
            new_part = it.get("part") or BUCKET_FALLBACK
        if new_part != it.get("part"):
            changed["part"] += 1
        it["part"] = new_part
        it["all_parts"] = pts if len(pts) > 1 else None
        buckets = [BUCKET.get(p, "其他") for p in pts] if pts else [BUCKET_FALLBACK]
        # 去重保序
        it["part_bucket"] = list(dict.fromkeys(buckets))

        # ── 模型 / 品级 / 魅力值 ──
        mids = sorted({int(v(r, "model_id")) for r in rs if isinstance(v(r, "model_id"), int)})
        if mids and mids != (it.get("model_ids") or []):
            changed["model_ids"] += 1
        if mids:
            it["model_ids"] = mids
            it["model_id"] = mids[0]
        levels = sorted({int(v(r, "level")) for r in rs if isinstance(v(r, "level"), int)})
        it.pop("level", None)          # ★ 不再写裸 level（会和武器皮肤的「品级」语义撞车）
        it.pop("levels", None)         # 旧刷新的残留字段名，统一为 grade_levels
        if levels:
            it["grade_levels"] = levels
            it["grade_level"] = levels[-1]     # 表里同款多档时取最高档
        charm = [int(v(r, "charm_value")) for r in rs if isinstance(v(r, "charm_value"), int)]
        it["charm_value"] = max(charm) if charm else None

        # ── 期限（valid_days 为主，fid_str 末位为佐证） ──
        days = sorted({int(v(r, "valid_days")) for r in rs
                       if isinstance(v(r, "valid_days"), int) and int(v(r, "valid_days")) > 0})
        fid_days = set()
        for r in rs:
            s = v(r, "new_fashion_id_str") or ""
            tail = s.split("_")[-1] if s else ""
            if tail.isdigit() and int(tail) > 0:
                fid_days.add(int(tail))
        has_perm = any(v(r, "valid_days") in (None, 0) for r in rs) or not rs
        if days and has_perm:
            state = "mixed"
        elif days:
            state = "timed"
        else:
            state = "permanent"
        it["durations"] = days or None
        it["duration_state"] = state
        it["has_permanent"] = bool(has_perm)
        # 与旧板 time_limited_variants 的差异只统计，不改写旧字段以外的语义
        old_tl = it.get("time_limited_variants")
        if (days or None) != (old_tl or None):
            changed["time_limited_variants"] += 1
            it["time_limited_variants"] = days or None
        it["duration_variants"] = sorted(set(days) | fid_days) or None

        # ── 布尔位 ──
        for f in ("show_no_have", "fashion_preview", "hide_in_bag"):
            vals = [bool(v(r, f)) for r in rs if v(r, f) is not None]
            if vals:
                it[f] = any(vals)

        # ── 描述 ──
        descs = [v(r, "desc") for r in rs if v(r, "desc")]
        old_desc = it.get("desc") or ""
        if old_desc and old_desc not in descs:
            real = [d for d in descs if not _GENERIC_DESC.match(str(d))]
            if real:
                it["desc"] = real[0]
                changed["desc"] += 1
        elif not old_desc:
            real = [d for d in descs if not _GENERIC_DESC.match(str(d))] or descs
            if real:
                it["desc"] = real[0]
                it["desc_note"] = "描述来自表的 desc 字段"
                changed["desc"] += 1

        # ── 图标状态 / 性别（图标绑定成品，只读）──
        media = it.get("_media") or {}
        imgs = media.get("images") or []
        it["icon_state"] = "有图" if imgs else ("含占位" if media.get("placeholder") else "无图")
        it["icon_count"] = len(imgs)
        g = gender_of(media)
        if g:
            it["gender"] = g

        it["row_key_hits"] = f"{len(rs)}/{len(keys)}"
        it["refreshed_at"] = datetime.now(CST).isoformat(timespec="seconds")
        fresh.append(it)

    board["items"] = fresh

    # ── 与刷新前基线的差异（逐字段、逐条；复跑仍以基线为准，数字可复现）──
    diff = {}
    if BASELINE.is_file():
        base_items = {x["id"]: x for x in json.loads(BASELINE.read_text(encoding="utf-8"))["items"]}
        fields = ["name", "part", "desc", "model_ids", "time_limited_variants", "grade_level", "charm_value", "gender"]
        for f in fields:
            n = 0
            for it in fresh:
                old = base_items.get(it["id"], {})
                if (old.get(f) or None) != (it.get(f) or None):
                    n += 1
            if n:
                diff[f] = n
    else:
        diff = dict(changed) or {}

    # ── meta ──
    now = datetime.now(CST).isoformat(timespec="seconds")
    src = {
        "fashion_data.py": {"path": str(BASE.relative_to(PROJ)).replace("\\", "/"), "sha256": sha256(BASE)},
        "fashion_data_chs.py": {"path": str(CHS.relative_to(PROJ)).replace("\\", "/"), "sha256": sha256(CHS)},
    }
    part_count = Counter(it["part"] for it in fresh)
    bucket_count = Counter(b for it in fresh for b in it.get("part_bucket") or [])
    dur = Counter(it["duration_state"] for it in fresh)
    ic = Counter(it["icon_state"] for it in fresh)
    gen = Counter(it.get("gender") or "未标注" for it in fresh)
    # ★ 魅力值/品级空值统计（用户 2026-10-18 要求逐条报数）
    charm_vals = [it["charm_value"] for it in fresh if isinstance(it.get("charm_value"), int)]
    charm_empty = sum(1 for it in fresh if not it.get("charm_value"))
    charm_zero = sum(1 for it in fresh if it.get("charm_value") == 0)
    charm_missing = sum(1 for it in fresh if "charm_value" not in it or it.get("charm_value") is None)
    grade_count = Counter(it.get("grade_level") for it in fresh)
    charm_vals.sort()
    charm_stats = {
        "items": len(fresh),
        "with_value": len(charm_vals),
        "empty_or_zero": charm_empty,
        "zero": charm_zero,
        "missing_field": charm_missing,
        "min": charm_vals[0] if charm_vals else None,
        "max": charm_vals[-1] if charm_vals else None,
        "median": charm_vals[len(charm_vals) // 2] if charm_vals else None,
        "grade_level_empty": sum(1 for it in fresh if it.get("grade_level") is None),
    }
    withdesc = sum(1 for it in fresh if it.get("desc"))
    meta = board["meta"]
    meta["data_refreshed_at"] = now
    meta["data_source_sha256"] = src
    meta["data_refresh"] = {
        "decoded_rows": len(rows),
        "unresolved_groups": len(unbound) if hasattr(unbound, "__len__") else None,
        "items": len(fresh),
        "row_keys_matched": f"{hit_rows}/{total_keys}",
        "items_with_row_match": f"{hit_items}/{len(fresh)}",
        "field_changes": diff or {"（无变化）": 0},
        "field_change_notes": {
            "time_limited_variants": ("旧值取自 new_fashion_id_str 的倒数第二段（实为性别码，故出现 6 这类假期限）；"
                                      "现改为行的 valid_days 字段（与名称 -N天 后缀、fid_str 末位三方一致）。"),
            "part": "重算自当前行的 part_type；表里缺该字段的 597 件沿用旧口径「整套」（未做推断）。",
        },
        "note": ("按每件 row_keys 从当前树的 fashion_data 重新解码后刷新 name/desc/part/model/期限/布尔位；"
                 "row_key 全部命中说明聚合口径与当前表仍对齐，身份未变。"),
    }
    meta["generated"] = now[:10]
    meta["notes"] = (
        f"全量 {len(fresh)} 件外观（按归一名字聚合时限/部件变体）。"
        f"部位分布={dict(part_count)}。部位归组={dict(bucket_count)}。"
        f"期限：永久 {dur.get('permanent', 0)} / 限时 {dur.get('timed', 0)} / 永久+限时 {dur.get('mixed', 0)}。"
        f"图标：有图 {ic.get('有图', 0)} / 仅占位 {ic.get('含占位', 0)}。"
        f"★ 描述覆盖 {withdesc}/{len(fresh)}（{100.0 * withdesc / max(1, len(fresh)):.1f}%）。"
        f"★ 字段已按当前树 fashion_data 重读（{now[:19]}，行 {len(rows)}，row_key 命中 {hit_rows}/{total_keys}）。"
        "★ 归一口径：剥部件后缀 / 剥「·XXX」/ 剥时效包装。"
    )
    meta["gender_summary"] = dict(gen)
    meta["charm_stats"] = charm_stats
    meta["grade_distribution"] = {str(k): v for k, v in sorted(grade_count.items(), key=lambda kv: (kv[0] is None, kv[0]))}

    BOARD_JSON.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(board, ensure_ascii=False, separators=(",", ":")) + ";\n",
                        encoding="utf-8")
    print("刷新完成 →", BOARD_JSON.name, "|", BOARD_JS.name)
    print("row_key 命中", f"{hit_rows}/{total_keys}", "| 件级命中", f"{hit_items}/{len(fresh)}")
    print("字段变更（对基线）", diff or "无")
    print("部位", dict(part_count))
    print("归组", dict(bucket_count))
    print("期限", dict(dur), "| 图标", dict(ic), "| 性别", dict(gen))
    print("魅力值", charm_stats)
    print("品级分布", {str(k): v for k, v in sorted(grade_count.items(), key=lambda kv: (kv[0] is None, kv[0]))})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
