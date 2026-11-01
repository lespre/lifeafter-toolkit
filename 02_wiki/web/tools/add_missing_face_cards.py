# -*- coding: utf-8 -*-
r"""补齐（一）人物时装 · 头饰 / 面饰 / 挂饰 里**漏掉的条目**（face_* 卡）。

背景：
  这批卡是早先从独立面容板 fashion_face 并入的，来源只取了
  「面饰专池 BA entry010816/009169」那批名字，**不是整张表的全量**。
  player_module_appear_data 里 part=2(头饰) 797 行、part=20001(面饰) 390 行、
  part=1(挂饰) 13 行，按「去掉 -N天 时限后缀」归并后共 190 个条目，
  板上只有 177 个 ⇒ 漏 13 个（例：星穹环冕 / 炽天之冕 / 垂垂兔耳 / 桂影花枝 /
  喵影星帷 / 八载甜梦 / 白昼光影 / 王面面具 / 瓷影流珠 / 青瓷流梦 /
  入侵者挂饰 / 救救我挂饰 / 明日世界的角色用圣诞帽）。

规则（唯一口径，可复算）：
  1. 分组：同表内 (part, name 去掉尾部 `-N天`) 相同的行归一张卡；
  2. 部位：part 2→头饰 / 20001→面饰 / 1→挂饰（内部部位代码，不看名字）；
  3. 卡名 = 去时限后缀的基名；row_key = 组内最小行键；
     row_variants = 组内全部行键（升序，含基行）；
     time_limited_variants = 组内出现过的 valid_days（去掉 None，升序）；
  4. charm_value / desc 直接取该行；缺失就留空并写明原因，不伪造；
  5. 新卡 id 用 face_<4 位序号>，接在现有 face_* 最大序号之后；
     插入位置紧跟最后一张 face_* 卡（保持这组条目连续）；
  6. 已存在同名 face_* 卡 ⇒ 跳过（幂等）。

溯源（与现有 face_* 卡同构）：
  provenance.source_id=documents-py314-current、table=player_module_appear_data、
  row_key/field_refs/locator_chain 全部按行直取；charm/desc/icon 三块同源同表同行，
  不新增跨源 join（遵守 no-cross-source-field-join）。_prov_shape 用
  provenance_defaults._shape_signature() 现算，不写死常量。

用法：
    python add_missing_face_cards.py --dry     # 只报告缺哪些
    python add_missing_face_cards.py           # 落盘（2D 图/描述由 fill_face_media_desc.py 随后补）
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import struct
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

SHARED = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
if SHARED.exists():
    sys.path.insert(0, str(SHARED))

from board_io import write_board_pair  # noqa: E402
import notes_util  # noqa: E402
from provenance_defaults import _shape_signature  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/fashion_wardrobe.json"

TBL = "player_module_appear_data"
TBL_PATH = CD / f"{TBL}.py"
TBL_CHSE = CD / f"{TBL}_chs.py"
SRC_ID = "documents-py314-current"
MEDIA_ID = "fashion-face-player_module_appear_data-media"
CHARM_ID = "fashion-face-player_module_appear_data-charm"
PACK_SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"

PART_MAP = {2: "头饰", 20001: "面饰", 1: "挂饰"}
DUR = re.compile(r"-\s*(\d+)\s*天\s*$")


def load_table() -> dict:
    raw = TBL_PATH.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    from toolkit_core import bindict_table as BT
    pool = BT.parse_legacy_chs_pool(TBL_CHSE.read_bytes()) if TBL_CHSE.exists() else {}
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)
    out = {}
    for r in rows:
        v = {k: (vv[1] if isinstance(vv, tuple) else vv) for k, vv in r["values"].items()}
        try:
            out[int(r.get("key"))] = v
        except (TypeError, ValueError):
            continue
    return out


def group_rows(src: dict) -> dict:
    """(part, 基名) → 行键列表（升序）"""
    g = collections.defaultdict(list)
    for k, d in src.items():
        nm = str(d.get("name") or "").strip()
        base = DUR.sub("", nm).strip()
        if not base:
            continue
        g[(d.get("part"), base)].append(k)
    for v in g.values():
        v.sort()
    return dict(g)


def next_face_index(items: list) -> int:
    mx = -1
    for it in items:
        m = re.match(r"^face_(\d+)$", str(it.get("id", "")))
        if m:
            mx = max(mx, int(m.group(1)))
    return mx + 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    src = load_table()
    groups = group_rows(src)
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]

    have = {str(it.get("name")) for it in items if str(it.get("id", "")).startswith("face_")}
    todo = []
    for (part, base), keys in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[1][0])):
        if part not in PART_MAP:
            continue
        if base in have:
            continue
        todo.append((part, base, keys))

    print("表内条目 %d ｜ 板上 face_* 名 %d ｜ 缺 %d" % (len(groups), len(have), len(todo)))
    for part, base, keys in todo:
        print("  part=%-6s %-22s 行 %s" % (part, base, keys[:3]))

    if not todo:
        print("无缺口。")
        return 0
    if a.dry:
        print("（--dry：未写盘）")
        return 0

    idx = next_face_index(items)
    last_face_pos = -1
    for pos, it in enumerate(items):
        if str(it.get("id", "")).startswith("face_"):
            last_face_pos = pos

    new_cards = []
    for part, base, keys in todo:
        rk = keys[0]
        row = src[rk]
        rows = [src[k] for k in keys]
        days = sorted({r.get("valid_days") for r in rows if isinstance(r.get("valid_days"), int)})
        bucket = PART_MAP[part]
        cid = "face_%04d" % idx
        idx += 1
        cv = row.get("charm_value")
        desc = row.get("desc")
        prov = {
            "source_id": SRC_ID,
            "source_lock_sha256": PACK_SHA,
            "table": TBL,
            "row_key": str(rk),
            "field_refs": ["name", "part", "icon", "desc"],
            "name_source": f"{TBL}.name",
            "upstream": {"package_sha256": PACK_SHA, "role": TBL},
            "locator_chain": {
                "chain_status": "replayed-structural",
                "scope": "record",
                "no_cross_source_field_join": True,
                "steps": [{
                    "kind": "decoded-table-row",
                    "source_id": SRC_ID,
                    "table": TBL,
                    "row_key": str(rk),
                    "field_refs": ["name", "part", "icon", "desc"],
                }],
            },
            "charm_source": {
                "source_id": CHARM_ID,
                "source_lock_sha256": PACK_SHA,
                "table": TBL,
                "row_key": rk,
                "field_refs": ["charm_value"],
            },
            "desc_source": {
                "source_id": MEDIA_ID,
                "source_lock_sha256": PACK_SHA,
                "table": TBL,
                "row_key": rk,
                "field_refs": ["desc"],
            },
            "icon_source": {
                "source_id": MEDIA_ID,
                "source_lock_sha256": PACK_SHA,
                "table": TBL,
                "row_key": rk,
                "field_refs": ["icon"],
            },
        }
        card = {
            "id": cid,
            "name": base,
            "evidence": "structure",
            "source": (f"{TBL} 行解码（row_key {rk} 直取 name / part / icon / desc / charm_value；"
                       f"时限变体为同组行 row_variants 合并）"),
            "part": bucket,
            "part_bucket": [bucket],
            "part_source": TBL,
            "time_limited_variants": days,
            "desc": None,
            "desc_note": None,
            "icon_state": "缺图",
            "charm_value": cv,
            "row_variants": [str(k) for k in keys],
            "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "provenance": prov,
        }
        card["_prov_shape"] = _shape_signature(prov)
        if cv is None:
            card["charm_note"] = f"{TBL}.charm_value 为空（行 {rk}）"
        else:
            card["charm_note"] = f"{TBL}.charm_value（行 {rk}）"
        if not desc:
            card["desc_note"] = f"{TBL}.desc 为空（行 {rk}）"
        new_cards.append(card)

    pos = last_face_pos + 1 if last_face_pos >= 0 else 0
    items[pos:pos] = new_cards

    names = "、".join(c["name"] for c in new_cards)
    note = ("头饰/面饰/挂饰补漏：原并入只取了「面饰专池」那批名字，不是整表全量。"
            f"按 {TBL} 的 (part, 去时限名) 归并共 {len(groups)} 个条目、板上原有 {len(have)} 个，"
            f"本次补 {len(new_cards)} 个（{names}）；"
            "部位按内部代码 part 2/20001/1 判定，2D 图与描述随后由 fill_face_media_desc.py 按行回填。")
    notes_util.append_note(d, note)
    write_board_pair(BOARD, d)
    print("已补 %d 张卡（%s），写回 %s（共 %d 条）"
          % (len(new_cards), names, BOARD.name, len(items)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
