# -*- coding: utf-8 -*-
"""两条线模型：文字线（数据/文本）与渲染线（贴图/模型/材质）。

- 文字线：脚本表、配置、文本等可读数据（script*.npk、*.bin、*.txt …）
- 渲染线：纹理、模型、材质、音视频等资源（*.gpk、*.fpk、*.wpk、*.dds …）

纪律：只做“默认归类建议”，永远允许界面里手动改线；未知一律不猜。
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable


class DataLine(str, Enum):
    TEXT = "文字线"
    RENDER = "渲染线"

    @property
    def folder(self) -> str:
        return self.value


TEXT_EXTS = frozenset({".bin", ".txt", ".json", ".xml", ".csv", ".py", ".lua",
                       ".cfg", ".ini", ".bytes", ".dat", ".db", ".sqlite3", ".md"})
RENDER_EXTS = frozenset({".dds", ".tga", ".ktx", ".astc", ".png", ".jpg", ".jpeg", ".bmp",
                         ".wpk", ".mesh", ".gim", ".mod", ".mat", ".cube", ".shader",
                         ".dxbc", ".fsb", ".wav", ".mp4", ".webm", ".gif"})

# 包级默认绑定（基于本项目已证实的容器用途；可被界面覆盖）
_RENDER_PACKAGE_EXTS = frozenset({".gpk", ".fpk", ".wpk", ".idx"})


def classify_package(path) -> DataLine:
    """按包名/扩展名给出默认线路。script.*.npk = 文字线；GPK/FPK/WPK/IDX = 渲染线；
    其余 .npk 默认文字线（界面可改），未知扩展名也回文字线以便暴露给用户改。"""
    p = Path(path)
    ext = p.suffix.lower()
    if ext in _RENDER_PACKAGE_EXTS:
        return DataLine.RENDER
    if ext == ".npk":
        return DataLine.TEXT
    return DataLine.TEXT


def classify_leaf(name) -> DataLine | None:
    """叶文件/条目分类；无法判定时返回 None（不猜）。"""
    ext = Path(str(name)).suffix.lower()
    if ext in TEXT_EXTS:
        return DataLine.TEXT
    if ext in RENDER_EXTS:
        return DataLine.RENDER
    return None


def line_exports_dir(output_root, line: DataLine) -> Path:
    """分线导出根：<output>/exports/<文字线|渲染线>。"""
    return Path(output_root) / "exports" / line.folder


@dataclass(frozen=True)
class Direction:
    key: str
    label: str
    line: DataLine
    hint: str


DIRECTIONS: tuple[Direction, ...] = (
    Direction("text", "文字线（数据 / 文本）", DataLine.TEXT, "script*.npk 等数据表、文本容器"),
    Direction("render", "渲染线（贴图 / 模型 / 材质）", DataLine.RENDER, "gpk / fpk / wpk / idx 渲染资源容器"),
)


def direction_by_key(key: str) -> Direction | None:
    for spec in DIRECTIONS:
        if spec.key == key:
            return spec
    return None


def select_containers(container_names: Iterable[str], direction_keys: Iterable[str]) -> list[str]:
    """纯函数：按已选方向筛容器名（保持输入顺序，其余不做猜测）。"""
    wanted = {spec.line for spec in DIRECTIONS if spec.key in set(direction_keys)}
    return [str(name) for name in container_names if classify_package(name) in wanted]
