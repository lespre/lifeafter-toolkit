# -*- coding: utf-8 -*-
"""sync_board_tech_sources.py — 把每个板块实际用到的「表源」写进 meta.tech_sources

## 为什么

板块的溯源原先只散落在两处：
- `meta.provenance.source_locks`：一堆 `source_id` + sha，**没有表名**，玩家看不懂；
- `items[].provenance.table`：行级表名，但要逐条展开卡片的「技术详情」才看得到。

于是「这个板块到底读了哪几张表」在页面上无处可查（用户 2026-11-01 口径：
**这些表源都要写进板块对应的技术详情**）。本脚本把板级表源汇总成
`meta.tech_sources`，由前端在**板级**「技术详情 / 数据来源 / 审计信息」里渲染。

## 口径（全部由产物自身推得，不猜、不手填）

1. **行源表**（kind=row）：`items[].provenance.table` 计数（`items[].tables` 一并计入）；
   卡片数＝该表直接产出的条目数。
2. **文本池**（kind=chs）：`X_chs` 归为 X 的中文文本池（独立文件、独立 sha），单独成行，
   不与数据表混算。
3. **字段来源表**（kind=field）：条目 provenance 的字段级来源块
   `charm_source`（dict，含 table）/`desc_source`/`icon_source`/`name_source`/`part_source`（字符串）。
   字符串里的**裸字段名**（如 `part_type`、`pendant_item_icon`）视为行源表内部的字段，
   不虚构成表；资源路径（含 `→` / `ui/`）不记表。
4. **角色**（primary / comparison）：按锁名（路径里的标识符）或 sha256 与表对上；
   `X_chs` 的锁归到 X。
5. **兜底**：没对上任何表的 source_lock 照实记一条（kind=lock_only），
   保证「所有源锁都在技术详情里有交代」，不静默丢弃。

## 幂等

`meta.tech_sources` 每次整块重算；与现有内容一致则不写盘（字节级幂等）。

用法：
    python 02_wiki/web/tools/build/sync_board_tech_sources.py            # 全部板（dry-run）
    python 02_wiki/web/tools/build/sync_board_tech_sources.py --apply    # 落盘
    python 02_wiki/web/tools/build/sync_board_tech_sources.py --apply fashion_wardrobe
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter, OrderedDict

HERE = pathlib.Path(__file__).resolve()
TOOLS = HERE.parent.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "build"))

from la_paths import PROJ  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARDS = PROJ / "02_wiki/web/data/boards"

# 字段级来源块 → 中文用途（只影响展示，不影响判定）
FIELD_CN = OrderedDict([
    ("charm_source", "魅力值"),
    ("desc_source", "描述"),
    ("icon_source", "图标"),
    ("name_source", "名称"),
    ("part_source", "部位"),
    ("effect_source", "效果"),
])

RULE = (
    "行源表＝items[].provenance.table 计数（items[].tables 一并计入）；X_chs 记为独立的文本池；"
    "字段来源表来自条目 provenance 的 charm_source/desc_source/icon_source/name_source/part_source 块，"
    "裸字段名与资源路径不虚构成表；角色（主表/对照表）按锁路径标识符或 sha256 反查 "
    "meta.provenance.source_locks；未匹配到表的源锁以 lock_only 单列，不丢弃。"
)

_IDENT = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")
_IS_CHS = re.compile(r"_chs$")


def _split_source(raw):
    """拆出 (表名候选, 是否资源路径, 是否裸字段)。"""
    s = str(raw).strip()
    if not s:
        return None, True, False
    if "→" in s or "ui/" in s.replace("\\", "/").lower():
        return None, True, False            # 资源路径（图标 png 提取），不是表
    if ".py" in s:
        m = re.search(r"([A-Za-z0-9_]+)\.py", s)
        return (m.group(1) if m else None), False, False
    head = s.split("#")[0].strip()
    # 带括号补充说明：主名在括号前
    head = re.split(r"[（(]", head)[0].strip()
    head = head.replace("\\", "/").rstrip("/").split("/")[-1].strip()
    if not head:
        return None, True, False
    if "." in head:                          # table.field
        head = head.split(".")[0].strip()
    if not head:
        return None, True, False
    if _IDENT.fullmatch(head):
        return head, False, False
    return None, True, False


def norm_table(raw):
    """把表名/路径归一成表名（用于匹配与去重）。"""
    head, is_asset, _ = _split_source(raw) if raw is not None else (None, True, False)
    return head if not is_asset else None


def display_table(raw):
    """展示名：保留（xxx）补充说明，去掉路径前缀、.py 后缀与 .字段 尾巴。"""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = re.search(r"([A-Za-z0-9_]+)\.py", s)
    if m:
        return m.group(1)
    s = s.split("#")[0].strip()
    s = s.replace("\\", "/").rstrip("/").split("/")[-1]
    if s.endswith(".json"):
        s = s[:-5]
    if "." in s:
        head, tail = s.rsplit(".", 1)
        if head and _IDENT.fullmatch(tail):
            s = head                     # all_equips_data.charm_value → all_equips_data
    return s or None


def iter_boards(names):
    if names:
        out = []
        for n in names:
            p = BOARDS / (n if n.endswith(".json") else n + ".json")
            if p.exists():
                out.append(p)
        return out
    out = []
    for p in sorted(BOARDS.glob("*.json")):
        if p.name.startswith("_") or ".retired" in p.name:
            continue
        out.append(p)
    return out


def _idents(text):
    """从路径/锁名里抽标识符（用于锁→表匹配）。"""
    out = set()
    for tok in _IDENT.findall(str(text or "")):
        out.add(tok)
        if "/" in tok or "\\" in tok:
            out.add(tok.replace("\\", "/").split("/")[-1])
    return {t for t in out if len(t) >= 4}


def collect(board):
    items = board.get("items") or []
    prov = (board.get("meta") or {}).get("provenance") or {}
    locks = prov.get("source_locks") or []

    row_cards = Counter()
    row_display = {}
    field_cards = Counter()
    field_use = {}
    field_display = {}
    chs_cards = Counter()
    sha_to_table = {}
    known = set()

    def note_sha(sha, table_key):
        if isinstance(sha, str) and len(sha) == 64 and table_key:
            sha_to_table.setdefault(sha, table_key)

    for it in items:
        p = it.get("provenance") or {}
        row_key = norm_table(p.get("table"))
        if row_key:
            row_cards[row_key] += 1
            row_display.setdefault(row_key, display_table(p.get("table")) or row_key)
            known.add(row_key)
            note_sha(p.get("source_lock_sha256"), row_key)
        for t in (it.get("tables") or []):
            k = norm_table(t)
            if not k:
                continue
            if _IS_CHS.search(k):
                chs_cards[k] += 1
                known.add(k)
            elif k != row_key:
                row_cards[k] += 1
                row_display.setdefault(k, display_table(t) or k)
                known.add(k)
        for blk, cn in FIELD_CN.items():
            v = p.get(blk)
            if v is None:
                continue
            if isinstance(v, dict):
                k = norm_table(v.get("table"))
                disp = display_table(v.get("table")) or k
                if k:
                    note_sha(v.get("source_lock_sha256"), k)
            elif isinstance(v, str):
                k = norm_table(v)
                disp = display_table(v) or k
            else:
                k = None
                disp = None
            if not k:
                continue
            is_dict = isinstance(v, dict)
            raw_txt = "" if is_dict else str(v)
            if (k not in known and k not in row_cards and k not in field_cards
                    and not is_dict and "." not in raw_txt
                    and "（" not in raw_txt and "(" not in raw_txt):
                # 裸字段名（part_type / pendant_item_icon …）＝行源表内部字段，不虚构成表
                if row_key:
                    continue
            field_cards[k] += 1
            field_use.setdefault(k, Counter())[cn] += 1
            field_display.setdefault(k, disp or k)

    # ---- 锁 → 表 ----
    lock_of = {}
    matched = set()
    for pos, lk in enumerate(locks):
        if not isinstance(lk, dict):
            continue
        names = _idents(lk.get("path")) | _idents(lk.get("source_id"))
        target = None
        pool = set(row_cards) | set(field_cards) | set(chs_cards)
        # 1) 精确同名（路径里的标识符 == 表名）
        for cand in sorted(pool, key=len, reverse=True):
            if cand in names:
                target = cand
                break
        # 2) 前缀同名（common_item_text_sources → common_item；body_sfx_data_chs 已精确命中）
        if not target:
            best = None
            for cand in pool:
                for nm in names:
                    if nm.startswith(cand + "_") and (best is None or len(cand) > len(best)):
                        best = cand
            target = best
        # 3) sha 兜底
        if not target:
            sha = lk.get("sha256")
            if isinstance(sha, str) and sha in sha_to_table:
                target = sha_to_table[sha]
        if target:
            lock_of.setdefault(target, []).append(lk)
            matched.add(pos)

    def pick(table_key, field, fn=None):
        for lk in lock_of.get(table_key, []):
            v = lk.get(field)
            if fn is None or fn(v):
                return v
        return None

    def pick_role(table_key):
        roles = [lk.get("role") for lk in lock_of.get(table_key, [])]
        if "primary" in roles:
            return "primary"
        if "comparison" in roles:
            return "comparison"
        return None

    def entry(table_key, disp, kind, cards, fields=()):
        base = _IS_CHS.sub("", table_key)
        # 文本池的角色/来源跟着它所属的数据表走（body_sfx_data_chs → body_sfx_data）
        pool_keys = (table_key, base) if kind == "chs" else (table_key,)
        src_ids = []
        for pk in pool_keys:
            for lk in lock_of.get(pk, []):
                sid = lk.get("source_id")
                if sid and sid not in src_ids:
                    src_ids.append(sid)
        role = None
        for pk in pool_keys:
            role = pick_role(pk)
            if role:
                break
        # 归类兜底（前端分组口径，必须与 board_core.js 的 SRC_ROLE_CN 一致）：
        #   · 文本池（*_chs）自成一组，不跟随它所属数据表的 primary；
        #   · 字段补充表默认算「对照」，因为它只补字段、不出行条目；
        #   · 仅校验表（快照锁）单独一组；
        #   · 锁里确实没写 role 的行表 → unlabeled（如实标注，不猜）。
        if kind == "chs":
            role = "chs"
        elif role is None:
            if kind == "field":
                role = "comparison"
            elif kind == "lock_only":
                role = "lock_only"
            else:
                role = "unlabeled"
        path = next((v for v in (pick(pk, "path") for pk in pool_keys) if v), None)
        sha = next((v for v in (pick(pk, "sha256", lambda x: isinstance(x, str) and len(x) == 64)
                                for pk in pool_keys) if v), None)
        return {
            "table": disp,
            "table_key": table_key,
            "kind": kind,
            "role": role,
            "cards": cards,
            "fields": list(fields),
            "source_ids": src_ids,
            "path": path,
            "sha256": sha,
        }

    tables = []
    for key, n in row_cards.most_common():
        fields = [f for f, _ in field_use.get(key, Counter()).most_common()]
        tables.append(entry(key, row_display.get(key) or key, "row", n, fields))
    for key, n in field_cards.most_common():
        if key in row_cards:
            continue          # 已在行源表里合并（fields 已带上）
        tables.append(entry(key, field_display.get(key) or key, "field", n,
                            [f for f, _ in field_use.get(key, Counter()).most_common()]))
    for key, n in chs_cards.most_common():
        tables.append(entry(key, key, "chs", n, ["文本池（CHS）"]))
    lock_only_seen = set()
    for pos, lk in enumerate(locks):
        if pos in matched or not isinstance(lk, dict):
            continue
        disp = display_table(lk.get("path")) or (lk.get("source_id") or "")
        key = (disp, lk.get("source_id"), lk.get("sha256"))
        if key in lock_only_seen:      # 同一把锁被重复登记时只留一条
            continue
        lock_only_seen.add(key)
        tables.append({
            "table": disp,
            "table_key": None,
            "kind": "lock_only",
            "role": lk.get("role"),
            "cards": 0,
            "fields": [],
            "source_ids": [lk.get("source_id")] if lk.get("source_id") else [],
            "path": lk.get("path"),
            "sha256": lk.get("sha256") if isinstance(lk.get("sha256"), str) else None,
        })

    return {
        "board": None,
        "rule": RULE,
        "lock_count": len(locks),
        # 与 tables 行数严格一致（含仅校验表），避免前端「说 11 张、列 12 行」的自相矛盾
        "table_count": len(tables),
        "tables": tables,
    }


def main(argv):
    apply = "--apply" in argv
    names = [a for a in argv[1:] if not a.startswith("-")]
    changed = 0
    for path in iter_boards(names):
        board = json.loads(path.read_text(encoding="utf-8"))
        try:
            info = collect(board)
        except Exception as e:  # 单板失败不影响其他板
            print(f"[SKIP] {path.stem}: {e}")
            continue
        info["board"] = path.stem
        if info["table_count"] == 0:
            print(f"[SKIP] {path.stem}: 无表级证据（items 未记 provenance.table），不写空壳")
            continue
        if (board.get("meta") or {}).get("tech_sources") == info:
            continue
        changed += 1
        brief = ", ".join((t["table"] or "(lock_only)") for t in info["tables"][:6])
        print(f"[{'WRITE' if apply else 'DRY '}] {path.stem}: 表 {info['table_count']} / 锁 {info['lock_count']} -> {brief}")
        if apply:
            board.setdefault("meta", {})["tech_sources"] = info
            write_board_pair(path, board)
    print(f"\n{'已写盘' if apply else '待写'}板块数：{changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
