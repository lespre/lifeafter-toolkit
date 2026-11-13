#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_lottery_pool_ref_index.py — 奖池引用索引（池号 → 引用它的配置表）

## 为什么需要这个

老板板 `lottery_periods` 的期次时间轴要把「全量池」绑到活动上，就必须知道
**每个池号被哪张配置表引用**。但 11-03 树里的配置表绝大多数是 `<slot_N>` 匿名
字段名（`reward_pool_id` / `lottery_id` 这类语义名只在少数表上存在），
按字段名扫会大面积漏命中 —— 预览板就是因此只有一小部分池能追到来源表。

所以改成**字段名无关**的扫法：把整棵 cdata 树逐表解码，凡是某个整数字段值
落在已知池号集合里，就是一条引用。

## 口径

- 池号集合 = `LOTTERY_POOL_PE1103_v01` 里出现过的全部 pool_key（base + 4 个分服）。
- 引用 = 「表行某字段的整数值 == 池号」，逐行记录 (table, row_key, field)。
- 整数值来自表体行解码，不是字符串匹配；不含任何跨源 join。
- 预筛用 ULEB128 字节序列在 blob 里的存在性，只是为了跳过无关表的解码；
  命中与否以解码后的整数值判定，假阳性在解码阶段被过滤掉。

## 输出

`02_wiki/web/site_data/LOTTERY_POOL_REF_INDEX_v01/`
  · `pool_refs.json`  {pool_key: [{table, row_key, field}, ...]}
  · `manifest.json`   池数 / 命中表数 / 每张命中表的 sha256 / 树路径 / 目标池集合 sha256

用法：
  python 02_wiki/web/tools/build_lottery_pool_ref_index.py            # 预览
  python 02_wiki/web/tools/build_lottery_pool_ref_index.py --apply    # 落盘
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import struct
import sys
from collections import defaultdict

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from la_paths import SOURCE_PKG_ROOT, TOOLKIT_CORE, WEB, rel  # noqa: E402

POOL_DATASET = WEB / "site_data" / "LOTTERY_POOL_PE1103_v01"
OUT_DIR = WEB / "site_data" / "LOTTERY_POOL_REF_INDEX_v01"
TREE_CANDIDATES = (
    SOURCE_PKG_ROOT / "pe_device_20261103" / "cdata" / "com" / "cdata",
    SOURCE_PKG_ROOT / "pe_device_20261103" / "cdata" / "com" / "cdata",
)


def resolve_tree() -> pathlib.Path:
    for c in TREE_CANDIDATES:
        if c.is_dir():
            return c
    raise FileNotFoundError(f"找不到 cdata 树：{TREE_CANDIDATES[0]}")


def body_of(raw: bytes) -> bytes | None:
    at = raw.find(b"x{")
    if at < 0 or len(raw) - at < 10:
        return None
    ln = struct.unpack_from("<I", raw, at + 2)[0]
    if not (0 < ln <= len(raw) - at - 6):
        return None
    return raw[at + 6:at + 6 + ln]


def uleb_bytes(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | 0x80 if n else b)
        if not n:
            return bytes(out)


def sha256_of(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pool_keys() -> set[int]:
    """数据集里出现过的全部池号（base + 分服）。"""
    keys: set[int] = set()
    rows_path = POOL_DATASET / "rows.jsonl"
    with rows_path.open(encoding="utf-8") as f:
        for line in f:
            # 只取 pool_key，避开 json.loads 的全量解析开销
            i = line.find('"pool_key":')
            if i < 0:
                continue
            j = line.find(",", i)
            if j < 0:
                continue
            try:
                keys.add(int(line[i + 11:j]))
            except ValueError:
                continue
    return keys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    tree = resolve_tree()
    keys = load_pool_keys()
    pats = [uleb_bytes(k) for k in sorted(keys)]
    print("池号集合: %d 个（%d~%d）" % (len(keys), min(keys), max(keys)))

    # 延迟导入，避免顶层就吃 toolkit_core
    sys.path.insert(0, str(TOOLKIT_CORE))
    from toolkit_core import bindict_table as BT  # noqa: E402
    from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

    pool_refs: dict[int, list[dict]] = defaultdict(list)
    table_hits: dict[str, dict] = {}
    scanned = 0
    decoded = 0

    for p in sorted(tree.rglob("*.py")):
        if p.name.endswith("_chs.py"):
            continue
        scanned += 1
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        body = body_of(raw)
        if not body or len(body) < 8:
            continue
        try:
            count = struct.unpack_from("<I", body, 0)[0]
        except struct.error:
            continue
        if count <= 0:
            continue
        blob = body[8 + 4 * count:]
        if not blob:
            continue
        # 预筛：任一池号的 ULEB 字节序列出现在「表体任意位置」才解码。
        #   ★ 不能只看 blob 尾部：super_fashion_lottery_conf_data 的 lottery_id
        #     落在行键/槽位区，只筛 blob 会整张表漏掉（391019 / 391024 就是这样漏的）。
        if not any(pat in body for pat in pats):
            continue
        decoded += 1

        chs = p.with_name(p.stem + "_chs.py")
        pool: list = []
        if chs.is_file():
            try:
                pool = BT.parse_legacy_chs_pool(chs.read_bytes())
            except Exception:
                pool = []
        try:
            rows, _u = decode_table_rows_with_chs_slots(body, pool)
        except Exception:
            continue

        relp = p.relative_to(tree).as_posix()
        hit_pool: set[int] = set()

        def walk(v, sink):
            """整数值直接判；列表/字典递归（0x07 数组里的池号也要算引用）。"""
            if isinstance(v, bool):
                return
            if isinstance(v, int):
                if v in keys:
                    sink.add(v)
                return
            if isinstance(v, (list, tuple)):
                for x in v:
                    walk(x, sink)
            elif isinstance(v, dict):
                for x in v.values():
                    walk(x, sink)

        for r in rows:
            for f, v in (r["values"] or {}).items():
                vv = v[1] if isinstance(v, tuple) else v
                hits: set[int] = set()
                walk(vv, hits)
                if not hits:
                    continue
                hit_pool |= hits
                for pk in hits:
                    pool_refs[pk].append({"table": relp, "row_key": r["key"], "field": f})
        if hit_pool:
            # 去重（同一 (table,row_key,field,pool) 只留一条）
            for pk in hit_pool:
                seen = set()
                uniq = []
                for e in pool_refs[pk]:
                    if e["table"] != relp:
                        uniq.append(e)
                        continue
                    k = (e["row_key"], e["field"])
                    if k in seen:
                        continue
                    seen.add(k)
                    uniq.append(e)
                pool_refs[pk] = uniq
            table_hits[relp] = {"sha256": sha256_of(p), "pools": len(hit_pool)}

        if decoded % 200 == 0:
            print("  ... 已解码 %d 张（扫描 %d），命中池 %d" % (decoded, scanned, len(pool_refs)))

    print("扫描表 %d 张，触发解码 %d 张，命中表 %d 张，命中池 %d 个"
          % (scanned, decoded, len(table_hits), len(pool_refs)))

    # 排序，保证输出确定
    out_refs = {str(k): sorted(pool_refs[k], key=lambda e: (e["table"], e["row_key"], e["field"]))
                for k in sorted(pool_refs)}
    key_digest = hashlib.sha256(
        ",".join(str(k) for k in sorted(keys)).encode("utf-8")).hexdigest()

    man = {
        "generator": "02_wiki/web/tools/build_lottery_pool_ref_index.py",
        "generated_at": "2026-11-07",
        "tree": rel(tree),
        "pool_dataset": rel(POOL_DATASET),
        "pool_count": len(keys),
        "pool_keys_sha256": key_digest,
        "tables_scanned": scanned,
        "tables_decoded": decoded,
        "tables_hit": len(table_hits),
        "pools_with_ref": len(out_refs),
        "pools_without_ref": len(keys) - len(out_refs),
        "table_sha256": dict(sorted(table_hits.items())),
        "notes": "字段名无关的池引用扫描：整数值命中即引用，逐行记 (table,row_key,field)。"
                 "预筛仅用 ULEB 字节存在性，真伪由解码后的整数值判定。",
    }

    payload = json.dumps({"meta": man, "pool_refs": out_refs},
                         ensure_ascii=False, indent=1)
    print("产物大小 %.2f MB" % (len(payload.encode("utf-8")) / 1048576))
    if not a.apply:
        print("[预览] 未落盘。加 --apply 写入。")
        return 0
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "pool_refs.json").write_text(payload, encoding="utf-8", newline="\n")
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print("已写入 %s" % rel(OUT_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
