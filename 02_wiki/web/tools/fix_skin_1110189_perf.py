# -*- coding: utf-8 -*-
"""1110189 浪漫过载：补全战斗表现（sfx_items），音效下架。

- 数据源：weapon_skin_sfx_function_data 里 skin_id=1110189 的行
- 去掉 sfx_type=7（战斗音效），effect_show 里同步去掉「战斗音效」行
- 从 weapon_skin_audio_attachments 里移除 1110189（不再挂通用喷火器音）
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
CD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
import toolkit_core.bindict_table as BT  # noqa: E402

SKIN = "1110189"
SKIP_TYPES = {7}          # 战斗音效 → 下架
TYPE_NAMES = {3: "命中特效", 4: "击败特效", 6: "攻击弹道", 9: "攻击准星",
              10: "伤害跳字", 13: "核芯联动", 14: "蓄力特效", 15: "专属战斗动作",
              16: "专属待机动作", 20: "切枪动画"}


def rows_of(stem: str):
    raw = (CD / f"{stem}.py").read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + L]
    c = CD / f"{stem}_chs.py"
    pool = BT.parse_legacy_chs_pool(c.read_bytes()) if c.is_file() else []
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
    return rows, pool


def build_items() -> list[dict]:
    rows, _pool = rows_of("weapon_skin_sfx_function_data")
    out = []
    for r in rows:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in (r.get("values") or {}).items()}
        if v.get("skin_id") != int(SKIN):
            continue
        t = v.get("sfx_type")
        if t in SKIP_TYPES:
            continue
        cat = TYPE_NAMES.get(t, f"类型{t}")
        out.append({
            "id": str(r["key"]),
            "row_key": r["key"],
            "display_name": None,
            "sfx_category": cat,
            "sfx_name": None,
            "item_name": None,
            "sfx_type": t,
            "sfx_type_label": f"{cat}（{t}）",
            "sfx_params": v.get("sfx_params"),
            "inline_groups": [],
            "raw_fields": {"skin_id": int(SKIN), "level": v.get("level"), "sfx_type": t,
                           "sfx_params": v.get("sfx_params")},
            "text_status": "no_chs_text",
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "Current hotfix weapon_skin_sfx_function_data row for this skin; 战斗音效行按用户口径下架。",
        })
    out.sort(key=lambda x: (x["sfx_type"] or 0))
    return out


def main() -> int:
    bp = WEB / "data/boards/weapon_skin_sfx_text_sources.json"
    board = json.loads(bp.read_text(encoding="utf-8"))
    card = next(i for i in board["items"] if str(i.get("skin_id")) == SKIN)

    items = build_items()
    card["sfx_items"] = items
    card["sfx_item_count"] = len(items)
    card["named_sfx_item_count"] = sum(1 for x in items
                                       if isinstance(x.get("sfx_params"), str)
                                       and x["sfx_params"].startswith("effect/"))
    card["sfx_audio_state"] = "不适用（本期未提供独立音效）"
    card["sfx_audio_note"] = "2026-10-31 用户口径：音效下架，只保留视觉/战斗表现。"

    es = [e for e in (card.get("effect_show") or []) if e.get("slot") != "战斗音效"]
    card["effect_show"] = es
    card["effect_show_count"] = len(es)

    bp.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print("sfx_items %d 条：%s" % (len(items), [(x["sfx_type"], x["sfx_category"]) for x in items]))
    print("effect_show %d 条：%s" % (len(es), [e.get("slot") for e in es]))

    # 音效附件下架
    ap = WEB / "data/weapon_skin_audio_attachments.json"
    att = json.loads(ap.read_text(encoding="utf-8"))
    skins = att.get("skins", {})
    removed = skins.pop(SKIN, None)
    if removed:
        print("已移除音效附件：", removed.get("name"), "组数", len(removed.get("groups") or []))
    ap.write_text(json.dumps(att, ensure_ascii=False), encoding="utf-8")
    js = WEB / "data/weapon_skin_audio_attachments.js"
    js.write_text("window.WEAPON_SKIN_AUDIO_ATTACHMENTS=window.WEAPON_SKIN_AUDIO_ATTACHMENTS = "
                  + json.dumps(att, ensure_ascii=False) + ";\n", encoding="utf-8")
    print("已重写", js.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
