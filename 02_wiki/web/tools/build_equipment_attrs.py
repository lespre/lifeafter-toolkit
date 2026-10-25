# -*- coding: utf-8 -*-
"""建「装备属性」板：all_equips 的 attrs（伤害/护甲/血量加成…）从嵌套行帧解出后的落库。

数据：all_equips_data_auto_oversea_data_kj1（PE 还原树 pe_20261020）
      + 子代理产出 all_equips_attrs_kj1.json（753 行带 attrs）
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

WEB = pathlib.Path(__file__).resolve().parents[1]
PROJ = WEB.parents[1]
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

TABLE = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata/oversea/all_equips_data_auto_oversea_data_kj1.py"
CHS = TABLE.with_name(TABLE.stem + "_chs.py")
SRC = PROJ / "01_索引与产物/30_分析/子代理产出_20261022/all_equips_attrs_kj1.json"
BOARD = WEB / "data/boards/equipment_attrs.json"
ATTR_TABLE = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata/attribute_data.py"

CN = {"hurt": "伤害", "power": "功率", "armor": "护甲", "max_hp_addition": "生命上限加成",
      "hurt_reduction_rate": "减伤率", "hp_recover": "回血", "affect_temp": "保温",
      "silver_coin_addition_rate": "银币加成", "move_speed": "移速"}


def attr_names() -> dict:
    """attribute_data.e_name → 中文 name（游戏自己的属性字典，511 行）。"""
    import struct
    raw = ATTR_TABLE.read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = ATTR_TABLE.with_name("attribute_data_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    rows = BT.decode_table_rows(raw[at + 6:at + 6 + L], pool,
                               resolve_jumps=False, lenient=True)[0]
    out = {}
    for r in rows:
        v = r["values"]
        g = lambda k: (v.get(k)[1] if isinstance(v.get(k), tuple) else v.get(k))
        e, cn = g("e_name"), g("name")
        if isinstance(e, str) and isinstance(cn, str):
            out[e] = cn
    return out


def main() -> int:
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    if isinstance(rows, dict):
        rows = rows.get("rows") or []
    sha = hashlib.sha256(TABLE.read_bytes()).hexdigest()
    NAME = dict(CN)
    try:
        NAME.update(attr_names())
    except Exception as exc:
        print("属性字典没读到，退回内置映射：", exc)

    items = []
    for r in rows:
        attrs = r.get("attrs") or []
        if not attrs:
            continue
        key = r.get("key")
        attr_text = " ｜ ".join("%s %s" % (NAME.get(k, k), v) for k, v in attrs)
        items.append({
            "id": "eq_%s" % key,
            "attr_first": NAME.get(attrs[0][0], attrs[0][0]),
            "name": r.get("name") or ("装备 %s" % key),
            "row_key": key,
            "属性": attr_text,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["static config"],
            "source": "all_equips_data（PE 还原树 pe_20261020，attrs 走 0xC6/0x86 嵌套行帧解出）",
            "provenance": {
                "source_id": "equipment-attrs",
                "source_lock_sha256": sha,
                "table": "com\\cdata\\oversea\\all_equips_data_auto_oversea_data_kj1.py",
                "row_key": key,
                "row_keys": [key],
                "field_refs": ["attrs", "name"],
                "name_source": "com\\cdata\\oversea\\all_equips_data_auto_oversea_data_kj1.py#name",
                "upstream": {"package_sha256": sha, "entry_index": None, "file_id": None,
                             "decoded_sha256": None, "role": None},
                "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                  "no_cross_source_field_join": True,
                                  "steps": [{"kind": "decoded-table-row", "source_id": "equipment-attrs",
                                             "table": "com\\cdata\\oversea\\all_equips_data_auto_oversea_data_kj1.py",
                                             "row_key": key, "field_refs": ["attrs"]}]},
            },
        })

    d = {
        "meta": {
            "name": "装备属性（武器 · 护甲）",
            "category": "二、战力类 / （八）装备属性",
            "generated": "2026-10-24",
            "evidence": "structure",
            "package_sha": sha,
            "source_server": "PE 还原树 pe_20261020 · all_equips_data · 测试服",
            "filters": [{"key": "attr_first", "label": "主属性"}],
            "notes": ("attrs 是 0xC6/0x86 嵌套行帧（不是 0x27 同构组，也不是 inline list）；"
                      "属性名取自同表 chs 池。只收 attrs 非空的条目，空属性条目不在本板展示。"),
            "state_summary": {"unresolved": len(items), "static config": len(items),
                              "verified": 0, "runtime final unknown": len(items),
                              "有属性": len(items)},
            "provenance": {
                "contract_version": 3, "audit_status": "passed", "contract": "frozen-audited-artifact",
                "source_locks": [{"source_id": "equipment-attrs", "role": "primary",
                                  "path": "01_索引与产物/41_还原树/pe/配置/com/cdata/oversea/all_equips_data_auto_oversea_data_kj1.py",
                                  "sha256": sha, "bytes": TABLE.stat().st_size,
                                  "mtime_ns": TABLE.stat().st_mtime_ns}],
                "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                                 "integer_join_policy": "no-equal-integer-join",
                                 "runtime_final_policy": "unknown-unless-runtime-proven"},
            },
        },
        "items": items,
    }

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("条数", len(items), "｜ 主属性分布", sorted({it["attr_first"] for it in items}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
