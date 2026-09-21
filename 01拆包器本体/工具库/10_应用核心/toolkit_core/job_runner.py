# -*- coding: utf-8 -*-
"""拆包任务执行层：UI 线程绝不直接跑大 I/O；取消/暂停仅在安全任务边界生效。"""
from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
import time
from pathlib import Path
from threading import Event
from typing import Callable, Iterable

from toolkit_core.fpk_frames import iter_fpk_frames


@dataclass(frozen=True)
class PackageJob:
    source: Path
    output_root: Path
    line: str | None = None   # "文字线"/"渲染线"；None=旧行为（不分线）


def job_target(job: PackageJob) -> Path:
    """按线路计算导出目录：<root>/exports[/<line>]/<ext>/<stem>。"""
    ext = job.source.suffix.lower().lstrip(".")
    parts = [job.output_root, "exports"]
    if job.line:
        parts.append(job.line)
    parts.extend([ext, job.source.stem])
    return Path(*parts)


def _resource_root() -> Path:
    import sys
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))


def _load_backend():
    import sys
    # PyInstaller one-file: 后端资源位于 _MEIPASS；输出策略仍由 GUI 的 APP_HOME 负责。
    resource_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    core_dir = resource_root / "01_核心解包器"
    if str(core_dir) not in sys.path:
        sys.path.insert(0, str(core_dir))  # 后端运行时导入 npk_reader / la_unpack_core 等
    spec = importlib.util.spec_from_file_location("lifeafter_backend", core_dir / "lifeafter_unpacker_full.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _export_verified_fpk(source: Path, target: Path) -> Path:
    """Export a manifest only from sequentially verified FPK frame boundaries."""
    rows: list[dict] = []
    types: dict[str, int] = {}
    for frame, _payload in iter_fpk_frames(source):
        kind = frame.output_magic.lower()
        rows.append(
            {
                "idx": frame.index,
                "off": frame.offset,
                "comp": frame.packed_size,
                "out": frame.output_size,
                "output_magic": frame.output_magic,
                "storage": frame.storage,
                "padding_size": frame.padding_size,
                "boundary_verified": True,
            }
        )
        types[kind] = types.get(kind, 0) + 1
    report = {
        "source": str(source),
        "frame_boundary_method": "sequential_decompressobj_eof_plus_zero_padding",
        "total_frames": len(rows),
        "types": types,
        "rows": rows,
    }
    destination = target / "frames_full.json"
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return destination


def run_package_jobs(jobs: Iterable[PackageJob], *, pause_event: Event, cancel_event: Event,
                     on_progress: Callable[[int, int, str], None], on_log: Callable[[str], None],
                     on_job_start: Callable[[int, int, str], None] | None = None,
                     readable: bool = False) -> None:
    """按任务顺序执行。大包不并行，暂停和取消在每个包开始前检查。"""
    queue = list(jobs)
    backend = None
    total = len(queue)
    for number, job in enumerate(queue, 1):
        while pause_event.is_set() and not cancel_event.is_set():
            on_log("已暂停：等待当前安全边界恢复")
            cancel_event.wait(0.2)
        if cancel_event.is_set():
            on_log("已取消：未开始的任务不会执行")
            break
        ext = job.source.suffix.lower()
        target = job_target(job)
        target.mkdir(parents=True, exist_ok=True)
        tag = f"｜{job.line}" if job.line else ""
        size_mb = job.source.stat().st_size / 1024 / 1024
        on_log(f"▶ [{number}/{total}] {job.source.name}{tag}｜{size_mb:,.1f} MB → {target}")
        if on_job_start is not None:
            on_job_start(number, total, job.source.name)
        (target / "line.json").write_text(json.dumps({
            "line": job.line or "", "source": str(job.source), "target": str(target),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        started = time.time()
        try:
            if ext == ".fpk":
                manifest = _export_verified_fpk(job.source, target)
                on_log(f"  FPK 边界验证完成：{manifest.name}")
            elif ext == ".gpk":
                if backend is None:
                    backend = _load_backend()
                backend.extract_gpk(str(job.source), str(target))
            elif ext == ".npk":
                if backend is None:
                    backend = _load_backend()
                backend.extract_npk(str(job.source), str(target))
            elif ext == ".idx":
                if backend is None:
                    backend = _load_backend()
                sibling = job.source.with_suffix(".wpk")
                if not sibling.exists():
                    raise FileNotFoundError(f"IDX 需要同名 WPK：{sibling}")
                backend.parse_wpk_idx(str(job.source), str(sibling))
            else:
                raise ValueError(f"当前不支持的包格式：{ext}")
        except Exception as exc:
            on_log(f"❌ [{number}/{total}] {job.source.name} 失败：{exc}")
            raise RuntimeError(f"{job.source.name} 失败：{exc}") from exc
        on_log(f"✓ [{number}/{total}] {job.source.name} 完成（{time.time() - started:.1f}s）")
        if readable:
            try:
                from toolkit_core.readable import make_readable
                stats = make_readable(target, _resource_root(), on_log)
                on_log(f"  🧾 可读化：PNG {stats['png']}｜字符串 {stats['strings']}｜跳过 {stats['skipped']}｜失败 {stats['errors']}")
            except Exception as exc:
                on_log(f"  ⚠️ 可读化失败（不影响解包）：{exc}")
        on_progress(number, total, job.source.name)
