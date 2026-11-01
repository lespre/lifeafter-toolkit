# -*- coding: utf-8 -*-
"""cdata 表统一读取（legacy 0x73 / nxs 容器 / 新格式 .py 三种封装）。

## 背景

热更之后 `com/cdata` 下的表出现了三种封装，同一份「表数据」解法不同：

| 形态 | 特征 | 字符串池 |
|---|---|---|
| ① legacy | 文件里有 `x{` + 4 字节长度 + 表体 | `<stem>_chs.py`（旧池格式，`BT.parse_legacy_chs_pool`） |
| ② nxs 容器 | 文件头 `73 00`（0x73 标记）+ UTF-16 串区 + `0x7b` 载荷 + `76 01 0b` 索引 | `<stem>_chs.py`（同样是 0x73 容器池，`BT.parse_chs_pool`） |
| ③ 新格式 .py | 与 ② 同构，但文件扩展名仍是 `.py` | 可能是**加密池**（头 `37 cb b3 19…`），此时字段名退化成 `<slot_N>` |

2026-11-01 时装板块靠这个模块读通了三张此前解不开的表：
`fashion_value_word_data`（26 行卖点标签）、`other_get_method_data`（132 行获取方式）、
`add_friendliness_data`（10 行暴击档位）。

## 用法

```python
from toolkit_core import cdata_nxs

tab = cdata_nxs.load_table("fashion_value_word_data", cd_dir=CD)
for row in tab.rows:
    print(row["key"], row["fields"])       # fields 已把 (tag, value) 拆平
print(tab.kind, tab.meta.get("pool_missing"))
```

## 边界

* ③ 加密池不解 —— 字段名只能是 `<slot_N>`，`tab.meta["pool_missing"]` 为 True 时不要据此写字段名口径。
* jump 引用（`0x0b` 组）不在本模块展开；需要时用 `bindict_table.read_27_group` 自行处理
  （`02_wiki/web/tools/enrich_fashion_dimensions.py` 的 `jl()` 是现成范例）。
"""
from __future__ import annotations

import pathlib
import struct
from typing import Any

from toolkit_core import bindict_73 as B73
from toolkit_core import bindict_table as BT

__all__ = ["TableInfo", "load_table", "read_cdata_table", "find_table"]


class TableInfo:
    """一张表的读取结果。"""

    __slots__ = ("stem", "kind", "rows", "meta", "path")

    def __init__(self, stem: str, kind: str, rows: list[dict[str, Any]],
                 meta: dict[str, Any], path: pathlib.Path):
        self.stem = stem
        self.kind = kind            # 'legacy' | 'nxs' | 'nxs-nopool'
        self.rows = rows            # [{'key':…, 'fields': {字段: 值}}]
        self.meta = meta
        self.path = path

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self):
        return iter(self.rows)

    def by_key(self) -> dict[Any, dict[str, Any]]:
        return {r["key"]: r for r in self.rows}

    def __repr__(self) -> str:      # pragma: no cover - 调试用
        return f"<TableInfo {self.stem} kind={self.kind} rows={len(self.rows)}>"


def _flatten(values: dict[str, Any]) -> dict[str, Any]:
    """把 (tag, value) 拆成裸值；jump 引用保留原字符串（如 'jump:17087'）。"""
    out: dict[str, Any] = {}
    for k, v in (values or {}).items():
        out[k] = v[1] if isinstance(v, tuple) and len(v) == 2 else v
    return out


def find_table(stem: str, cd_dir: pathlib.Path) -> pathlib.Path | None:
    """按 stem 找表文件：优先 .py（还原树里的常规命名），其次 .nxs。"""
    cd = pathlib.Path(cd_dir)
    for ext in (".py", ".nxs"):
        p = cd / f"{stem}{ext}"
        if p.is_file():
            return p
    return None


def _legacy_rows(path: pathlib.Path, cd_dir: pathlib.Path):
    raw = path.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + ln]
    pool = BT.parse_legacy_chs_pool((pathlib.Path(cd_dir) / f"{path.stem}_chs.py").read_bytes())
    rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
    return rows, unbound, {"kind": "legacy", "pool_size": len(pool),
                           "body_len": ln, "unbound": len(unbound)}


def _nxs_rows(path: pathlib.Path, cd_dir: pathlib.Path):
    try:
        rows, unbound, meta = B73.decode_73_table(path)
        pool_missing = not meta.get("pool_matches_count", True)
    except Exception:                        # noqa: BLE001 - 池是加密格式时改用空池
        rows, unbound, meta = B73.decode_73_table(path, pool=[])
        pool_missing = True
    kind = "nxs-nopool" if pool_missing else "nxs"
    out = []
    for r in rows:
        vals = r.get("values")
        if isinstance(vals, str):           # 部分实现把 values 序列化成字符串
            import ast
            try:
                vals = ast.literal_eval(vals)
            except Exception:               # noqa: BLE001 - 解析不了就原样留着
                vals = {}
        out.append({"key": r.get("key"), "fields": _flatten(vals or {}), "raw": r})
    m = {"kind": kind, "unbound": len(unbound),
         "pool_size": meta.get("pool_size"), "pool_missing": pool_missing,
         "index_agrees": meta.get("index_agrees_with_bindict_table")}
    return out, unbound, m


def load_table(stem: str, cd_dir: pathlib.Path | str) -> TableInfo:
    """读一张 cdata 表；自动识别 legacy / nxs / 新格式 .py。"""
    cd = pathlib.Path(cd_dir)
    path = find_table(stem, cd)
    if path is None:
        raise FileNotFoundError("找不到表：%s（%s）" % (stem, cd))

    raw_head = path.read_bytes()[:4]
    # legacy 表优先：文件里有合法 `x{` 长度前缀
    try:
        got = _legacy_rows(path, cd)
    except Exception:                        # noqa: BLE001 - 不是 legacy 就走 nxs
        got = None
    if got is not None:
        rows, unbound, meta = got
        out = [{"key": r.get("key"), "fields": _flatten(r.get("values") or {}), "raw": r}
               for r in rows]
        return TableInfo(stem, "legacy", out, meta, path)

    rows, unbound, meta = _nxs_rows(path, cd)
    return TableInfo(stem, meta.get("kind", "nxs"), rows, meta, path)


def read_cdata_table(stem: str, cd_dir: pathlib.Path | str,
                     field: str | None = None) -> dict[Any, Any]:
    """便捷入口：读表并返回 {key: {字段: 值}}；给了 field 则返回 {key: 该字段值}。"""
    tab = load_table(stem, cd_dir)
    if field is None:
        return {r["key"]: r["fields"] for r in tab.rows}
    return {r["key"]: r["fields"].get(field) for r in tab.rows}


if __name__ == "__main__":                   # 手动自检：python -m toolkit_core.cdata_nxs <stem> <cd_dir>
    import sys
    stem = sys.argv[1] if len(sys.argv) > 1 else "fashion_value_word_data"
    cd = sys.argv[2] if len(sys.argv) > 2 else "."
    t = load_table(stem, cd)
    print("%s | kind=%s rows=%d meta=%s" % (t.stem, t.kind, len(t.rows), t.meta))
    for r in t.rows[:5]:
        print("  ", r["key"], str(r["fields"])[:160])
