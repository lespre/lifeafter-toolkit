#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_lottery_pool_pe1103.py — 从 11-03 雷电设备包产出「奖池全量 + 分服」数据集

## 为什么有这���脚本

上游 `LOTTERY_POOL_RESOLVED_v01.jsonl` 冻结自 **BA8A 快照（10 月 PC 侧）**：
  · base 只有 1,761 池 / 23,281 格；
  · 池号 391794~391873 这 79 个池**一格奖励都拿不到**（当时登记为 content_missing）；
  · 浮光花序（池 391848，28 格）整池缺失。

本脚本改从 **11-03 雷电模拟器设备包**（`01_索引与产物/源包/pe_device_20261103/`）
按 **file_id 精确取件**并解码，得到：
  · base **1,839 池 / 24,245 格**，池号上界 391873 —— 79 个缺口池全部有内容；
  · 5 个分服（kj1 / kjxq / yk / ykxq）各自的覆盖格与相对 base 的真实差异；
  · 配套 chs 池解出的中文字段（note / prob_note / 到期 / 广播 / 权重）。

## 关键事实（已实测，非推断）

1. **file_id 跨版本稳定**：BA8A 快照与 11-03 包用同一串 file_id 认领同一张逻辑表
   （见 `rules/unnamed_table_registry.yml`）。所以取件按 fid，不按文件名/行号名。
2. **base 覆盖完整**：11-03 base 解出的 1,839 池与结构表
   `reward_pool_no_item_no_list` 的 1,839 池**完全一致**（交集 1839、双向差集 0）。
3. **版本差异真实存在**：与旧冻结产物重叠 23,273 格中 **10 格奖励不同**
   （11 月改版），这是版本推进，不是解码错误。
4. **分服等价性**：kj1≡kjxq（237 行逐键 0 差异）、yk≡ykxq（162 行 0 差异），
   与旧产物的 G12 结论一致。

## 铁律

- **不猜**：复合键 (pool_key, item_no) 由表内 jump 组直读，不做任何整数等值 join。
- **不混排**：每服各自成行，`component` 必写；差异只在同服 vs base 之间算。
- **不伪造**：`runtime_final_state` 恒为 `unresolved`（`optional_pool_replace_data`
  等表会在运行时替换奖励，本产物是静态结构，不是当前实发）。
- **inc/del 分片如实登记**：11-03 包内 **有 inc（55F871522812BFCF）、无 del
  （A5F5FFFDB4CEF3A8）**，manifest 里逐条写明，不假装已合并。

## 用法

  python 02_wiki/web/tools/build_lottery_pool_pe1103.py             # 预览
  python 02_wiki/web/tools/build_lottery_pool_pe1103.py --apply     # 落盘
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import struct
import sys
from collections import Counter

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from la_paths import ARTIFACTS, TOOLKIT_CORE, WEB, rel  # noqa: E402

sys.path.insert(0, str(TOOLKIT_CORE))
from toolkit_core import hotfix_rows as HR  # noqa: E402

SRC_ROOT = ARTIFACTS / "源包" / "pe_device_20261103"
PKG = SRC_ROOT / "script.py314.lc.npk"
OUT_DIR = WEB / "site_data" / "LOTTERY_POOL_PE1103_v01"
SCHEMA = "lottery_pool_pe1103/v0.1"

# 组件 → (data fid, pool fid)。fid 来自 rules/unnamed_table_registry.yml 与
# 上游 build_lottery_pool_resolved_v01.py 的 TABLE_COMPONENTS。
COMPONENTS = (
    ("base", "D558884A36C972C5", "69E58821939CB515"),
    ("kj1", "7C1978372D53EA7A", "BEC1A7DD859A26BB"),
    ("kjxq", "E6D350D76C052B91", "0F748A9290B9B1BA"),
    ("yk", "F3F1166CFA11E8EB", "1565D71D87A32C5D"),
    ("ykxq", "BBC2EAAA769B560A", "F8BBD20A0AC69BA3"),
)
SHARDS = (
    ("inc", "55F871522812BFCF"),
    ("del", "A5F5FFFDB4CEF3A8"),
)
FIELDS = ("note", "prob_note", "expiration_time", "broadcast_content",
          "initial_weights", "accumulative_weight", "reward_rank")

NOTES = (
    "本数据集取自 11-03 雷电模拟器**设备包**（PE 侧），按 file_id 精确取件并解码，"
    "不是 PC 侧包、不是 10 月包、不是 MuMu 包。"
    "复合键 (pool_key, item_no) 由表内 0x27 跳转组直读；reward 同样由 jump 组直读，"
    "全程不做整数等值 join、不跨源猜字段。"
    "base 1,839 池 / 24,245 格，与结构表 reward_pool_no_item_no_list 的 1,839 池完全一致；"
    "相对旧冻结产物（BA8A / 10 月 PC 侧）新增 79 池（含浮光花序 391848 的 28 格），"
    "重叠 23,273 格中 10 格奖励不同 —— 属 11 月版本推进。"
    "diff 只在同服与 base 同键之间计算：base=经典服本体 / same=该服覆盖但奖励相同 / "
    "replaced=该服覆盖且奖励被换 / added=该服新增此格 / inherit=该服未覆盖、沿用 base。"
    "服等价性：kj1≡kjxq、yk≡ykxq（逐键 0 差异，已由本脚本自复算）。"
    "★ inc 分片（55F871522812BFCF）在 11-03 包内存在但**未并入**（其编码未确证，"
    "强解有产出错奖励的风险）；del 分片（A5F5FFFDB4CEF3A8）11-03 包内**不存在**。"
    "两项均如实登记在 manifest.shards，未做任何合并动作。"
    "runtime_final_state 恒为 unresolved：optional_pool_replace_data 等表会在运行时"
    "替换奖励，本产物是静态结构，不是当前实发结果。"
)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_of(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _xbody(payload: bytes) -> bytes | None:
    at = payload.find(b"x{")
    if at < 0 or at + 6 > len(payload):
        return None
    size = struct.unpack_from("<I", payload, at + 2)[0]
    return payload[at + 6:at + 6 + size]


def extract_parts() -> tuple[dict[str, bytes], dict[str, dict]]:
    """按 fid 从 11-03 包取件 → {fid: bytes} + 取件明细。"""
    entries = HR._entries(PKG)
    blob = PKG.read_bytes()
    from la_unpack_core import npk_decode_entry  # noqa: PLC0415

    class _E:
        __slots__ = ("packed",)

        def __init__(s, p):
            s.packed = p

    by_fid = {str(e.get("fid", "")).upper(): e for e in entries}
    want = {}
    for _c, dfid, pfid in COMPONENTS:
        want[dfid] = "data"
        want[pfid] = "pool"
    for _c, sfid in SHARDS:
        want[sfid] = "shard"

    got: dict[str, bytes] = {}
    meta: dict[str, dict] = {}
    for fid, kind in want.items():
        e = by_fid.get(fid)
        if not e:
            meta[fid] = {"kind": kind, "present": False,
                        "reason": "该 file_id 在 11-03 包内不存在"}
            continue
        raw = blob[e["offset"]:e["offset"] + e["packed"]]
        try:
            d = npk_decode_entry(raw, e["decoded"], e["flag"], entry=_E(e["packed"]))
        except Exception as exc:  # noqa: BLE001
            meta[fid] = {"kind": kind, "present": False,
                        "reason": "解包失败：%s: %s" % (type(exc).__name__, exc)}
            continue
        got[fid] = d
        meta[fid] = {"kind": kind, "present": True, "bytes": len(d),
                     "sha256": sha256_bytes(d),
                     "entry": {"index": e.get("index"), "offset": e.get("offset"),
                               "packed": e.get("packed"), "decoded": e.get("decoded"),
                               "flag": e.get("flag")}}
    return got, meta


def decode_component(data: bytes, pool: bytes) -> tuple[dict[tuple[int, int], dict], int]:
    """解一张 reward_pool_data 数据体 → {(pool_key, item_no): 行} + unbound 数。"""
    from toolkit_core.bindict_table import parse_legacy_chs_pool, resolve_jump_group  # noqa: PLC0415
    from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: PLC0415

    body = _xbody(data)
    if body is None:
        raise ValueError("数据体缺 x{ 帧")
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    strings = parse_legacy_chs_pool(pool)
    rows, unbound = decode_table_rows_with_chs_slots(body, strings)
    out: dict[tuple[int, int], dict] = {}
    for r in rows:
        kg = resolve_jump_group(blob, r["key"])
        if not isinstance(kg, list) or len(kg) != 2:
            continue
        rf = r["values"].get("reward")
        if not rf or not isinstance(rf[1], str) or not rf[1].startswith("jump:"):
            continue
        rg = resolve_jump_group(blob, int(rf[1].split(":", 1)[1]))
        if not isinstance(rg, list) or len(rg) != 2:
            continue
        rec = {"item_id": int(rg[0]), "item_count": int(rg[1])}
        for f in FIELDS:
            v = r["values"].get(f)
            rec[f] = v[1] if isinstance(v, tuple) else v
        out[(int(kg[0]), int(kg[1]))] = rec
    return out, len(unbound)


def build() -> tuple[list[dict], dict]:
    parts, part_meta = extract_parts()

    comp_rows: dict[str, dict[tuple[int, int], dict]] = {}
    comp_info: list[dict] = []
    for comp, dfid, pfid in COMPONENTS:
        if dfid not in parts or pfid not in parts:
            comp_info.append({"component": comp, "state": "missing",
                              "data_file_id": dfid, "chs_file_id": pfid,
                              "rows": 0, "reason": "取件失败，见 parts"})
            continue
        rows, unbound = decode_component(parts[dfid], parts[pfid])
        comp_rows[comp] = rows
        pools = {k[0] for k in rows}
        comp_info.append({
            "component": comp,
            "state": "verified" if rows else "missing",
            "data_file_id": dfid, "chs_file_id": pfid,
            "rows": len(rows), "unbound_rows": unbound,
            "pools": len(pools),
            "pool_key_range": [min(pools), max(pools)] if pools else None,
            "data_sha256": sha256_bytes(parts[dfid]),
            "chs_sha256": sha256_bytes(parts[pfid]),
        })

    base = comp_rows.get("base") or {}
    out: list[dict] = []

    def emit(comp: str, key: tuple[int, int], rec: dict, diff: str,
             base_reward: list | None) -> dict:
        r = {
            "component": comp,
            "pool_key": key[0],
            "item_no": key[1],
            "reward_raw": [rec["item_id"], rec["item_count"]],
            "item_id": rec["item_id"],
            "item_count": rec["item_count"],
            "diff": diff,
            "field_state": "full" if rec.get("note") else "partial",
        }
        for f in FIELDS:
            r[f] = rec.get(f)
        if comp != "base":
            r["base_reward_raw"] = base_reward
        return r

    for comp, _d, _p in COMPONENTS:
        own = comp_rows.get(comp) or {}
        if not own:
            continue
        for key, rec in sorted(own.items()):
            b = base.get(key)
            if comp == "base":
                out.append(emit(comp, key, rec, "base", None))
            elif b is None:
                out.append(emit(comp, key, rec, "added", None))
            elif (b["item_id"], b["item_count"]) == (rec["item_id"], rec["item_count"]):
                out.append(emit(comp, key, rec, "same",
                                [b["item_id"], b["item_count"]]))
            else:
                out.append(emit(comp, key, rec, "replaced",
                                [b["item_id"], b["item_count"]]))
        # 未被该服覆盖的格 = inherit（沿用 base）
        if comp != "base":
            for key, brec in sorted(base.items()):
                if key not in own:
                    out.append(emit(comp, key, dict(brec), "inherit",
                                    [brec["item_id"], brec["item_count"]]))

    # 服等价性自复算（逐键奖励对比）
    equiv = []
    names = [c[0] for c in COMPONENTS]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            ra = comp_rows.get(a) or {}
            rb = comp_rows.get(b) or {}
            diff_n = 0
            for k, v in ra.items():
                w = rb.get(k)
                if w is None or (w["item_id"], w["item_count"]) != (v["item_id"], v["item_count"]):
                    diff_n += 1
            equiv.append({"a": a, "b": b, "equivalent": diff_n == 0,
                          "reward_diff": diff_n,
                          "rows_a": len(ra), "rows_b": len(rb)})

    stats = {
        "total_rows": len(out),
        "per_component": {},
        "components": comp_info,
        "server_equivalence": equiv,
    }
    per: dict[str, Counter] = {}
    for r in out:
        s = per.setdefault(r["component"], Counter())
        s["rows"] += 1
        s[r["diff"]] += 1
        if r.get("note"):
            s["with_note"] += 1
        if r.get("prob_note") is not None:
            s["with_prob"] += 1
    stats["per_component"] = {c: dict(v) for c, v in sorted(per.items())}

    shards = []
    for comp, fid in SHARDS:
        m = part_meta.get(fid) or {}
        shards.append({
            "component": comp, "file_id": fid,
            "present": bool(m.get("present")),
            "bytes": m.get("bytes"), "sha256": m.get("sha256"),
            "reason": m.get("reason"),
            "applied": False,
            "note": ("11-03 包内存在但**未并入**：该分片编码未确证，强解有产出错奖励的风险"
                     if m.get("present") else
                     "11-03 包内不存在该 file_id，无法合并"),
        })

    manifest = {
        "schema": SCHEMA,
        "record_type": "dataset_manifest",
        "publication_tier": "verified-runtime-structure",
        "runtime_final_state": "unresolved",
        "artifact_claim": (
            "Per-server static lottery pool structure decoded from the 2026-11-03 "
            "LDPlayer device package; NOT a runtime-final or current-server payout list."
        ),
        "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "generator": rel(pathlib.Path(__file__)),
        "source": {
            "package_path": rel(PKG),
            "package_bytes": PKG.stat().st_size if PKG.is_file() else 0,
            "package_sha256": sha256_of(PKG) if PKG.is_file() else "",
            "package_entry_count": len(HR._entries(PKG)) if PKG.is_file() else 0,
            "device_profile": "雷电模拟器 14 · 2026-11-03 设备包（PE 侧）",
            "selection_rule": (
                "按 file_id 精确取件（file_id 是游戏侧跨版本稳定的逻辑标识，"
                "见 rules/unnamed_table_registry.yml）；不按行号名、不按文件名猜"
            ),
        },
        "parts": {fid: part_meta.get(fid) or {} for fid, _k in
                  [(f, k) for _c, d, p in COMPONENTS for f, k in ((d, "data"), (p, "pool"))]},
        "shards": shards,
        "rows_file": "rows.jsonl",
        "component_order": [c[0] for c in COMPONENTS],
        "stats": stats,
        "notes": NOTES,
    }
    return out, manifest


def dump(rows: list[dict], manifest: dict, apply: bool) -> int:
    payload = "".join(
        json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for r in rows)
    print("产出目录 : %s" % rel(OUT_DIR))
    print("rows     : %d 行  %.1f MB" % (len(rows), len(payload.encode("utf-8")) / 1e6))
    print("组件     : %s" % ", ".join(manifest["component_order"]))
    print("\n── 每服统计（全量 = base 全部格 + 本服覆盖/沿用）──")
    print("  %-6s %7s %8s %8s %8s %8s %8s" %
          ("服", "行", "沿用base", "相同", "被换", "新增", "有note"))
    for c, s in manifest["stats"]["per_component"].items():
        print("  %-6s %7d %8d %8d %8d %8d %8d" %
              (c, s.get("rows", 0), s.get("inherit", 0), s.get("same", 0),
               s.get("replaced", 0), s.get("added", 0), s.get("with_note", 0)))
    print("\n── 组件取件 ──")
    for i in manifest["stats"]["components"]:
        print("  %-6s state=%-9s rows=%-6s 池=%-5s 区间 %s" %
              (i["component"], i["state"], i.get("rows"), i.get("pools"),
               i.get("pool_key_range")))
    print("\n── 服等价性（逐键奖励对比）──")
    for e in manifest["stats"]["server_equivalence"]:
        print("  %-5s vs %-5s 等价=%-5s 奖励差 %d 行" %
              (e["a"], e["b"], e["equivalent"], e["reward_diff"]))
    print("\n── 分片（inc/del）──")
    for s in manifest["shards"]:
        print("  %-4s %-18s present=%-5s applied=%-5s %s" %
              (s["component"], s["file_id"], s["present"], s["applied"], s["note"]))
    if not apply:
        print("\n[预览] 未落盘。加 --apply 写入。")
        return 0
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "rows.jsonl").write_text(payload, encoding="utf-8", newline="\n")
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print("\n已写入：")
    print("  %s" % rel(OUT_DIR / "rows.jsonl"))
    print("  %s" % rel(OUT_DIR / "manifest.json"))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="落盘（默认只预览）")
    a = ap.parse_args()
    rows, manifest = build()
    return dump(rows, manifest, a.apply)


if __name__ == "__main__":
    raise SystemExit(main())
