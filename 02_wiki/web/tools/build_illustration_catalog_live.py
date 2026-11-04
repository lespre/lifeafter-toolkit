# -*- coding: utf-8 -*-
r"""图鉴收集总表构建器 —— 从 PE 活树 illustration_collect_* 系列表逐表重建。

用法::

    python 02_wiki/web/tools/build_illustration_catalog_live.py [--dry]

口径（2026-11-04 重写，替换 tools/rebuild_illustration.py 的两表版）::

    illustration_collect_food_data        581 → 图鉴·食物（食谱大全）
    illustration_collect_ingredient_data  247 → 图鉴·食材（食材图鉴）
    illustration_collect_item_data        373 → 特殊能力，其中 33 条按 spore 表重锚
    illustration_collect_spore_data        33 → 图鉴·孢子技能（与 item_data 同名 1:1，不重复造条）
    illustration_collect_monster_data     260 → 图鉴·怪物
    illustration_collect_ocean_item_data   32 → 图鉴·海域特产
    illustration_collect_ocean_relic_data  42 → 图鉴·遗失碎片
    illustration_collect_knight_collection  4 → 图鉴·骑士纪念物
    illustration_collect_big_type_data      8 → 图鉴·大类（点数上限取 big_type_point_num.cn）

非条目表（报告里给行数，不产生条目）::

    illustration_collect_big_type_point_num  8 行 → 已并入大类条目的 point
    illustration_collect_quest_icon_data    10 行 → 纯图标资源（finish/progress icon），无名称/点数
    illustration_collect_hurt_monster        0 行可解（0x73 模块，无内联表体；语义是怪物类型→受击阈值）
    illustration_collect_map_data            树里缺 .py（只有 .nxs 与 _chs），0 行

铁律:
  * 名字只从活树取：edible_item_data（食谱/食材）→ 道具总表板兜底 → 「道具 <id>」。
  * 已有 id 的 provenance 逐条沿用旧板原样（同 id 同结构）；新条目按同表构造同结构。
  * 幂等：同一天连跑两次，.json/.js 字节完全相同。
  * 只写 boards/illustration_catalog.{json,js}，不跑 build_wiki.py。
"""
from __future__ import annotations

import argparse
import copy
import datetime
import json
import sys
from collections import Counter
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from la_paths import PROJ  # noqa: E402

WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/illustration_catalog.json"

from _src import cdata_dir  # noqa: E402
import rebuild_lottery_periods as R  # noqa: E402
from board_io import write_board_pair  # noqa: E402
from provenance_defaults import SHAPE_KEY, _shape_signature  # noqa: E402

# 跟随 LA_SOURCE / LA_CDATA_ROOT：Table() 内部用 R.TREE 计算 rel，换源时必须同步
CD = Path(cdata_dir())
if CD != Path(R.TREE):
    R.TREE = CD

UPSTREAM_ROLE = "SuperFashion"
FIELD_REFS = ["item_id", "name", "slot", "kind"]
STEP_REFS = ["name", "desc"]


# ─────────────────────────────────────────── 读表
def opt(stem: str):
    return R._opt_table(CD / (stem + ".py"), CD / (stem + "_chs.py"))


def val(row: dict, key: str):
    return row["values"].get(key)


def txt(v) -> str:
    return str(v or "").strip()


def build_name_map() -> dict[str, str]:
    """item_id → 名字。活树优先（edible_item_data 带全量食谱/食材名），道具总表板兜底。"""
    names: dict[str, str] = {}
    ed = opt("edible_item_data")
    for k, v in ed.by_key.items():
        n = txt(val(v, "name"))
        if n:
            names.setdefault(str(k), n)
    p = WEB / "data/boards/item_master_full.json"
    if p.is_file():
        try:
            for it in json.loads(p.read_text(encoding="utf-8")).get("items") or []:
                n = txt(it.get("name"))
                if n:
                    names.setdefault(str(it.get("item_id")), n)
        except Exception:
            pass
    return names


# ─────────────────────────────────────────── 溯源
def make_prov(lock: dict, table: str, row_key: int) -> dict:
    """按旧板同结构构造 provenance（键集合 = add4586e5ef0b884 形态）。"""
    sid = lock.get("source_id") or "documents-py314-current"
    return {
        "source_id": sid,
        "source_lock_sha256": lock.get("sha256", ""),
        "table": table,
        "row_key": row_key,
        "field_refs": list(FIELD_REFS),
        "upstream": {"role": UPSTREAM_ROLE},
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{
                "kind": "decoded-table-row",
                "source_id": sid,
                "table": table,
                "row_key": row_key,
                "field_refs": list(STEP_REFS),
            }],
        },
    }


def attach_prov(item: dict, table: str, row_key: int, old: dict, lock: dict,
                *, force_new: bool = False) -> None:
    """同 id 沿用旧板 provenance 原样；新 id 按同表构造。

    force_new=True：id 虽是旧的，但字段来源已换表（孢子技能从 item_data 重锚到 spore），
    此时必须按新表行构造，否则 source 与 provenance.table 会对不上。
    """
    prev = None if force_new else old.get(item["id"])
    if prev and isinstance(prev.get("provenance"), dict):
        item["provenance"] = copy.deepcopy(prev["provenance"])
        item["_prov_shape"] = prev.get(SHAPE_KEY) or _shape_signature(item["provenance"])
    else:
        item["provenance"] = make_prov(lock, table, row_key)
        item["_prov_shape"] = _shape_signature(item["provenance"])


def base_item(item_id, name, kind, point, source) -> dict:
    return {
        "item_id": item_id,
        "name": name,
        "kind": kind,
        "point": point,
        "evidence": "structure",
        "evidence_level": "static/candidate",
        "status_tags": ["static config"],
        "source": source,
    }


def finish(it: dict) -> dict:
    """按旧板字段顺序收尾（id 打头，provenance 与 _prov_shape 结尾）。"""
    out = {"id": it.pop("id")}
    out.update(it)
    return out


# ─────────────────────────────────────────── 主流程
def build(dry: bool = False) -> int:
    old_board = json.loads(BOARD.read_text(encoding="utf-8")) if BOARD.is_file() else {"meta": {}, "items": []}
    OLD = {it["id"]: it for it in old_board.get("items") or [] if isinstance(it, dict) and it.get("id")}
    meta = copy.deepcopy(old_board.get("meta") or {})
    locks = ((meta.get("provenance") or {}).get("source_locks") or [{}])
    lock = locks[0]
    names = build_name_map()

    items: list[dict] = []
    per_table: list[tuple[str, int, int, str]] = []   # (表, 读入行数, 产出条目, 说明)

    def emit(table: str, prefix: str, kind: str, id_field: str, desc_kind: str, *, items_iter,
             extra_tag: str | None = None) -> int:
        n = 0
        for row in items_iter:
            key = row["key"]
            raw_id = val(row, id_field)
            if raw_id is None:
                # monster / ocean_relic / knight 等表没有 item_id 列：条目身份就是行键
                raw_id = key
            name = txt(val(row, "name"))
            if not name:
                continue
            it = base_item(raw_id, name, kind, val(row, "point_num"), table)
            if extra_tag:
                it["status_tags"] = it["status_tags"] + [extra_tag]
            if desc_kind == "desc":
                it["desc"] = txt(val(row, "desc"))
            elif desc_kind == "extra_desc":
                it["extra_desc"] = txt(val(row, "extra_desc"))
            it["id"] = f"{prefix}_{key}"
            attach_prov(it, table, key, OLD, lock)
            items.append(finish(it))
            n += 1
        return n

    # 1) 食谱（食物）
    t = opt("illustration_collect_food_data")
    rows = sorted(t.by_key.values(), key=lambda r: r["key"])
    n = 0
    for row in rows:
        iid = val(row, "item_id")
        if iid is None:
            continue
        s = str(iid)
        it = base_item(s, names.get(s) or f"道具 {s}", "图鉴·食物", val(row, "point_num"),
                       "illustration_collect_food_data")
        it["extra_desc"] = txt(val(row, "extra_desc"))
        it["id"] = f"ifood_{row['key']}"
        attach_prov(it, "illustration_collect_food_data", row["key"], OLD, lock)
        items.append(finish(it))
        n += 1
    per_table.append(("illustration_collect_food_data", len(t.by_key), n, "食谱/食物，名字走 edible_item_data"))

    # 2) 食材
    t = opt("illustration_collect_ingredient_data")
    rows = sorted(t.by_key.values(), key=lambda r: r["key"])
    n = 0
    for row in rows:
        iid = val(row, "item_id")
        if iid is None:
            continue
        s = str(iid)
        it = base_item(s, names.get(s) or f"道具 {s}", "图鉴·食材", val(row, "point_num"),
                       "illustration_collect_ingredient_data")
        it["extra_desc"] = txt(val(row, "extra_desc"))
        it["id"] = f"iingr_{row['key']}"
        attach_prov(it, "illustration_collect_ingredient_data", row["key"], OLD, lock)
        items.append(finish(it))
        n += 1
    per_table.append(("illustration_collect_ingredient_data", len(t.by_key), n, "食材图鉴"))

    # 3) 孢子技能：先取名字集合（决定 item_data 里哪 33 条要重锚到本表）
    spore = opt("illustration_collect_spore_data")
    spore_rows = {txt(val(r, "name")): r for r in spore.by_key.values() if txt(val(r, "name"))}
    spore_names = set(spore_rows)

    # 4) 特殊能力（item_data 有名行，剔除已重锚的孢子技能）
    t = opt("illustration_collect_item_data")
    n_item = 0
    n_moved = 0
    for row in sorted(t.by_key.values(), key=lambda r: r["key"]):
        name = txt(val(row, "name"))
        if not name:
            continue
        if name in spore_names:
            n_moved += 1
            continue
        it = base_item(val(row, "item_id"), name, "图鉴·特殊能力", val(row, "point_num"),
                       "illustration_collect_item_data")
        it["desc"] = txt(val(row, "desc"))
        it["id"] = f"iitem_{row['key']}"
        attach_prov(it, "illustration_collect_item_data", row["key"], OLD, lock)
        items.append(finish(it))
        n_item += 1
    per_table.append(("illustration_collect_item_data", len(t.by_key), n_item,
                      f"仅有名行；其中 {n_moved} 条同名孢子技能重锚到 spore 表"))

    # 5) 孢子技能条目（id 沿用旧板同名 iitem_* 的 id，避免站内链接失效）
    old_by_name = {}
    for it in items:
        old_by_name.setdefault(it["name"], it["id"])
    for it in OLD.values():
        old_by_name.setdefault(txt(it.get("name")), it["id"])
    n = 0
    for row in sorted(spore.by_key.values(), key=lambda r: r["key"]):
        name = txt(val(row, "name"))
        if not name:
            continue
        it = base_item(val(row, "item_id") if val(row, "item_id") is not None else row["key"],
                       name, "图鉴·孢子技能", val(row, "point_num"),
                       "illustration_collect_spore_data")
        it["desc"] = txt(val(row, "desc"))
        it["id"] = old_by_name.get(name) or f"ispore_{row['key']}"
        attach_prov(it, "illustration_collect_spore_data", row["key"], OLD, lock, force_new=True)
        items.append(finish(it))
        n += 1
    per_table.append(("illustration_collect_spore_data", len(spore.by_key), n,
                      "与 item_data 同名 1:1，不重复造条；id 沿用旧 iitem_*"))

    # 6) 怪物
    t = opt("illustration_collect_monster_data")
    n = emit("illustration_collect_monster_data", "imon", "图鉴·怪物", "item_id", "desc",
             items_iter=sorted(t.by_key.values(), key=lambda r: r["key"]))
    per_table.append(("illustration_collect_monster_data", len(t.by_key), n, "怪物研究学"))

    # 7) 海域特产
    t = opt("illustration_collect_ocean_item_data")
    n = emit("illustration_collect_ocean_item_data", "iocn", "图鉴·海域特产", "item_id", "desc",
             items_iter=sorted(t.by_key.values(), key=lambda r: r["key"]))
    per_table.append(("illustration_collect_ocean_item_data", len(t.by_key), n, "海洋收集·物产"))

    # 8) 遗失碎片
    t = opt("illustration_collect_ocean_relic_data")
    n = emit("illustration_collect_ocean_relic_data", "irel", "图鉴·遗失碎片", "item_id", "desc",
             items_iter=sorted(t.by_key.values(), key=lambda r: r["key"]))
    per_table.append(("illustration_collect_ocean_relic_data", len(t.by_key), n, "海洋收集·遗物"))

    # 9) 骑士纪念物
    t = opt("illustration_collect_knight_collection_data")
    n = emit("illustration_collect_knight_collection_data", "iknt", "图鉴·骑士纪念物", "item_id", "desc",
             items_iter=sorted(t.by_key.values(), key=lambda r: r["key"]))
    per_table.append(("illustration_collect_knight_collection_data", len(t.by_key), n, "骑士纪念物"))

    # 10) 大类：名称/标题来自 big_type_data，点数上限来自 big_type_point_num.cn
    bt = opt("illustration_collect_big_type_data")
    bp = opt("illustration_collect_big_type_point_num")
    n = 0
    for key in sorted(bt.by_key):
        row = bt.by_key[key]
        name = txt(val(row, "big_type_name")) or txt(val(row, "title"))
        if not name:
            continue
        point = val(bp.by_key[key], "cn") if key in bp.by_key else None
        types = bt.jump_values(val(row, "include_types"))
        it = base_item(key, name, "图鉴·大类", point, "illustration_collect_big_type_data")
        it["extra_desc"] = txt(val(row, "title"))
        it["desc"] = f"包含 {len(types)} 个子类" if types else ""
        it["id"] = f"ibigt_{key}"
        attach_prov(it, "illustration_collect_big_type_data", key, OLD, lock)
        # 点数上限来自另一张表，写进同一份 provenance 的 note，不另造条目
        if key in bp.by_key:
            it["provenance"] = copy.deepcopy(it["provenance"])
            it["provenance"]["note"] = f"point 取自 illustration_collect_big_type_point_num 行 {key} 的 cn 列"
            it["_prov_shape"] = _shape_signature(it["provenance"])
        items.append(finish(it))
        n += 1
    per_table.append(("illustration_collect_big_type_data", len(bt.by_key), n,
                      "8 大类；point 并入 big_type_point_num.cn"))

    # 非条目表：只统计行数
    for stem, note in [
        ("illustration_collect_big_type_point_num", "行数已并入大类条目 point（cn 列）"),
        ("illustration_collect_quest_icon_data", "纯图标资源表（finish/progress icon），无名称/点数"),
        ("illustration_collect_hurt_monster", "无内联表体（0x73 模块），0 行可解；怪物类型→受击阈值"),
        ("illustration_collect_map_data", "树里缺 .py（仅 .nxs 与 _chs），0 行"),
    ]:
        t = opt(stem)
        per_table.append((stem, len(getattr(t, "by_key", {})), 0, note))

    # ── 去重 / 完整性
    seen, dup = set(), []
    for it in items:
        if it["id"] in seen:
            dup.append(it["id"])
        seen.add(it["id"])
    assert not dup, f"id 重复: {dup[:10]}"

    # ── meta
    kinds = Counter(it["kind"] for it in items)
    state = {"条目": len(items)}
    for k, c in kinds.items():
        state[k.replace("图鉴·", "")] = c
    meta["generated"] = datetime.date.today().isoformat()
    meta["state_summary"] = state
    meta["source_label"] = ("PE 测试服还原树 com\\cdata · illustration_collect_* 系列 "
                            f"（{len(per_table)} 张表）")
    meta["notes"] = (
        "逐表重建：food 581 / ingredient 247 / item 340 / spore 33 / monster 260 / "
        "ocean_item 32 / ocean_relic 42 / knight 4 / big_type 8。"
        "孢子技能 33 条与 illustration_collect_item_data 同名 1:1，从 item_data 移出并重锚到 "
        "spore 表（id 沿用旧板 iitem_*，站内链接不变），不重复造条。"
        "大类 8 条为分类行，point 取 illustration_collect_big_type_point_num.cn（各服点数上限）。"
        "名字只从活树取：edible_item_data → 道具总表板兜底 → 「道具 <id>」；"
        "quest_icon_data / hurt_monster / map_data 为非条目表，不产生条目（见构建报告）。"
        "provenance 同 id 沿用旧板原样，新条目按同表同结构构造；包锁沿用旧板 source_locks。"
    )

    board = {"meta": meta, "periods": old_board.get("periods") or [], "items": items}

    # ── 报告
    old_ids = set(OLD)
    new_ids = {it["id"] for it in items}
    miss = sorted(old_ids - new_ids)
    add = len(new_ids - old_ids)
    named = sum(1 for it in items
                if txt(it.get("name")) and not str(it.get("name")).startswith("道具 "))
    with_point = sum(1 for it in items if it.get("point") is not None)
    print(f"图鉴收集总表：{len(items)} 条（旧板 {len(old_ids)} 条，新增 {add}，缺 {len(miss)}）")
    print(f"{'来源表':44s} {'行':>5} {'条目':>5}  说明")
    for stem, rows, ents, note in per_table:
        print(f"{stem:44s} {rows:>5} {ents:>5}  {note}")
    print(f"名字覆盖 {named}/{len(items)}（{named/len(items)*100:.1f}%）")
    print(f"点数覆盖 {with_point}/{len(items)}（{with_point/len(items)*100:.1f}%）")
    print("类别分布：" + " / ".join(f"{k} {v}" for k, v in kinds.most_common()))
    if miss:
        print(f"旧板缺失 id（前 20）：{miss[:20]}")

    if dry:
        print("--dry：未写盘")
        return 0

    text, js = write_board_pair(BOARD, board)
    print(f"已写 {BOARD.relative_to(PROJ)}（{len(text.encode('utf-8'))/1048576:.2f} MB）"
          f" + 同名 .js（{len(js.encode('utf-8'))/1048576:.2f} MB）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只统计，不写盘")
    a = ap.parse_args()
    return build(dry=a.dry)


if __name__ == "__main__":
    raise SystemExit(main())
