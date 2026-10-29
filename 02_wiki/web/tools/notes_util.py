# -*- coding: utf-8 -*-
"""notes_util.py — 板级 meta.notes 的**幂等追加**助手

## 为什么需要它

多个板级后处理脚本会在 `meta.notes` 末尾追加一句口径说明。原写法是
无条件拼接：

```python
d["meta"]["notes"] = (d["meta"].get("notes") or "") + " ｜ 某说明"
```

于是**每跑一次重建脚本就多一段 notes**：
- 产物噪声无界增长（实测 vehicle_full 累积到 31 段 / 单段重复 8 次）；
- **幂等性永远不成立** —— 重跑后文件哈希必变，条目级 diff 每次都报「修改」，
  编排器（build_pipeline.py）的重跑校验与灰度回滚判据全部失效。

## 铁律

口径说明是**幂等追加**：同一句说明已存在则不再追加。
需要表达「同一句的更新版本」时，用 `replace_note()` 显式替换，
不要靠追加产生第 N 份副本。

用法:
```python
from notes_util import append_note, replace_note

append_note(d, "同名（含时限变体）合并成一张卡，编号见详情")
replace_note(d, "类型=vehicle_brand_data.type_name（6 类），子类=brands 池",
             "类型=vehicle_brand_data.type_name（6 类），子类=brands 池（口径 2026-10-30 复核）")
```
"""
from __future__ import annotations

SEP = " ｜ "


def _split(notes: str) -> list[str]:
    return [p for p in (notes or "").split(SEP) if p.strip()]


def append_note(board: dict, note: str, sep: str = SEP) -> str:
    """幂等追加一条口径说明。已存在则原样返回，不重复追加。

    board: 板 dict（就地修改其 meta.notes）
    返回追加后的 notes 全文。
    """
    note = (note or "").strip()
    if not note:
        return (board.get("meta") or {}).get("notes") or ""
    meta = board.setdefault("meta", {})
    parts = _split(meta.get("notes") or "")
    if note not in parts:
        parts.append(note)
        meta["notes"] = sep.join(parts)
    return meta.get("notes") or ""


def replace_note(board: dict, old: str, new: str, sep: str = SEP) -> str:
    """把某条口径说明替换为新版本（幂等）。

    old 不存在时按追加处理；存在多份时全部替换（顺带收敛历史重复）。
    """
    old = (old or "").strip()
    new = (new or "").strip()
    meta = board.setdefault("meta", {})
    parts = _split(meta.get("notes") or "")
    if not old:
        if new and new not in parts:
            parts.append(new)
    else:
        if new:
            parts = [new if p == old else p for p in parts]
        else:
            parts = [p for p in parts if p != old]
    meta["notes"] = sep.join(parts)
    return meta.get("notes") or ""


def dedupe_notes(board: dict, sep: str = SEP) -> tuple[str, int]:
    """收敛历史重复段（保留首次出现顺序）。返回 (收敛后 notes, 去掉段数)。"""
    meta = board.setdefault("meta", {})
    parts = _split(meta.get("notes") or "")
    seen: set[str] = set()
    out: list[str] = []
    for p in parts:
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    removed = len(parts) - len(out)
    meta["notes"] = sep.join(out)
    return meta.get("notes") or "", removed
