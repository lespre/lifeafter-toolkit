# -*- coding: utf-8 -*-
"""effect_show_data 专用解析入口（Weapon Skin Effect Source Binding 阶段）。

放在 pipelines/parsing 是硬要求：专用解析逻辑不得塞进 builder / UI / board exporter。

解析正解（见 skill weapon-skin-combat-performance/references/combat-effect-naming-chain-2026-09.md）：
  x{ body(count) → blob → tail = 76 01 0b + u8 bucket(59) + 59×8B hash 节点
  → 节点区后 uleb 流 = (行 key, 行 offset)×59（真实行表）；行内容=类目块
  ⚠️ parse_index 从节点读出的 1110xxx key 是误读假 key，禁止使用。

实现复用仓库既有 `tools/rebuild_weapon_skin_catalog_current.decode_effect_show_rows`
（不重复实现），本模块只负责：定位 BA8A entry payload → 调解析 → 返回行 + 定位信息。
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORKCOPY = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
ES_DATA_ENTRY = 3671
ES_CHS_ENTRY = 19852
SKIN_DATA_ENTRY = 11817


def _payload(entry: int) -> bytes | None:
    p = WORKCOPY / f"{entry:06d}.bin"
    if not p.exists():
        p = WORKCOPY / f"{entry}.bin"
    return p.read_bytes() if p.exists() else None


def parse(skin_payload: bytes | None = None, es_payload: bytes | None = None,
          es_chs_payload: bytes | None = None) -> dict:
    """返回 {rows, registry(skin_id→es 行 key), status, reason}。CHS 必须同快照配对（缺则解析失败）。"""
    out: dict = {"rows": [], "registry": {}, "status": "unavailable", "reason": None}
    es_base = es_payload if es_payload is not None else _payload(ES_DATA_ENTRY)
    es_chs = es_chs_payload if es_chs_payload is not None else _payload(ES_CHS_ENTRY)
    sk_base = skin_payload if skin_payload is not None else _payload(SKIN_DATA_ENTRY)
    if not es_base or not sk_base:
        out["reason"] = f"BA8A entry payload 不可读（{WORKCOPY}）"
        return out
    sys.path.insert(0, str(REPO / "tools"))
    mod = importlib.import_module("rebuild_weapon_skin_catalog_current")
    try:
        rows = mod.decode_effect_show_rows(es_base, es_chs or b"")
        out["rows"] = rows or []
        out["status"] = "parsed"
    except Exception as e:                                     # noqa: BLE001
        out["reason"] = f"decode_effect_show_rows 失败：{str(e)[:160]}"
        return out
    try:
        reg, _hash = mod.decode_es_registry(sk_base, es_base)
        out["registry"] = dict(reg or {})
    except Exception as e:                                     # noqa: BLE001
        out["reason"] = f"decode_es_registry 失败：{str(e)[:160]}"
    return out
