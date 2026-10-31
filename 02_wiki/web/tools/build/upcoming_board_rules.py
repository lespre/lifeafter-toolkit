#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""upcoming_board_rules.py — 「新更新与预告」板的口径工具（构建器与修复脚本共用）

为什么单独成文件：同一套口径（占位名解析顺序、计数重算、notes 文案）既要在
`build_upcoming_auto.py` 重建时生效，也要能在不重跑构建（缺 huodong 源表）时
用 `fix_upcoming_auto_20261101.py` 修正既有产物。两处若各写一份必然分叉。

★ 占位名解析顺序（2026-11-01 用户判定）：
    时装部位表 fashion_face_slots（player_module_appear_data.part → 部位）
    → 时装板 fashion_wardrobe → 全量道具表 item_master_full
  三处都查不到 ⇒ 显式标「未解析道具 · <id>」并打 unresolved，**绝不编造**。

★ 计数一律由条目/期次实时重算（state_summary / periods.member_count /
  evidence_detail / icon_stats），不再从别的板 meta 抄、也不手填。
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

PLACEHOLDER = re.compile(r"^(?:道具|时装部件|物品|装备|时装|资源)\s*(\d+)$")

# player_module_appear_data.part → 部位中文（★ 唯一口径，描述文字不可信）
PART_CN = {2: "头饰", 20001: "面饰", 1: "挂饰"}

NOTE_MAIN = "自动从武器皮肤板与奖池板筛选未上架条目（以构建日为界）；不再人工维护预告卡。"
NOTE_LISTED = ("上架状态以 listing_status / sale_date 为准：listing_status=on_sale 的皮肤不进本板"
               "（2026-10-29 人工确认彩虹过载 1110087、全糖暴击 1110088 已上线）。")
NOTE_COUNTS = ("meta.state_summary / periods.member_count / evidence_detail / icon_stats 由条目实时重算，"
               "不再手填（2026-11-01 修：原写「武器皮肤 11」而实际 9 条）。")
NOTE_NAMES = ("占位名修复（2026-11-01）：姓名按 时装部位表 → 时装板 → 全量道具表 顺序求；"
              "仍查不到的显式标「未解析」并打 unresolved，不编造。")
NOTE_SCOPE = ("2026-11-01：预告专栏已摘除独立武器皮肤预览板 skin_behavior_preview，"
              "本板武器皮肤段保留（武器皮肤全量见 一、时装类（二）武器皮肤）。")
CATEGORY = "置顶、活动奖池与预告 / （二）预告专栏"


def load_name_index(boards: Path) -> tuple[dict, dict, dict]:
    """返回 (时装部位表, 时装板, 全量道具表) 三个 id→行 索引。"""
    def _index(name: str, key: str) -> dict:
        p = boards / name
        if not p.exists():
            return {}
        out = {}
        for it in json.loads(p.read_text(encoding="utf-8")).get("items") or []:
            k = it.get(key)
            if k is not None:
                out[str(k)] = it
        return out

    return (_index("fashion_face_slots.json", "row_key"),
            _index("fashion_wardrobe.json", "item_id"),
            _index("item_master_full.json", "item_id"))


def resolve_name(item_id: str, idx: tuple[dict, dict, dict]) -> tuple[str, str, str] | None:
    """按可信度顺序求真名。返回 (显示名, 名称来源, 补充说明) 或 None。"""
    face, wardrobe, master = idx

    row = face.get(item_id)
    if row:
        nm = (row.get("display_name") or row.get("name") or "").strip()
        if nm:
            part = PART_CN.get(row.get("part_code"))
            disp = "%s（%s）" % (nm, part) if part else nm
            return (disp,
                    "fashion_face_slots.row_key=%s display_name（部位 part_code=%s→%s）"
                    % (item_id, row.get("part_code"), part or "未映射"),
                    "部位取 player_module_appear_data.part")

    row = wardrobe.get(item_id)
    if row:
        nm = (row.get("name") or "").strip()
        if nm:
            return nm, "fashion_wardrobe.item_id=%s name" % item_id, ""

    row = master.get(item_id)
    if row:
        nm = (row.get("name") or "").strip()
        if nm and row.get("name_status") != "unresolved":
            return nm, "item_master_full.item_id=%s name" % item_id, ""
    return None


def resolved_name(item_id, raw_name, idx) -> tuple[str, dict]:
    """构建器用：给出 (最终名, 要合并进条目的附加字段)。

    非占位名原样返回；占位名按 resolve_name 求，查不到标未解析。
    """
    raw = str(raw_name or "")
    m = PLACEHOLDER.match(raw)
    if not m:
        return raw, {}
    iid = str(item_id or m.group(1))
    got = resolve_name(iid, idx)
    if got:
        disp, src, note = got
        extra = {"name_status": "resolved", "name_source": src}
        if note:
            extra["name_note"] = note
        return disp, extra
    return ("未解析道具 · %s" % iid,
            {"name_status": "unresolved",
             "name_note": ("item_id %s 在 fashion_face_slots / fashion_wardrobe / "
                           "item_master_full 均无名称行；保留 ID，不编造名称。" % iid),
             "unresolved": True})


def fix_placeholders(board: dict, idx) -> list[str]:
    """就地修补成品板里的占位名。返回改动日志。"""
    log: list[str] = []
    for it in board.get("items") or []:
        m = PLACEHOLDER.match(str(it.get("name") or ""))
        if not m:
            continue
        item_id = str(it.get("item_id") or m.group(1))
        new, extra = resolved_name(item_id, it.get("name"), idx)
        log.append("%s：%r → %r（%s）"
                   % (it.get("id"), it.get("name"), new,
                      extra.get("name_source") or "无名称行，标未解析"))
        it["name"] = new
        unresolved = extra.pop("unresolved", False)
        it.update(extra)
        if unresolved:
            tags = list(it.get("status_tags") or [])
            if "unresolved" not in tags:
                tags.append("unresolved")
            it["status_tags"] = tags
        prov = it.setdefault("provenance", {})
        prov["name_source"] = extra.get("name_source") or "unresolved（三表均无名称行）"
    return log


def recount(board: dict) -> dict:
    """由条目/期次实时重算全部计数。返回前后对比，便于打印。"""
    items = board.get("items") or []
    periods = board.get("periods") or []
    meta = board.setdefault("meta", {})

    per_member = Counter(it.get("period_id") for it in items)
    for p in periods:
        p["member_count"] = per_member.get(p.get("period_id"), 0)

    skin = sum(1 for it in items if it.get("kind") == "武器皮肤")
    pool = len(items) - skin
    pool_periods = sum(1 for p in periods if p.get("family_key") != "UpcomingSkin")
    old = dict(meta.get("state_summary") or {})
    meta["state_summary"] = {"武器皮肤": skin, "奖池成员": pool,
                             "奖池期次": pool_periods, "合计": len(items)}

    ev = Counter(str(it.get("evidence") or "") for it in items)
    lv = Counter(str(it.get("evidence_level") or "") for it in items)
    tg = Counter(t for it in items for t in (it.get("status_tags") or []))
    fam = Counter(str(p.get("family") or "") for p in periods)
    meta["evidence_detail"] = {
        "structure": ev.get("structure", 0),
        "candidate": ev.get("candidate", 0),
        "evidence_levels": dict(sorted(lv.items())),
        "status_tags": dict(sorted(tg.items())),
        "families": dict(sorted(fam.items())),
    }

    state = Counter(str(it.get("icon_state") or "未标注") for it in items)
    meta["icon_stats"] = {"items_total": len(items),
                          "items_with_icon": state.get("有图", 0),
                          "by_state": dict(sorted(state.items()))}
    return {"state_summary": (old, meta["state_summary"]),
            "periods": [(p.get("period_id"), p.get("member_count")) for p in periods]}
