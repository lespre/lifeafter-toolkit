# -*- coding: utf-8 -*-
r"""展示大奖 id → 名字：**直解树里承载名字的表**（补 结构产物 CSV 只覆盖 180 张的缺口）。

## 为什么单开

`lottery chain` 原来只从 `表结构解析_*/结构/*.rows.csv`（180 张）回填名字。
而奖池的「展示大奖」大量落在 CSV 没覆盖的表里，于是永远报「缺口」：
  · `player_module_appear_data`（头饰/挂件/面部外观）——★ 741470120 星穹环冕 就在这里
  · `weapon_skin_data`（**无 name 字段** —— 武器皮肤名要另找）
  · `fashion_data` / `gift_data` / `vehicle_ui_data` …
用户口径：「这几个玩意早就热更来了，肯定是你方法还有问题」—— 对：不是数据没有，
是**名字源只认 CSV 那 180 张**。

## 口径

    名字来源优先级（apply_names 里串）：csv 结构产物 > 本模块（表直解）> ns 索引 > common_item(ok)

★ 只收「按值命中行」的名字：行 key == id 且该行有 name 字段。
★ 不做跨表撞车兜底：一个 id 在两张表里都有名字时，全部列出（带表名），不猜哪个对。
"""
from __future__ import annotations

import json
import struct
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

#: 承载名字的候选表 → 取值规则
#:  字段元组 = 按序取第一个非空字段
#:  ⭐ 冒号后的 `index_by` = **按哪个字段当键**（None/缺省 = 按行 key）。
#:    为什么需要：`weapon_skin_sfx_function_data` 的行 key 是特效行号（1120360），
#:    而皮肤 id 在 `skin_id` 字段里 —— 不按字段取键就永远查不到「斩神-星辰刀」。
NAME_TABLES: Dict[str, Tuple] = {
    "player_module_appear_data": ("name",),
    "fashion_data": ("name",),
    "gift_data": ("name",),
    "vehicle_ui_data": ("name",),
    "box_data": ("name",),
    # ★ 2026-09-30 加（实测：奖池「展示道具」9 件里有 4 件只在这几张表里有名字）：
    "daily_items_limit_alarm_data": ("desc",),            # 异变核芯-贯通战术 / 余烬流火
    "body_sfx_data": ("buff_item_name",),                 # 星月华章
    "weapon_skin_sfx_function_data": ("sfx_name", "skin_id"),   # 斩神-星辰刀（按 skin_id 取键）
}
#: 备选名字字段（按序取第一个非空）
NAME_FIELDS = ("name", "name_chs", "item_name", "cn_name", "title", "label")
#: ★ 占位/噪声名（不能当名字用）。实测：皮肤 1110185 在特效表里的 `sfx_name` 是「真实」——
#:   那是特效占位词，不是展示名；照收会让用户以为解出来了（宁缺勿假）。
PLACEHOLDER_NAMES = {"真实", "测试", "临时", "占位", "未使用", "test", "dummy", "none", "null"}


def _paths():
    from toolkit_core import paths as P
    return P


def tree_cdata() -> Path:
    """`com\\cdata` 目录（★ 新层级优先；老铺法兜底）。

    ★ 对标 E:\\mrzh 后 cdata 表**每容器一份** ⇒ 凡「只取一个目录」都不可靠；
      要扫全量用 `table_locator.cdata_dirs()`，要取某张表用 `best_table_path()`。
    """
    try:
        from toolkit_core import table_locator as _TL
        dirs = _TL.cdata_dirs()
        if dirs:
            return dirs[0]
    except Exception:                                      # noqa: BLE001
        pass
    return _paths().cdata_dir()


def index_path() -> Path:
    return _paths().INDEX_ROOT / "items" / "show_item_names.json"


def _mods():
    from toolkit_core import lottery_chain as LC
    return LC._mods()


def _frame(path: Path, min_len: int = 256):
    b = path.read_bytes()
    best = None
    i = 0
    while True:
        j = b.find(b"x{", i)
        if j < 0:
            break
        i = j + 1
        if j + 10 > len(b):
            continue
        ln = struct.unpack_from("<I", b, j + 2)[0]
        if ln < min_len or j + 6 + ln > len(b):
            continue
        if best is None or ln > best[1]:
            best = (j, ln)
    return best, b


def scan_table(short: str) -> Dict[int, str]:
    """解一张名字表 → {行key: 名字}。解不出就返回空（不猜）。

    ★ 2026-09-30：**走 `table_locator`**（按 fid 定位 + overlay/Documents 副本优先）
      —— 别再用「树里的路径」直接取：同名表有多副本且内容不同，
      路径取到的那份**可能就是底座**（热更新增的行全没有）。
    """
    from toolkit_core import table_locator as TL
    p = None
    got = TL.best_path_for_fid(TL.fid_of_path("com\\cdata\\" + (short if short.endswith(".py")
                                                               else short + ".py"))
                               or "", name_hint=short)
    if got:
        p = got[0]
    if p is None:                         # 兜底：老口径（同目录按名取）
        cd = tree_cdata()
        cand = cd / (short if short.endswith(".py") else short + ".py")
        if cand.is_file():
            p = cand
    if p is None:
        return {}
    chs = p.with_name(p.stem + "_chs.py")
    M = _mods()
    fr, b = _frame(p)
    if not fr:
        return {}
    pool = M["MP"].pool_of_file(str(chs)) if chs.is_file() else []
    body = b[fr[0] + 6: fr[0] + 6 + fr[1]]
    try:
        rows, _u = M["BP"].decode_table_rows_with_chs_slots(body, pool)
    except Exception:                                               # noqa: BLE001
        return {}
    out: Dict[int, str] = {}
    fields = NAME_TABLES[short]
    index_by = fields[1] if len(fields) > 1 else None
    for r in rows:
        k = r.get("key")
        vals = r.get("values") or {}
        if index_by:                       # ★ 按指定字段当键（如 skin_id）
            x = vals.get(index_by)
            k = x[1] if isinstance(x, (list, tuple)) and len(x) > 1 else x
        if not isinstance(k, int):
            continue
        for f in fields[0] if isinstance(fields[0], tuple) else (fields[0],):
            if f in vals:
                v = vals[f]
                txt = v[1] if isinstance(v, (list, tuple)) and len(v) > 1 else v
                if isinstance(txt, str) and txt.strip():
                    if txt.strip().casefold() in {x.casefold() for x in PLACEHOLDER_NAMES}:
                        continue                      # ★ 占位词不当名字
                    out[int(k)] = txt.strip()
                    break
    return out


def build(out: Optional[Path] = None, *, verbose: bool = True) -> dict:
    t0 = time.time()
    out = Path(out) if out else index_path()
    tables: Dict[str, int] = {}
    items: Dict[str, dict] = {}
    for short in NAME_TABLES:
        got = scan_table(short)
        tables[short] = len(got)
        for k, nm in got.items():
            lst = items.setdefault(str(k), {})
            lst.setdefault(nm, []).append(short)
    rep = {"schema": "show-item-names/v1",
           "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "why": ("展示大奖的 id 大量落在 结构产物 CSV 未覆盖的表里；"
                   "本模块直解树里的名字表补这个缺口（含 player_module_appear_data）"),
           "tables": tables, "count": len(items), "seconds": round(time.time() - t0, 1)}
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(rep, items=items)
    out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    rep["out"] = str(out)
    if verbose:
        print("★ 展示大奖名字表直解：%d 条（%s）"
              % (rep["count"], " · ".join("%s=%d" % kv for kv in tables.items())))
        print("   → %s（%.1fs）" % (out, rep["seconds"]))
    return rep


def _load(out: Optional[Path] = None) -> dict:
    p = Path(out) if out else index_path()
    if not p.is_file():
        return {}
    try:
        return (json.loads(p.read_text(encoding="utf-8")).get("items") or {})
    except (OSError, ValueError):
        return {}


def lookup(ids, out: Optional[Path] = None) -> Dict[int, List[Tuple[str, List[str]]]]:
    """id → [(名字, [来源表…]), …]（多表命中就都列，不猜）。"""
    items = _load(out)
    res: Dict[int, List[Tuple[str, List[str]]]] = {}
    for i in ids:
        try:
            k = str(int(i))
        except (TypeError, ValueError):
            continue
        rec = items.get(k)
        if rec:
            res[int(k)] = sorted(((nm, sorted(t)) for nm, t in rec.items()),
                                 key=lambda x: x[0])
    return res


def stats(out: Optional[Path] = None) -> dict:
    p = Path(out) if out else index_path()
    if not p.is_file():
        return {"exists": False, "path": str(p)}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"exists": True, "path": str(p), "count": 0}
    return {"exists": True, "path": str(p), "count": len(d.get("items") or {}),
            "tables": d.get("tables") or {}, "generated": d.get("generated")}
