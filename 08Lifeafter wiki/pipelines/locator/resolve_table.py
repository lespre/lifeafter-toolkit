"""统一表定位 facade v1.1 —— data + CHS 配对的唯一入口。

CHS 配对规则（唯一规则，禁止各 builder 自找 CHS）：
  1. `data/table_index_entries.jsonl` 按 table_name 匹配（默认含 oversea/channel 变体）
  2. 以 family 聚合：`plain`/`base`/`inc`/`del` = 表体或差分件，`chs` = 文本池
  3. family 选择：优先含「精确端名表体」的 family → 非 oversea → chs 数多
  4. data_entry = 该 family 内 best body（精确端名 > 非 oversea > 体积大）
  5. chs_entry = 同 family 内 **stem 匹配** 的 `<body_stem>_chs` → 否则同 family 任一 `_chs` → 否则跨 family 找 `<stem>_chs`
  6. data_fid/chs_fid：entry → 当前包条目表反查（BA8A 工作副本无 FID ⇒ null）

失败返回结构化 status（STATUS），不抛异常、不静默降级。
"""
from __future__ import annotations

import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
INVENTORY = REPO / "data" / "table_index_entries.jsonl"
SOURCES = REPO / "registry" / "sources.json"
SNAPSHOTS = REPO / "registry" / "snapshots.json"

STATUS = {
    "ok": "data + chs 均已定位",
    "module_only": "只有模块 stub，无 table_body",
    "data_body_not_found": "inventory 无该表记录",
    "chs_not_found": "未找到配对 CHS 条目",
    "snapshot_mismatch": "该 snapshot 下不存在该 entry",
}


@lru_cache(maxsize=4)
def load_inventory_for(snapshot_id: str | None = None) -> tuple[dict[str, Any], ...]:
    """按 snapshot 取它自己基准的 inventory；无自带基准时用历史默认清单。"""
    from pipelines.locator.payload_resolver import INVENTORY_BY_BASIS, REPO
    rel = INVENTORY_BY_BASIS.get(snapshot_id or "")
    path = (REPO / rel) if rel and (REPO / rel).exists() else INVENTORY
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return tuple(rows)


@lru_cache(maxsize=1)
def load_inventory() -> tuple[dict[str, Any], ...]:
    out: list[dict[str, Any]] = []
    with INVENTORY.open(encoding="utf-8") as fh:
        for line in fh:
            out.append(json.loads(line))
    return tuple(out)


@lru_cache(maxsize=1)
def _table_sources() -> dict[str, dict[str, Any]]:
    doc = json.loads(SOURCES.read_text(encoding="utf-8"))
    return {r["logical_path"]: r for r in doc.get("table_sources", [])}


@lru_cache(maxsize=1)
def _snapshots() -> dict[str, dict[str, Any]]:
    return {s["snapshot_id"]: s for s in json.loads(SNAPSHOTS.read_text(encoding="utf-8"))["snapshots"]}


@lru_cache(maxsize=4)
def _entry_fid_map(package_hint: str | None) -> dict[int, str]:
    if not package_hint:
        return {}
    try:
        sys.path.insert(0, str(REPO / "tools"))
        sys.path.insert(0, r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
        from live_npk_reader import LiveNpkReader

        reader = LiveNpkReader(Path(package_hint), "workbench-locator")
        return {e.entry_index: f"{e.file_id:016X}" for e in reader._entries}  # noqa: SLF001
    except Exception:  # noqa: BLE001
        return {}


def _stem(name: str) -> str:
    return Path(str(name)).stem


def _score(row: dict[str, Any], table_name: str) -> tuple[int, int, int]:
    """越小越优先：精确端名 → 非 oversea → 体积大。"""
    tn = str(row.get("table_name") or "")
    exact = 0 if tn.endswith(table_name) or _stem(tn) == Path(table_name).stem else 1
    oversea = 1 if "oversea" in tn else 0
    size = int(row.get("size") or 0)
    return (exact, oversea, -size)


def resolve_table(snapshot_id: str, table_name: str, *, variant: str | None = None,
                  include_oversea: bool = True) -> dict[str, Any]:
    key = re.sub(r"[\\/]+", "\\\\", table_name)
    want_stem = _stem(key)
    # 匹配规则：stem == want 或 stem 以 want 开头（覆盖 _auto_oversea_data_kj1 等变体）
    def _hit(r: dict[str, Any]) -> bool:
        tn = str(r.get("table_name") or "")
        if not include_oversea and "oversea" in tn:
            return False
        s = _stem(tn)
        return s == want_stem or s.startswith(want_stem + "_")

    rows = [r for r in load_inventory_for(snapshot_id) if _hit(r)]
    result: dict[str, Any] = {
        "snapshot_id": snapshot_id, "table_name": table_name, "module_entry": None, "data_entry": None, "chs_entry": None,
        "data_fid": None, "chs_fid": None, "family": None, "schema": None, "provenance": {},
        "status": "data_body_not_found", "reason": STATUS["data_body_not_found"], "variant": variant,
        "data_candidates": [], "chs_candidates": [], "chs_pairing": None,
    }
    if not rows:
        return result
    if variant:
        filt = [r for r in rows if variant in str(r.get("table_name") or "")]
        if filt:
            rows = filt

    fams: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        fams.setdefault(str(r.get("family") or ""), []).append(r)

    def fam_rank(item: tuple[str, list[dict[str, Any]]]) -> tuple[int, int, int]:
        fam, group = item
        bodies = [r for r in group if r.get("table_body")]
        exact = 0 if any(_stem(r.get("table_name")) == want_stem for r in bodies) else 1
        oversea = 1 if "oversea" in fam else 0
        chs_n = sum(1 for r in group if r.get("role") == "chs")
        return (exact, oversea, -chs_n)

    fam, group = min(fams.items(), key=fam_rank)
    bodies = sorted((r for r in group if r.get("table_body")), key=lambda r: _score(r, key))
    chs_rows = sorted((r for r in group if r.get("role") == "chs"), key=lambda r: _score(r, key))
    body = bodies[0] if bodies else None
    if body is None:  # 该 family 无表体 ⇒ 换一个含表体的 family
        for alt, alt_group in sorted(fams.items(), key=fam_rank):
            alt_bodies = sorted((r for r in alt_group if r.get("table_body")), key=lambda r: _score(r, key))
            if alt_bodies:
                fam, group, bodies, body = alt, alt_group, alt_bodies, alt_bodies[0]
                chs_rows = sorted((r for r in alt_group if r.get("role") == "chs"), key=lambda r: _score(r, key))
                break

    chs = None
    if body is not None:
        stem = _stem(body.get("table_name"))
        same_stem = [r for r in chs_rows if _stem(r.get("table_name")) == f"{stem}_chs"]
        if same_stem:
            chs, pairing = same_stem[0], "stem-match"
        elif chs_rows:
            chs, pairing = chs_rows[0], "family-fallback"
        else:
            cross = [r for r in load_inventory() if _stem(r.get("table_name")) == f"{stem}_chs"]
            chs, pairing = (cross[0], "cross-family-stem-match") if cross else (None, None)
    else:
        pairing = None

    result.update({
        "family": fam,
        "data_entry": body.get("entry") if body else None,
        "chs_entry": chs.get("entry") if chs else None,
        "chs_pairing": pairing,
        "data_candidates": [r.get("entry") for r in bodies[:8]],
        "chs_candidates": [r.get("entry") for r in chs_rows[:8]],
    })
    module = next((r for r in group if r.get("role") in ("plain", "base") and not r.get("table_body")), None)
    result["module_entry"] = module.get("entry") if module else None

    snap = _snapshots().get(snapshot_id)
    pkg_hint = None
    if snap and "Documents" in str(snap.get("package") or ""):
        pkg_hint = r"E:\mrzh\Documents\script.py314.lc.npk"
    elif snap and snap.get("client_channel") == "live":
        pkg_hint = snap.get("package")
    fids = _entry_fid_map(pkg_hint)
    if body:
        result["data_fid"] = fids.get(body.get("entry"))
    if chs:
        result["chs_fid"] = fids.get(chs.get("entry"))
    known = _table_sources().get(key)
    if known:
        result["provenance"]["canonical_source"] = "registry/sources.json#table_sources"
        if not result["data_fid"]:
            result["data_fid"] = known.get("FID")
    result["provenance"].update({"inventory_family": fam, "inventory_records": len(group), "package": rows[0].get("package"),
                                 "roles": sorted({str(r.get("role")) for r in group}),
                                 "pairing_rule": "same-family stem-match <stem>_chs"})
    result["schema"] = None
    if body is None:
        result.update(status="module_only", reason=STATUS["module_only"])
    elif chs is None:
        result.update(status="chs_not_found", reason=STATUS["chs_not_found"])
    else:
        result.update(status="ok", reason=None)
    # v1.2：snapshot-native payload 状态覆盖（只降级不升级；禁止跨 snapshot 复用 entry）
    from pipelines.locator.payload_resolver import resolve_payload

    data_ref = resolve_payload(snapshot_id, table_name, entry_hint=body.get("entry") if body else None, entry_basis_hint=snapshot_id, role="data")
    chs_ref = resolve_payload(snapshot_id, (chs.get("table_name") if chs else table_name + "_chs"),
                              entry_hint=chs.get("entry") if chs else None, entry_basis_hint=snapshot_id, role="chs")
    result["data_payload_ref"] = data_ref.as_dict()
    result["chs_payload_ref"] = chs_ref.as_dict()
    result["entry_basis"] = data_ref.entry_basis
    if data_ref.status != "ok":
        result["status"] = data_ref.status
        result["reason"] = f"payload resolution: {data_ref.status}"
    elif chs_ref.status != "ok":
        result["chs_status"] = chs_ref.status
        result["reason"] = (result.get("reason") or "") + f" | chs payload: {chs_ref.status}"
    return result


if __name__ == "__main__":
    import sys as _sys

    name = _sys.argv[1] if len(_sys.argv) > 1 else "com\\cdata\\common_item_data_base.py"
    snap_id = _sys.argv[2] if len(_sys.argv) > 2 else "test-documents-328b8446"
    print(json.dumps(resolve_table(snap_id, name), ensure_ascii=False, indent=1))
