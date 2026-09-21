"""覆盖度 / 绑定状态汇总服务（Workbench v1.3，状态页数据源）。

数据全部来自 registry / artifacts/active / residuals / state —— **不手写数字**。
不把 snapshot 混成一个覆盖率：BA8A（inventory 基准）与 current（热更包）分别统计。
"""
from __future__ import annotations

import datetime
import functools
import hashlib
import json
from typing import Any

from .bindings import (active_current_snapshot, binding_status, inventory_basis_snapshot,
                       snapshot_bindings, snapshots)
from .store import ACTIVE, REGISTRY, RESIDUALS, STATE, load_json


@functools.lru_cache(maxsize=16)
def _sha256(path_str: str) -> str:
    h = hashlib.sha256()
    with open(path_str, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@functools.lru_cache(maxsize=16)
def _line_count(path_str: str) -> int:
    n = 0
    with open(path_str, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                n += 1
    return n


class CoverageService:
    def coverage(self) -> dict[str, Any]:
        binds = snapshot_bindings()
        per_snapshot: dict[str, dict[str, Any]] = {}
        per_table: list[dict[str, Any]] = []
        status_tally: dict[str, int] = {}
        ok = not_ok = 0
        for logical, block in sorted(binds.items()):
            row = {"logical_table": logical, "bindings": {}}
            for sid in (block.get("bindings") or {}):
                st = binding_status(logical, sid)
                status = st["status"]
                row["bindings"][sid] = {"status": status, "data_status": st["data_status"],
                                        "chs_status": st["chs_status"],
                                        "data_entry": st["data_entry"],
                                        "declared_size": st["declared_size"],
                                        "file_id": st["file_id"]}
                bucket = per_snapshot.setdefault(sid, {"tables": 0, "ok": 0, "not_ok": 0, "statuses": {}})
                bucket["tables"] += 1
                bucket["statuses"][str(status)] = bucket["statuses"].get(str(status), 0) + 1
                if status == "ok":
                    bucket["ok"] += 1
                    ok += 1
                else:
                    bucket["not_ok"] += 1
                    not_ok += 1
                status_tally[str(st)] = status_tally.get(str(st), 0) + 1
            per_table.append(row)

        unresolved: dict[str, dict[str, Any]] = {}
        if RESIDUALS.exists():
            for d in sorted(p for p in RESIDUALS.iterdir() if p.is_dir()):
                files = {}
                for p in sorted(d.glob("*.json")):
                    try:
                        doc = json.loads(p.read_text(encoding="utf-8"))
                    except (OSError, ValueError):
                        continue
                    if isinstance(doc, dict) and doc.get("count") is not None:
                        files[p.stem] = {"count": doc.get("count"),
                                         "buckets": doc.get("bucket_counts") or doc.get("buckets")}
                if files:
                    unresolved[d.name] = files

        artifacts: list[dict[str, Any]] = []
        if ACTIVE.exists():
            for d in sorted(p for p in ACTIVE.iterdir() if p.is_dir()):
                for f in sorted(d.iterdir()):
                    if f.suffix not in (".jsonl", ".json") or f.name.endswith("MANIFEST.json"):
                        continue
                    entry = {"domain": d.name, "artifact": f"artifacts/active/{d.name}/{f.name}",
                             "bytes": f.stat().st_size, "sha256": _sha256(str(f)),
                             "mtime": datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%dT%H:%M:%S")}
                    if f.suffix == ".jsonl":
                        entry["rows"] = _line_count(str(f))
                    artifacts.append(entry)

        regression = load_json(STATE / "REGRESSION.json") if (STATE / "REGRESSION.json").exists() else None
        web = load_json(REGISTRY / "web_client.json") if (REGISTRY / "web_client.json").exists() else None
        return {
            "generated": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "workbench_version": "v1.3",
            "snapshots": [{k: s.get(k) for k in ("snapshot_id", "client_channel", "package_scope", "sha256",
                                                 "bytes", "status", "server_branch", "source_role", "label")}
                          for s in snapshots()],
            "inventory_basis_snapshot": inventory_basis_snapshot(),
            "active_current_snapshot": active_current_snapshot(),
            "snapshot_table_coverage": per_snapshot,
            "tables": per_table,
            "physical_binding_coverage": {"total": ok + not_ok, "ok": ok, "not_ok": not_ok,
                                          "statuses": status_tally},
            "unresolved_counts": unresolved,
            "active_artifacts": artifacts,
            "regression": regression,
            "web_client": web,
            "notes": {
                "snapshot_rule": "entry 只在自己 snapshot 有效；BA8A 与 current 为同一逻辑表的不同物理实例",
                "wording": "snapshot entry-space mismatch 是当前继续解析/复现的主要基础设施阻断；"
                           "修复后重新分类，不预设 residual 会全部消失",
            },
        }
