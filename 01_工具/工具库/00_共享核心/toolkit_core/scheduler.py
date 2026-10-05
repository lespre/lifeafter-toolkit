# -*- coding: utf-8 -*-
"""按 I/O 与 CPU 类型分流的保守调度计划器。"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable


class JobKind(str, Enum):
    LARGE_ARCHIVE_READ = "large_archive_read"  # FPK/GPK 全量读取：同盘必须串行
    SMALL_SCAN = "small_scan"                  # 小文件/索引枚举：线程池
    CPU_CONVERT = "cpu_convert"                # DDS/PNG/ASTC：进程池


@dataclass(frozen=True)
class SchedulePlan:
    max_cpu_workers: int
    large_archive_workers: int
    scan_workers: int
    convert_workers: int
    queue_size: int
    cancel_supported: bool = True


class SmartScheduler:
    """只生成计划；实际执行器必须把取消事件和进度队列传入 worker。"""

    def __init__(self, *, cpu_count: int | None = None, cpu_percent: float | None = None,
                 gpu_percent: float | None = None) -> None:
        import os
        self.cpu_count = max(1, cpu_count or (os.cpu_count() or 1))
        self.cpu_percent = 0.0 if cpu_percent is None else cpu_percent
        self.gpu_percent = 0.0 if gpu_percent is None else gpu_percent

    def plan(self, jobs: Iterable[tuple[JobKind, Path, Path]]) -> SchedulePlan:
        # 固定上限为总核心 80%，其余给系统/浏览器/游戏客户端。
        max_workers = max(1, int(self.cpu_count * 0.8))
        busy = max(self.cpu_percent, self.gpu_percent)
        if busy >= 85:
            budget = max(1, int(self.cpu_count * 0.4))
        elif busy >= 70:
            budget = max(1, int(self.cpu_count * 0.6))
        else:
            budget = max_workers

        kinds = {kind for kind, _src, _dst in jobs}
        # 67GB FPK / GPK 顺序读。即使输出异盘，同一来源盘也最多一个大包。
        large = 1 if JobKind.LARGE_ARCHIVE_READ in kinds else 0
        # 轻任务可并发，但不能挤占大包读的 I/O 与内存。
        scan = min(max(1, budget // 2), 8) if JobKind.SMALL_SCAN in kinds else 0
        convert = 1 if busy >= 80 else min(max(1, budget // 2), 8)
        if JobKind.CPU_CONVERT not in kinds:
            convert = 0
        return SchedulePlan(
            max_cpu_workers=budget,
            large_archive_workers=large,
            scan_workers=scan,
            convert_workers=convert,
            queue_size=max(4, min(32, budget * 2)),
        )
