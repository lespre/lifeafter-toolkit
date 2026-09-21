# -*- coding: utf-8 -*-
"""新拆包器核心：所有派生产物只能写到 EXE 同级或用户显式选择的外置目录。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

DEFAULT_OUTPUT_ROOT = Path(r"E:/la拆包项目/03拆包产物").resolve()


class OutputPolicy:
    """输出目录安全策略，不依赖 PyInstaller 的临时解包目录。"""

    def __init__(self, exe_dir: Optional[Path] = None) -> None:
        self.exe_dir = Path(exe_dir or Path(__file__).resolve().parents[2]).resolve()

    @staticmethod
    def _is_relative_to(child: Path, parent: Path) -> bool:
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False

    def resolve(self, selected: Optional[Path | str], *, source_root: Path | str) -> Path:
        """返回已创建、且永远不落在原始游戏目录内的输出根。"""
        source = Path(source_root).resolve()
        target = (Path(selected) if selected else DEFAULT_OUTPUT_ROOT).resolve()
        if self._is_relative_to(target, source):
            raise ValueError("输出目录不能位于游戏源目录内，请选工具包外置 output")
        if "_MEI" in str(target).upper():
            raise ValueError("输出目录不能位于 PyInstaller 临时目录")
        target.mkdir(parents=True, exist_ok=True)
        for folder in ("jobs", "logs", "exports", "previews", "indexes"):
            (target / folder).mkdir(exist_ok=True)
        return target


def resolve_index_database(*, output_dir: Path, exe_dir: Path, default_root: Path,
                           meipass: Path | None = None) -> Path:
    """索引库发现链：用户输出目录 → exe 同级（内置）→ 默认产物根 → 冻结资源目录。

    未命中的候选都保留原义：返回第一个候选（=输出目录路径），供“重建索引”使用。
    """
    candidates = [Path(output_dir) / "indexes" / "lifeafter_files.sqlite3",
                  Path(exe_dir) / "indexes" / "lifeafter_files.sqlite3",
                  Path(default_root) / "indexes" / "lifeafter_files.sqlite3"]
    if meipass is not None:
        candidates.append(Path(meipass) / "indexes" / "lifeafter_files.sqlite3")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]
