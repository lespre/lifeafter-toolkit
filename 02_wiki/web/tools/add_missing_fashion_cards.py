# -*- coding: utf-8 -*-
r"""补 2 款「头顶类」缺失时装卡（fw_* 系，落「头发」桶）。

背景（用户口径）：这个游戏头部只有三类 —— **头发（最主要）/ 面饰（戴脸上）/ 头饰（戴头上）**，
但**文案乱用**（大量时装名叫「某某-头饰」其实归头发），所以只能按**内部部位码**分：
  · fashion_data.part_type = hat / player_appear_data.part = 1  → 头发
  · player_module_appear_data.part = 2 → 头饰、20001 → 面饰
本脚本按这条口径走，**不按名字改桶**。

只补四款（其余缺口 三周年纪念 / 150级头盔 / 150头 / 明艳黄 等是开发占位或纯配色行，不在补列）：

  A. 沙漠珍珠裁切-头饰   fashion_data 466580..466586（永久 + 1/3/5/7/14/30 天）
     model 3659，icons jump:180947 → icon_h_f_3659002 / icon_h_m_3659002
     ★ desc 表里写的是「占位占位」⇒ 视为占位，不留脏文案，只写 desc_note 说明。

  B. 绒帽团团-头饰       player_appear_data 1375301 / 11375301（无 fashion_data 行）
     模型 character/players2021/b_f_3753/h_f_3753001.gim 与 b_m_3753/h_m_3753001.gim
     ⇒ 按「模型名去扩展名 = 图标基名」得 icon_h_f_3753001 / icon_h_m_3753001（女/男）。

写盘：卡片走 fw_* schema（与板上其它时装卡同构），起源走 fashion_data / player_appear_data
各自的行锁；图标用 pe_fetch 实导到 assets/fashion_posters/，取不到如实标缺图，不造假图。
幂等：板上已有同名卡就跳过；已导出且体积正常的 PNG 不重复导。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

SHARED = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
sys.path.insert(0, str(SHARED))
FETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"
sys.path.insert(0, str(FETCH))

from board_io import write_board_pair  # noqa: E402
import notes_util  # noqa: E402
from toolkit_core import bindict_table as BT  # noqa: E402
import pe_fetch  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
OUT = WEB / "assets/fashion_posters"

FD_SHA = "0a9d368c03d17c1b1ea19706d4975a64cdfe7281e3c2bdc015385d933df32b0b"
PA_SHA = "61f7189bd6f94f58c07d350405a8820bc461183f03cee0b968df8dd2ff4cb199"
FD_SRC = "fashion-wardrobe-struct"
PA_SRC = "fashion-parts-supplement-player_appear_data"
PLACEHOLDER_DESC = {"占位占位", "占位", "TODO", "-"}
MIN_PNG = 512
SUFFIXES = ("_b", "_s", "")

# 目标（行键 → 展示名）；按「去 -N天」分组
TARGETS = [
    {"table": "fashion_data", "rows": [466580, 466581, 466582, 466583, 466584, 466585, 466586],
     "name": "沙漠珍珠裁切-头饰", "part": "头发", "part_label": "头饰",
     "part_source": "part_type", "src": FD_SRC, "sha": FD_SHA,
     "table_str": "com\\cdata\\fashion_data.py"},
    {"table": "player_appear_data", "rows": [1375301, 11375301],
     "name": "绒帽团团-头饰", "part": "头发", "part_label": "头饰",
     "part_source": "player_appear_data.part_code", "src": PA_SRC, "sha": PA_SHA,
     "table_str": "com\\cdata\\player_appear_data.py"},
    # C/D. 耀·炽海天姿：**不是** 炽海天姿 的别名（原先判错，2026-11-01 全量审计纠正）。
    #   证据：icons 不同（jump:367808 vs 212896、衣服 jump:376846 vs 284028）、
    #   appear_ids 不同（头饰 jump:367798 vs 212886、衣服 jump:376853 vs 284058）、
    #   player_appear_data 里也是独立行（1500103 / 3500102 vs 1500101 / 3500101）。
    #   板上同类「典藏/幻彩」变体一律独立成卡（102 张）⇒ 这里按同一惯例补。
    {"table": "fashion_data", "rows": [463730, 463731, 463732, 463733, 463734, 463735, 463736],
     "name": "耀·炽海天姿-头饰", "part": "头发", "part_label": "头饰",
     "part_source": "part_type", "src": FD_SRC, "sha": FD_SHA,
     "table_str": "com\\cdata\\fashion_data.py"},
    {"table": "fashion_data", "rows": [463770, 463771, 463772, 463773, 463774, 463775, 463776],
     "name": "耀·炽海天姿-衣服", "part": "衣服", "part_label": "衣服",
     "part_source": "part_type", "src": FD_SRC, "sha": FD_SHA,
     "table_str": "com\\cdata\\fashion_data.py"},
]


def load(stem):
    raw = (CD / (stem + ".py")).read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * cnt:]
    pool = BT.parse_legacy_chs_pool((CD / (stem + "_chs.py")).read_bytes())
    rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
    out = {}
    for r in rows:
        out[r["key"]] = {k: (v[1] if isinstance(v, tuple) else v) for k, v in r["values"].items()}
    return out, blob, pool


def gs(blob, pool, off, depth=0):
    if depth > 6 or not off:
        return []
    g = BT.read_27_group(blob, off)
    if not g:
        return []
    kind, els = g
    out = []
    if kind == 0x0B:
        for e in els:
            out.extend(gs(blob, pool, e, depth + 1))
    elif kind == 0x05:
        for e in els:
            if 0 <= e < len(pool):
                out.append(pool[e])
    return out


def icon_paths(table, row, blob, pool):
    """返回按性别排序的图标基路径列表（去扩展名）。"""
    if table == "fashion_data":
        ic = row.get("icons")
        if isinstance(ic, str) and ic.startswith("jump:"):
            return [p for p in gs(blob, pool, int(ic.split(":")[1])) if p]
        if isinstance(ic, str) and ic:
            return [ic]
        return []
    # player_appear_data：模型名去扩展名 = 图标基名（模型 h_f_3753001.gim → icon_h_f_3753001）
    out = []
    for fld in ("model_name", "high_model_name"):
        m = str(row.get(fld) or "").replace("\\", "/")
        if m.endswith(".gim"):
            stem = m.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            p = "ui/item_icon/icon_" + stem
            if not stem.endswith("_high001") and p not in out:
                out.append(p)
    return out


def gender_of(path: str):
    if "_f_" in path:
        return "女"
    if "_m_" in path:
        return "男"
    return None


def probe(conn, base):
    for s in SUFFIXES:
        r = pe_fetch.resolve(base, s, conn)
        if r:
            return r[0]
    return None


def main() -> int:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    have = {str(x.get("name")) for x in items}
    conn = pe_fetch.con()
    OUT.mkdir(parents=True, exist_ok=True)

    added, skipped = [], []
    for t in TARGETS:
        if t["name"] in have:
            skipped.append(t["name"])
            continue
        src, blob, pool = load(t["table"])
        rows = [src[k] for k in t["rows"] if k in src]
        if not rows:
            skipped.append(t["name"] + "（源行缺失）")
            continue
        base_row = src[t["rows"][0]]
        cid = "fw_" + hashlib.sha1(
            ("%s|%s" % (t["name"], t["rows"][0])).encode("utf-8")).hexdigest()[:10]

        paths = []
        for r in rows:
            for p in icon_paths(t["table"], r, blob, pool):
                if p.startswith("ui/") and p not in paths:
                    paths.append(p)
        imgs, icons_all, missing = [], [], []
        for i, p in enumerate(paths):
            g = gender_of(p)
            rel = "assets/fashion_posters/%s%s.png" % (cid, "" if i == 0 else "_%d" % i)
            dst = WEB / rel
            ok = dst.is_file() and dst.stat().st_size > MIN_PNG
            full = probe(conn, p)
            if not ok and full:
                if dst.exists():
                    dst.unlink()
                try:
                    ok = bool(pe_fetch.export(full, dst)) and dst.stat().st_size > MIN_PNG
                except Exception:
                    ok = False
            if ok:
                icons_all.append({"path": p, "gender": g, "png": rel})
                imgs.append({"png": rel, "base": p.rsplit("/", 1)[-1],
                             "label": g or "图标",
                             "source": "%s → %s" % (t["table_str"], p),
                             "fetch": "pe", "bytes": dst.stat().st_size})
            else:
                icons_all.append({"path": p, "gender": g, "png": None})
                missing.append(p)

        days = sorted({r.get("valid_days") for r in rows if isinstance(r.get("valid_days"), int)})
        desc = base_row.get("desc")
        desc_note = None
        if not desc:
            desc_note = "%s.desc 为空" % t["table"]
        elif str(desc).strip() in PLACEHOLDER_DESC:
            desc_note = "%s.desc 是占位文本「%s」，不作为描述展示" % (t["table"], desc)
            desc = None
        else:
            desc_note = "%s.desc" % t["table"]

        prov = {
            "source_id": t["src"],
            "source_lock_sha256": t["sha"],
            "table": t["table_str"],
            "row_key": t["rows"][0],
            "row_keys": list(t["rows"]),
            "field_refs": (["name", "desc", "model_id", "charm_value", "level", "icons",
                            "valid_days", "part_type"] if t["table"] == "fashion_data"
                           else ["name", "part", "model_name"]),
            "name_source": "%s#name（去 -N天 后缀）" % t["table_str"],
            "part_source": t["part_source"],
            "rebuild": "add-missing-20261101（按部位码补漏款）",
            "upstream": {"package_sha256": t["sha"], "entry_index": None,
                         "file_id": None, "decoded_sha256": None, "role": None},
            "locator_chain": {
                "chain_status": "replayed-structural",
                "scope": "record",
                "no_cross_source_field_join": True,
                "steps": [{
                    "kind": "decoded-table-row",
                    "source_id": t["src"],
                    "table": t["table_str"],
                    "row_key": t["rows"][0],
                    "field_refs": (["name", "desc", "model_id", "charm_value", "level",
                                    "icons", "valid_days", "part_type"]
                                   if t["table"] == "fashion_data"
                                   else ["name", "part", "model_name"]),
                }],
            },
        }

        card = {
            "id": cid,
            "name": t["name"],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": ("fashion_data 表逐行解码（name/desc/model_id/charm_value/level/icons 字段）"
                       if t["table"] == "fashion_data"
                       else "player_appear_data 表逐行解码（name/part/model_name 字段）"),
            "tables": [t["table"] + ".py", t["table"] + "_chs.py"],
            "row_keys": list(t["rows"]),
            "name_variants": sorted({str(r.get("name")) for r in rows}),
            "part": t["part"],
            "part_source": t["part_source"],
            "part_label": t["part_label"],
            "part_bucket": [t["part"]],
            "model_id": base_row.get("model_id"),
            "model_ids": [base_row.get("model_id")] if base_row.get("model_id") is not None else [],
            "grade_level": base_row.get("level"),
            "grade_levels": [base_row.get("level")] if base_row.get("level") is not None else [],
            "charm_value": base_row.get("charm_value"),
            "durations": days,
            "duration_variants": days,
            "time_limited_variants": days,
            "has_permanent": any(r.get("valid_days") is None for r in rows),
            "duration_state": ("mixed" if days and any(r.get("valid_days") is None for r in rows)
                               else ("timed" if days else "permanent")),
            "desc": desc,
            "desc_note": desc_note,
            "icon_state": "有图" if imgs else "缺图",
            "icon_count": len(imgs),
            "icons_all": icons_all,
            "status_tags": ["static config"],
            "provenance": prov,
        }
        if imgs:
            card["_media"] = {"images": imgs, "icons_total": len(imgs), "total": len(imgs)}
        else:
            card["_media"] = {"images": [], "total": 0}
            card["icon_missing_reason"] = "表里登记的图标路径在 PE 包里取不到图"
        if missing and imgs:
            card["icon_notes"] = missing
        added.append(card)

    if not added:
        print("无需补卡（已存在或源行缺失）：", skipped)
        return 0

    items.extend(added)
    note = ("按用户口径「头部只有 头发/面饰/头饰 三类、文案乱用只能看部位码」补漏款时装卡："
            + "；".join("%s（%s %s）" % (c["name"], c["provenance"]["table"],
                                        c["provenance"]["row_key"]) for c in added)
            + "。归属按部位码（fashion_data.part_type=hat / player_appear_data.part=1 → 头发），"
              "不按名字里的「-头饰」字样改桶。"
            + ("耀·炽海天姿 在 2026-11-01 全量审计里改判为独立外观（icons 与 appear_ids 都和 炽海天姿 不同），"
               "按板上「典藏/幻彩变体独立成卡」的惯例单独出卡，不再当 version_merge 别名。"
               if any("耀·炽海天姿" in c["name"] for c in added) else "")
            + "".join(" %s 的描述是占位文本，未采用。" % c["name"] for c in added
                      if c.get("desc_note") and "占位文本" in (c.get("desc_note") or "")))
    notes_util.append_note(board, note)
    write_board_pair(BOARD, board)
    print("已补 %d 张：%s" % (len(added), "、".join(c["name"] for c in added)))
    for c in added:
        print("  %-24s %s 有图%d 行%s" % (c["name"], c["icon_state"], c["icon_count"],
                                          c["provenance"]["row_key"]))
    if skipped:
        print("  跳过：", skipped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
