# -*- coding: utf-8 -*-
"""lottery_enrich.py — 奖池数据的四个补充维度（深挖 A~D 的产出）

主产物 `LOTTERY_POOL_SERVERS_v01/rows.jsonl` 回答「某服某池某格发什么」。
本模块补四个它装不下的维度，各写一个独立小文件（不动 rows.jsonl）：

  1. `child_pools.json`  —— 深挖 A：奖励 = 「抽子池 N 次」的 43 个格，
                            展开成具体物品清单（只一层，已验证无多层嵌套）
  2. `activities.json`   —— 深挖 C：活动 ↔ 池 绑定（220/223 lottery_id 可对上池）
  3. `desc_blocks.json`  —— 深挖 D：24 个概率公示块，以及与池的配对结果
  4. `runtime_replace.json` —— 深挖 B：185 条运行时替换规则（runtime_final 边界）
  另附 `servers.json`    —— 服身份：哪些服内容完全等价、官方 oversea 映射

## 铁律

- 判不出就写 `unresolved`，不给猜测值。
- 每个结论都带 `evidence`（可复算判据）与计数，便于门禁复验。
- 幂等：同输入 → 字节一致（除 manifest 里的时间戳，本模块无时间戳）。
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
_TOOLKIT = _HERE.parents[2] / "00_规范与工具/工具/工具库/00_共享核心"
if _TOOLKIT.is_dir():
    sys.path.insert(0, str(_TOOLKIT))

import lottery_servers as LS  # noqa: E402
import pe_source as P  # noqa: E402
from la_paths import rel  # noqa: E402
from toolkit_core import bindict_table as BT  # noqa: E402
from toolkit_core import lottery_locate as LL  # noqa: E402
from toolkit_core import script_table_replay as R  # noqa: E402

# 概率公示（base 经典服）
DESC_CHS = P.CD / "desc_info_data_chs.py"
OVERSEA = P.CD / "oversea"
OVERSEA_MAP = OVERSEA / "oversea_table_map_data.py"

QTY_TAIL = re.compile(r"\s*[*×xX]\s*(\d+)\s*$")
QTY_MID = re.compile(r"[*×xX]\s*(\d+)\s*$")

STATE_VERIFIED = "verified"
STATE_CANDIDATE = "candidate"
STATE_UNRESOLVED = "unresolved"


# ── 通用小工具 ────────────────────────────────────────────────────
def _val(payload, default=None):
    return payload[1] if payload else default


def _int(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return int(x)
    return None


def split_name_qty(s: str) -> tuple[str, int | None]:
    s = (s or "").strip()
    m = QTY_MID.search(s)
    if m:
        return s[:m.start()].strip(), int(m.group(1))
    return s, None


def norm_name(s: str) -> str:
    s = (s or "").replace("：", ":").replace("，", ",").replace("（", "(").replace("）", ")")
    return s.replace("＊", "*").replace("　", "").strip()


def base_pool_index() -> tuple[dict[int, list[dict]], set[int]]:
    """base 全量行 → 池索引（一次扫描，避免反复读数据集）。"""
    pools: dict[int, list[dict]] = defaultdict(list)
    for r in LS.iter_pe1103_rows():
        if r.get("component") != "base":
            continue
        pools[r["pool_key"]].append(r)
    for k in pools:
        pools[k].sort(key=lambda r: (r["item_no"] is None, r["item_no"]))
    return pools, set(pools)


# ── 深挖 A：child_pool 展开 ───────────────────────────────────────
CHILD_NOTES = (
    "奖励格的 reward_raw = [子池号, 次数]，语义是「开该子池 N 次」而不是发某个道具；"
    "子池号与池表 key 同域（390000~391793）。已全量验证：43 格 ↔ 上游 targets 的 "
    "reward_target_type=child_pool 双向 43/43 一致；37 个子池全部存在于池表；"
    "子池内部再无 child_pool 引用 ⇒ 只有一层，不需要递归。"
    "「命中但未标」= 0，说明不存在漏标的池号引用；池号区间内另有 28 个普通道具 id "
    "与池号同号段，已用「是否在池表里」区分，不是按号段猜的。"
)


def build_child_pools(pools: dict[int, list[dict]]) -> dict:
    entries = []
    for pk, rows in sorted(pools.items()):
        for r in rows:
            iid = r["item_id"]
            if iid is None or iid not in pools:
                continue
            child = pools[iid]
            entries.append({
                "parent_pool": pk,
                "parent_slot": r["item_no"],
                "parent_note": r["note"],
                "child_pool": iid,
                "times": r["item_count"],
                "state": STATE_VERIFIED,
                "child_items": [
                    {"slot": c["item_no"], "item_id": c["item_id"],
                     "count": c["item_count"], "note": c["note"],
                     "prob_note": c["prob_note"]}
                    for c in child
                ],
            })
    return {
        "schema": "lottery_child_pools/v0.1",
        "generator": rel(pathlib.Path(__file__)),
        "state": STATE_VERIFIED,
        "count": len(entries),
        "child_pools": len({e["child_pool"] for e in entries}),
        "parent_pools": len({e["parent_pool"] for e in entries}),
        "max_depth": 1,
        "notes": CHILD_NOTES,
        "entries": entries,
    }


# ── 深挖 C：活动 ↔ 池 绑定 ───────────────────────────────────────
ACT_NOTES = (
    "来源 super_fashion_lottery_conf_data（223 行，主键 activity_key）。"
    "lottery_id 即池 key；220/223 能对上 base 池表，3 个对不上"
    "（391820 / 391821 / 391848，超出静态池上限 391793，属于更新期次的池，"
    "静态层拿不到 → 保留 unresolved，不补）。"
    "★ 池会跨活动复用：40 个池被 2~3 个活动引用，所以「池 → 活动」是多对多，"
    "不能当唯一归属展示。panel_show_item_ids 是台面展示位（1~4 个），"
    "214/223 可解，只是大奖预览，不是完整奖励清单。"
)


def build_activities(pools: set[int]) -> dict:
    t = P.load("super_fashion_lottery_conf_data")
    blob = t["blob"]
    entries = []
    pool2act: dict[int, list[int]] = defaultdict(list)
    for r in t["rows"]:
        v = r.get("values") or {}
        lid = _int(_val(v.get("lottery_id")))
        pl = v.get("panel_show_item_ids")
        shown = None
        if pl:
            raw = pl[1]
            if isinstance(raw, str) and raw.startswith("jump:"):
                shown = BT.resolve_jump_group(blob, int(raw[5:]))
            elif isinstance(raw, list):
                shown = raw
        e = {
            "activity_key": r.get("key"),
            "lottery_id": lid,
            "lottery_group_id": _int(_val(v.get("lottery_group_id"))),
            "gift_hd_id": _int(_val(v.get("gift_hd_id"))),
            "exchange_shop_conf_id": _int(_val(v.get("exchange_shop_conf_id"))),
            "panel_show_item_ids": shown,
            "state": STATE_VERIFIED if lid in pools else STATE_UNRESOLVED,
        }
        entries.append(e)
        if lid in pools:
            pool2act[lid].append(r.get("key"))
    return {
        "schema": "lottery_activities/v0.1",
        "generator": rel(pathlib.Path(__file__)),
        "source_table": "super_fashion_lottery_conf_data",
        "activities": len(entries),
        "bound": sum(1 for e in entries if e["state"] == STATE_VERIFIED),
        "pools_bound": len(pool2act),
        "pool_coverage_of_base": round(len(pool2act) / max(1, len(pools)), 4),
        "multi_activity_pools": sum(1 for v in pool2act.values() if len(v) > 1),
        "notes": ACT_NOTES,
        "entries": entries,
        "pool_to_activities": {str(k): v for k, v in sorted(pool2act.items())},
    }


# ── 深挖 D：概率公示块 ───────────────────────────────────────────
DESC_NOTES = (
    "desc_info_data_chs.py 共 24 个公示块，条目形如 (序号, '名字*数量', '概率%')。"
    "★ 关键结论：公示给出的概率是**独立权威源** —— 池行的 prob_note 在这些块对应的池里"
    "大量为 None（如霸王秘宝池 391473 的 8 格全部无 prob_note，但公示合计正好 100%）。"
    "★ 配对判据（可复算）：格数相等 + 逐项名字归一后同序匹配 + 数量一致；"
    "得分 = 项命中均值（名字全等 1 分、包含 0.5 分，数量再对加 0.5 分，封顶 1）。"
    "实测只有「霸王秘宝概率公示」达到 1.00（8/8 名字 + 8/8 数量）；"
    "因此「用公示页反推池」不可行，公示只适合做交叉校验，不适合当主源。"
    "对不上的块多为新活动（奖励名不在旧快照池表里）或通用文案（'其他奖励'/'稀有奖励'）。"
)


def build_desc_blocks(pools: dict[int, list[dict]]) -> dict:
    if not DESC_CHS.is_file():
        return {"schema": "lottery_desc_blocks/v0.1", "state": STATE_UNRESOLVED,
                "notes": "desc_info_data_chs.py 不存在", "blocks": []}
    blocks = LL.prob_blocks(DESC_CHS)
    by_size = defaultdict(list)
    for pk, rows in pools.items():
        by_size[len(rows)].append(pk)

    out = []
    for b in blocks:
        ents = b.get("entries") or []
        n = len(ents)
        best = None
        for pk in by_size.get(n, []):
            rows = pools[pk]
            score = 0.0
            qty_ok = 0
            for i, e in enumerate(ents):
                if i >= len(rows):
                    break
                nm, qty = split_name_qty(e[1]) if len(e) > 1 else ("", None)
                rn, rq = split_name_qty(rows[i]["note"] or "")
                a, bb = norm_name(nm), norm_name(rn)
                if not a or not bb:
                    s = 0.0
                elif a == bb:
                    s = 1.0
                elif a in bb or bb in a:
                    s = 0.5
                else:
                    s = 0.0
                if s and qty is not None:
                    cnt = rows[i]["item_count"]
                    if cnt is not None and int(cnt) == int(qty):
                        s = min(1.0, s + 0.5)
                        qty_ok += 1
                score += s
            score /= max(1, n)
            if best is None or score > best[0]:
                best = (score, pk, qty_ok)
        if best and best[0] >= 0.9:
            state = STATE_VERIFIED
        elif best and best[0] >= 0.5:
            state = STATE_CANDIDATE
        else:
            state = STATE_UNRESOLVED
        out.append({
            "name": b.get("name"),
            "entry_count": n,
            "matched_pool": best[1] if best else None,
            "match_score": round(best[0], 3) if best else None,
            "qty_matched": best[2] if best else 0,
            "state": state,
            "entries": [{"no": e[0], "label": e[1],
                         "prob_text": e[2] if len(e) > 2 else None}
                        for e in ents],
        })
    dist = Counter(x["state"] for x in out)
    return {
        "schema": "lottery_desc_blocks/v0.1",
        "generator": rel(pathlib.Path(__file__)),
        "source": rel(DESC_CHS),
        "blocks": len(out),
        "state_dist": dict(dist),
        "notes": DESC_NOTES,
        "items": out,
    }


# ── 深挖 B：运行时替换 ───────────────────────────────────────────
REPL_NOTES = (
    "optional_pool_replace_data 185 行，字段 lottery_id / lottery_replace_id / item_no / "
    "replace_reward。语义：第 lottery_replace_id 期把 lottery_id 池的 item_no 格换成 "
    "replace_reward 指向的子池（item_no 缺失 = 整池替换，实测 64 行）。"
    "replace_reward 全为池号（185 个里 177 个在 base 池表里），不是道具 id。"
    "★ 8 个替换目标（391809/391810/391811/391812/391835/391836/391845/391846）"
    "超出静态池上限 391793，且 5 个服都没有这些池 ⇒ 更新期次才有的池，"
    "静态层拿不到，标 unresolved，不编造内容。"
    "optional_version_data 30 行把「活动期」与 lottery_replace_id 关联（该表只出现奇数期号），"
    "替换表本身有 64 个期号 ⇒ 34 期缺少版本元数据。"
    "这就是 runtime_final 恒为 unresolved 的机制来源：静态表存的是基础期，"
    "实际每期会换，静态层无法确定「现在跑的是哪一期」。"
)


def build_runtime_replace(pools: set[int], pool_index: dict[int, list[dict]]) -> dict:
    t = P.load("optional_pool_replace_data")
    entries = []
    missing = []
    for r in t["rows"]:
        v = r.get("values") or {}
        lid = _int(_val(v.get("lottery_id")))
        rid = _int(_val(v.get("lottery_replace_id")))
        no = _int(_val(v.get("item_no")))
        rw = _int(_val(v.get("replace_reward")))
        state = STATE_VERIFIED if rw in pools else STATE_UNRESOLVED
        if state == STATE_UNRESOLVED and rw is not None:
            missing.append(rw)
        e = {
            "lottery_id": lid,
            "replace_id": rid,
            "item_no": no,
            "replace_reward": rw,
            "whole_pool": no is None,
            "state": state,
        }
        if state == STATE_VERIFIED:
            e["replace_items"] = [
                {"slot": c["item_no"], "item_id": c["item_id"],
                 "count": c["item_count"], "note": c["note"]}
                for c in pool_index.get(rw) or []
            ]
        entries.append(e)

    vt = P.load("optional_version_data")
    vids = sorted({_int(_val((r.get("values") or {}).get("lottery_replace_id")))
                   for r in vt["rows"]} - {None})
    rids = sorted({e["replace_id"] for e in entries if e["replace_id"] is not None})
    return {
        "schema": "lottery_runtime_replace/v0.1",
        "generator": rel(pathlib.Path(__file__)),
        "source_table": "optional_pool_replace_data",
        "rules": len(entries),
        "verified": sum(1 for e in entries if e["state"] == STATE_VERIFIED),
        "unresolved": len(entries) - sum(1 for e in entries if e["state"] == STATE_VERIFIED),
        "replace_ids": len(rids),
        "version_known_ids": len(vids),
        "ids_without_version": len(set(rids) - set(vids)),
        "unresolved_target_pools": sorted(set(missing)),
        "affected_pools": sorted({e["lottery_id"] for e in entries if e["lottery_id"]}),
        "notes": REPL_NOTES,
        "entries": entries,
    }


# ── 服身份 ───────────────────────────────────────────────────────
SERVER_NOTES = (
    "★ 5 个 component 实际只有 3 套内容：kj1 ≡ kjxq（23,286 行逐键奖励 0 差异）、"
    "yk ≡ ykxq（23,281 行 0 差异）。base 是全量底座。"
    "官方 oversea_table_map_data（2,651 条 主表→覆盖表 映射，需 "
    "script_table_replay(int_keys_only=False) 才能解，默认会把这些字符串键全丢掉）"
    "记录 12 个服后缀；其中 reward_pool_data 官方映射到 ykxq。"
    "但实测磁盘上 reward_pool_data 覆盖表只有 kj1(237 行)/kjxq(237 行)/yk(162 行) 有真实数据，"
    "其余 10 个后缀是 0 行空壳 ⇒ 「官方映射」描述的是加载关系，不等于该服有差异。"
    "带「异变核芯-极光狙击」的是 kj 系（简单生存服特征），yk 系没有。"
)


def build_server_identity() -> dict:
    # 行级对比（用 reward_raw，不用字节）
    by = defaultdict(dict)
    counts = Counter()
    for r in LS.iter_pe1103_rows():
        by[r["component"]][(r["pool_key"], r["item_no"])] = r["reward_raw"]
        counts[r["component"]] += 1

    pairs = [("kj1", "kjxq"), ("yk", "ykxq"), ("base", "kj1"), ("base", "yk")]
    cmp = []
    for a, b in pairs:
        if a not in by or b not in by:
            continue
        ka, kb = set(by[a]), set(by[b])
        diff = sum(1 for k in ka & kb if by[a][k] != by[b][k])
        cmp.append({
            "a": a, "b": b,
            "a_rows": len(ka), "b_rows": len(kb),
            "common": len(ka & kb),
            "reward_diff": diff,
            "only_a": len(ka - kb),
            "only_b": len(kb - ka),
            "equivalent": diff == 0 and not (ka - kb) and not (kb - ka),
        })

    official = {}
    srv_count = Counter()
    if OVERSEA_MAP.is_file():
        m, _ = R.replay_module(OVERSEA_MAP, int_keys_only=False)
        suf = re.compile(r"_auto_oversea_data_([a-z0-9]+)$")
        for k, v in m.items():
            if not isinstance(v, str):
                continue
            g = suf.search(v)
            if not g:
                continue
            srv_count[g.group(1)] += 1
            if k.startswith("com.cdata."):
                official[k[len("com.cdata."):]] = {"oversea_table": g.group(0), "suffix": g.group(1)}
    return {
        "schema": "lottery_server_identity/v0.1",
        "generator": rel(pathlib.Path(__file__)),
        "components": sorted(counts),
        "rows_per_component": dict(sorted(counts.items())),
        "equivalence": cmp,
        "official_oversea_map": {
            "source": rel(OVERSEA_MAP),
            "entries": len(official),
            "suffix_table_counts": dict(srv_count.most_common()),
        },
        "lottery_tables_official": {
            k: v for k, v in sorted(official.items())
            if "lottery" in k or "reward_pool" in k or "desc_info" in k
        },
        "notes": SERVER_NOTES,
    }


# ── 总装 ─────────────────────────────────────────────────────────
def build_all() -> dict[str, dict]:
    pools, pool_keys = base_pool_index()
    return {
        "child_pools": build_child_pools(pools),
        "activities": build_activities(pool_keys),
        "desc_blocks": build_desc_blocks(pools),
        "runtime_replace": build_runtime_replace(pool_keys, pools),
        "servers": build_server_identity(),
    }


__all__ = [
    "build_all", "build_child_pools", "build_activities",
    "build_desc_blocks", "build_runtime_replace", "build_server_identity",
    "base_pool_index",
]
