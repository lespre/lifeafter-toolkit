"""artifact / registry 统一读取层（含访问边界守卫）。

**Workbench 数据边界的唯一执行点**：任何越界读取直接抛错，不静默降级。
"""
from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "registry"
ACTIVE = REPO / "artifacts" / "active"
RESIDUALS = REPO / "residuals"
EVIDENCE = REPO / "evidence"
STATE = REPO / "state"          # canonical 状态（PROJECT_STATE.md / REGRESSION.json）；v1.3 起可读

ALLOWED_ROOTS = (REGISTRY, ACTIVE, RESIDUALS, EVIDENCE, STATE)
FORBIDDEN_MARKERS = ("data/boards", "data\\boards", "historical", "06（agent写）", ".db", "script.py314", "script.py3")


class AccessBoundaryError(RuntimeError):
    """越界读取：Workbench service 不得读 legacy 数据。"""


def assert_allowed(path: Path) -> Path:
    p = Path(path).resolve()
    if not any(str(p).startswith(str(root)) for root in ALLOWED_ROOTS):
        raise AccessBoundaryError(f"path outside workbench roots: {p}")
    text = str(p).replace("\\", "/")
    for marker in FORBIDDEN_MARKERS:
        if marker.replace("\\", "/") in text:
            raise AccessBoundaryError(f"forbidden legacy source: {p}")
    return p


def load_json(path: Path) -> Any:
    return json.loads(assert_allowed(path).read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with assert_allowed(path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with assert_allowed(path).open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def registry(name: str) -> Any:
    return load_json(REGISTRY / name)


@functools.lru_cache(maxsize=32)
def cached_jsonl(path_str: str) -> tuple[dict[str, Any], ...]:
    return tuple(load_jsonl(Path(path_str)))


def active_path(domain: str, name: str) -> Path:
    return ACTIVE / domain / name
