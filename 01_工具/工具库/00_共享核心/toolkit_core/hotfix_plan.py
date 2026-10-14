# -*- coding: utf-8 -*-
"""热更只拆计划：把 overlay、fid diff 和空间预估汇成可复核计划。"""
from __future__ import annotations

from pathlib import Path


def build_hotfix_plan(*, client_root: str | Path, version: dict,
                      overlay_packages: list[dict], pkg_diff: dict | None = None,
                      storage: dict | None = None) -> dict:
    pkg_diff = pkg_diff or {}
    overlay_bytes = sum(int(x.get("size") or 0) for x in overlay_packages)
    return {
        "scope": "hotfix", "client_root": str(client_root),
        "version": version,
        "overlay": {"package_count": len(overlay_packages),
                     "bytes": overlay_bytes, "packages": overlay_packages},
        "fid_diff": {"added": len(pkg_diff.get("added", [])),
                     "removed": len(pkg_diff.get("removed", [])),
                     "changed": len(pkg_diff.get("changed", []))},
        "requires_full_tree": False,
        "storage": storage,
        "notes": [
            "pkg_N.pi 只能发现新增/移除 fid；同路径内容变更必须结合 overlay 或本地快照。",
            "没有全量还原树时，新增资源可以保存为容器+行号/fid 证据，不伪造逻辑路径。",
        ],
    }
