# -*- coding: utf-8 -*-
"""lottery_servers.py — 分服奖池合成（全量 + 分服）

## 这份东西解决什么

`LOTTERY_POOL_RESOLVED_v01.jsonl` 有权威的「服 → 池 → 格 → 奖励 id+数量」，
但**没有中文字段**（note / 概率 / 到期 / 广播），而且 5 个服是平铺的，
没有「某服最终全量池」这个视图。

本模块做两件事：

  1. **字段补全**：从 PE 还原树里各服自己的 `reward_pool_data` 数据体取
     `note / prob_note / expiration_time / broadcast_content / initial_weights`，
     按 **reward 值**挂回权威键。
  2. **分服合成**：以 base 为底座，用各服 overlay 按 `(pool_key, item_no)`
     upsert，得到每服最终全量行，并标出 `same / replaced / added`。

## 为什么不需要自己重解复合键

`(pool_key, item_no)` 存在 `row_locator.index_key_group_offset` 指向的 0x27 组里，
位置随版本变化、按 offset 跨版本不可复用；而 `decode_table_rows` 给出的
`inline_groups[0]` 实测是**下一行**的键组（错位一格），直接拿来会得到
「整池错位」的假差异（v1 就是这么错的）。

所以这里**不重解键**，改用冻结产物已校验的权威键（单组件内 100% 唯一），
只用 reward 值做字段挂载 —— 实测 base 覆盖 23,268/23,281 = 99.9%，
kj1/kjxq 覆盖 237/237 = 100%。

## 铁律

- 不猜：某服数据体找不到 → 该服整块标 `missing`，不出空行冒充。
- 不混排：每服各自成行，`component` 字段必写；差异只在同服 vs base 之间算。
- `runtime_final` 恒为 `unresolved`：`optional_*` 会在运行时替换奖励，
  静态结构 ≠ 当前实发。
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter, defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import unnamed_registry as UREG  # noqa: E402
from la_paths import INDEX_ROOT, WEB, rel  # noqa: E402
from pe_source import body_of, blob_of  # noqa: E402

from toolkit_core import bindict_table as BT  # noqa: E402

# 冻结产物：权威键 + 奖励原值
FROZEN_CANDIDATES = (
    WEB / "site_data" / "LOTTERY_POOL_RESOLVED_v01.jsonl",
    INDEX_ROOT / "site_data" / "LOTTERY_POOL_RESOLVED_v01.jsonl",
)

# 挂到每一行上的中文字段（顺序即产物字段顺序，便于人读）
FIELD_KEYS = ("note", "prob_note", "expiration_time", "broadcast_content",
              "initial_weights", "accumulative_weight", "reward_rank")

STATE_VERIFIED = "verified"
STATE_MISSING = "missing"
STATE_DEGRADED = "degraded"


def frozen_path() -> pathlib.Path:
    for p in FROZEN_CANDIDATES:
        if p.is_file():
            return p
    raise FileNotFoundError("找不到冻结产物 LOTTERY_POOL_RESOLVED_v01.jsonl")


def load_manifest() -> dict:
    """读冻结产物首行 manifest（组件清单、快照 sha、统计）。"""
    with frozen_path().open(encoding="utf-8") as f:
        return json.loads(f.readline())


def manifest_components() -> list[dict]:
    """组件（= 服）清单，以冻结产物为准，不在代码里硬编码服名单。"""
    m = load_manifest()
    out = []
    for c in m.get("components") or []:
        data = c.get("data_entry") or {}
        chs = c.get("chs_entry") or {}
        out.append({
            "name": c.get("name"),
            "role": c.get("component_role"),
            "channel": c.get("channel"),
            "reliability_state": c.get("reliability_state"),
            "dataset_partition": c.get("dataset_partition"),
            "data_file_id": data.get("file_id"),
            "chs_file_id": chs.get("file_id"),
            "manifest_rows": c.get("rows"),
        })
    return out


def frozen_records() -> tuple[list[dict], dict]:
    """冻结产物的池行记录（按文件顺序），附 manifest。"""
    out: list[dict] = []
    with frozen_path().open(encoding="utf-8") as f:
        manifest = json.loads(f.readline())
        for line in f:
            d = json.loads(line)
            src = d.get("source") or {}
            lk = d.get("lookup_key") or {}
            pk = (lk.get("pool_key") or {}).get("value")
            no = (lk.get("item_no") or {}).get("value")
            if pk is None or no is None:
                continue
            rw = ((d.get("static_config") or {}).get("reward_raw") or {}).get("value")
            out.append({
                "component": src.get("component"),
                "partition": d.get("dataset_partition"),
                "pool_key": int(pk),
                "item_no": int(no),
                "reward_raw": list(rw) if isinstance(rw, list) else None,
                "dispatch": ((d.get("static_projection") or {})
                             .get("static_dispatch_candidate")),
                "record_id": d.get("record_id"),
            })
    return out, manifest


# ── 树内数据体定位（按 file_id，不分有名/无名）──────────────────────
def resolve_by_file_id(file_id: str) -> pathlib.Path | None:
    """按 file_id 在还原树里定位数据体。

    ★ 这是「以身份哈希为主键」的落点：`kj1` 的数据体在 `com/cdata/oversea/`
      有可读文件名，`base` / `ykxq` 的却在 `_未命名/` 只有行号名 —— 按 fid
      反查两边都能找到，按名字只能找到一半。
    """
    if not file_id:
        return None
    p, _state = UREG.resolve_entry(file_id, "", None)
    return p


def read_rows(path: pathlib.Path, pool: list[str]) -> tuple[list[dict], str]:
    """解数据体 → 行列表 + 状态。"""
    raw = path.read_bytes()
    try:
        body = body_of(raw)
    except ValueError:
        return [], STATE_MISSING
    rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False)
    if not rows:
        return [], STATE_MISSING
    blob = blob_of(body)
    out = []
    for r in rows:
        vals = r.get("values") or {}
        rw = vals.get("reward")
        raw_v = rw[1] if rw else None
        if isinstance(raw_v, str) and raw_v.startswith("jump:"):
            raw_v = BT.resolve_jump_group(blob, int(raw_v[5:]))
        rec = {"reward": tuple(raw_v) if isinstance(raw_v, list) else None}
        for k in FIELD_KEYS:
            payload = vals.get(k)
            rec[k] = payload[1] if payload else None
        out.append(rec)
    return out, STATE_VERIFIED


def field_index(rows: list[dict]) -> dict:
    """`reward 元组 → 字段字典`。

    同一 reward 可能对应多条行（同 reward 不同策划备注），实测 5,050 个 reward
    里 561 个 note 不唯一（多为「新币8000 / 新币 / 新币*8000」这类同义写法）。
    取舍规则：**取 note 最长的一条**（信息量最大），并列时取先出现的。
    这是展示层妥协，`note_conflict` 会标出存在多写法的情况。
    """
    idx: dict = {}
    conflict: set = set()
    for r in rows:
        k = r.get("reward")
        if not k:
            continue
        cur = idx.get(k)
        if cur is None:
            idx[k] = dict(r)
            continue
        if (r.get("note") or "") != (cur.get("note") or ""):
            conflict.add(k)
        if len(r.get("note") or "") > len(cur.get("note") or ""):
            merged = dict(cur)
            merged.update({kk: vv for kk, vv in r.items() if vv is not None})
            idx[k] = merged
    for k in conflict:
        if k in idx:
            idx[k]["note_conflict"] = True
    return idx


def component_data(comp: dict) -> dict:
    """取一个服的数据体与字段索引。"""
    data_p = resolve_by_file_id(comp.get("data_file_id"))
    pool_p = resolve_by_file_id(comp.get("chs_file_id"))
    info = {
        "component": comp["name"],
        "data_file_id": comp.get("data_file_id"),
        "pool_file_id": comp.get("chs_file_id"),
        "data_path": rel(data_p) if data_p else None,
        "pool_path": rel(pool_p) if pool_p else None,
        "state": STATE_MISSING,
        "rows": 0,
        "pool_strings": 0,
    }
    if data_p is None:
        return {"info": info, "index": {}}
    pool: list[str] = []
    if pool_p is not None:
        pool = BT.parse_legacy_chs_pool(pool_p.read_bytes())
    rows, state = read_rows(data_p, pool)
    info.update({"state": state, "rows": len(rows), "pool_strings": len(pool)})
    idx = field_index(rows)
    info["distinct_rewards"] = len(idx)
    info["with_note"] = sum(1 for v in idx.values() if v.get("note"))
    info["with_prob"] = sum(1 for v in idx.values() if v.get("prob_note") is not None)
    return {"info": info, "index": idx}


def merged_rows(frozen: list[dict], components: list[dict]) -> tuple[list[dict], list[dict]]:
    """合成每服**全量**行。

    全量 = base 的每一格都在，channel 的覆盖叠在上面。返回每行带 `diff`：

      · `base`     base 服自己的行
      · `inherit`  该服 overlay **没有覆盖**这一格，沿用 base（字段取该服数据体，
                   取不到则回落 base）
      · `same`     该服 overlay 覆盖了这一格，但奖励与 base 相同（多为补中文名/概率）
      · `replaced` 该服 overlay 把奖励换了
      · `added`    base 没有这一格，该服新增

    ★ 为什么必须补 inherit：overlay 是**覆盖表**，只含被改动的池。
      只输出 overlay 行会让人误以为「这个服只有 237 格」，而实际上它有 23,281 格。
    """
    by_comp: dict[str, dict] = {}
    infos: list[dict] = []
    for comp in components:
        got = component_data(comp)
        by_comp[comp["name"]] = got
        info = got["info"]
        info.update({"role": comp.get("role"), "channel": comp.get("channel"),
                     "reliability_state": comp.get("reliability_state"),
                     "manifest_rows": comp.get("manifest_rows")})
        infos.append(info)

    base_idx = by_comp.get("base", {}).get("index") or {}
    base_rows: dict[tuple, dict] = {}
    for r in frozen:
        if r["component"] == "base":
            base_rows[(r["pool_key"], r["item_no"])] = r

    def emit(comp: str, r: dict, diff: str, base_raw, own_idx: dict) -> dict:
        reward = tuple(r["reward_raw"]) if r["reward_raw"] else None
        fields = own_idx.get(reward) if reward else None
        if not fields:
            fields = base_idx.get(reward) or {}
        rec = {
            "component": comp,
            "pool_key": r["pool_key"],
            "item_no": r["item_no"],
            "reward_raw": r["reward_raw"],
            "item_id": reward[0] if reward else None,
            "item_count": reward[1] if len(reward) > 1 else None,
            "dispatch": r["dispatch"],
            "partition": r["partition"],
            "field_state": ("full" if fields.get("note") else
                            ("partial" if fields else "none")),
            "diff": diff,
        }
        for k in FIELD_KEYS:
            rec[k] = fields.get(k)
        rec["note_conflict"] = bool(fields.get("note_conflict"))
        if comp != "base":
            rec["base_reward_raw"] = base_raw
        return rec

    out: list[dict] = []
    for comp in components:
        name = comp["name"]
        own = {name: {(r["pool_key"], r["item_no"]): r
                      for r in frozen if r["component"] == name}}
        own_rows = own[name]
        own_idx = by_comp[name]["index"]

        # ① base 全量，按该服 overlay 打标
        for k, b in base_rows.items():
            if name == "base":
                out.append(emit(name, b, "base", None, own_idx))
                continue
            o = own_rows.get(k)
            if o is None:
                out.append(emit(name, b, "inherit", b["reward_raw"], own_idx))
            elif o["reward_raw"] == b["reward_raw"]:
                out.append(emit(name, o, "same", b["reward_raw"], own_idx))
            else:
                out.append(emit(name, o, "replaced", b["reward_raw"], own_idx))
        # ② 该服新增的格
        if name != "base":
            for k, o in own_rows.items():
                if k not in base_rows:
                    out.append(emit(name, o, "added", None, own_idx))
    return out, infos


def summarize(rows: list[dict], infos: list[dict]) -> dict:
    """产物级统计（写 manifest）。"""
    per = {}
    for r in rows:
        c = r["component"]
        s = per.setdefault(c, Counter())
        s["rows"] += 1
        s[r["diff"]] += 1
        s["field_" + r["field_state"]] += 1
        if r["note"]:
            s["with_note"] += 1
        if r["prob_note"] is not None:
            s["with_prob"] += 1
        if r.get("note_conflict"):
            s["note_conflict"] += 1
    return {
        "total_rows": len(rows),
        "per_component": {c: dict(v) for c, v in sorted(per.items())},
        "components": infos,
    }


# ── 消费入口（给看板 / 查询脚本用，不依赖生成过程）────────────────
def product_dir() -> pathlib.Path:
    return WEB / "site_data" / "LOTTERY_POOL_SERVERS_v01"


# ── 11-03 雷电设备包（PE 侧）冻结数据集（当前奖池源）────────────────
PE1103_DIR = WEB / "site_data" / "LOTTERY_POOL_PE1103_v01"
PE1103_ROWS = PE1103_DIR / "rows.jsonl"


def iter_pe1103_rows():
    """流式读 11-03 奖池冻结数据集的行。

    每行 = 某服某池某一格的静态结构，字段与旧分服产物同构：
    component / pool_key / item_no / reward_raw / item_id / item_count /
    note / prob_note / expiration_time / broadcast_content / initial_weights /
    accumulative_weight / reward_rank / field_state / diff。

    ★ 该数据集自带 diff 标记（base/inherit/same/replaced/added）——
      它在解码时已逐格与 base 对比过，**不需要再重算**。
    """
    if not PE1103_ROWS.is_file():
        raise FileNotFoundError(
            "11-03 奖池数据集不存在：%s（先跑 build_lottery_pool_pe1103.py）" % rel(PE1103_ROWS))
    with PE1103_ROWS.open(encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def pe1103_components() -> list[dict]:
    """11-03 数据集的组件（= 服）清单，取自其 manifest，不在代码里硬编码服名单。

    manifest 里的组件条目形如
    {"component": "base", "data_file_id": ..., "data_sha256": ..., "rows": ...,
     "pools": ..., "pool_key_range": [...], "state": "verified", "unbound_rows": 0}
    """
    man = json.loads((PE1103_DIR / "manifest.json").read_text(encoding="utf-8"))
    stats = man.get("stats") or {}
    out = []
    for info in (stats.get("components") or []):
        out.append({
            "name": info.get("component"),
            "data_file_id": info.get("data_file_id"),
            "data_sha256": info.get("data_sha256"),
            "rows": info.get("rows"),
            "pools": info.get("pools"),
            "pool_key_range": info.get("pool_key_range"),
            "state": info.get("state"),
            "unbound_rows": info.get("unbound_rows"),
        })
    return out


def iter_rows(components: tuple[str, ...] | None = None):
    """流式读已落盘的分服产物。产物不存在时抛 FileNotFoundError（不静默）。"""
    p = product_dir() / "rows.jsonl"
    if not p.is_file():
        raise FileNotFoundError(
            "分服产物不存在：%s（先跑 build_lottery_servers.py --apply）" % rel(p))
    with p.open(encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            if components is None or d.get("component") in components:
                yield d


def pool_of(component: str, pool_key: int) -> list[dict]:
    """某服某池的全部格（按 item_no 升序）。这是「查一个池在两服各发什么」的入口。"""
    rows = [r for r in iter_rows((component,)) if r.get("pool_key") == pool_key]
    return sorted(rows, key=lambda r: (r.get("item_no") is None, r.get("item_no")))


def diff_of(component: str) -> list[dict]:
    """某服相对 base 的全部差异格（replaced + added）。"""
    return [r for r in iter_rows((component,)) if r.get("diff") in ("replaced", "added")]


__all__ = [
    "FIELD_KEYS", "STATE_VERIFIED", "STATE_MISSING", "STATE_DEGRADED",
    "frozen_path", "load_manifest", "manifest_components", "frozen_records",
    "resolve_by_file_id", "read_rows", "field_index", "component_data",
    "merged_rows", "summarize",
    "product_dir", "iter_rows", "pool_of", "diff_of",
]
