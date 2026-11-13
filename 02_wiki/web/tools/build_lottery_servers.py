#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_lottery_servers.py — 产出「全量 + 分服」奖池解析数据集

## 产出

  `02_wiki/web/site_data/LOTTERY_POOL_SERVERS_v01/manifest.json`
  `02_wiki/web/site_data/LOTTERY_POOL_SERVERS_v01/rows.jsonl`

每行 = 某服某池某一格的最终静态结构，含 item_id / 数量 / 中文备注 /
概率 / 到期 / 广播模板，以及相对 base 的差异标记。

## 与其他产物的关系

- **上游**：`LOTTERY_POOL_RESOLVED_v01.jsonl`（冻结快照，提供权威复合键
  `(pool_key, item_no)` 与奖励原值）+ PE 还原树（提供中文字段）。
- **不改上游**：本脚本只读，不改冻结产物，也不改任何板产物。
- **不替代**：`runtime_final_state` 恒为 `unresolved` —— `optional_pool_replace_data`
  等表会在运行时替换奖励，本产物是**静态结构**，不是当前实发。

## 幂等

同输入 → 字节一致。行按冻结产物文件顺序输出，JSON 键排序固定，
manifest 除 `generated_at` 外全部由输入推导。

用法：
  python 02_wiki/web/tools/build_lottery_servers.py            # 预览（不落盘）
  python 02_wiki/web/tools/build_lottery_servers.py --apply    # 落盘
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import sys
from collections import Counter

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import lottery_servers as LS  # noqa: E402
import lottery_enrich as LE  # noqa: E402
from la_paths import WEB, rel  # noqa: E402

OUT_DIR = WEB / "site_data" / "LOTTERY_POOL_SERVERS_v01"
SCHEMA = "lottery_pool_servers/v0.1"

# 补充维度文件（深挖 A~D 的产出，见 lottery_enrich.py）
ENRICH_ORDER = ("child_pools", "activities", "desc_blocks", "runtime_replace", "servers")

NOTES = (
    "每条 = 某服某池某一格的静态结构；component 字段区分服，禁止跨服比较 slot 序号。"
    "★ 数据源（2026-11-07 起）：雷电模拟器 14 · 2026-11-03 设备包（PE 侧），"
    "按 file_id 精确取件解码的冻结数据集 LOTTERY_POOL_PE1103_v01。"
    "复合键 (pool_key, item_no)、奖励原值、中文备注、概率、到期、广播模板全部同源直读 —— "
    "**不跨源拼字段**（旧口径是从 PC 侧冻结产物拿键、再按 reward 值往 PE 树挂中文字段，属跨源拼接）。"
    "base 1,839 池 / 24,245 格（unbound_rows=0）；kj1/kjxq 各 24,250 行"
    "（inherit 24,013 / same 224 / replaced 8 / added 5）；yk/ykxq 各 24,245 行"
    "（inherit 24,083 / same 144 / replaced 18）。"
    "diff 由上游数据集在解码时逐格与 base 对比得出："
    "same=奖励相同仅补字段 / replaced=奖励被换 / added=base 无此格 / inherit=该服未覆盖、沿用 base。"
    "note 是策划备注，与道具正式名可能不同写法；展示时建议 item_id + note 并列。"
    "probability_semantics：prob_note 是静态权重/概率标注，不含保底与 pity 算法。"
    "runtime_final_state 恒为 unresolved：optional_* 系列表会在运行时替换奖励，本产物不是当前实发结果。"
    "验收由 check_lottery_servers.py 的 G1~G13 逐项复算（键唯一 / diff 自证 / "
    "note 与概率覆盖率 / 服等价性 / 子池 / 活动 / 运行时替换 / 公示块）。"
    "★ 分片：inc 分片未并入（编码未确证）、del 分片 11-03 包内不存在 —— 二者都在 manifest.shards 里如实登记。"
)


def sha256_of(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build() -> tuple[list[dict], dict, dict]:
    # ★ 上游：11-03 雷电设备包（PE 侧）按 file_id 精确取件解码的冻结数据集。
    #   旧口径（9 月 PC 侧 LOTTERY_POOL_RESOLVED_v01）已下线 ——
    #   它把 391794~391873 共 79 个池记成「内容未随包下发」，而 11-03 包里
    #   这 79 个池每一格都有内容。
    #   新数据集自带 diff 标记（base/inherit/same/replaced/added）与中文字段，
    #   故**不再重算 merged_rows**（那会把已解码的字段当成"待挂载"再拼一次）。
    frozen_p = LS.PE1103_ROWS
    if not frozen_p.is_file():
        raise FileNotFoundError(
            "11-03 奖池数据集不存在：%s（先跑 build_lottery_pool_pe1103.py）" % rel(frozen_p))
    rows = list(LS.iter_pe1103_rows())
    comps = LS.pe1103_components()
    rows_by_comp = Counter(r.get("component") for r in rows)
    infos = [{
        "name": c["name"],
        "role": "classic" if c["name"] == "base" else "channel",
        "channel": None if c["name"] == "base" else c["name"],
        # manifest_rows = 该组件**自身**的行数（解码出来的原始行）
        "manifest_rows": c.get("rows"),
        # rows = 本产物里该服的**全量**行数（base 打底 + overlay 覆盖后展开）
        "rows": rows_by_comp.get(c["name"], 0),
        "pools": c.get("pools"),
        "pool_key_range": c.get("pool_key_range"),
        "state": c.get("state"),
        "unbound_rows": c.get("unbound_rows"),
        "data_file_id": c.get("data_file_id"),
        "sha256": c.get("data_sha256"),
    } for c in comps]
    stats = LS.summarize(rows, infos)
    enrich = LE.build_all()

    pe_manifest = json.loads((LS.PE1103_DIR / "manifest.json").read_text(encoding="utf-8"))
    src_snapshot = pe_manifest.get("source") or {}
    manifest = {
        "schema": SCHEMA,
        "record_type": "dataset_manifest",
        "publication_tier": "verified-runtime-structure",
        "runtime_final_state": "unresolved",
        "artifact_claim": (
            "Per-server static lottery pool structure with decoded reward, quantity, "
            "Chinese note, probability annotation and expiry; NOT a runtime-final "
            "or current-server payout list."
        ),
        "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "generator": rel(pathlib.Path(__file__)),
        "upstream": {
            "dataset": "LOTTERY_POOL_PE1103_v01",
            "path": rel(frozen_p),
            "sha256": sha256_of(frozen_p),
            "snapshot_path": src_snapshot.get("path"),
            "snapshot_sha256": src_snapshot.get("package_sha256"),
            "snapshot_bytes": src_snapshot.get("package_bytes"),
            "manifest_sha256": None,
            "device_profile": src_snapshot.get("device_profile"),
            "selection_rule": src_snapshot.get("selection_rule"),
        },
        "rows_file": "rows.jsonl",
        "component_order": [c["name"] for c in comps],
        "stats": stats,
        "enrich": _enrich_index(enrich),
        "notes": NOTES,
    }
    return rows, manifest, enrich


def _enrich_index(enrich: dict) -> dict:
    """补充维度的索引（manifest 只写摘要，正文在同目录小文件里）。"""
    out = {}
    for k in ENRICH_ORDER:
        d = enrich.get(k) or {}
        item = {"file": k + ".json", "schema": d.get("schema")}
        for key in ("count", "child_pools", "child_pool", "activities", "bound",
                    "pools_bound", "multi_activity_pools", "blocks", "state_dist",
                    "rules", "verified", "unresolved", "replace_ids",
                    "version_known_ids", "ids_without_version",
                    "rows_per_component"):
            if key in d:
                item[key] = d[key]
        out[k] = item
    return out


def dump(rows: list[dict], manifest: dict, enrich: dict, apply: bool) -> int:
    lines = [json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
             for r in rows]
    payload = "\n".join(lines) + "\n"
    man = json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    extras = {
        k: json.dumps(enrich[k], ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        for k in ENRICH_ORDER if k in enrich
    }

    print("产出目录 : %s" % rel(OUT_DIR))
    print("rows     : %d 行  %.1f MB" % (len(rows), len(payload.encode("utf-8")) / 1e6))
    print("组件     : %s" % ", ".join(manifest["component_order"]))
    print("\n── 每服统计（全量 = base 全部格 + 本服覆盖）──")
    print("  %-6s %7s %8s %8s %8s %7s %8s %6s" %
          ("服", "行", "沿用base", "相同", "被换", "新增", "有note", "有概率"))
    for c, s in manifest["stats"]["per_component"].items():
        print("  %-6s %7d %8d %8d %8d %7d %8d %6d" %
              (c, s.get("rows", 0), s.get("inherit", 0), s.get("same", 0),
               s.get("replaced", 0), s.get("added", 0),
               s.get("with_note", 0), s.get("with_prob", 0)))
    print("\n── 补充维度 ──")
    for k in ENRICH_ORDER:
        d = enrich.get(k) or {}
        bits = []
        for key in ("count", "activities", "bound", "blocks", "rules",
                    "verified", "unresolved"):
            if key in d:
                bits.append("%s=%s" % (key, d[key]))
        if d.get("state_dist"):
            bits.append(str(d["state_dist"]))
        print("  %-16s %s" % (k, "  ".join(bits)))
    print("\n── 服等价性（逐键奖励对比）──")
    for e in (enrich.get("servers") or {}).get("equivalence") or []:
        print("  %-5s vs %-5s 等价=%-5s 奖励差 %d 行" %
              (e["a"], e["b"], e["equivalent"], e["reward_diff"]))
    print("\n── 数据源 ──")
    for i in manifest["stats"]["components"]:
        print("  %-6s state=%-8s rows=%-6s pools=%-6s → %s" %
              (i.get("name"), i.get("state"), i.get("manifest_rows"), i.get("pools"),
               i.get("data_file_id")))

    if not apply:
        print("\n[预览] 未落盘。加 --apply 写入。")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "manifest.json").write_text(man, encoding="utf-8", newline="\n")
    (OUT_DIR / "rows.jsonl").write_text(payload, encoding="utf-8", newline="\n")
    for name, text in extras.items():
        (OUT_DIR / (name + ".json")).write_text(text, encoding="utf-8", newline="\n")
    print("\n已写入：")
    print("  %s" % rel(OUT_DIR / "manifest.json"))
    print("  %s" % rel(OUT_DIR / "rows.jsonl"))
    for name in extras:
        print("  %s" % rel(OUT_DIR / (name + ".json")))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="落盘（默认只预览）")
    a = ap.parse_args()
    rows, manifest, enrich = build()
    return dump(rows, manifest, enrich, a.apply)


if __name__ == "__main__":
    raise SystemExit(main())
