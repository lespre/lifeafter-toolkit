# -*- coding: utf-8 -*-
r"""prune_stale_row_keys.py — 清理板上「源表已不存在」的行键

## 背景

热更后源表行会**被删或重排**，板上仍留着旧行键。这些失效键不影响页面显示，
但会让溯源统计（行键数 / 覆盖表数）偏大，人工核对时也对不上源表。

本工具按 `provenance.table` 定位还原树里的源表，实际解码出该表**当前**的
全部行键集合，板上凡是不在集合里的行键一律判为失效，并按保守策略清理。

## ★ 行键集合必须用「完整行集」（lenient）

`decode_table_rows(..., lenient=False)` 是**严格值解码**：值流没走完、行尾是
`inline list variant` 的行会**整行丢弃**（进 unbound）。这些行的**行键在索引里
本来就有**，只是值解不全 —— 用严格行集去比对，会把大批「活着的行」误判成失效。

实测（2026-11-01，fashion_wardrobe）：
- `fashion_data` 严格 10,933 行 / 丢弃 236 行 / 完整 11,169 行
- `player_appear_data` 严格 5,367 行 / 丢弃 237 行 / 完整 5,604 行
- 被丢弃行的 `show_name` / `desc` 与卡片名字对得上（fd 227/233、pa 58/58），
  说明**行是真存在的**；严格集里恰好「少」这些键，于是凭空产生 304 个
  "失效键"假象。

因此默认 `lenient=True`（= 严格行 + unbound 行 = 索引里的全部行键）。
`--strict` 仅用于**对照复现**，且**禁止写盘**。

## 清理策略（只动行键相关字段）

| 位置 | 处理 |
|---|---|
| `items[].row_keys` | 剔除失效键 |
| `items[].provenance.row_keys` | 剔除失效键 |
| `items[].provenance.row_key` | **不删字段**，保留原值；在卡片上写 `stale_row_key` 记录原值，并在 `source` 末尾追加一句说明 |
| `items[].row_variants` | 移除失效的行条目（元素是 dict 时取 `row_key`，否则元素本身即行键） |

**绝对不动**：`durations` / `has_permanent` / `duration_state` / `name` / `part` /
`desc` / 图标相关字段（`icon_state` / `icons_all` / `_media` …）以及其它一切字段。

`row_keys` 清理后变空的卡**不删卡**，在报告里单列（这是需要人工判断的信号）。

## 幂等

- 同一输入重跑，产物字节不变：
  - 已记录过 `stale_row_key` 的卡不再重复改写 `source`；
  - `meta.notes` 只在本次**确有清理动作**时用 `notes_util.append_note()` 幂等追加
    （无动作则不碰 notes，避免计数变化导致 notes 反复改）；
  - 无失效键时**完全不写盘**。
- 输出统一走 `board_io.write_board_pair()`：`.json` 与同名 `.js` 同步写，
  UTF-8 + LF。

## 安全

- 源表**只**从还原树 `01_索引与产物/41_还原树/pe/配置/com/cdata` 解码，
  不扫客户端 npk。
- 某张卡的表在还原树里找不到 / 解码失败 → **整表跳过**并在报告里列出，
  绝不臆造行键集合去误删。

## 用法

```bash
# 预演（默认就是 dry-run，不写盘）
python 02_wiki/web/tools/prune_stale_row_keys.py
python 02_wiki/web/tools/prune_stale_row_keys.py --dry

# 落盘（写 .json + .js）
python 02_wiki/web/tools/prune_stale_row_keys.py --apply

# 对照：用严格值解码的行集再看一遍（只统计，永远不会写盘）
python 02_wiki/web/tools/prune_stale_row_keys.py --strict

# 附带机读报告
python 02_wiki/web/tools/prune_stale_row_keys.py --apply --report 90_临时/prune.json
```

退出码：0 正常；1 板不存在；2 有整表被跳过（数据不完整，需人工确认）；
3 用了 `--strict`（对照模式，不写盘）。
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

SHARED = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
if SHARED.exists():
    sys.path.insert(0, str(SHARED))

from board_io import write_board_pair  # noqa: E402
from notes_util import append_note  # noqa: E402

from toolkit_core import bindict_table as BT  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
DEFAULT_BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"


# ---------------------------------------------------------------- 基础工具


def md5_of(path: pathlib.Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_table(value) -> str:
    """`com\\cdata\\fashion_data.py` / `player_module_appear_data` → 表名（无目录无后缀）。"""
    s = str(value or "").strip().replace("\\", "/")
    if not s:
        return ""
    s = s.rsplit("/", 1)[-1]
    if s.endswith(".py"):
        s = s[:-3]
    return s


def canon_key(value):
    """行键归一：数字串 → int，其余去空白后保留原样。用于跨 int/str 比较。"""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if not s:
        return s
    try:
        return int(s)
    except ValueError:
        return s


def load_table_keys(name: str, lenient: bool = True) -> dict:
    """解码 legacy 0x73 表，返回当前全部行键集合及其解码统计。

    lenient=True（默认）→ 严格行 + unbound 行 = 索引里的全部行键（完整行集）。
    lenient=False → 严格值解码行集（会漏掉行尾 inline list variant 的行）。
    """
    py = CD / f"{name}.py"
    chs = CD / f"{name}_chs.py"
    if not py.exists():
        raise FileNotFoundError(f"源表不存在：{py}")
    raw = py.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        raise ValueError(f"{name}.py 未找到 body 头 'x{{'")
    length = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6:at + 6 + length]
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else {}
    rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=lenient)
    keys = {canon_key(r["key"]) for r in rows if r.get("key") is not None}
    return {"keys": keys, "rows": len(rows), "unbound": len(unbound), "mode": lenient}


# ---------------------------------------------------------------- 清理主逻辑


def variant_key(entry):
    """row_variants 元素可能是 dict（取 row_key）或裸行键。"""
    if isinstance(entry, dict):
        return entry.get("row_key")
    return entry


def prune(board: dict, tables_cache: dict, lenient: bool = True) -> dict:
    """就地清理 board，返回统计。"""
    stat = {
        "cards_changed": 0,
        "keys_removed": 0,          # 从 row_keys / provenance.row_keys / row_variants 剔除
        "keys_recorded": 0,         # provenance.row_key 失效、保留原值并记 stale_row_key
        "by_table": collections.Counter(),
        "distinct_keys": set(),
        "emptied": [],
        "already_recorded": 0,
        "skipped": collections.Counter(),
        "changed_cards": [],
    }

    for item in board.get("items") or []:
        prov = item.get("provenance")
        if not isinstance(prov, dict):
            stat["skipped"]["<无 provenance>"] += 1
            continue

        table = norm_table(prov.get("table"))
        if not table:
            stat["skipped"]["<无表名>"] += 1
            continue
        if table not in tables_cache:
            try:
                tables_cache[table] = load_table_keys(table, lenient=lenient)
            except Exception as exc:  # 找不到证据就不动
                tables_cache[table] = None
                stat["skipped"][f"{table}（{exc}）"] += 1
                continue
        info = tables_cache[table]
        if info is None:
            stat["skipped"][table] += 1
            continue
        keys = info["keys"]

        changed = False
        card_keys = []

        # 1) items[].row_keys
        row_keys = item.get("row_keys")
        if isinstance(row_keys, list):
            kept = [k for k in row_keys if canon_key(k) in keys]
            dropped = [k for k in row_keys if canon_key(k) not in keys]
            if dropped:
                item["row_keys"] = kept
                changed = True
                stat["keys_removed"] += len(dropped)
                stat["by_table"][table] += len(dropped)
                card_keys.extend(dropped)

        # 2) provenance.row_keys
        p_row_keys = prov.get("row_keys")
        if isinstance(p_row_keys, list):
            kept = [k for k in p_row_keys if canon_key(k) in keys]
            dropped = [k for k in p_row_keys if canon_key(k) not in keys]
            if dropped:
                prov["row_keys"] = kept
                changed = True
                stat["keys_removed"] += len(dropped)
                stat["by_table"][table] += len(dropped)
                card_keys.extend(dropped)

        # 3) provenance.row_key —— 保留原值，另记 stale_row_key
        p_key = prov.get("row_key")
        if p_key is not None and canon_key(p_key) not in keys:
            if item.get("stale_row_key") == p_key:
                stat["already_recorded"] += 1
            else:
                item["stale_row_key"] = p_key
                # 有剩余行键才说「按剩余行键重建」；一个不剩就如实说保留原值，
                # 不写「已重建」这种没有证据的话。
                survivors = bool(item.get("row_keys")) or bool(prov.get("row_keys"))
                if survivors:
                    sentence = f"原行键 {p_key} 在热更后已不存在，已按剩余行键重建"
                else:
                    sentence = (f"原行键 {p_key} 在热更后已不存在"
                                f"（已无其余行键，保留原值供人工复核）")
                src = item.get("source")
                if isinstance(src, str) and src.strip():
                    if sentence not in src:
                        item["source"] = src.rstrip("；;。 ") + "；" + sentence
                elif src is None:
                    item["source"] = sentence
                changed = True
                stat["keys_recorded"] += 1
                stat["by_table"][table] += 1
                card_keys.append(p_key)

        # 4) row_variants —— 移除失效条目
        variants = item.get("row_variants")
        if isinstance(variants, list) and variants:
            kept, dropped = [], []
            for entry in variants:
                k = variant_key(entry)
                (kept if canon_key(k) in keys else dropped).append(entry)
            if dropped:
                item["row_variants"] = kept
                changed = True
                stat["keys_removed"] += len(dropped)
                stat["by_table"][table] += len(dropped)
                card_keys.extend(variant_key(e) for e in dropped)

        if changed:
            stat["cards_changed"] += 1
            stat["changed_cards"].append({"id": item.get("id"), "name": item.get("name"),
                                          "table": table, "keys": card_keys})
            stat["distinct_keys"].update(canon_key(k) for k in card_keys)

        # 5) 变空检测：清理后 row_keys 为空的卡一律上报（需人工判断）
        if isinstance(item.get("row_keys"), list) and not item["row_keys"]:
            stat["emptied"].append({"id": item.get("id"), "name": item.get("name"),
                                    "table": table,
                                    "was": row_keys if isinstance(row_keys, list) else None})

    return stat


def build_note(stat: dict) -> str:
    total = stat["keys_removed"] + stat["keys_recorded"]
    tables = " / ".join(f"{t}（{n}）" for t, n in stat["by_table"].most_common())
    return (f"行键复核：清理了 {stat['cards_changed']} 张卡的 {total} 个失效行键"
            f"（热更后源表行已删/重排），涉及表 {tables or '无'}；"
            f"原行键失效的卡保留 provenance.row_key 原值并记 stale_row_key；"
            f"未改动时限与归属字段")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="清理板上引用了源表已不存在行的行键（默认 dry-run）")
    ap.add_argument("--apply", action="store_true", help="真正写盘（.json + 同名 .js）")
    ap.add_argument("--dry", action="store_true", help="只统计不写盘（默认行为）")
    ap.add_argument("--strict", action="store_true",
                    help="对照模式：用严格值解码的行集比对（会误判，仅统计，永不写盘）")
    ap.add_argument("--board", default=str(DEFAULT_BOARD), help="板 json 路径")
    ap.add_argument("--report", default="", help="另存一份机读 JSON 统计")
    args = ap.parse_args(argv)

    board_path = pathlib.Path(args.board)
    if not board_path.is_absolute():
        board_path = PROJ / board_path
    if not board_path.exists():
        print(f"[ERR] 板不存在：{board_path}")
        return 1

    lenient = not args.strict
    md5_before = md5_of(board_path)
    board = json.loads(board_path.read_text(encoding="utf-8-sig"))

    tables_cache: dict = {}
    stat = prune(board, tables_cache, lenient=lenient)
    cards_total = len(board.get("items") or [])

    total = stat["keys_removed"] + stat["keys_recorded"]
    try:
        shown = board_path.relative_to(PROJ)
    except ValueError:
        shown = board_path
    print(f"板：{shown}")
    print(f"  行键集合口径        {'完整行集（严格行+unbound 行）' if lenient else '严格值解码行集（对照用）'}")
    print(f"  卡片总数            {cards_total}")
    print(f"  受影响卡片          {stat['cards_changed']}")
    print(f"  失效行键（总处数）  {total}"
          f"    其中 剔除 {stat['keys_removed']} / 保留并记 stale_row_key {stat['keys_recorded']}")
    print(f"  失效行键（去重）    {len(stat['distinct_keys'])}")
    if stat["already_recorded"]:
        print(f"  已记录过 stale_row_key 的卡  {stat['already_recorded']}（幂等跳过改写 source）")
    print("  源表解码：")
    for t, info in sorted(tables_cache.items()):
        if info is None:
            continue
        print(f"    {t:<40} 行 {info['rows']:<6} 丢弃(unbound) {info['unbound']:<4} 行键 {len(info['keys'])}")
    if stat["by_table"]:
        print("  失效键按表分组：")
        for t, n in stat["by_table"].most_common():
            print(f"    {t:<40} {n}")
    if stat["skipped"]:
        print("  【跳过】以下表无法解码，整表未动：")
        for t, n in stat["skipped"].items():
            print(f"    {t}  （卡 {n}）")

    if stat["emptied"]:
        print(f"  【需人工判断】row_keys 为空的卡 {len(stat['emptied'])} 张：")
        for e in stat["emptied"]:
            print(f"    {e['id']}  {e['name']}   表={e['table']}  原 row_keys={e['was']}")
    else:
        print("  row_keys 为空的卡：无")

    if not lenient:
        print("\n[strict] 对照模式：以上失效键多为「值解码被丢弃但行仍在」的假阳性，"
              "本模式永不写盘。")
        if args.report:
            _write_report(args.report, stat, cards_total, md5_before, None, applied=False)
        return 2 if stat["skipped"] else 3

    if not args.apply or args.dry:
        print("\n[dry-run] 未写盘。确认无误后加 --apply。")
        if stat["changed_cards"]:
            print("  受影响卡片前 10 张：")
            for c in stat["changed_cards"][:10]:
                print(f"    {c['id']}  {c['name']}  {c['keys']}")
        if args.report:
            _write_report(args.report, stat, cards_total, md5_before, None, applied=False)
        return 2 if stat["skipped"] else 0

    if total == 0:
        print("\n[apply] 没有需要清理的行键，未写盘（幂等：字节不变）。")
        print(f"  md5(json) = {md5_before}")
        if args.report:
            _write_report(args.report, stat, cards_total, md5_before, md5_before, applied=False)
        return 2 if stat["skipped"] else 0

    append_note(board, build_note(stat))
    write_board_pair(board_path, board)

    md5_after = md5_of(board_path)
    print(f"\n[apply] 已写盘：{board_path.name} + {board_path.with_suffix('.js').name}")
    print(f"  md5(json) {md5_before} → {md5_after}")
    if args.report:
        _write_report(args.report, stat, cards_total, md5_before, md5_after, applied=True)
    return 2 if stat["skipped"] else 0


def _write_report(path: str, stat: dict, cards_total: int, md5_before: str,
                  md5_after, applied: bool) -> None:
    p = pathlib.Path(path)
    if not p.is_absolute():
        p = PROJ / p
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "md5_before": md5_before,
        "md5_after": md5_after,
        "applied": applied,
        "cards_total": cards_total,
        "cards_changed": stat["cards_changed"],
        "keys_removed": stat["keys_removed"],
        "keys_recorded": stat["keys_recorded"],
        "keys_total": stat["keys_removed"] + stat["keys_recorded"],
        "distinct_keys": len(stat["distinct_keys"]),
        "by_table": dict(stat["by_table"].most_common()),
        "skipped": dict(stat["skipped"]),
        "emptied": stat["emptied"],
        "changed_cards": stat["changed_cards"],
    }
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  报告：{p}")


if __name__ == "__main__":
    raise SystemExit(main())
