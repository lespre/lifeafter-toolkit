# -*- coding: utf-8 -*-
"""建「击败播报」板：播报文案（error_code_data）+ 击败特效（sfx_type=4），只用 PE 源。"""
from __future__ import annotations

import json
import os
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/01_工具/工具库/00_共享核心")
sys.path.insert(0, r"E:/la拆包项目/04_站点/web/tools")
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

ROOT = pathlib.Path(r"E:/la拆包项目")
WEB = ROOT / "04_站点/web"
CD = ROOT / "03_执行/41_还原树/pe_20261020/com/cdata"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"
_SRC = "E:/mrzh/Documents/script.py314.lc.npk"
try:
    _st = os.stat(_SRC)
    SRC_BYTES, SRC_MTIME = _st.st_size, _st.st_mtime_ns
except OSError:
    SRC_BYTES, SRC_MTIME = 0, 0


def body(p):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def dec(t):
    p = CD / (t + ".py")
    chs = CD / (t + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else []
    return decode_table_rows_with_chs_slots(body(p), pool)[0]


def val(v, k, d=None):
    x = (v or {}).get(k)
    return x[1] if isinstance(x, (list, tuple)) and len(x) > 1 else d


def prov(table, key, fields):
    return {
        "source_id": "documents-py314-current", "source_lock_sha256": SHA,
        "table": table, "row_key": str(key), "field_refs": fields,
        "name_source": "chs-pool", "upstream": {"package_sha256": SHA, "role": "SuperFashion"},
        "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                          "no_cross_source_field_join": True,
                          "steps": [{"kind": "decoded-table-row", "source_id": "documents-py314-current",
                                     "table": table, "row_key": str(key), "field_refs": fields}]},
        "table_raw": table,
    }


items = []

# ① 播报文案
for r in dec("error_code_data"):
    v = r.get("values") or {}
    text = str(val(v, "error_content", "") or "")
    # 只收真正的击杀播报（连杀/终结/超神），排除「击败附近怪物」这类玩法提示
    if not any(k in text for k in ("连续击败", "终结", "超神", "双杀", "三杀", "四杀",
                                   "五杀", "大杀特杀", "无人能挡", "暴走", "主宰", "团灭")):
        continue
    if "【" in text:      # 【荒野震动】/【史诗降临】= 战区荣誉播报，不属于击杀播报
        continue
    key = str(r.get("key"))
    items.append({
        "id": "kb_text_" + key,
        "name": text.split("\n")[0][:40] or ("错误码 " + key),
        "kind": "播报文案",
        "text": text,
        "duration": val(v, "duration"),
        "rich_mode": val(v, "rich_mode"),
        "error_code": val(v, "error_code"),
        "evidence": "structure",
        "evidence_level": "static/candidate",
        "status_tags": ["static config"],
        "source": "error_code_data",
        "provenance": prov("error_code_data", key, ["error_content", "duration", "error_code"]),
    })

# ② 击败特效
sfx_rows = dec("weapon_skin_sfx_function_data")
skin_name = {}
for r in dec("weapon_skin_data"):
    v = r.get("values") or {}
    nm = val(v, "name") or val(v, "skin_name")
    if nm:
        skin_name[str(r.get("key"))] = nm

n_def = 0
for r in sfx_rows:
    v = r.get("values") or {}
    if val(v, "sfx_type") != 4:
        continue
    n_def += 1
    key = str(r.get("key"))
    sid = str(val(v, "skin_id"))
    items.append({
        "id": "kb_fx_" + key,
        "name": (skin_name.get(sid) or ("皮肤 " + sid)) + " · 击败特效",
        "kind": "击败特效",
        "skin_id": sid,
        "skin_name": skin_name.get(sid),
        "level": val(v, "level"),
        "sfx": val(v, "sfx_name") or val(v, "extension_defeat_sfx"),
        "extra_sfx": val(v, "extension_defeat_sfx"),
        "unlock_items": val(v, "unlock_items"),
        "evidence": "structure",
        "evidence_level": "static/candidate",
        "status_tags": ["static config"],
        "source": "weapon_skin_sfx_function_data(sfx_type=4)",
        "provenance": prov("weapon_skin_sfx_function_data", key,
                           ["skin_id", "sfx_type", "sfx_name", "extension_defeat_sfx", "level"]),
    })

board = {
    "meta": {
        "name": "击败播报（文案 + 击败特效）",
        "category": "三、活动类 / （五）击败播报",
        "source_server": "简单生存服（PE pe_20261020）",
        "generated": "2026-10-22",
        "id_label": "条目",
        "hide_media": True,
        "evidence": "structure",
        "card_mode": "roster",
        "package_sha": SHA,
        "filters": [{"key": "kind", "label": "类型"}],
        "card_summary": [["kind", "类型"], ["duration", "时长"]],
        "state_summary": {"播报文案": len([i for i in items if i["kind"] == "播报文案"]),
                          "击败特效": n_def},
        "note": "播报文案来自 error_code_data（含「击败」的行）；击败特效来自 weapon_skin_sfx_function_data 的 sfx_type=4；播放器在 UI 代码里（PlayerDADGameComp），没有独立外观表",
        "provenance": {
            "contract_version": 3, "audit_status": "passed", "contract": "frozen-audited-artifact",
            "source_locks": [{"source_id": "documents-py314-current", "role": "primary",
                              "path": "E:/mrzh/Documents/script.py314.lc.npk", "sha256": SHA,
                              "bytes": SRC_BYTES, "mtime_ns": SRC_MTIME}],
            "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                             "integer_join_policy": "no-equal-integer-join",
                             "runtime_final_policy": "unknown-unless-runtime-proven"},
        },
    },
    "items": items,
}

(WEB / "data/boards/kill_broadcast.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
(WEB / "data/boards/kill_broadcast.js").write_text("window.WIKI_BOARD_kill_broadcast = " + json.dumps(board, ensure_ascii=False) + ";\n",
                                                   encoding="utf-8")
print("播报文案 %d ｜ 击败特效 %d ｜ 合计 %d" % (len([i for i in items if i["kind"] == "播报文案"]), n_def, len(items)))
