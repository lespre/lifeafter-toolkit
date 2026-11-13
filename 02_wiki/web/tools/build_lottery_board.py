#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_lottery_board.py — 把分服奖池产物接成 wiki 板

产出 `02_wiki/web/data/boards/lottery_servers.json`（build_wiki.py 会派生同名 .js）。

## 数据体量策略

分服产物是十万行级，直接铺成 items 会让页面卡死（前端是 `file://` 打开，
不能用 fetch，只能整块 <script src> 加载）。

所以按「池」聚合，只存**不重复的部分**：

  · `cells`  = base 服的每一格（全量唯一）
  · `ov`     = 各分服相对 base 的**覆盖格**（只存 same/replaced/added）
  · 前端的「某服全量」= cells 打底 + ov 覆盖，与产物的对应行一一对应

规模从几十 MB 降到 ~2MB，且不丢任何一格。

## 数据源（2026-11-07 起）

`LOTTERY_POOL_PE1103_v01` —— 雷电模拟器 14 · 2026-11-03 设备包（PE 侧）
按 file_id 精确取件解码的冻结数据集。字段名与旧分服产物同构
（component / pool_key / item_no / item_id / item_count / note / prob_note /
diff），故可直接复用同一套聚合逻辑。

旧口径（9 月 PC 侧冻结产物 `LOTTERY_POOL_RESOLVED_v01`）已下线：
它把 391794~391873 共 79 个池登记为 `content_missing`（"池内容未随包下发"），
而 11-03 设备包里这 79 个池**每一格都有内容** —— 缺口登记已撤销。

## 口径铁律

- 键 `(pool_key, item_no)` 与奖励原值来自同一冻结数据集，不跨源拼字段。
- 差异只在同池同格、与 base 之间计算，禁止跨服比 slot。
- `runtime_final_state` 恒为 unresolved。

用法：
  python 02_wiki/web/tools/build_lottery_board.py            # 预览
  python 02_wiki/web/tools/build_lottery_board.py --apply    # 落盘
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import lottery_servers as LS  # noqa: E402
import rebuild_lottery_periods as RLP  # noqa: E402
from la_paths import WEB, rel  # noqa: E402

TREE = RLP.TREE

# ★ 数据源：11-03 雷电设备包（PE 侧）按 file_id 精确取件解码的冻结数据集。
#   旧口径 LOTTERY_POOL_SERVERS_v01（9 月 PC 侧）已下线。
PE1103_DIR = WEB / "site_data" / "LOTTERY_POOL_PE1103_v01"
PE1103_ROWS = PE1103_DIR / "rows.jsonl"
# 补充维度仍取旧产物的 enrich 目录（子池/活动/运行时替换/服等价性，
#   这几张表在 11-03 树里同样存在，但口径与旧 enrich 一致，复用可避免重复推导）
PRODUCT = WEB / "site_data" / "LOTTERY_POOL_SERVERS_v01"
OUT = WEB / "data" / "boards" / "lottery_servers.json"

BASE = "base"
CHANNELS = ("kj1", "kjxq", "yk", "ykxq")

NOTES = (
    "【口径】每条 = 一个奖池；cells 是经典服（base）逐格，ov 是各分服相对 base 的覆盖格。"
    "前端渲染某服视图 = cells 打底 + ov 覆盖。"
    "【数据源】雷电模拟器 14 · 2026-11-03 设备包（PE 侧），按 file_id 精确取件解码的"
    "冻结数据集 LOTTERY_POOL_PE1103_v01：base 1,839 池 / 24,245 格，"
    "kj1/kjxq 各 24,250 行（8 格替换 + 5 格新增 + 224 格同值），yk/ykxq 各 24,245 行"
    "（18 格替换 + 144 格同值）。复合键 (pool_key, item_no) 与奖励原值同源直读，不跨源拼字段。"
    "【差异】diff 只在同池同格对比：same=奖励相同仅补字段、replaced=被换、added=该服新增、"
    "inherit=该服没覆盖这一格、沿用 base。"
    "【服】5 个服实际只有 3 套内容：kj1≡kjxq、yk≡ykxq（逐键奖励 0 差异，已由门禁 G12 复算）。"
    "【未证明】runtime_final_state=unresolved：optional_pool_replace_data 会在运行时按「期」替换奖励，"
    "静态表只是基础期，不是当前实发。"
    "【缺口登记已撤销】旧口径把 391794~391873 共 79 个池登记为 content_missing"
    "（「池内容未随包下发」）；11-03 设备包里这 79 个池每一格都有内容，"
    "故本板不再有 content_missing 条目。"
    "【分片】inc 分片未并入（编码未确证）、del 分片 11-03 包内不存在。"
)


def sha256_of(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(name: str):
    p = PRODUCT / name
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def cells_of(r: dict) -> list:
    """一格压成 [slot, item_id, count, note, prob]（None 保留，前端可判空）。"""
    return [r.get("item_no"), r.get("item_id"), r.get("item_count"),
            r.get("note"), r.get("prob_note")]


def iter_pe1103_rows():
    """流式读 11-03 雷电设备包（PE 侧）冻结数据集的行。

    字段名与旧分服产物同构：component / pool_key / item_no / item_id /
    item_count / note / prob_note / diff。产物不存在时抛 FileNotFoundError
    （不静默降级 —— 静默会让本板悄悄回到旧口径）。
    """
    if not PE1103_ROWS.is_file():
        raise FileNotFoundError(
            "11-03 奖池数据集不存在：%s（先跑 build_lottery_pool_pe1103.py）" % rel(PE1103_ROWS))
    with PE1103_ROWS.open(encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def _uleb(buf: bytes, i: int, n: int) -> tuple[int, int]:
    """读一个 ULEB128；越界或多于 5 字节判失败。"""
    value = 0
    shift = 0
    while i < n and shift <= 28:
        b = buf[i]
        i += 1
        value |= (b & 0x7F) << shift
        if not b & 0x80:
            return value, i
        shift += 7
    raise ValueError("uleb overrun")


def nil_key_value(raw: bytes) -> dict[int, int]:
    """解 `reward_pool_no_item_no_list` 表体里的 [池号][值] 连续对。

    这张表是 0x73 包装的 legacy 表体（`x{` + u32 长度 + 表体），表体里是一串
    `[池号 ULEB][值 ULEB]`。表头那个 code-object 解析器对这张表解出 0 行，
    所以这里只**取键**：键限定 300000~999999，值限定 <=100000，并只保留
    「连续整数段 >= 5」的键 —— 孤立命中一律当字节噪声丢掉。

    返回值原样带出，不赋予「槽位数」语义：实测值域 1~500（391848 处是 157），
    与池内格数不吻合，只能当结构项数看。
    """
    at = raw.find(b"x{")
    if at < 0 or at + 6 > len(raw):
        return {}
    n = len(raw)
    i = at + 6
    pairs: dict[int, int] = {}
    while i < n - 3:
        try:
            key, j = _uleb(raw, i, n)
        except ValueError:
            i += 1
            continue
        if not 300000 <= key <= 999999:
            i += 1
            continue
        try:
            value, k = _uleb(raw, j, n)
        except ValueError:
            i += 1
            continue
        if value > 100000:
            i += 1
            continue
        pairs[key] = value
        i = k

    keep: dict[int, int] = {}
    run: list[int] = []
    for key in sorted(pairs):
        if run and key == run[-1] + 1:
            run.append(key)
            continue
        if len(run) >= 5:
            for x in run:
                keep[x] = pairs[x]
        run = [key]
    if len(run) >= 5:
        for x in run:
            keep[x] = pairs[x]
    return keep


def gap_pool_index() -> dict[int, dict]:
    """池结构表里有、内容表里一格都没有的池（分片未随包下发）。

    判据（全部可复算）：
      ① `reward_pool_no_item_no_list` 的 [池号][值] 对里有该池 ⇒ 池本身存在；
      ② `nucleus_lottery_pool_data.reward_pool_id` 直接引用该池 ⇒ 归属异变核芯，
         档位名取同行的 `reward_display_group_name`；
      ③ 内容侧不参与判断 —— 内容表缺失是既定事实，这里的池天然是 0 格。
    """
    nil_p = TREE / "reward_pool_no_item_no_list.py"
    if not nil_p.is_file():
        return {}
    exists = nil_key_value(nil_p.read_bytes())
    if not exists:
        return {}

    owner: dict[int, dict] = {}
    np_p = TREE / "nucleus_lottery_pool_data.py"
    chs_p = TREE / "nucleus_lottery_pool_data_chs.py"
    if np_p.is_file():
        try:
            tab = RLP.Table(np_p, chs_p if chs_p.is_file() else None)
        except Exception:
            tab = None
        if tab is not None:
            for _k, row in tab.by_key.items():
                v = row["values"]
                pk = v.get("reward_pool_id")
                if not isinstance(pk, int) or pk in owner:
                    continue
                owner[pk] = {
                    "tier": v.get("reward_display_group_name"),
                    "group": v.get("nucleus_lottery_pool_id"),
                }

    out: dict[int, dict] = {}
    for pk, count in exists.items():
        o = owner.get(pk) or {}
        out[pk] = {"count": count, "tier": o.get("tier"), "group": o.get("group")}
    return out


def pool_name(pk: int, cells: list) -> str:
    notes = []
    for c in cells:
        n = (c[3] or "").strip()
        if n and n not in notes:
            notes.append(n)
        if len(notes) >= 3:
            break
    tail = " / ".join(notes) if notes else "（无中文备注）"
    return "%d · %s" % (pk, tail)


def build() -> dict:
    man = load_json("manifest.json") or {}
    child = load_json("child_pools.json") or {}
    acts = load_json("activities.json") or {}
    repl = load_json("runtime_replace.json") or {}

    # 池 → 活动（多对多，来自 activities.pool_to_activities）
    p2a = {int(k): v for k, v in (acts.get("pool_to_activities") or {}).items()}
    act_lid = {e.get("activity_key"): e.get("lottery_id")
               for e in (acts.get("entries") or [])}
    # 池 → 子池展开（父池格上标注「抽子池 N 次」）
    child_by_parent: dict[tuple, dict] = {}
    for e in (child.get("entries") or []):
        child_by_parent[(e["parent_pool"], e["parent_slot"])] = e
    # 池 → 会被运行时替换的格
    repl_by_pool: dict[int, list] = {}
    for e in (repl.get("entries") or []):
        repl_by_pool.setdefault(e["lottery_id"], []).append(e)

    # ── 扫 rows：一次流式，按池分桶 ────────────────────────────
    #   数据源 = 11-03 雷电设备包（PE 侧）冻结数据集。
    #   ★ 旧口径（9 月 PC 侧 LOTTERY_POOL_SERVERS_v01）已下线。
    base_cells: dict[int, list] = {}
    ov: dict[str, dict[int, list]] = {c: {} for c in CHANNELS}
    order: list[int] = []
    for r in iter_pe1103_rows():
        comp = r.get("component")
        pk = r.get("pool_key")
        if pk is None:
            continue
        if comp == BASE:
            if pk not in base_cells:
                base_cells[pk] = []
                order.append(pk)
            base_cells[pk].append(cells_of(r))
        elif comp in ov and r.get("diff") in ("same", "replaced", "added"):
            ov[comp].setdefault(pk, []).append(cells_of(r))

    for pk in base_cells:
        base_cells[pk].sort(key=lambda c: (c[0] is None, c[0]))

    items = []
    st: dict[str, int] = {}
    # ★ 池集合必须取 base ∪ 各服 overlay：只在分服出现的池（如 391711 的 5 个
    #   异变核芯）base 里没有，只从 base 取会整池漏掉 —— 而它恰恰是最强的分服差异证据。
    all_pools = set(base_cells)
    for c in CHANNELS:
        all_pools |= set(ov[c])
    for pk in sorted(all_pools):
        cells = base_cells.get(pk) or []
        rec = {
            "id": "pool_%d" % pk,
            "name": pool_name(pk, cells) if cells else "%d · 仅分服有此池" % pk,
            "evidence": "structure",
            "state": "verified" if cells else "channel_only",
            "evidence_level": "static/candidate",
            "source": "reward_pool_data",
            "pool": pk,
            "格数": len(cells),
            "cells": cells,
            "source_ref": {
                "table": "reward_pool_data",
                "row_key": "%d:*" % pk,
                "note": ("复合键 (pool_key, item_no) 与奖励原值、中文备注、概率同源直读"
                         "自 11-03 雷电设备包（PE 侧）按 file_id 精确取件解码的冻结数据集"),
            },
        }

        # 分服覆盖：只写非空，省体积
        o = {}
        for c in CHANNELS:
            got = ov[c].get(pk)
            if got:
                o[c] = sorted(got, key=lambda x: (x[0] is None, x[0]))
        if o:
            rec["ov"] = o
            rec["覆盖格数"] = {c: len(rows) for c, rows in o.items()}
            if not cells:
                # 仅分服存在的池：格数取该服覆盖行数；名字取第一格中文备注
                rec["格数"] = max(len(rows) for rows in o.values())
                first = next((r[3] for rows in o.values() for r in rows if r[3]), None)
                if first:
                    rec["name"] = "%d · %s（仅分服）" % (pk, first)

        # 活动绑定（多对多）
        if pk in p2a:
            rec["活动"] = p2a[pk]
            rec["类别"] = "活动 " + "、".join(str(x) for x in p2a[pk][:3])

        # 子池标记
        kids = [(s, e["child_pool"], e["times"])
                for (pp, s), e in child_by_parent.items() if pp == pk]
        if kids:
            rec["子池"] = [{"slot": s, "child_pool": cp, "times": t} for s, cp, t in sorted(kids)]

        # 运行时替换标记
        if pk in repl_by_pool:
            rs = repl_by_pool[pk]
            rec["运行时替换"] = {
                "规则数": len(rs),
                "整池替换": sum(1 for e in rs if e.get("whole_pool")),
                "期数": len({e.get("replace_id") for e in rs}),
                "未解析目标": sorted({e["replace_reward"] for e in rs
                                      if e.get("state") == "unresolved"}),
            }

        st[rec["state"]] = st.get(rec["state"], 0) + 1
        items.append(rec)

    # ── 缺口池登记已撤销（2026-11-07）────────────────────────────
    #   旧口径按「reward_pool_data 的 inc/del 分片未随包下发」把 391794~391873
    #   共 79 个池登记为 state=content_missing / evidence_level=existence-only。
    #   11-03 雷电设备包按 file_id 精确取件后，这 79 个池**每一格都有内容**
    #   （已在 all_pools 里正常出条目），故不再追加缺口条目。
    #   gap_pool_index() 保留在模块里：它是「池结构表有、内容表没有」这个
    #   判据的可复算实现，未来若再遇分片缺失可直接复用。
    gaps = gap_pool_index()
    still_missing = [pk for pk in sorted(gaps) if pk not in all_pools]
    if still_missing:
        print("⚠ 仍有 %d 个池在结构表里但内容表无格：%s"
              % (len(still_missing), still_missing[:20]))
    else:
        print("缺口池复核：结构表里的池在 11-03 内容表中全部有格，无需登记 content_missing")

    pe_rows_sha = sha256_of(PE1103_ROWS) if PE1103_ROWS.is_file() else "0" * 64
    board = {
        "meta": {
            "name": "奖池分服全量 · 5 服池级对照（经典服 / 简单生存服）",
            "category": "四、奖池 / （二）分服全量池对照",
            "source_server": (
                "雷电模拟器 14 · 2026-11-03 设备包（PE 侧）："
                "base 1,839 池 / 24,245 格 + kj1/kjxq/yk/ykxq 四服覆盖表；"
                "按 file_id 精确取件解码的冻结数据集提供权威复合键与中文字段"
            ),
            "package_sha": pe_rows_sha,
            "generated": "2026-11-07",
            "evidence": "structure",
            "notes": NOTES,
            "state_summary": st,
            "runtime_final_state": "unresolved",
            "provenance": {
                "contract_version": 3,
                "contract": "frozen-audited-artifact",
                "audit_status": "passed",
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
                "source_locks": [
                    {
                        "source_id": "lottery-pool-pe1103-v01",
                        "sha256": pe_rows_sha,
                        "bytes": PE1103_ROWS.stat().st_size if PE1103_ROWS.is_file() else 0,
                        "mtime_ns": PE1103_ROWS.stat().st_mtime_ns if PE1103_ROWS.is_file() else 0,
                        "role": "primary",
                        "path": "02_wiki/web/site_data/LOTTERY_POOL_PE1103_v01/rows.jsonl",
                    },
                    {
                        "source_id": "lottery-pool-servers-v01",
                        "sha256": sha256_of(PRODUCT / "rows.jsonl")
                        if (PRODUCT / "rows.jsonl").is_file() else "0" * 64,
                        "bytes": (PRODUCT / "rows.jsonl").stat().st_size
                        if (PRODUCT / "rows.jsonl").is_file() else 0,
                        "mtime_ns": (PRODUCT / "rows.jsonl").stat().st_mtime_ns
                        if (PRODUCT / "rows.jsonl").is_file() else 0,
                        "role": "comparison",
                    },
                ],
                "cross_source_note": (
                    "复合键 (pool_key, item_no) 与奖励原值、中文备注、概率全部取自同一冻结数据集"
                    "（11-03 雷电设备包按 file_id 精确取件解码），**不跨源拼字段**。"
                    "comparison 源锁只是补充维度（子池/活动/运行时替换/服等价性）的来源说明，"
                    "不是本板字段的拼接方。"
                ),
            },
        },
        "items": items,
    }
    return board


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    b = build()
    text = json.dumps(b, ensure_ascii=False, separators=(",", ":"))
    size = len(text.encode("utf-8"))
    print("板 %s" % rel(OUT))
    print("池  : %d 条" % len(b["items"]))
    print("大小: %.2f MB" % (size / 1e6))
    print("状态: %s" % b["meta"]["state_summary"])
    print("\n前 5 池：")
    for it in b["items"][:5]:
        print("  %-46s 格%2d %s" % (it["name"][:46], it["格数"],
                                    ("覆盖 " + str(it.get("覆盖格数"))) if it.get("覆盖格数") else ""))
    if not a.apply:
        print("\n[预览] 未落盘。加 --apply 写入。")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print("\n已写入 %s" % rel(OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
