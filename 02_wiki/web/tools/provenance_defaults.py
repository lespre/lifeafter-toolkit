# -*- coding: utf-8 -*-
"""provenance_defaults.py — 溯源**板级常量**的按形态上提与回退

## 为什么有这个模块

2026-10-30 实测：item_master_full 板 30,252 条里，`provenance` 下的
`package_sha256` / `table` / `snapshot` / `audit_status` 等**板级常量被逐条重复写了
30,252 遍** —— 全同字段合计 18.8MB（占该板 30%）。全部入库板合计可省 54.5MB。

同一个常量写 N 遍，既浪费体积，也让「这条记录来自哪个包」这类**板级事实**
散落在 3 万个条目里，改一次要改 3 万处。

## 核心难点：条目有多种形态

实测 item_master_full 有 **4 种条目形态**（原生形态 / record 扁平形态 /
名册级 / 变体形态），它们的 provenance 键集合不同：

    27695 条  FID, audit_status, client, entry, ..., table, upstream
     1189 条  audit_status, field_refs, hide_in_bag, ..., record, upstream
      802 条  FID, audit_status, client, entry, ..., roster, upstream
      566 条  FID, audit_status, client, entry, ..., name_field_chs_slot, ...

    同一个键名在不同形态里**取值可能不同**（如 `table`：原生形态是
    ``com\\cdata\\common_item_data_base.py``，record 形态是别的表）。
    且某些形态**天生就没有**某个键（record 形态没有 `package`）。

⇒ **全局统一上提会丢事实**。必须**按形态分组**上提：
同一形态内的全同字段才上提到该形态的默认值里。

## 上提后的数据形态

    meta.provenance_defaults = {
      "<形态签名>": {           # 形态签名 = 该形态 provenance 键集合的稳定哈希
        "package": "...",      # 该形态内全同的字段 → 默认值
        "upstream": {...}      # 嵌套（upstream 的一层子字段）
      },
      ...
    }

条目里被上提的键被删除。回退时按**该条目原本属于哪个形态**取默认值。

## ★ 回退必须知道「条目原本有哪些键」

上提把键从条目里删了 ⇒ 回退时若无条件补默认值，会给原本没有该键的条目
**凭空添加字段**（实测 record 形态天生没有 `package`，补上就是篡改事实）。

解决办法：**形态签名本身就是「原本有哪些键」的完整记录**。
条目上提前会记住自己的形态签名，回退时用签名找到默认值；
而形态签名 → 默认值表里只包含**该形态原本就有**的键 ⇒ 回退天然安全。

回退口径：

    effective_provenance(item, board):
        形态默认值（该形态原本有的键） ← 条目现存键（优先）

## 铁律

- **只上提同一形态内取值完全一致的字段**：形态内只要有一个条目取值不同，
  该字段就留在条目级（少数派保留自己的值）。
- **不改取值**：上提的是「同一个值搬个地方」，不是「重新生成一个值」。
- **幂等**：上提后再跑一次，上提数 = 0。
- **不影响条目指纹**：`snapshot.py` 的 `IGNORE_KEYS` 含 `provenance`，
  且指纹用 `canonical()`（sort_keys + 紧凑分隔符）计算 ⇒ 板体积与指纹解耦。
- **门禁校验字段不外推**：`source_id` / `source_lock_sha256` /
  `locator_chain` / `field_refs` / `row_key` / `roster` 永远留在条目级
  —— 门禁要逐条核对「这个 sha 属于哪个 source」，外推就核对不了。

## 用法

```python
from provenance_defaults import hoist_board_defaults, effective_provenance
```
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

# 上提结果的存放位置（板级 meta 下）
DEFAULTS_KEY = "provenance_defaults"

# 条目上记形态签名的键。
# ★ 放在**条目层**（item._prov_shape）而非 provenance 内 ——
#   放 provenance 内会污染溯源内容（回退比对时多出一个键 ⇒ 判定不等价）。
SHAPE_KEY = "_prov_shape"

# 不上提的字段：门禁按条目核对，条目级必须保留
NEVER_HOIST = frozenset({
    "source_id",
    "source_lock_sha256",
    "locator_chain",
    "field_refs",
    "row_key",
    "roster",
})

# 形态签名用的**稳定键**：条目级事实，永不上提 ⇒ 签名不受上提影响。
# 实测 item_master_full 的 4 种形态可由此完全区分：
#   原生形态  locator_chain + field_refs + row_key
#   record    locator_chain + field_refs + row_key + record
#   名册级    roster
#   变体形态  locator_chain + field_refs + row_key
# ⚠️ 原生形态与变体形态的稳定键相同 —— 需再纳入 row_offset / schema_ref 等
#    也永不上提的键加以区分（见 STABLE_KEYS 全集）。
STABLE_KEYS = frozenset({
    "source_id",
    "source_lock_sha256",
    "locator_chain",
    "field_refs",
    "row_key",
    "roster",
    "record",
    "row_offset",
    "schema_ref",
    "name_value_chs_slot",
    "name_field_chs_slot",
    "identity",
    "max_stack_num",
    "hide_in_bag",
    "marker",
    "name",
})

# 嵌套字典的子字段可上提，但**只上提一层**：
#   provenance.upstream.package_sha256 等 —— upstream 本身是 dict，
#   其中的 package_sha256 / entry_index / file_id 常是板级常量。
#   ★ 不递归更深层：locator_chain.steps 是条目级定位链，绝不能上提。
NESTED_HOIST = {
    "upstream": ("package_sha256", "entry_index", "file_id"),
}

# ★ upstream 本身**不作为整体上提**：
#   实测有些板的 upstream 是**字符串**（如 "gift_data_text_sources board; ..."），
#   有些是 dict，还有些 dict 里带额外键（decoded_sha256 / role 等）。
#   若把 upstream 当普通字段整体上提，会把这些差异抹平 ⇒ 丢事实。
#   ⇒ upstream 只能走 NESTED_HOIST 的子字段路径，且子字段必须**全同**才上提。
NO_WHOLE_HOIST = frozenset(NESTED_HOIST.keys())


def _key_of(value: Any) -> str:
    """字段取值的可比较键（区分类型，避免 1 与 "1" 混同）。"""
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _shape_signature(prov: dict[str, Any]) -> str:
    """形态签名 = provenance **稳定键**集合的哈希。

    ★ 只用**永不上提**的键算签名（NEVER_HOIST ∪ 不会被整组上提的键）。
      原因：上提会把普通键从 provenance 里删掉，若签名基于全部键，
      上提后条目自身的键集合就变了 ⇒ 二次运行算出的签名不同 ⇒ 幂等性破坏、
      回退也匹配不上。
      用稳定键（locator_chain / field_refs / row_key / record / roster 等条目级事实）
      计算签名，既能区分形态，又不受上提影响。
    """
    keys = sorted(k for k in prov.keys() if k in STABLE_KEYS)
    h = hashlib.sha256("\n".join(keys).encode("utf-8")).hexdigest()[:16]
    return h


def _group_by_shape(items: list[Any]) -> dict[str, list[dict[str, Any]]]:
    """按形态签名分组。"""
    groups: dict[str, list[dict[str, Any]]] = {}
    for it in items:
        if not isinstance(it, dict):
            continue
        p = it.get("provenance")
        if not isinstance(p, dict):
            continue
        sig = it.get(SHAPE_KEY)
        if not isinstance(sig, str):
            sig = _shape_signature(p)
        groups.setdefault(sig, []).append(p)
    return groups


def find_uniform_by_shape(board: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """找出每个形态内取值完全一致且可上提的字段。

    返回 {形态签名: {字段名: 取值}}。

    ★ 上提条件（三条全满足才上提）：
      ① 该形态内**每个条目都有**这个键（否则缺失的条目回退时会凭空得到值）；
      ② 该形态内所有条目该键的取值**完全一致**；
      ③ 取值**非 null**（null = 「此处没有值」，不是「值是 null」）。
    """
    items = board.get("items")
    if not isinstance(items, list) or not items:
        return {}
    out: dict[str, dict[str, Any]] = {}
    for sig, provs in _group_by_shape(items).items():
        n = len(provs)
        vals: dict[str, dict[str, Any]] = {}
        counts: dict[str, int] = {}
        for p in provs:
            for k, v in p.items():
                if k in NEVER_HOIST or k in NO_WHOLE_HOIST:
                    continue
                kk = _key_of(v)
                slot = vals.setdefault(k, {})
                if kk not in slot:
                    slot[kk] = v
                counts[k] = counts.get(k, 0) + 1
        uniform: dict[str, Any] = {}
        for k, slot in vals.items():
            # ① 每个条目都有该键
            if counts.get(k, 0) != n:
                continue
            # ② 取值完全一致
            if len(slot) != 1:
                continue
            v = next(iter(slot.values()))
            # ③ 非 null
            if v is None:
                continue
            uniform[k] = v

        # 嵌套：upstream 的全同子字段（同样要求「每个条目都有 + 取值一致 + 非 null」）
        nested_vals: dict[str, dict[str, Any]] = {}
        for outer, allowed in NESTED_HOIST.items():
            sub: dict[str, dict[str, Any]] = {}
            sub_counts: dict[str, int] = {}
            for p in provs:
                node = p.get(outer)
                if not isinstance(node, dict):
                    continue
                for k in allowed:
                    if k not in node:
                        continue
                    v = node[k]
                    kk = _key_of(v)
                    slot = sub.setdefault(k, {})
                    if kk not in slot:
                        slot[kk] = v
                    sub_counts[k] = sub_counts.get(k, 0) + 1
            picked: dict[str, Any] = {}
            for k, slot in sub.items():
                # ★ 只有当「所有条目都有该子键」才上提 ——
                #   否则缺该子键的条目回退时会凭空得到值。
                if sub_counts.get(k, 0) != n:
                    continue
                if len(slot) != 1:
                    continue
                v = next(iter(slot.values()))
                if v is None:
                    continue
                picked[k] = v
            if picked:
                nested_vals[outer] = picked
        for outer, picked in nested_vals.items():
            uniform[outer] = picked
        if uniform:
            out[sig] = uniform
    return out


def hoist_board_defaults(board: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """把形态内全同的溯源字段上提到 meta.provenance_defaults。

    返回 (新板, 上提的字段数)。幂等：已上提的板再跑一次，上提数 = 0。
    """
    meta = board.get("meta")
    if not isinstance(meta, dict):
        return board, 0

    items = board.get("items")
    if not isinstance(items, list) or not items:
        return board, 0

    defaults = meta.get(DEFAULTS_KEY)
    if not isinstance(defaults, dict):
        defaults = {}

    uniform = find_uniform_by_shape(board)
    if not uniform:
        return board, 0

    # 记录每个条目的形态签名（供回退定位），并删除该形态要上提的键
    #
    # ★ 签名必须在**上提前**基于原始键集合算好，写进条目层（item._prov_shape）。
    #   上提会改变 provenance 的键集合，若签名靠「回退时现算」，
    #   就会与默认值表的键对不上 ⇒ 回退失效。
    #   条目层存签名 ⇒ 上提后依然稳定命中。
    hoisted = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        p = it.get("provenance")
        if not isinstance(p, dict):
            continue
        sig = it.get(SHAPE_KEY)
        if not isinstance(sig, str):
            sig = _shape_signature(p)
            it[SHAPE_KEY] = sig
        picked = uniform.get(sig) or {}
        for k, v in picked.items():
            if isinstance(v, dict):
                # 嵌套：只删该形态内值相同的子键
                node = p.get(k)
                if not isinstance(node, dict):
                    continue
                for sub_k, sub_v in list(v.items()):
                    if sub_k in node and _key_of(node[sub_k]) == _key_of(sub_v):
                        del node[sub_k]
                        hoisted += 1
            else:
                if k in p and _key_of(p[k]) == _key_of(v):
                    del p[k]
                    hoisted += 1

    # 写回默认值表
    new_defaults = {k: dict(v) for k, v in defaults.items()}
    for sig, picked in uniform.items():
        cur = new_defaults.get(sig)
        cur = dict(cur) if isinstance(cur, dict) else {}
        for k, v in picked.items():
            if isinstance(v, dict):
                sub = cur.get(k)
                sub = dict(sub) if isinstance(sub, dict) else {}
                sub.update(v)
                cur[k] = sub
            else:
                cur[k] = v
        new_defaults[sig] = cur
    meta[DEFAULTS_KEY] = new_defaults
    board["meta"] = meta
    return board, hoisted


def board_defaults(board: dict[str, Any]) -> dict[str, Any]:
    """取板级溯源默认值表（无则空 dict）。"""
    meta = board.get("meta") if isinstance(board, dict) else None
    d = meta.get(DEFAULTS_KEY) if isinstance(meta, dict) else None
    return d if isinstance(d, dict) else {}


def effective_provenance(item: dict[str, Any], board: dict[str, Any]) -> dict[str, Any]:
    """取条目的**有效溯源**：形态默认值 + 条目现存键，条目级优先。

    这是上提后的唯一读取口径 —— 前端与门禁都应走这里，
    否则上提会让「源快照摘要」等展示项消失。

    ★ 形态默认值里只含该形态**原本就有**的键 ⇒ 回退不会凭空添加字段。
    """
    p = item.get("provenance") if isinstance(item, dict) else None
    if not isinstance(p, dict):
        p = {}
    defaults = board_defaults(board)
    if not defaults:
        return p

    sig = item.get(SHAPE_KEY) if isinstance(item, dict) else None
    if not isinstance(sig, str):
        sig = _shape_signature(p)
    shape_def = defaults.get(sig)
    if not isinstance(shape_def, dict):
        return p

    merged: dict[str, Any] = {}
    for k, dv in shape_def.items():
        if isinstance(dv, dict):
            node = p.get(k)
            if isinstance(node, dict):
                # 条目级 upstream 是 dict：板级默认 + 条目级实值（条目级优先）。
                # ★ 必须**逐子键**回填：条目级可能只剩部分子键（如 role），
                #   其余子键（package_sha256 等）已被上提 ⇒ 直接用条目级 dict
                #   覆盖板级默认会把这部分信息丢掉。
                sub = dict(dv)
                sub.update(node)
                merged[k] = sub
            elif node is None:
                # 条目级没有该键 ⇒ 用板级默认（该形态原本有此键，故回退安全）
                merged[k] = dict(dv)
            else:
                # 条目级该键是**非 dict**（如 upstream 是字符串）⇒ 条目级优先，
                # 不能用板级 dict 覆盖它（那是另一种事实：字符串说明与记录形态）
                merged[k] = node
        else:
            merged[k] = dv
    # 条目现存键覆盖板级默认
    for k, v in p.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            # 两边都是 dict ⇒ 已在上方逐子键合并过，不能整体覆盖
            continue
        merged[k] = v
    return merged


if __name__ == "__main__":
    import copy
    import pathlib
    import sys

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from board_io import dumps_board

    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not src:
        print(__doc__)
        raise SystemExit(0)
    d = json.loads(src.read_text(encoding="utf-8-sig"))
    uni = find_uniform_by_shape(d)
    print(f"{src.name}  形态 {len(uni)} 种")
    for sig, picked in uni.items():
        print(f"  形态 {sig}: {sorted(picked.keys())}")
    before = copy.deepcopy(d)
    after, n = hoist_board_defaults(d)
    # ★ 语义等价校验
    bad = 0
    for bi, ai in zip(before["items"], after["items"]):
        b = bi.get("provenance") or {}
        a = effective_provenance(ai, after)
        if _key_of(b) != _key_of(a):
            bad += 1
    old = len(src.read_bytes())
    new = len(dumps_board(after).encode("utf-8"))
    print(f"  上提 {n} 处；有效溯源等价: {'✅' if bad == 0 else f'❌ {bad} 条不一致'}")
    print(f"  体积 {old/1048576:.2f}MB → {new/1048576:.2f}MB")
