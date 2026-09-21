"""分页参数归一化（Workbench v1.3，API-first 查询统一入口）。

硬规则：任何列表端点都不得默认返回全量。
- `page_size` 上限 = PAGE_SIZE_MAX（200），超出即截断并把 `clamped=true` 回报给调用方
- `offset/limit` 保留为兼容别名（统一折算到 page/page_size），不再各写一套
"""
from __future__ import annotations

PAGE_SIZE_MAX = 200
PAGE_SIZE_DEFAULT = 50
OFFSET_HARD_LIMIT = 200_000


def norm_page(page=None, page_size=None, limit=None, offset=None):
    """→ (page:int>=1, page_size:int in [1,200], clamped:bool)"""
    raw = page_size if page_size is not None else (limit if limit is not None else PAGE_SIZE_DEFAULT)
    try:
        size = int(raw)
    except (TypeError, ValueError):
        size = PAGE_SIZE_DEFAULT
    clamped = size > PAGE_SIZE_MAX or size < 1
    size = max(1, min(size, PAGE_SIZE_MAX))

    p = page
    if p is None and offset is not None:
        try:
            off = max(0, min(int(offset), OFFSET_HARD_LIMIT))
        except (TypeError, ValueError):
            off = 0
        p = off // size + 1
    try:
        p = int(p or 1)
    except (TypeError, ValueError):
        p = 1
    return max(1, p), size, clamped


def slice_page(rows: list, page: int, page_size: int):
    start = (page - 1) * page_size
    return rows[start:start + page_size]


def page_meta(total: int, page: int, page_size: int, *, clamped: bool = False, **extra) -> dict:
    pages = (total + page_size - 1) // page_size if page_size else 0
    out = {"total": total, "page": page, "page_size": page_size, "pages": pages,
           "page_size_max": PAGE_SIZE_MAX, "clamped": clamped,
           "has_prev": page > 1, "has_next": page < pages}
    out.update(extra)
    return out
