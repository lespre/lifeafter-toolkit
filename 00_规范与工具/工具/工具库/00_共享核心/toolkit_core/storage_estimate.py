# -*- coding: utf-8 -*-
"""拆包前空间预估：明确分开源包、解码产物、索引和临时空间。"""
from __future__ import annotations

import os
import time
from pathlib import Path

_CONTAINER_EXTS = {".gpk", ".fpk", ".npk", ".wpk", ".idx", ".thh", ".thx"}


def human_bytes(value: int | float) -> str:
    n = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.1f} TB"


def estimate_storage(*, source_bytes: int, decoded_bytes: int | None = None,
                     index_bytes: int | None = None, temp_bytes: int | None = None,
                     free_bytes: int | None = None, mode: str = "full",
                     safety_ratio: float = 0.15) -> dict:
    """估算执行期间需要的空间；不把估算包装成精确值。"""
    source_bytes = max(0, int(source_bytes))
    if decoded_bytes is None:
        # 没有条目级 decoded 大小时，给保守区间中位值，并标记来源。
        decoded_bytes = int(source_bytes * (1.35 if mode == "full" else 1.0))
        decoded_basis = "按源包体积保守估算（缺少条目级 decoded 大小）"
    else:
        decoded_bytes = max(0, int(decoded_bytes))
        decoded_basis = "按条目 decoded 大小汇总"
    index_bytes = max(128 * 1024**2, int(index_bytes or max(256 * 1024**2, source_bytes * 0.02)))
    temp_bytes = max(64 * 1024**2, int(temp_bytes or decoded_bytes * 0.10))
    base = source_bytes + decoded_bytes + index_bytes + temp_bytes
    safety = int(base * max(0.0, safety_ratio))
    required = base + safety
    enough = free_bytes is None or int(free_bytes) >= required
    return {
        "mode": mode, "source_bytes": source_bytes,
        "decoded_bytes": decoded_bytes, "index_bytes": index_bytes,
        "temp_bytes": temp_bytes, "safety_bytes": safety,
        "required_bytes": required, "free_bytes": free_bytes,
        "enough": enough, "verdict": "空间足够" if enough else "空间不足",
        "decoded_basis": decoded_basis,
        "human": {k: human_bytes(v) for k, v in {
            "source": source_bytes, "decoded": decoded_bytes, "index": index_bytes,
            "temp": temp_bytes, "safety": safety, "required": required,
            "free": free_bytes or 0}.items()},
    }


def scan_source(root: Path | str, *, mode: str = "full",
                max_files: int = 250_000, timeout: float = 30.0) -> dict:
    """有访问上限地统计容器文件；不读取大文件内容。"""
    root = Path(root).resolve()
    total = 0
    count = 0
    dirs_seen = 0
    started = time.monotonic()
    complete = True
    by_ext: dict[str, int] = {}
    if root.is_dir():
        for base, dirs, files in os.walk(root):
            dirs_seen += 1
            if dirs_seen > max_files or time.monotonic() - started > timeout:
                complete = False
                dirs[:] = []
                break
            for name in files:
                if count >= max_files or time.monotonic() - started > timeout:
                    complete = False
                    break
                p = Path(base) / name
                if p.suffix.lower() not in _CONTAINER_EXTS:
                    continue
                try:
                    size = p.stat().st_size
                except OSError:
                    continue
                total += size; count += 1
                by_ext[p.suffix.lower()] = by_ext.get(p.suffix.lower(), 0) + size
            if not complete:
                break
    try:
        free = __import__("shutil").disk_usage(root).free
    except OSError:
        free = None
    rep = estimate_storage(source_bytes=total, free_bytes=free, mode=mode)
    rep.update({"root": str(root), "container_count": count,
                "directories_seen": dirs_seen, "scan_complete": complete,
                "scan_limit": max_files, "scan_timeout": timeout,
                "source_by_extension": by_ext})
    return rep
