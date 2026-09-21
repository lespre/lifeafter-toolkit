"""统一 decoder facade v1.1 —— 外部业务代码解析的唯一入口。

对外只需要两个函数：
    decode_table(resolved)                  # resolved = pipelines.locator.resolve_table(...)
    resolve_and_decode(snapshot_id, table_name, variant=None)

外部禁止再自行 `_xbody` / `parse_index` / 找 CHS / 猜 frame（有测试守护）。
内部仍复用既有实现：toolkit_core.bindict_table、parse_legacy_chs_pool、decode_table_rows_with_chs_slots。
"""
from __future__ import annotations

import json
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
TOOLKIT = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
WORKCOPY = Path(r"E:/la拆包项目/03拆包产物/config_work/script_py314_docs_BA8A239A/entries")
for _path in (str(TOOLKIT), str(REPO / "tools"), str(REPO)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

XFRAME_MARKER = b"x{"

FAILURE_KINDS = ("ok", "module_only", "data_body_not_found", "chs_not_found", "unsupported_frame",
                 "unsupported_index_tail", "schema_decode_failed", "malformed_payload", "snapshot_mismatch",
                 "payload_not_available")


@dataclass
class DecodeResult:
    status: str
    reason: str | None = None
    rows: list[dict[str, Any]] = field(default_factory=list)
    keys: list[int] = field(default_factory=list)
    schemas: dict[str, int] = field(default_factory=dict)
    row_count: int = 0
    unique_keys: int = 0
    chs_strings: int = 0
    provenance: dict[str, Any] = field(default_factory=dict)
    engine: dict[str, Any] = field(default_factory=lambda: {"impl": "toolkit_core.bindict_table",
                                                            "facade": "pipelines/parsing/decoder.py v1.1"})

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "reason": self.reason, "row_count": self.row_count, "unique_keys": self.unique_keys,
                "schemas": self.schemas, "chs_strings": self.chs_strings, "provenance": self.provenance, "engine": self.engine}


def unwrap_xbody(payload: bytes) -> bytes:
    at = payload.find(XFRAME_MARKER)
    if at < 0:
        raise ValueError("no x{ frame")
    length = struct.unpack_from("<I", payload, at + 2)[0]
    end = at + 6 + length
    if end > len(payload):
        raise ValueError("x{ frame exceeds payload")
    return payload[at + 6:end]


def parse_keys(blob: bytes) -> list[int]:
    from toolkit_core.bindict_table import parse_index

    try:
        return [int(r["key"]) for r in parse_index(blob) if isinstance(r.get("key"), int)]
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"index: {exc}") from exc


def _read_payload(snapshot_id: str, entry: int) -> tuple[bytes | None, str | None]:
    """注意：entry 序号属于 **inventory 的索引空间**（当前实测与 BA8A 工作副本一致，
    与当前热更包不一致 ⇒ 读当前包存在跨索引空间风险，v1.2 需改按 FID 定位）。"""
    """取条目 payload：本地快照目录 → 当前包（entry 直读）。"""
    if entry is None:
        return None, "data_body_not_found"
    src_dir = WORKCOPY if snapshot_id == "test-documents-ba8a239a" else None
    if src_dir:
        # 工作副本按 entry 复制；BA8A 内 entry 序号与当前包不同，按 manifest 反查不可得 ⇒ 直接按序号读
        for cand in (src_dir / f"{entry:06d}.bin",):
            if cand.exists():
                return cand.read_bytes(), None
        return None, "payload_not_available"
    try:
        # v1.2 修复（2026-09-13）：直读包条目表（entry 序号属该 snapshot 自己的 package-native 基准）。
        # 旧实现依赖 LiveNpkReader 私有 _entries 且字段映射不符 ⇒ 恒 payload_not_available / 内容损坏。
        import struct as _struct

        # 工具库核心解包器不在默认 sys.path（与其余 tools/ 调用一致，先注册）
        _tk = Path(r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")
        if str(_tk) not in sys.path:
            sys.path.insert(0, str(_tk))
        from npk_reader import aes_ecb as _aes, unpack_entry as _unpack  # noqa: E402

        pkg = Path(r"E:\mrzh\Documents\script.py314.lc.npk")
        with open(pkg, "rb") as fh:
            head = _aes(fh.read(64))
            table_off = _struct.unpack_from("<I", head, 16)[0]
            fh.seek(table_off + entry * 48)
            row = _aes(fh.read(48))
            if len(row) != 48:
                return None, "payload_not_available"
            offset = _struct.unpack_from("<I", row, 8)[0]
            packed_size = _struct.unpack_from("<I", row, 12)[0]
            declared_size = _struct.unpack_from("<I", row, 16)[0]
            flag = _struct.unpack_from("<i", row, 28)[0]
            if offset <= 0 or packed_size <= 0:
                return None, "payload_not_available"
            fh.seek(offset)
            packed = fh.read(packed_size)
        return _unpack(packed, declared_size, flag), None
    except Exception:  # noqa: BLE001
        return None, "payload_not_available"

def _classify(exc: Exception) -> str:
    text = str(exc)
    if "not a supported 0x76 index tail" in text:
        return "unsupported_index_tail"
    if "truncated" in text or "shorter than header" in text:
        return "malformed_payload"
    if "frame" in text:
        return "unsupported_frame"
    return "schema_decode_failed"


def decode_table(resolved: dict[str, Any]) -> DecodeResult:
    snapshot_id = resolved.get("snapshot_id")
    ref = resolved.get("data_payload_ref") or {}
    if ref.get("snapshot_id") and ref.get("snapshot_id") != snapshot_id:
        # v1.2 不变量：跨 snapshot payload 一律 hard fail，不做“先试试看”
        return DecodeResult(status="snapshot_mismatch",
                            reason=f"payload_ref.snapshot={ref.get('snapshot_id')} != requested={snapshot_id}",
                            provenance={"payload_ref": ref})
    if ref.get("entry_index") is not None:
        resolved = {**resolved, "data_entry": ref["entry_index"]}
    data_entry = resolved.get("data_entry")
    chs_entry = resolved.get("chs_entry")
    prov = {"snapshot_id": snapshot_id, "data_entry": data_entry, "chs_entry": chs_entry,
            "data_fid": resolved.get("data_fid"), "chs_fid": resolved.get("chs_fid"),
            "family": resolved.get("family"), "locator_status": resolved.get("status")}
    if not data_entry:
        return DecodeResult(status=resolved.get("status") or "data_body_not_found", reason=resolved.get("reason"), provenance=prov)
    payload, err = _read_payload(snapshot_id, data_entry)
    if payload is None:
        return DecodeResult(status=err or "payload_not_available",
                            reason=f"data entry {data_entry} 的 payload 不可取（快照不匹配或未复制）", provenance=prov)
    frame_state = "x{ container"
    try:
        blob = unwrap_xbody(payload)
    except ValueError as exc:
        # fallback：部分表的 payload 本身就是裸表体（无 x{ 容器）⇒ 直接尝试解码
        blob = payload
        frame_state = f"raw-body fallback（{exc}）"
    chs_payload = None
    if chs_entry:
        chs_payload, _ = _read_payload(snapshot_id, chs_entry)
    from toolkit_core.bindict_table import parse_legacy_chs_pool

    pool: dict[Any, Any] = {}
    if chs_payload:
        try:
            pool = parse_legacy_chs_pool(chs_payload)
        except Exception:  # noqa: BLE001
            pool = {}
    from bindict_provenance import decode_table_rows_with_chs_slots

    try:
        rows, unbound = decode_table_rows_with_chs_slots(blob, pool)
    except Exception as exc:  # noqa: BLE001
        return DecodeResult(status=_classify(exc), reason=str(exc)[:200], chs_strings=len(pool), provenance=prov)
    keys = [r["key"] for r in rows if isinstance(r.get("key"), int)]
    schemas: dict[str, int] = {}
    for r in rows:
        sch = r.get("schema")
        if sch is not None:
            schemas[str(sch)] = schemas.get(str(sch), 0) + 1
    status = "ok" if rows else "schema_decode_failed"
    reason = None if rows else ("CHS 池为空且无内联文本" if not pool else "解码 0 行；frame=" + frame_state)
    prov["frame_state"] = frame_state
    return DecodeResult(status=status, reason=reason, rows=rows, keys=keys, schemas=schemas, row_count=len(rows),
                        unique_keys=len(set(keys)), chs_strings=len(pool), provenance=prov)


def decode_family(resolved: dict[str, Any]) -> dict[str, Any]:
    """对 family 内全部 data 候选 × 配对 CHS 解码，返回 union key set（v1.1 批量用）。"""
    import copy

    snapshot_id = resolved.get("snapshot_id")
    chs_by_stem: dict[str, list[int]] = {}
    out_candidates = []
    keys_union: set[int] = set()
    best: DecodeResult | None = None
    ref = resolved.get("data_payload_ref") or {}
    native = ref.get("entry_index")
    candidates: list[int] = []
    if native is not None:
        candidates.append(native)                     # snapshot-native 优先，且不与旧基准混合
    # 只有在“候选与本 snapshot 同基准”时才把 inventory 候选纳入
    if ref.get("entry_basis", "").endswith("inventory-basis"):
        candidates += [e for e in (resolved.get("data_candidates") or []) if e not in candidates]
    if not candidates and resolved.get("data_entry") is not None:
        candidates.append(resolved["data_entry"])
    for entry in candidates:
        single = copy.deepcopy(resolved)
        single["data_entry"] = entry
        # 每个 body 单独 stem 配对 CHS（若 locator 给的单体 CHS 不匹配则回退）
        res = decode_table(single)
        out_candidates.append({"data_entry": entry, "chs_entry": single.get("chs_entry"), "status": res.status,
                               "rows": res.row_count, "keys": res.unique_keys, "reason": res.reason})
        if res.status == "ok":
            keys_union.update(res.keys)
            if best is None or res.row_count > best.row_count:
                best = res
    # 聚合口径：ok > 具体失败（按信息量排序）> payload_not_available
    priority = ["ok", "schema_decode_failed", "unsupported_index_tail", "unsupported_frame", "malformed_payload",
                "chs_not_found", "module_only", "snapshot_mismatch", "data_body_not_found", "payload_not_available"]
    statuses = [c["status"] for c in out_candidates]
    if keys_union:
        status = "ok"
    elif not out_candidates:
        status = "data_body_not_found"
    else:
        status = next((s for s in priority if s in statuses), sorted(statuses)[0])
    return {
        "snapshot_id": snapshot_id, "family": resolved.get("family"), "status": status,
        "candidates": out_candidates, "union_keys": sorted(keys_union), "union_key_count": len(keys_union),
        "chs_entry": resolved.get("chs_entry"), "chs_pairing": resolved.get("chs_pairing"),
        "best": best.as_dict() if best else None,
        "provenance": {"data_candidates": resolved.get("data_candidates"), "chs_candidates": resolved.get("chs_candidates"),
                       "data_fid": resolved.get("data_fid"), "chs_fid": resolved.get("chs_fid")},
    }


def resolve_and_decode(snapshot_id: str, table_name: str, *, variant: str | None = None,
                       include_oversea: bool = True) -> DecodeResult:
    from pipelines.locator.resolve_table import resolve_table

    return decode_table(resolve_table(snapshot_id, table_name, variant=variant, include_oversea=include_oversea))


def resolve_and_decode_family(snapshot_id: str, table_name: str, *, variant: str | None = None,
                              include_oversea: bool = True) -> dict[str, Any]:
    from pipelines.locator.resolve_table import resolve_table

    return decode_family(resolve_table(snapshot_id, table_name, variant=variant, include_oversea=include_oversea))


if __name__ == "__main__":
    snap = sys.argv[2] if len(sys.argv) > 2 else "test-documents-328b8446"
    res = resolve_and_decode(snap, sys.argv[1] if len(sys.argv) > 1 else "com\\cdata\\common_item_data_base.py")
    print(json.dumps(res.as_dict(), ensure_ascii=False, indent=1))
