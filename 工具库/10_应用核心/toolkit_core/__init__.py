"""明日之后拆包器核心。

公共入口优先使用 :mod:`toolkit_core.unified_index`；旧脚本仍保留兼容，
但不再作为 GPK 文件索引的权威实现。
"""

from .unified_index import UnifiedFileIndex, build_database, path_fid

__all__ = ["UnifiedFileIndex", "build_database", "path_fid"]
