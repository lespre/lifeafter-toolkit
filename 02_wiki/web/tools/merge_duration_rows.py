# -*- coding: utf-8 -*-
r"""把「源表里有、但没并进卡」的**同名字时限变体行**合并进已有卡（幂等）。

背景：`fashion_data` 在 10-30 热更后新增了一批行（键段 6372xxxxx），名字形如
`琳夜柔歌-头饰-14天`。板的 rebuild 是 10-24 做的，这批行没被并进对应卡的
`row_keys / durations`，于是页面上该件的「可选时限」少了几档 —— 卡不是丢了，是**档位少了**。

做法（只做这一件事，不动名字/部位/图标）：
  1. 扫 fashion_data 全部行，凡是没被任何卡的 row_keys 引用、且
     「去尾部 -N天 / 去部位后缀」后能对上板上某张卡的名字 → 视为该卡的变体行；
  2. 把行键并入卡的 row_keys / provenance.row_keys，重算
     durations / duration_variants / time_limited_variants / has_permanent / duration_state；
  3. 不新增卡、不改归属、不动图标与描述。

幂等：已并入的行不会再被选中；重跑字节不变。
用法：python 02_wiki/web/tools/merge_duration_rows.py [--dry]
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

SHARED = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
sys.path.insert(0, str(SHARED))

from board_io import write_board_pair  # noqa: E402
import notes_util  # noqa: E402
from toolkit_core import bindict_table as BT  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
TBL = "fashion_data"
PARTS = ("头饰", "面饰", "衣服", "背包", "头发", "整套", "挂饰", "投影", "戒指")

DUR = re.compile(r"\s*[-－]\s*(\d+)\s*天\s*$")
PARTSUF = re.compile(r"\s*[-－]\s*(?:" + "|".join(PARTS) + r")\s*$")


def load(name: str) -> dict:
    raw = (CD / f"{name}.py").read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    pool = BT.parse_legacy_chs_pool((CD / f"{name}_chs.py").read_bytes())
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)
    out = {}
    for r in rows:
        v = {k: (vv[1] if isinstance(vv, tuple) else vv) for k, vv in r["values"].items()}
        try:
            out[int(r.get("key"))] = v
        except (TypeError, ValueError):
            pass
    return out


def base_of(name) -> str:
    t = str(name or "").strip().replace("（", "(").replace("）", ")")
    for _ in range(3):
        t2 = DUR.sub("", t)
        if t2 == t:
            break
        t = t2
    return PARTSUF.sub("", t).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    src = load(TBL)

    used: set[int] = set()
    for it in items:
        prov = it.get("provenance") or {}
        tbl = str(prov.get("table") or "").replace("\\", "/").rsplit("/", 1)[-1].replace(".py", "")
        if tbl != TBL:
            continue
        for k in list(it.get("row_keys") or []) + list(prov.get("row_keys") or []):
            try:
                used.add(int(k))
            except (TypeError, ValueError):
                pass
        if prov.get("row_key") is not None:
            try:
                used.add(int(prov["row_key"]))
            except (TypeError, ValueError):
                pass

    # 卡（只看 fashion_data 起家的卡）按 base 名索引
    card_by_base = collections.defaultdict(list)
    for it in items:
        prov = it.get("provenance") or {}
        tbl = str(prov.get("table") or "").replace("\\", "/").rsplit("/", 1)[-1].replace(".py", "")
        if tbl != TBL:
            continue
        card_by_base[base_of(it.get("name"))].append(it)
        card_by_base[str(it.get("name") or "")].append(it)

    plan: dict[str, list[tuple[int, dict]]] = collections.defaultdict(list)
    for k, v in src.items():
        if k in used:
            continue
        b = base_of(v.get("name"))
        if b in card_by_base:
            plan[b].append((k, v))

    total = sum(len(x) for x in plan.values())
    print("未引用且能对上卡的变体行：%d 行 / %d 张卡" % (total, len(plan)))
    for b, kv in sorted(plan.items(), key=lambda x: -len(x[1])):
        print("  %-16s +%d 行 %s" % (b, len(kv), [k for k, _ in kv][:8]))

    # ★ 不在这里提前 return：即使没有新行要并，也要走下面的「时限档位重算」，
    #   否则修正 valid_days 类型坑的那一轮永远跑不到。
    if not plan:
        print("没有需要新并入的变体行；继续做时限档位重算。")
    if a.dry:
        print("（--dry：未写盘）")
        return 0

    changed = 0
    merged_rows = 0
    touched: list[dict] = []
    touched_ids: set[str] = set()
    for b, kv in plan.items():
        for it in card_by_base[b]:
            prov = it.setdefault("provenance", {})
            rks = {int(x) for x in (it.get("row_keys") or [])}
            rks |= {int(x) for x in (prov.get("row_keys") or [])}
            add = {k for k, _ in kv} - rks
            if not add:
                continue
            if it["id"] not in touched_ids:
                touched_ids.add(it["id"])
                touched.append(it)
            # 合并并统一按行键升序（原顺序 = 基行在前，这里改为数值序，保证幂等）
            allk = sorted(rks | add)
            if int(prov.get("row_key")) in allk:
                allk.remove(int(prov["row_key"]))
            allk = [int(prov["row_key"])] + allk
            it["row_keys"] = allk
            prov["row_keys"] = list(allk)
            merged_rows += len(add)
            changed += 1

    # ── 只给「本次真的并了行」的卡重算时限档位 ──────────────────────
    # ★★ 千万不要对所有 fashion_data 卡重算：板上的 durations **不是**只由 row_keys 推出来的
    #    （还有没并入 row_keys 的变体行），全量重算会把档位抹掉 —— 实测抹坏 451 张
    #    （三载之伴-头饰 30天→空、ERP异能研析-衣服 丢 1 天）。
    #    `valid_days` 在表里 int / 字符串混用，这里统一 int() 强转，别再 isinstance 过滤。
    fixed = 0
    for it in touched:
        rows = [src[k] for k in sorted({int(x) for x in (it.get("row_keys") or [])
                                        if str(x).lstrip("-").isdigit()}) if k in src]
        if not rows:
            continue
        days = set()
        for r in rows:
            dv = r.get("valid_days")
            if dv in (None, ""):
                continue
            try:
                days.add(int(dv))
            except (TypeError, ValueError):
                pass
        days = sorted(days)
        has_perm = any((r.get("valid_days") in (None, "")) for r in rows)
        state = "mixed" if (days and has_perm) else ("timed" if days else "permanent")
        it["durations"] = days
        it["duration_variants"] = days
        it["time_limited_variants"] = days
        it["has_permanent"] = has_perm
        it["duration_state"] = state
        fixed += 1

    if not changed and not fixed:
        print("无缺口，无需合并。")
        return 0

    note = ("%s 热更后新增的同名时限变体行已并入对应卡（只补 row_keys 与时限档位，不新增卡、不改归属）："
            "新并入 %d 行 / %d 张卡；另按 row_keys 重算时限档位 %d 张卡。"
            % (TBL, merged_rows, changed, fixed))
    notes_util.append_note(board, note)
    write_board_pair(BOARD, board)
    print("已合并 %d 行 / %d 张卡；重算时限 %d 张卡" % (merged_rows, changed, fixed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
