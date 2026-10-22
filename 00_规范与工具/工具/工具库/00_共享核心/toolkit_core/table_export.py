# -*- coding: utf-8 -*-
"""解析结果 → 表格文件 的通用导出器（①-2 的「通用导出器」缺口）。

## 为什么需要

历史上每次要一张表，都得现写一个一次性脚本（`qj_*.py` 之类写了 40+ 个）。
每次都要重新搞清：去哪拿 body、池子怎么解、是哪一族、行怎么落文件。
本模块把这条链固定下来，出口是一条命令，而不是又一份脚本。

## 表族与判据

| 族 | 特征 | 解码入口 |
|---|---|---|
| `hd86` | 含 0x86 detail-row（`optional_hd_exchange_*` 这类商品详情） | `decode_optional_hd_exchange_records` |
| `kj1`  | KJ1 桶表（键是 inline 字符串池 + 桶偏移表） | `decode_kj1_table` |
| `d6`   | 普通 D6/C6/96 基表 | `decode_table_rows` |
| `auto` | 默认：按上面的顺序依次试，谁的产出像行就用谁 | — |

## 输出

`csv`（默认，带表头）/ `json`（保留嵌套）/ `md`（人读用）。

## 不做什么

不改任何源数据；不做「看起来对」的字段命名 —— 列名直接来自解码器给的键，
拿不准就留 `col_<n>`，**不猜**。
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from toolkit_core.bindict_table import (
    decode_kj1_table,
    decode_optional_hd_exchange_records,
    decode_table_rows,
    parse_chs_pool,
    parse_legacy_chs_pool,
)


# ── 池子 ────────────────────────────────────────────────────
def chs_pool_of(body: bytes) -> list[str]:
    """取中文池。两种布局都试，取条数多的那个（少的通常是解歪了）。"""
    got = []
    for fn in (parse_chs_pool, parse_legacy_chs_pool):
        try:
            pool = fn(body)
        except Exception:  # noqa: BLE001
            continue
        if pool and len(pool) > len(got):
            got = pool
    return got


# ── 族判定与解码 ────────────────────────────────────────────
def _looks_like_rows(rows: Any) -> bool:
    return isinstance(rows, list) and bool(rows) and isinstance(rows[0], dict)


def export_body(body: bytes, *, family: str = "auto", resolve_jumps: bool = False) -> dict:
    """把一段表体解成行。返回 {family, rows, unbound, pool_size, tried}。

    ★ 逐个族试、如实记录试过哪些与各自结果 —— 不静默挑一个。
    """
    pool = chs_pool_of(body)
    tried: list[dict] = []
    order = ["hd86", "kj1", "d6"] if family == "auto" else [family]

    for fam in order:
        try:
            if fam == "hd86":
                rows = decode_optional_hd_exchange_records(body)
                unbound: list = []
            elif fam == "kj1":
                rows, unbound = decode_kj1_table(body, pool)
                if not _looks_like_rows(rows) and isinstance(rows, tuple):
                    rows, unbound = rows
            elif fam == "d6":
                rows, unbound = decode_table_rows(body, pool, resolve_jumps=resolve_jumps)
            else:
                raise ValueError(f"未知表族：{fam}")
        except Exception as exc:  # noqa: BLE001
            tried.append({"family": fam, "ok": False, "error": f"{type(exc).__name__}: {exc}"})
            continue
        ok = _looks_like_rows(rows)
        tried.append({"family": fam, "ok": ok, "rows": len(rows) if isinstance(rows, list) else None})
        if ok:
            return {"family": fam, "rows": rows, "unbound": unbound or [],
                    "pool_size": len(pool), "tried": tried}
    return {"family": None, "rows": [], "unbound": [], "pool_size": len(pool), "tried": tried}


def export_entry_bytes(data: bytes, **kw) -> dict:
    """从「条目解码后的完整载荷」导出。

    载荷布局：`... 'x{' <u32 表体长度> <base_body> ...`
    ⇒ 先切出 base_body 再解。切不出就如实说明，不猜别的切法。
    """
    body, how = extract_body(data)
    if body is None:
        return {"family": None, "rows": [], "unbound": [], "pool_size": 0,
                "tried": [{"family": "extract", "ok": False, "error": how}],
                "bytes": len(data), "body": how}
    rep = export_body(body, **kw)
    rep["bytes"] = len(data)
    rep["body"] = how
    return rep


BODY_MAGIC = b"x{"


def extract_body(payload: bytes) -> tuple[bytes | None, str]:
    """从条目载荷切出 base_body。

    ★ 这层包装是实测出来的（tests/test_86_detail_row.py 对真实条目 2949 的用法）：
        x = b.find(b"x{"); ln = u32@(x+2); body = b[x+6 : x+6+ln]
      把它固化到这里，免得每个新表都重推一遍。
    """
    import struct as _s
    x = payload.find(BODY_MAGIC)
    if x < 0:
        return None, "载荷里找不到 'x{' 表体标记"
    if x + 6 > len(payload):
        return None, "表体标记之后不足 6 字节，取不到长度"
    ln = _s.unpack_from("<I", payload, x + 2)[0]
    if x + 6 + ln > len(payload):
        return None, f"声明表体 {ln} B 超出载荷（其后只剩 {len(payload) - x - 6} B）"
    return payload[x + 6: x + 6 + ln], "表体标记偏移 %d，表体 %d B" % (x, ln)


# ── 落文件 ──────────────────────────────────────────────────
def _flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return " | ".join(_flatten(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _columns(rows: list[dict]) -> list[str]:
    cols: list[str] = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    # 稳定：标量列在前，嵌套在后，各自按首次出现顺序
    scalar = [c for c in cols if not any(isinstance(r.get(c), (dict, list)) for r in rows)]
    nested = [c for c in cols if c not in scalar]
    return scalar + nested


def render(rows: list[dict], fmt: str = "csv") -> str:
    """把行渲染成文本。列名直接来自解码器，不重命名、不猜。"""
    fmt = (fmt or "csv").lower()
    if fmt == "json":
        return json.dumps(rows, ensure_ascii=False, indent=1)
    if fmt == "md":
        cols = _columns(rows)
        out = io.StringIO()
        out.write("| " + " | ".join(cols) + " |\n")
        out.write("|" + "|".join("---" for _ in cols) + "|\n")
        for r in rows:
            out.write("| " + " | ".join(_flatten(r.get(c)).replace("|", "\\|") for c in cols) + " |\n")
        return out.getvalue()
    # csv
    cols = _columns(rows)
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(cols)
    for r in rows:
        w.writerow([_flatten(r.get(c)) for c in cols])
    return out.getvalue()


def write_table(rows: list[dict], out_path: Path | str, fmt: str = "csv") -> Path:
    p = Path(out_path)
    if p.suffix and fmt == "csv":
        fmt = p.suffix.lstrip(".").lower()
    text = render(rows, fmt)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8-sig" if fmt == "csv" else "utf-8")
    return p


def human_summary(rep: dict) -> str:
    """给命令输出用的一行摘要（如实在失败时说清试过什么）。"""
    if rep.get("family"):
        return (f"表族 {rep['family']}：{len(rep['rows'])} 行"
                f"，中文池 {rep.get('pool_size', 0)} 条"
                + (f"，未绑定 {len(rep['unbound'])} 条" if rep.get("unbound") else ""))
    tried = "；".join(f"{t['family']}={t.get('error') or '无行'}" for t in rep.get("tried", []))
    return f"三种表族都解不出行（试过：{tried}）"


if __name__ == "__main__":
    import sys
    for path in sys.argv[1:]:
        data = Path(path).read_bytes()
        rep = export_entry_bytes(data)
        print(f"  {path}: {human_summary(rep)}")
        for t in rep.get("tried", []):
            print("    ·", t)
