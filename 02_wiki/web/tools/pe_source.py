# -*- coding: utf-8 -*-
"""pe_source.py — 「PE 还原树 / 表缓存」只读取数层（重建脚本共用）

## 为什么有这一层

热更后要能**不碰客户端、不碰 APK** 地重建板块：源只有两处

  ① `01_索引与产物/41_还原树/pe/配置/com/cdata/<表>.py`（+ `_chs.py` 配对池）
  ② `01_索引与产物/30_分析/90_表缓存/base_<FID>.py`（大表：common_item 等
     在 cdata 里只有 815B MergedTableData 桩，数据体只在哈希命名的缓存副本里）

本模块把「怎么取表、怎么解行、怎么解 jump 帧」收敛成一处，重建脚本只写业务筛选，
不再各自拼 `x{` 容器、也不再各自猜 jump 基准。

## 铁律（踩过的坑）

- `x{` 帧：`u32 body_len @x+2`，body = `raw[x+6 : x+6+len]`。
- **jump 基准 = `blob = body[8 + 4*count:]`**（count 取 body 头部 u32，不是解出的行数）。
  拿 body/payload 当基址会整体错 `8+4*count` 字节，表现为「jump 全是坏引用」的假结论。
- `0x36` = 映射行：`36 <kt> <vt> <uleb n> + n×(uleb key, uleb value)`；
  nucleus_build_data 的 `rank_to_desc` 就是 `n → CHS 池槽`（星级段）。
- `0x27` = 组：`27 <kind> <uleb n> + n×元素`（kind 0x01=uleb / 0x12=f32 / 0x22=f64）。
- 缓存表的池要**自己配对**：common_item 的 CLS 池在 `base_EF3A8474A5E5F7A4.py`
  （55,408 串）；配错池的表现是字段值成片 `<oob:NNNN>`，不是「字段为空」。
"""
from __future__ import annotations

import functools
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from la_paths import ANALYSIS_ROOT, TREE_ROOT, TOOLKIT_CORE  # noqa: E402

if str(TOOLKIT_CORE) not in sys.path:
    sys.path.insert(0, str(TOOLKIT_CORE))
from toolkit_core import bindict_table as BT  # noqa: E402

CD = Path(TREE_ROOT / "pe/配置/com/cdata")
CACHE = Path(ANALYSIS_ROOT / "90_表缓存")
LEDGER = Path(TREE_ROOT / "pe/pe_config_merge_ledger_v2.json")

# 源标识：还原树配置目录（逐表行级）/ 表缓存（大表数据体）
SOURCE_TREE = "pe-restore-tree-config"
SOURCE_CACHE = "pe-table-cache"

# common_item：cdata 里是 815B 桩，真数据体在缓存里；池 = base_EF3A8474A5E5F7A4
COMMON_ITEM_FID = "B42760CCA41DBC25"
COMMON_ITEM_POOL_FID = "EF3A8474A5E5F7A4"


# ── 文件与锁 ────────────────────────────────────────────────────────
def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def lock_of(path: Path, *, source_id: str, role: str = "primary", root: Path | None = None) -> dict:
    """一条 source_locks 记录（sha256/bytes/mtime_ns/path_hint 全取自磁盘）。"""
    st = path.stat()
    try:
        hint = str(path.relative_to(root or TREE_ROOT)).replace("\\", "/")
    except ValueError:
        try:
            hint = str(path.relative_to(ANALYSIS_ROOT.parent)).replace("\\", "/")
        except ValueError:
            hint = path.name
    return {
        "source_id": source_id,
        "role": role,
        "sha256": sha256_of(path),
        "bytes": st.st_size,
        "mtime_ns": st.st_mtime_ns,
        "path_hint": hint,
    }


# ── 表定位与解码 ────────────────────────────────────────────────────
def paths_of(stem: str) -> tuple[Path | None, Path | None]:
    """返回 (base, chs)。cdata 优先，其次表缓存（按 FID 命名）。"""
    base = CD / f"{stem}.py"
    chs = CD / f"{stem}_chs.py"
    if base.is_file():
        return base, (chs if chs.is_file() else None)
    return None, None


def body_of(raw: bytes) -> bytes:
    at = raw.find(b"x{")
    if at < 0:
        raise ValueError("payload 里没有 x{ 表体帧")
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + ln]
    if len(body) != ln:
        raise ValueError(f"x{{ 帧长度越界（声明 {ln}，实得 {len(body)}）")
    return body


def blob_of(body: bytes) -> bytes:
    """jump 基准段：body[8 + 4*count:]（count 取 body 头部 u32）。"""
    count = struct.unpack_from("<I", body, 0)[0]
    return body[8 + 4 * count:]


@functools.lru_cache(maxsize=8)
def _load_cached(key: str) -> dict:
    base, chs = paths_of(key)
    pool: list[str] = []
    if chs is not None:
        pool = BT.parse_legacy_chs_pool(chs.read_bytes())
    body = body_of(base.read_bytes())
    rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False)
    return {
        "rows": rows,
        "unbound": unbound,
        "pool": pool,
        "body": body,
        "blob": blob_of(body),
        "base": base,
        "chs": chs,
        "source_id": SOURCE_TREE,
    }


def load(stem: str) -> dict:
    """解一张 cdata 表（带配对池）。返回 rows/unbound/pool/body/blob/base/chs。"""
    return _load_cached(stem)


@functools.lru_cache(maxsize=1)
def load_cached_table(base_fid: str, pool_fid: str | None) -> dict:
    """解表缓存里按 FID 命名的表体（大表：common_item 等）。"""
    base = CACHE / f"base_{base_fid}.py"
    if not base.is_file():
        raise FileNotFoundError(f"表缓存缺 base_{base_fid}.py")
    pool: list[str] = []
    pool_path = CACHE / f"base_{pool_fid}.py" if pool_fid else None
    if pool_path is not None and pool_path.is_file():
        pool = BT.parse_legacy_chs_pool(pool_path.read_bytes())
    body = body_of(base.read_bytes())
    rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False)
    return {
        "rows": rows,
        "unbound": unbound,
        "pool": pool,
        "body": body,
        "blob": blob_of(body),
        "base": base,
        "pool_path": pool_path,
        "source_id": SOURCE_CACHE,
    }


def common_item() -> dict:
    """common_item 全量行（缓存 base + 自带池）。按 id 建索引缓存在返回值的 'by_id'。"""
    t = load_cached_table(COMMON_ITEM_FID, COMMON_ITEM_POOL_FID)
    if "by_id" not in t:
        t = dict(t)
        t["by_id"] = {int(r["key"]): r for r in t["rows"]}
    return t


# ── 取值与帧解析 ────────────────────────────────────────────────────
def val(row: dict, field: str, default: Any = None) -> Any:
    """取行字段值（未解出的字段返回 default）。"""
    payload = (row.get("values") or {}).get(field)
    if payload is None:
        return default
    try:
        return payload[1]
    except (IndexError, TypeError):
        return default


def text(row: dict, field: str) -> str | None:
    v = val(row, field)
    return v if isinstance(v, str) and not v.startswith("jump:") else None


def jump_target(row: dict, field: str) -> int | None:
    v = val(row, field)
    if isinstance(v, str) and v.startswith("jump:"):
        return int(v[5:])
    return None


def frame(blob: bytes, off: int) -> dict | None:
    """解一个 jump 目标帧（0x27 组 / 0x36 映射行），解不出返回 None。

    - ``{"kind": "ints",    "values": [int...]}``
    - ``{"kind": "floats",  "values": [float...]}``
    - ``{"kind": "mapping", "pairs": [(key, value), ...]}``
    """
    if off is None or off < 0 or off >= len(blob):
        return None
    head = blob[off]
    if head == 0x36:
        p = off + 1
        p += 2  # kt / vt 各 1B
        n, p = BT.uleb(blob, p, len(blob))
        pairs = []
        for _ in range(n):
            k, p = BT.uleb(blob, p, len(blob))
            v, p = BT.uleb(blob, p, len(blob))
            pairs.append((k, v))
        return {"kind": "mapping", "pairs": pairs}
    if head == 0x27:
        kind = blob[off + 1]
        n, p = BT.uleb(blob, off + 2, len(blob))
        if kind == 0x01:
            out = []
            for _ in range(n):
                v, p = BT.uleb(blob, p, len(blob))
                out.append(v)
            return {"kind": "ints", "values": out}
        if kind in (0x12, 0x22):
            fmt = "<%d%s" % (n, "f" if kind == 0x12 else "d")
            size = 4 if kind == 0x12 else 8
            if p + n * size > len(blob):
                return None
            return {"kind": "floats", "values": [round(v, 6) for v in struct.unpack_from(fmt, blob, p)]}
        return None
    return None


def frame_at(row_field_value: Any, blob: bytes) -> dict | None:
    """字段值是 'jump:N' 时解帧。"""
    if isinstance(row_field_value, str) and row_field_value.startswith("jump:"):
        return frame(blob, int(row_field_value[5:]))
    return None


# ── 溯源构造 ────────────────────────────────────────────────────────
def item_provenance(
    *,
    source_id: str,
    lock_sha: str,
    table: str,
    row_key: Any,
    field_refs: list[str],
    name_source: str,
    upstream_role: str,
    entry: dict | None = None,
    cross_source: str | None = None,
    package_sha: str | None = None,
) -> dict:
    """条目级 provenance（门禁要求的字段一次给全）。"""
    out: dict[str, Any] = {
        "source_id": source_id,
        "source_lock_sha256": lock_sha,
        "table": table,
        "row_key": str(row_key),
        "field_refs": list(field_refs),
        "name_source": name_source,
        # package_sha256 = 上游快照标识。本仓库以「源表文件 sha256」为快照口径
        # （树内逐表锁；不是客户端 npk sha，故 meta.notes 会写明口径）。
        "upstream": {"role": upstream_role, "package_sha256": package_sha or lock_sha},
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": cross_source is None,
            "steps": [{
                "kind": "decoded-table-row",
                "source_id": source_id,
                "table": table,
                "row_key": str(row_key),
                "field_refs": list(field_refs),
            }],
        },
    }
    if entry:
        out["source_entries"] = [entry]
    if cross_source:
        # 跨源名/图标挂接：明确标注，不假装是同源字段合并
        out["cross_source_join"] = cross_source
        out["locator_chain"]["no_cross_source_field_join"] = False
    return out


def entry_of(table: dict, role: str) -> dict:
    """解码快照记录（base 表体的 sha/bytes），用于 source_entries。"""
    return {
        "role": role,
        "path_hint": str(table["base"]).replace("\\", "/").split("/")[-1],
        "decoded_sha256": hashlib.sha256(table["body"]).hexdigest(),
        "rows": len(table["rows"]),
    }


def ledger_files() -> list[dict]:
    """还原树合并账本 v2 的 files 记录（一行 = 一个已落盘配置文件）。"""
    raw = LEDGER.read_bytes()
    return json.loads(raw.decode("utf-8")).get("files") or []


def read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def board_path(board_id: str) -> Path:
    return Path(_HERE).parent / "data" / "boards" / f"{board_id}.json"


def old_board(board_id: str) -> dict | None:
    """读「当前板」用于重建比对：先在 boards/，其次在 retired 归档目录。

    2026-11-04 现状：部分板块被 `purge_retired_boards.py` 归档到
    `data/boards/_archive_retired_<日期>/`，比对时要能找回来（只读，不改归档）。
    """
    live = board_path(board_id)
    if live.is_file():
        return read_json(live)
    base = live.parent
    for cand in sorted(base.glob("_archive_retired_*/" + board_id + ".json"), reverse=True):
        return read_json(cand)
    return None


__all__ = [
    "CD", "CACHE", "LEDGER", "SOURCE_TREE", "SOURCE_CACHE",
    "COMMON_ITEM_FID", "COMMON_ITEM_POOL_FID",
    "sha256_of", "lock_of", "paths_of", "body_of", "blob_of",
    "load", "load_cached_table", "common_item",
    "val", "text", "jump_target", "frame", "frame_at",
    "item_provenance", "entry_of", "ledger_files", "read_json", "board_path", "old_board",
]
