# -*- coding: utf-8 -*-
"""unnamed_registry.py — 「无名大表 → 逻辑表名」契约的读取与解析（只读）

还原树 `pe/配置/<容器>/_未命名/` 里的编译表 blob 没有游戏内路径，只有 64-bit
`file_id` 和一个「行号占位名」。本模块把 `rules/unnamed_table_registry.yml` 的登记
翻译成**当前磁盘上的真实路径**，供消费层（`pe_source`、产出脚本、验收脚本）复用。

## 为什么键是 file_id 而不是行号

`file_id` 是游戏侧稳定的逻辑标识：冻结产物锁定的 BA8 快照与本机当前 npk 是**两个
不同版本**，同一张逻辑表用的却是同一串 file_id。行号只是在包里的摆放位置，换包即变。

## 三级解析（逐级降级，降级会明确告知）

  ① `pe_index.fid_names` 里按 `(file_id, 容器前缀)` 精确反查  → state="verified"
  ② 索引不可用/查不到时，退回登记时实测的 `observed_row_name`  → state="degraded-row-name"
  ③ 都没有 → 返回 None（调用方必须当成「缺表」，不许猜）

## 用法

```python
from unnamed_registry import paths_for_table, resolve_entry

base, pool = paths_for_table("reward_pool_data")   # (Path|None, Path|None)
if base is None:
    raise SystemExit("无名大表未登记或不在树里")
```
"""
from __future__ import annotations

import functools
import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import INDEX_ROOT, RULES_DIR, TREE_ROOT  # noqa: E402

REGISTRY = RULES_DIR / "unnamed_table_registry.yml"
PE_IDX = INDEX_ROOT / "热更检测" / "pe_index.sqlite3"

STATE_VERIFIED = "verified"
STATE_DEGRADED = "degraded-row-name"


@functools.lru_cache(maxsize=1)
def load_registry() -> dict:
    """读契约文件（缓存）。缺 PyYAML 时给出可执行提示，不静默返回空。"""
    if not REGISTRY.is_file():
        raise FileNotFoundError("契约文件不存在：%s" % REGISTRY)
    try:
        import yaml
    except ImportError as e:  # pragma: no cover - 环境问题
        raise RuntimeError(
            "缺 PyYAML，无法读 %s。装：pip install pyyaml" % REGISTRY.name) from e
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}


def tree_root() -> pathlib.Path:
    """无名层所在的根（相对 TREE_ROOT，由契约的 tree_rel_root 决定）。"""
    return TREE_ROOT / str(load_registry().get("tree_rel_root") or "pe/配置")


@functools.lru_cache(maxsize=1)
def _fid_name_index() -> dict[str, list[str]] | None:
    """`file_id → [Windows 风格占位名]`。索引缺失时返回 None（不抛）。"""
    if not PE_IDX.is_file():
        return None
    out: dict[str, list[str]] = {}
    try:
        con = sqlite3.connect("file:%s?mode=ro" % PE_IDX.as_posix(), uri=True)
        try:
            for fid, name in con.execute("select fid, name from fid_names"):
                if fid and name:
                    out.setdefault(str(fid).upper(), []).append(name)
        finally:
            con.close()
    except sqlite3.Error:
        return None
    return out


def _to_path(name: str) -> pathlib.Path:
    return tree_root() / pathlib.PureWindowsPath(name).as_posix()


def resolve_entry(file_id: str, container: str | None,
                  row_name: str | None = None) -> tuple[pathlib.Path | None, str]:
    """把一个登记项解析成当前磁盘路径。返回 ``(path|None, state)``。

    ★ 只在 `(file_id, container)` 精确匹配时才返回 verified —— 同一行号名在不同
      容器下对应不同 file_id，按名字模糊找会串表。

    `container` 传 None 或 "" 表示**不限容器**：按 file_id 全库反查。
    这是「以身份哈希为主键」的用法（分服解析走这条），因为同一个 file_id
    可能是有名文件（`com/cdata/oversea/xxx.py`）也可能是无名 blob
    （`Documents/.../_未命名/00019997.bin`），按名字判断会把一半漏掉。
    """
    fid = str(file_id or "").upper()
    if not fid:
        return None, "missing"

    idx = _fid_name_index()
    if idx is not None and fid in idx:
        if not container:
            hits = list(idx[fid])
        else:
            prefix = container.replace("/", "\\") + "\\_未命名\\"
            hits = [n for n in idx[fid] if n.replace("/", "\\").startswith(prefix)]
        if hits:
            # 同一 fid 可能有多条记录（不同容器），取最短者（最接近逻辑名的一条）
            return _to_path(sorted(hits, key=len)[0]), STATE_VERIFIED

    if row_name and container:
        p = _to_path(container.replace("/", "\\") + "\\_未命名\\" + row_name)
        if p.is_file():
            return p, STATE_DEGRADED
    return None, "missing"


def entry_of(logical_name: str, *, component: str | None = None) -> dict | None:
    """按逻辑表名取登记条目。

    `component` 缺省取 `base` —— 同名逻辑表在不同服各有一份数据体
    （如 `reward_pool_data` 的 base 与 ykxq 都是无名大表），必须按组件区分，
    否则会把两个服的表当成同一张。
    """
    want = component or "base"
    pool = [t for t in (load_registry().get("tables") or [])
            if t.get("logical_name") == logical_name]
    for t in pool:
        if (t.get("component") or "base") == want:
            return t
    return None


def components_of(logical_name: str) -> list[str]:
    """这张逻辑表登记了哪些组件（供分服解析枚举用）。"""
    return [(t.get("component") or "base")
            for t in (load_registry().get("tables") or [])
            if t.get("logical_name") == logical_name]


def paths_for_table(logical_name: str,
                    component: str | None = None) -> tuple[pathlib.Path | None, pathlib.Path | None]:
    """返回 ``(表体, 配对池)`` 的当前路径。未登记或找不到给 ``(None, None)``。

    这是 `pe_source.paths_of` 的回退入口：`com/cdata/<表>.py` 不是真表体时才调用。
    """
    t = entry_of(logical_name, component=component)
    if not t:
        return None, None
    container = t.get("container") or ""
    data = t.get("data") or {}
    pool = t.get("pool") or {}
    base, _ = resolve_entry(data.get("file_id"), container, data.get("observed_row_name"))
    chs, _ = resolve_entry(pool.get("file_id"), container, pool.get("observed_row_name")) \
        if pool else (None, "absent")
    return base, chs


def states_for_table(logical_name: str, component: str | None = None) -> dict:
    """登记项的解析状态（给验收脚本/产出 manifest 写溯源用）。"""
    t = entry_of(logical_name, component=component)
    if not t:
        return {"logical_name": logical_name, "component": component or "base",
                "registered": False}
    container = t.get("container") or ""
    out: dict = {"logical_name": logical_name, "component": t.get("component") or "base",
                 "registered": True, "container": container, "tree_root": str(tree_root())}
    for kind in ("data", "pool"):
        spec = t.get(kind) or {}
        if not spec:
            continue
        p, state = resolve_entry(spec.get("file_id"), container, spec.get("observed_row_name"))
        out[kind] = {"file_id": spec.get("file_id"), "state": state,
                     "path": str(p) if p else None}
    return out


__all__ = [
    "REGISTRY", "PE_IDX", "STATE_VERIFIED", "STATE_DEGRADED",
    "load_registry", "tree_root", "resolve_entry", "entry_of", "components_of",
    "paths_for_table", "states_for_table",
]
