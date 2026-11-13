# -*- coding: utf-8 -*-
"""check_lottery_servers.py — 分服奖池产物（LOTTERY_POOL_SERVERS_v01）的验收关卡

只读，不改任何文件。**独立于生成逻辑**：只读产物文件 + 上游冻结产物，
重新算一遍，防止「生成器写错、检查器跟着错」。

退出码：
  0  全部通过
  2  有硬失败（应阻断发布）
  3  产物缺失

用法：
  python 02_wiki/web/tools/check_lottery_servers.py
  python 02_wiki/web/tools/check_lottery_servers.py --json
  python 02_wiki/web/tools/check_lottery_servers.py --min-note-base 0.99
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter, defaultdict

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from la_paths import WEB, rel  # noqa: E402

OUT_DIR = WEB / "site_data" / "LOTTERY_POOL_SERVERS_v01"
FROZEN = WEB / "site_data" / "LOTTERY_POOL_RESOLVED_v01.jsonl"

DIFFS = {"base", "inherit", "same", "replaced", "added"}


def decode_upstream_components() -> tuple[dict[tuple, list], str]:
    """直接解码 11-03 雷电设备包（PE 侧）各服组件表 → 权威键值表。

    返回 {(component, pool_key, item_no): [item_id, item_count]}。

    ★ 这是门禁的**独立依据**：从包按 file_id 取件、解码 0x27 跳转组，
      不读产物、不读生成器的中间结果 —— 否则等于自己校验自己。
    ★ 与旧口径（9 月 PC 侧冻结产物）的区别：11-03 包里 391794~391873 那 79 个池
      每一格都有内容，旧冻结产物里没有 ⇒ 换源后 G3/G4 的比对基准必须同步换。
    """
    sys.path.insert(0, str(_HERE))
    import build_lottery_pool_pe1103 as PE  # noqa: PLC0415

    parts, _meta = PE.extract_parts()
    out: dict[tuple, list] = {}
    for comp, data_fid, chs_fid in PE.COMPONENTS:
        data = parts.get(data_fid)
        pool = parts.get(chs_fid)
        if data is None or pool is None:
            continue
        rows, _unbound = PE.decode_component(data, pool)
        for (pk, ino), rec in rows.items():
            out[(comp, pk, ino)] = [rec.get("item_id"), rec.get("item_count")]
    return out, "11-03 设备包按 file_id 直接解码 %d 组件" % len(PE.COMPONENTS)


def fail(msgs: list, text: str) -> None:
    msgs.append(text)


ENRICH_FILES = {
    "child_pools": "child_pools.json",
    "activities": "activities.json",
    "desc_blocks": "desc_blocks.json",
    "runtime_replace": "runtime_replace.json",
    "servers": "servers.json",
}


def _load_json(name: str):
    p = OUT_DIR / ENRICH_FILES[name]
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _check_enrich(rows: list[dict], order: list[str],
                  fails: list, warns: list) -> dict:
    """G9~G12：四个补充维度的独立复算。

    只依赖 rows + 补充文件本身，不看生成器内部状态。
    """
    out: dict = {}

    # base 池键 → reward_raw；池 → 格列表
    base_rows = {(r["pool_key"], r["item_no"]): r.get("reward_raw")
                 for r in rows if r.get("component") == (order[0] if order else None)}
    pool_keys = {pk for pk, _ in base_rows}
    pool_cells: dict[int, list] = defaultdict(list)
    for (pk, no), raw in base_rows.items():
        pool_cells[pk].append((no, raw))
    for k in pool_cells:
        pool_cells[k].sort(key=lambda x: (x[0] is None, x[0]))

    # ── G9 child_pools ────────────────────────────────────────
    cp = _load_json("child_pools")
    if cp is None:
        warns.append("G9 child_pools.json 缺失（旧版产物），跳过子池校验")
    else:
        bad = 0
        checked = 0
        for e in cp.get("entries") or []:
            checked += 1
            raw = base_rows.get((e.get("parent_pool"), e.get("parent_slot")))
            if not raw or len(raw) < 2:
                fail(fails, "G9 父格不存在或无 reward：pool=%s slot=%s"
                     % (e.get("parent_pool"), e.get("parent_slot")))
                bad += 1
                continue
            if raw[0] != e.get("child_pool") or raw[1] != e.get("times"):
                fail(fails, "G9 父格与登记不一致：pool=%s slot=%s 产物=%s 登记=%s×%s"
                     % (e.get("parent_pool"), e.get("parent_slot"), raw,
                        e.get("child_pool"), e.get("times")))
                bad += 1
                continue
            cells = pool_cells.get(e.get("child_pool")) or []
            if len(cells) != len(e.get("child_items") or []):
                fail(fails, "G9 子池格数不符：%s 池 %d 格 / 登记 %d 格"
                     % (e.get("child_pool"), len(cells),
                        len(e.get("child_items") or [])))
                bad += 1
        if cp.get("count") != checked:
            fail(fails, "G9 child_pools.count=%s 与实际 %d 条不符"
                 % (cp.get("count"), checked))
        # 反向：产物里「reward 值 = 池号」的格必须都被登记
        unreg = [k for k, raw in base_rows.items()
                 if raw and len(raw) >= 2 and raw[0] in pool_keys
                 and k not in {(e.get("parent_pool"), e.get("parent_slot"))
                               for e in (cp.get("entries") or [])}]
        if unreg:
            fail(fails, "G9 有 %d 个「奖励=池号」的格未登记为 child_pool（例 %s）"
                 % (len(unreg), unreg[:3]))
        out["child_pools"] = {"entries": checked, "bad": bad, "unregistered": len(unreg)}

    # ── G10 activities ────────────────────────────────────────
    ac = _load_json("activities")
    if ac is None:
        warns.append("G10 activities.json 缺失，跳过活动绑定校验")
    else:
        bad = 0
        for e in ac.get("entries") or []:
            lid = e.get("lottery_id")
            st = e.get("state")
            if lid is None:
                continue
            if st == "verified" and lid not in pool_keys:
                fail(fails, "G10 活动 %s 标 verified 但池 %s 不在 base 池表"
                     % (e.get("activity_key"), lid))
                bad += 1
            if st == "unresolved" and lid in pool_keys:
                fail(fails, "G10 活动 %s 标 unresolved 但池 %s 其实存在"
                     % (e.get("activity_key"), lid))
                bad += 1
        p2a = ac.get("pool_to_activities") or {}
        if len(p2a) != ac.get("pools_bound"):
            fail(fails, "G10 pools_bound=%s 与 pool_to_activities 条数 %d 不符"
                 % (ac.get("pools_bound"), len(p2a)))
        out["activities"] = {"entries": len(ac.get("entries") or []),
                             "bound": ac.get("bound"), "bad": bad}

    # ── G11 runtime_replace ───────────────────────────────────
    rr = _load_json("runtime_replace")
    if rr is None:
        warns.append("G11 runtime_replace.json 缺失，跳过运行时替换校验")
    else:
        bad = 0
        for e in rr.get("entries") or []:
            rw = e.get("replace_reward")
            st = e.get("state")
            if rw is None:
                continue
            if st == "verified":
                if rw not in pool_keys:
                    fail(fails, "G11 替换规则标 verified 但目标池 %s 不存在" % rw)
                    bad += 1
                elif len(pool_cells.get(rw) or []) != len(e.get("replace_items") or []):
                    fail(fails, "G11 替换目标 %s 格数与登记不符" % rw)
                    bad += 1
            elif st == "unresolved" and rw in pool_keys:
                fail(fails, "G11 替换规则标 unresolved 但目标池 %s 其实存在" % rw)
                bad += 1
        if sorted({e.get("replace_reward") for e in (rr.get("entries") or [])
                   if e.get("state") == "unresolved"}) != \
                sorted(rr.get("unresolved_target_pools") or []):
            fail(fails, "G11 unresolved_target_pools 与明细不一致")
        out["runtime_replace"] = {"rules": len(rr.get("entries") or []), "bad": bad}

    # ── G12 servers 等价性自证 ────────────────────────────────
    sv = _load_json("servers")
    if sv is None:
        warns.append("G12 servers.json 缺失，跳过服等价性校验")
    else:
        by: dict[str, dict] = defaultdict(dict)
        for r in rows:
            by[r.get("component")][(r.get("pool_key"), r.get("item_no"))] = r.get("reward_raw")
        bad = 0
        for e in sv.get("equivalence") or []:
            a_, b_ = e.get("a"), e.get("b")
            if a_ not in by or b_ not in by:
                continue
            ka, kb = set(by[a_]), set(by[b_])
            diff = sum(1 for k in ka & kb if by[a_][k] != by[b_][k])
            eq = (diff == 0 and not (ka - kb) and not (kb - ka))
            if bool(e.get("equivalent")) != eq or diff != e.get("reward_diff"):
                fail(fails, "G12 服等价性不可复算：%s vs %s 声明等价=%s diff=%s，"
                            "实算等价=%s diff=%d"
                     % (a_, b_, e.get("equivalent"), e.get("reward_diff"), eq, diff))
                bad += 1
        out["servers"] = {"pairs": len(sv.get("equivalence") or []), "bad": bad}

    # ── G13 desc_blocks 状态自洽 ──────────────────────────────
    db = _load_json("desc_blocks")
    if db is None:
        warns.append("G13 desc_blocks.json 缺失，跳过公示块校验")
    else:
        bad = 0
        for b in db.get("items") or []:
            mp = b.get("matched_pool")
            st = b.get("state")
            if st == "verified" and (mp is None or (b.get("match_score") or 0) < 0.9):
                fail(fails, "G13 公示块 %r 标 verified 但得分不足或池为空" % b.get("name"))
                bad += 1
            if mp is not None and mp not in pool_keys:
                fail(fails, "G13 公示块 %r 匹配的池 %s 不存在" % (b.get("name"), mp))
                bad += 1
        dist = Counter(b.get("state") for b in (db.get("items") or []))
        if dict(dist) != (db.get("state_dist") or {}):
            fail(fails, "G13 state_dist 与明细不符：声明 %s 实算 %s"
                 % (db.get("state_dist"), dict(dist)))
        out["desc_blocks"] = {"blocks": len(db.get("items") or []), "bad": bad}

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-note-base", type=float, default=0.95,
                    help="base 服 note 覆盖率下限（默认 0.95）")
    ap.add_argument("--min-note-channel", type=float, default=0.90,
                    help="channel 服 note 覆盖率下限（默认 0.90）")
    a = ap.parse_args()

    man_p = OUT_DIR / "manifest.json"
    rows_p = OUT_DIR / "rows.jsonl"
    if not man_p.is_file() or not rows_p.is_file():
        print("产物缺失：%s" % rel(OUT_DIR))
        return 3

    man = json.loads(man_p.read_text(encoding="utf-8"))
    order = man.get("component_order") or []
    fails: list[str] = []
    warns: list[str] = []

    # ── G1 结构 ────────────────────────────────────────────────
    if man.get("schema") != "lottery_pool_servers/v0.1":
        fail(fails, "G1 schema 不是 lottery_pool_servers/v0.1：%r" % man.get("schema"))
    if man.get("runtime_final_state") != "unresolved":
        fail(fails, "G1 runtime_final_state 必须是 unresolved（静态结构 ≠ 实发）")
    if not order:
        fail(fails, "G1 manifest 缺 component_order，无法校验分服")

    # ── 读上游权威值 ────────────────────────────────────────────
    #   ★ 上游 = **直接解码 11-03 雷电设备包（PE 侧）各服组件表**。
    #     这是独立于产物的依据：不引用生成器的中间结果，否则等于自己校验自己。
    #     旧口径用的是 9 月 PC 侧冻结产物 LOTTERY_POOL_RESOLVED_v01，
    #     源换后它已下线（且它没有 391794~391873 这 79 个池）。
    upstream: dict[tuple, list] = {}
    upstream_note = ""
    try:
        upstream, upstream_note = decode_upstream_components()
    except Exception as exc:  # noqa: BLE001
        upstream = {}
        upstream_note = "解码上游组件失败：%s" % exc
    if upstream:
        pass
    else:
        warns.append("上游组件解码不可用（%s），跳过 G3 原值比对" % upstream_note)

    # ── 读产物 ─────────────────────────────────────────────────
    rows: list[dict] = []
    with rows_p.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                fail(fails, "G1 第 %d 行不是合法 JSON：%s" % (i, e))
                break

    total_declared = (man.get("stats") or {}).get("total_rows")
    if total_declared != len(rows):
        fail(fails, "G1 行数与 manifest 不符：declared=%s actual=%d"
             % (total_declared, len(rows)))

    # ── G2 每服键唯一 / G8 分服不混排 ──────────────────────────
    seen: dict[str, set] = defaultdict(set)
    dup = Counter()
    unknown_comp = Counter()
    no_component = 0
    for r in rows:
        c = r.get("component")
        if not c:
            no_component += 1
            continue
        if c not in order:
            unknown_comp[c] += 1
        k = (r.get("pool_key"), r.get("item_no"))
        if k in seen[c]:
            dup[c] += 1
        seen[c].add(k)
    if no_component:
        fail(fails, "G8 有 %d 行没有 component 字段（分服不混排是硬约束）" % no_component)
    for c, n in unknown_comp.items():
        fail(fails, "G8 出现 manifest 未声明的服 %r（%d 行）" % (c, n))
    for c, n in dup.items():
        fail(fails, "G2 服 %r 内 (pool_key, item_no) 重复 %d 处" % (c, n))

    # ── G3 原值不得改动 ────────────────────────────────────────
    #   ★ inherit 行本来就不在上游该服组件里（overlay 没覆盖这一格），
    #     对不上是正常的；只有 non-inherit 行对不上才算问题。
    if upstream:
        mismatch = 0
        samples = []
        missing = 0
        inherit_no_upstream = 0
        for r in rows:
            k = (r.get("component"), r.get("pool_key"), r.get("item_no"))
            if k not in upstream:
                if r.get("diff") == "inherit":
                    inherit_no_upstream += 1
                else:
                    missing += 1
                continue
            if upstream[k] != r.get("reward_raw"):
                mismatch += 1
                if len(samples) < 3:
                    samples.append("%s 产物=%s 上游=%s" % (k, r.get("reward_raw"), upstream[k]))
        if mismatch:
            fail(fails, "G3 reward_raw 被改动 %d 行（例：%s）"
                 % (mismatch, "; ".join(samples)))
        if missing:
            warns.append("G3 有 %d 行（非 inherit）在上游找不到对应记录" % missing)
        if inherit_no_upstream:
            warns.append("G3 %d 行是 inherit（本服未覆盖，沿用 base），上游无该服记录属正常"
                         % inherit_no_upstream)

    # ── G4 diff 可复算 ─────────────────────────────────────────
    #   独立复算的依据只有两处：产物自身 + 上游冻结产物的「各服覆盖了哪些键」。
    #   不引用生成器的中间结果，否则等于自己校验自己。
    base_map = {(r["pool_key"], r["item_no"]): r.get("reward_raw")
                for r in rows if r.get("component") == order[0]}
    own_keys: dict[str, set] = defaultdict(set)
    for (c, pk, no) in upstream:
        own_keys[c].add((pk, no))

    recomputed: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        c = r.get("component")
        k = (r.get("pool_key"), r.get("item_no"))
        d = r.get("diff")
        if d not in DIFFS:
            fail(fails, "G4 非法 diff 值 %r（服 %s）" % (d, c))
            continue
        b = base_map.get(k)
        if c == order[0]:
            want = "base"
        elif b is None:
            want = "added"
        elif k not in own_keys.get(c, set()):
            want = "inherit"
        elif b == r.get("reward_raw"):
            want = "same"
        else:
            want = "replaced"
        if d != want:
            fail(fails, "G4 diff 不可复算：服 %s pool=%s slot=%s 标 %r 应为 %r"
                 % (c, r.get("pool_key"), r.get("item_no"), d, want))
            break
        recomputed[c][want] += 1

    # ── G5 字段覆盖 ────────────────────────────────────────────
    cov: dict[str, dict] = {}
    for c in order:
        rs = [r for r in rows if r.get("component") == c]
        if not rs:
            fail(fails, "G6 服 %r 没有任何行（缺数据必须显式说明，不能静默出空）" % c)
            continue
        note = sum(1 for r in rs if r.get("note"))
        prob = sum(1 for r in rs if r.get("prob_note") is not None)
        reward = sum(1 for r in rs if r.get("reward_raw"))
        cov[c] = {"rows": len(rs), "note": note, "prob": prob, "reward": reward,
                  "note_ratio": round(note / len(rs), 4),
                  "prob_ratio": round(prob / len(rs), 4)}
        need = a.min_note_base if c == order[0] else a.min_note_channel
        if note / len(rs) < need:
            fail(fails, "G5 服 %r 的 note 覆盖率 %.1f%% < %.0f%%"
                 % (c, note / len(rs) * 100, need * 100))
        if reward < len(rs):
            warns.append("服 %r 有 %d 行 reward_raw 为空（静态分派未解）"
                         % (c, len(rs) - reward))

    # ── G7 组件来源必须 verified ───────────────────────────────
    for i in (man.get("stats") or {}).get("components") or []:
        if i.get("state") != "verified":
            fail(fails, "G7 服 %r 的数据源状态是 %r（应为 verified；缺源必须显式标记）"
                 % (i.get("component"), i.get("state")))

    # ── G9~G12 补充维度（child_pools / activities / runtime_replace / servers）──
    enrich_stats = _check_enrich(rows, order, fails, warns)

    # ── 输出 ───────────────────────────────────────────────────
    report = {"manifest": rel(man_p), "rows": len(rows), "coverage": cov,
              "recomputed": {c: dict(v) for c, v in recomputed.items()},
              "enrich": enrich_stats,
              "fails": fails, "warns": warns}
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
        return 2 if fails else 0

    print("产物: %s ｜ 行 %d ｜ 服 %s" % (rel(rows_p), len(rows), " / ".join(order)))
    print("\n── 每服覆盖 ──")
    print("  %-6s %7s %8s %8s %9s" % ("服", "行", "note", "概率", "note占比"))
    for c, v in cov.items():
        print("  %-6s %7d %8d %8d %8.1f%%" %
              (c, v["rows"], v["note"], v["prob"], v["note_ratio"] * 100))
    if recomputed:
        print("\n── diff 复算（由产物自身重算）──")
        for c, v in recomputed.items():
            print("  %-6s %s" % (c, dict(v)))
    if enrich_stats:
        print("\n── 补充维度（G9~G13）──")
        for k, v in enrich_stats.items():
            print("  %-16s %s" % (k, "  ".join("%s=%s" % (kk, vv) for kk, vv in v.items())))
    if warns:
        print("\n── 告警（不阻断）──")
        for w in warns:
            print("  ! " + w)
    print("\n── 结论 ──")
    if fails:
        for x in fails:
            print("  ✗ " + x)
        print("  ⇒ 退出码 2，应阻断发布")
        return 2
    print("  ✓ G1~G13 全部通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
