# -*- coding: utf-8 -*-
r"""解码_0x73.py — 把 `0x73` 包装的 bindict 表导出成 JSON / TSV。

用法
    python 解码_0x73.py <表.py> [--chs 表_chs.py] [-o 输出目录]
                        [--format json,tsv] [--name 前缀] [--quiet]

例
    python 解码_0x73.py \
      "E:/la拆包项目/01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata/weapon_skin_data.py" \
      -o "E:/la拆包项目/01_索引与产物/30_分析/热更检测/task_0x73_decode"

输出（--name 默认取输入文件名去扩展名）
    <name>.json        全表：meta + rows（含字段类型）
    <name>.tsv         一行一 key，列 = schema 字段顺序
    <name>.meta.json   仅自检元信息（容器/表体/索引/统计）
退出码
    0 成功；2 载荷不是 0x73 表；3 有行解不出（仍会写文件）
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _cand in (_HERE.parents[1], _HERE.parents[2]):
    if (_cand / "toolkit_core").is_dir() and str(_cand) not in sys.path:
        sys.path.insert(0, str(_cand))

from toolkit_core import bindict_table as BT          # noqa: E402
from toolkit_core.bindict_73 import (                 # noqa: E402
    Bindict73Error,
    decode_73_table,
    extract_body,
)

DEFAULT_OUT = Path(r"E:/la拆包项目/01_索引与产物/30_分析/热更检测/task_0x73_decode")


def field_order(body: bytes, rows: list[dict], pool: list[str]) -> list[str]:
    """按 schema 声明顺序取列名；拿不到就按出现顺序兜底。"""
    count = int.from_bytes(body[:4], "little")
    blob_off = 8 + 4 * count
    for row in rows:
        schema_ref = row.get("schema")
        if schema_ref is None:
            continue
        try:
            blob = body[blob_off:]
            _bits, fields, _end = BT._schema_at(blob, schema_ref, pool)   # noqa: SLF001
            names = [name for _slot, _t, name in fields]
            if names:
                return names
        except Exception:            # noqa: BLE001 — 兜底即可
            break
    seen: list[str] = []
    for row in rows:
        for name in row.get("values") or {}:
            if name not in seen:
                seen.append(name)
    return seen


def _plain(value):
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    return value


def export(path: Path, outdir: Path, name: str, fmt: set[str], chs: Path | None) -> int:
    rows, unbound, meta = decode_73_table(path, chs=chs)
    body, _cm = extract_body(path)

    from toolkit_core.bindict_73 import load_pool_for
    pool = load_pool_for(chs or path)

    cols = field_order(body, rows, pool)

    if "json" in fmt:
        payload = {
            "meta": meta,
            "columns": cols,
            "rows": [
                {
                    "key": r["key"],
                    "start": r.get("start"),
                    "marker": r.get("marker"),
                    "schema": r.get("schema"),
                    "bitmap": r.get("bitmap"),
                    "values": {n: _plain(v[1]) for n, v in (r.get("values") or {}).items()},
                    "types": {n: v[0] for n, v in (r.get("values") or {}).items()},
                    "inline_groups": _plain(r.get("inline_groups") or []),
                    "tail": r.get("tail") or "",
                }
                for r in rows
            ],
            "unbound": unbound,
        }
        (outdir / f"{name}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    if "tsv" in fmt:
        lines = ["key\t" + "\t".join(cols) + "\tinline_groups"]
        for r in rows:
            vals = r.get("values") or {}
            cells = []
            for c in cols:
                v = vals.get(c)
                cell = "" if v is None else v[1]
                if isinstance(cell, float):
                    cell = repr(cell)
                cells.append(str(cell).replace("\t", " ").replace("\n", " "))
            groups = json.dumps(_plain(r.get("inline_groups") or []), ensure_ascii=False,
                                separators=(",", ":"))
            lines.append(f"{r['key']}\t" + "\t".join(cells) + f"\t{groups}")
        (outdir / f"{name}.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    (outdir / f"{name}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")

    c = meta["container"]
    b = meta["body"]
    i = meta["index"]
    print(f"[ok] {path.name}")
    print(f"     容器 {c['kind']}  载荷 @{c['payload_off']}+{c['payload_len']}  ({c['payload_tag']})")
    print(f"     表体 count={b['count']} reserved={b['reserved']} ends_all_zero={b['ends_all_zero']} "
          f"de={b['de']} blob_off={b['blob_off']}")
    print(f"     索引 {i['tag']} 桶数={i['bucket_count']}({i['bucket_count_encoding']}) "
          f"节点={i['node_records']} 桶偏移指向节点首字节={i['bucket_offsets_are_node_starts']}")
    print(f"     行 {meta['rows']['decoded']} 条，unbound={meta['rows']['unbound']}，"
          f"key {meta['rows']['key_min']}..{meta['rows']['key_max']}，"
          f"pool={meta['pool_size']}（与 count 一致={meta['pool_matches_count']}）")
    if meta["warnings"]:
        for w in meta["warnings"]:
            print(f"     [warn] {w}")
    print(f"     → {outdir}")
    return 0 if not unbound else 3


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="解 0x73 包装的 bindict 表并导出 JSON/TSV")
    ap.add_argument("input", type=Path, help="`*_data.py`（0x73 容器）或裸表体")
    ap.add_argument("--chs", type=Path, default=None, help="配对 `*_data_chs.py`（默认按文件名自动找）")
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT, help="输出目录")
    ap.add_argument("--format", default="json,tsv", help="json,tsv（默认两者）")
    ap.add_argument("--name", default=None, help="输出文件名前缀（默认输入文件名去扩展名）")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    fmt = {x.strip().lower() for x in args.format.split(",") if x.strip()}
    bad = fmt - {"json", "tsv"}
    if bad:
        ap.error("未知格式：%s" % ",".join(sorted(bad)))
    args.out.mkdir(parents=True, exist_ok=True)
    name = args.name or args.input.stem

    try:
        rc = export(args.input, args.out, name, fmt, args.chs)
    except Bindict73Error as exc:
        print(f"[fail] 不是可解的 0x73 bindict 表：{exc}", file=sys.stderr)
        return 2
    if not args.quiet:
        print("     输出：" + ", ".join(f"{name}.{e}" for e in sorted(fmt)) + f", {name}.meta.json")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
