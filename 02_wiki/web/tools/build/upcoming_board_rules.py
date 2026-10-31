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
NOTE_WINDOW = ("预告窗口口径（2026-11-01 修）：奖池成员看期次状态（进行中/未开始 = 仍在窗口，"
               "期次结束才剔除）；武器皮肤看源表 release_state（仍为未上线就保留，"
               "预计上架日已过只标「已过预计」，不再当成过期整条隐藏）。")
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


def enrich_period_status(board: dict, boards: Path) -> list[str]:
    """给奖池成员/期次补 period_status（源 = lottery_periods.periods[].status）。

    ★ 为什么需要：前端原先只按 expect_date 判断「是否还在预告窗口」，
      奖池成员的上架日 = 期次开始日，一开始就整批被判过期 → 页面被清空。
      有了期次状态（进行中/未开始/已结束）才能区分「活动还在跑」和「真过期」。
    """
    p = boards / "lottery_periods.json"
    if not p.exists():
        return []
    src = json.loads(p.read_text(encoding="utf-8"))
    per = {str(x.get("period_id")): x for x in (src.get("periods") or [])}
    got: list[str] = []
    for it in board.get("items") or []:
        pid = str(it.get("period_id") or "")
        if it.get("family_key") != "UpcomingPool":
            continue
        # up_pool_lp_3637 → lp_3637
        key = pid[len("up_pool_"):] if pid.startswith("up_pool_") else pid
        row = per.get(key)
        if not row:
            continue
        st = str(row.get("status") or "").strip()
        if st:
            it["period_status"] = st
            it["period_start"] = row.get("start") or ""
            if row.get("end"):
                it["period_end"] = row.get("end")
            got.append("%s ← %s(%s)" % (it.get("id"), st, key))
    for pg in board.get("periods") or []:
        pid = str(pg.get("period_id") or "")
        key = pid[len("up_pool_"):] if pid.startswith("up_pool_") else pid
        row = per.get(key)
        if not row:
            continue
        st = str(row.get("status") or "").strip()
        if st:
            pg["status"] = st
        if row.get("end"):
            pg["end"] = row.get("end")
    return got


def ensure_source_locks(board: dict, boards: Path) -> list[str]:
    """补齐板级 source_locks：条目实际用到、但板级没声明的 sha 会被门禁判红。

    2026-11-01 实测：重建皮肤段后条目引用了两个 playertest 热更包的 sha
    （ebf1076… / 83787cd…），而本板 meta.provenance.source_locks 只声明了两条
    documents 快照 —— `publication_contract_errors` 逐条核对 sha 归属，直接红板。

    口径：锁记录**只能从声明过该 sha 的源板搬**，搬不到就报出来，绝不编造 sha。
    角色：本板已有 primary 时，新补的一律记 comparison（同一板只认一个主源）。
    """
    meta = board.setdefault("meta", {})
    prov = meta.setdefault("provenance", {})
    locks = prov.setdefault("source_locks", [])
    have = {str(lk.get("sha256")) for lk in locks}
    want = {str((it.get("provenance") or {}).get("source_lock_sha256"))
            for it in (board.get("items") or [])} - {"", "None", "none"}
    missing = sorted(want - have)
    if not missing:
        return []

    pool: dict[str, dict] = {}
    for name in ("weapon_skin_sfx_text_sources.json", "lottery_periods.json"):
        p = boards / name
        if not p.exists():
            continue
        src = json.loads(p.read_text(encoding="utf-8"))
        for lk in (((src.get("meta") or {}).get("provenance") or {}).get("source_locks") or []):
            pool.setdefault(str(lk.get("sha256")), dict(lk))

    has_primary = any(str(lk.get("role")) == "primary" for lk in locks)
    log: list[str] = []
    for sha in missing:
        lk = pool.get(sha)
        if not lk:
            log.append("⚠ 无法补齐锁 %s（源板未声明，需人工确认）" % sha[:12])
            continue
        new = {"source_id": lk.get("source_id"), "role": "comparison" if has_primary else "primary",
               "sha256": sha, "path": lk.get("path", ""), "bytes": lk.get("bytes", 0),
               "mtime_ns": lk.get("mtime_ns", 0)}
        locks.append(new)
        log.append("补锁 %s（%s，%s）" % (sha[:12], new["source_id"], new["role"]))
    prov["source_locks"] = locks
    return log


def rebuild_skin_items(board: dict, boards: Path, today: str) -> list[str]:
    """按当前 `weapon_skin_sfx_text_sources` 重建「武器皮肤 · 未上线」段（口径同构建器）。

    用户 2026-11-01 指出：2026-10-30 热更新增的皮肤（1110194 青瓷鉴心 / 1110205 瑞秋之狙）
    与已命名条目（1110189 浪漫过载）没进预告板 —— 因为本板仍是 10-21 的旧快照。
    这里直接以源板为唯一事实来源重算这一段的条目集合，不保留历史残留。

    返回改动日志（新增/移除/改名）。
    """
    p = boards / "weapon_skin_sfx_text_sources.json"
    if not p.exists():
        return ["缺源板 weapon_skin_sfx_text_sources.json，跳过"]
    src = json.loads(p.read_text(encoding="utf-8"))

    keep = [it for it in (board.get("items") or []) if it.get("kind") != "武器皮肤"]
    old = {str(it.get("item_id")): it for it in (board.get("items") or [])
           if it.get("kind") == "武器皮肤"}

    log: list[str] = []
    new: list[dict] = []
    for it in src.get("items") or []:
        # 上架状态优先（与 board.html listingOf 口径一致）：已上线的永不进预告
        if str(it.get("listing_status") or "") == "on_sale":
            continue
        st = str(it.get("release_state") or "")
        sd = str(it.get("sale_date") or "")
        if not (st in ("upcoming", "no_sale_field") or (sd and sd > today)):
            continue
        sid = it.get("skin_id") or it.get("id")
        nm = (it.get("name_display") or it.get("name") or "").strip()
        if not nm:
            nm, _ex = resolved_name(str(sid), "", load_name_index(boards))
        media = it.get("_media") or {"images": [], "total": 0}
        new.append({
            "id": "up_skin_%s" % sid,
            "name": nm or ("未命名皮肤 · ID %s" % sid),
            "item_id": sid,
            "kind": "武器皮肤",
            "grade": it.get("grade"),
            "weapon_type": it.get("weapon_type_label"),
            "expect_date": sd or "未定",
            "release_state": st or "unknown",
            "family": "武器皮肤（未上线）", "period_id": "up_skin",
            "period_label": "武器皮肤 · 未上线",
            "family_key": "UpcomingSkin",
            "evidence": it.get("evidence") or "structure",
            "evidence_level": it.get("evidence_level") or "structure-only",
            "status_tags": it.get("status_tags") or ["verified", "static config"],
            "_media": media,
            "icon_state": it.get("icon_state") or ("有图" if (media.get("images") or []) else "未下发"),
            "charm_value": it.get("charm_value"),
            "official_desc": it.get("official_desc") or "",
            "hotfix_source": it.get("hotfix_source") or "",
            "version_status": it.get("version_status") or "",
            "source": "weapon_skin_sfx_text_sources（release_state=%s）" % st,
            "provenance": it.get("provenance"),
        })

    new.sort(key=lambda x: (str(x.get("expect_date") or ""), x.get("item_id") or 0), reverse=True)
    new_ids = {str(x.get("item_id")) for x in new}
    for sid, it in old.items():
        if sid not in new_ids:
            log.append("移除 %s %s（源表已不再算未上线）" % (sid, it.get("name")))
    for it in new:
        sid = str(it.get("item_id"))
        if sid not in old:
            log.append("新增 %s %s（%s，%s 上架）"
                       % (sid, it.get("name"), it.get("hotfix_source") or "源表",
                          it.get("expect_date")))
        elif old[sid].get("name") != it.get("name"):
            log.append("改名 %s %r → %r" % (sid, old[sid].get("name"), it.get("name")))

    # 皮肤段在前、奖池段在后，与既有阅读顺序一致
    board["items"] = new + keep
    return log


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
