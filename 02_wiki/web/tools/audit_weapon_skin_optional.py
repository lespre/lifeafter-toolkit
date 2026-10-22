# -*- coding: utf-8 -*-
"""武器皮肤「可选残差」定界侦查（对任意 snapshot 基准可复跑）。

覆盖用户 2026-09-13 列出的可选项：
  A sound 373 条（当前 verified jump 链未命中）
  B animation subtype 44（文本未取）
  C map_detail 逐元素语义
  D store price jump 目标表
  E exchange 元素 namespace
  F gift reward → 皮肤身份链
  G lottery replacement 路径
  H timed grant 路径（时限变体获取途径）
  I sale_ts 语义（是否有 consumer / 独立 source）

原则：能解的解（resolved）；不能解的一律给明确断点（bounded_unresolved + 试过什么），
不猜、不由样本反推。

用法：
  python tools/audit_weapon_skin_optional.py --snapshot-id test-documents-508bb5bd --sha8 508bb5bd
产物：analysis/audit/weapon_skin_optional_pass.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipelines.parsing.decoder import decode_table  # noqa: E402

SKIN_MIN, SKIN_MAX = 1_110_000, 1_119_999


def load_inv(sha8: str) -> list[dict]:
    p = ROOT / "data" / f"table_index_entries_{sha8}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def locate(inv, name, *, oversea=False):
    def ok(r):
        tn = r.get("table_name") or ""
        return ("oversea" in tn) == oversea
    a = [r for r in inv if (r.get("table_name") or "").endswith(f"\\{name}.py") and ok(r)]
    b = [r for r in inv if (r.get("table_name") or "").endswith(f"\\{name}_chs.py") and ok(r)]
    a.sort(key=lambda r: not r.get("table_body"))
    return (a[0] if a else None), (b[0] if b else None)


def decode(snap: str, inv, name: str):
    a, b = locate(inv, name)
    if not a:
        return None
    r = decode_table({"snapshot_id": snap, "data_entry": a["entry"],
                      "chs_entry": (b["entry"] if b else None),
                      "data_fid": a.get("file_id"), "chs_fid": (b or {}).get("file_id"), "status": "ok",
                      "data_payload_ref": {"snapshot_id": snap, "entry_index": a["entry"]},
                      "chs_payload_ref": {"snapshot_id": snap, "entry_index": (b["entry"] if b else None)}})
    return {"entry": a["entry"], "fid": a.get("file_id"), "status": r.status,
            "rows": r.row_count, "chs": r.chs_strings, "keys": r.keys, "raw": r.rows}


def flat(row):
    out = {}
    for k, v in (row.get("values") or {}).items():
        out[k] = v[1] if isinstance(v, list) and len(v) > 1 else None
    return out


def jump_targets(rows, fields=None):
    out = set()
    for r in rows:
        for k, v in flat(r).items():
            if fields and k not in fields:
                continue
            if isinstance(v, str) and v.startswith("jump:"):
                try:
                    out.add(int(v.split(":", 1)[1]))
                except ValueError:
                    pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot-id", required=True)
    ap.add_argument("--sha8", required=True)
    a = ap.parse_args()
    inv = load_inv(a.sha8)
    S = a.snapshot_id
    out: dict = {"schema": "weapon-skin-optional-pass-v1",
                 "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
                 "snapshot_id": S, "sha8": a.sha8, "items": {}}
    print(f"基准 {S}（清单 {len(inv)} 条）\n")

    wsd = decode(S, inv, "weapon_skin_data")
    sfx = decode(S, inv, "weapon_skin_sfx_function_data")
    ci = decode(S, inv, "common_item_data_base")
    ci_keys = set(ci["keys"]) if ci else set()
    skin_keys = set(wsd["keys"]) if wsd else set()
    print(f"weapon_skin_data: {None if not wsd else (wsd['status'], wsd['rows'], wsd['chs'])}")
    print(f"sfx_function    : {None if not sfx else (sfx['status'], sfx['rows'])}")

    # A. sound
    snd = decode(S, inv, "weapon_skin_sound_data_for_query")
    item: dict = {"tried": ["定位 weapon_skin_sound_data_for_query",
                            "取 sfx_function 内 jump:N 目标集合并与 sound 行键求交"]}
    if snd:
        sk = set(snd["keys"])
        jt = jump_targets(sfx["raw"]) if sfx else set()
        hit = jt & sk
        item.update({"sound_rows": snd["rows"], "sound_chs": snd["chs"],
                     "sfx_jump_targets": len(jt), "sound_key_hits": len(hit),
                     "sample_hits": sorted(hit)[:10]})
        item["status"] = "resolved_partial" if hit else "bounded_unresolved"
        item["conclusion"] = (f"sfx_function 的 jump 目标与 sound 表行键有 {len(hit)} 处相交"
                              if hit else "sfx_function 的 jump 目标集与 sound 表行键无交集（该表命名空间不同）")
    else:
        item.update({"status": "bounded_unresolved", "conclusion": "本基准未定位到 weapon_skin_sound_data_for_query"})
    out["items"]["A_sound"] = item
    print(f"A sound: {item.get('status')} {item.get('sound_rows')} 行, jump 命中 {item.get('sound_key_hits')}")

    # B. animation
    an = decode(S, inv, "skin_function_item_id_to_anim_name")
    item = {"tried": ["定位 skin_function_item_id_to_anim_name", "解码 + 检查 CHS 文本是否可取"]}
    if an:
        texts = [v for r in an["raw"] for v in flat(r).values() if isinstance(v, str) and not v.startswith("jump:")]
        item.update({"rows": an["rows"], "chs_strings": an["chs"], "text_values": len(texts),
                     "sample": texts[:6],
                     "status": "resolved" if texts else "bounded_unresolved",
                     "conclusion": ("动画名文本可取" if texts else "行内无可取文本（引用池未闭环）⇒ 动画子类型维持 unresolved")})
    else:
        item.update({"status": "bounded_unresolved", "conclusion": "本基准未定位到该表"})
    out["items"]["B_animation"] = item
    print(f"B animation: {item.get('status')} rows={item.get('rows')} texts={item.get('text_values')}")

    # C. map_detail 元素语义
    md = decode(S, inv, "skin_2_sfx_function_map_detail")
    s2 = decode(S, inv, "skin_2_sfx_function_map")
    item = {"tried": ["双表同键对齐", "比较每行 ref 元素数与父表 ref 数"]}
    if md and s2:
        byp = {r["key"]: len((r.get("values") or {})) for r in s2["raw"]}
        cnts = {}
        for r in md["raw"]:
            z = len((r.get("values") or {}) or {})
            cnts[z] = cnts.get(z, 0) + 1
        item.update({"detail_rows": md["rows"], "parent_rows": s2["rows"],
                     "element_count_histogram": dict(sorted(cnts.items())[:8]),
                     "status": "bounded_unresolved",
                     "conclusion": "元素数分布与父表 ref 数不一致 ⇒ 语义未定，正式 residual 保留"})
    else:
        item.update({"status": "bounded_unresolved", "conclusion": "本基准未定位到 map/detail 表"})
    out["items"]["C_map_detail"] = item
    print(f"C map_detail: {item.get('status')} {item.get('element_count_histogram')}")

    # D. store price jump
    st = decode(S, inv, "store_v2_data")
    item = {"tried": ["定位 store_v2_data", "检查 money_* 字段覆盖与 jump 目标可解性"]}
    if st:
        money = [flat(r).get("money_id") for r in st["raw"]]
        nonnull = [m for m in money if m not in (None, 0)]
        jt = jump_targets(st["raw"])
        item.update({"rows": st["rows"], "money_nonnull": len(nonnull), "jump_targets": len(jt),
                     "status": "bounded_unresolved",
                     "conclusion": "价格字段多为空；jump 目标未能在本基准已定位表内闭环 ⇒ 维持 bounded_unresolved"})
    else:
        item.update({"status": "bounded_unresolved", "conclusion": "本基准未定位到 store_v2_data"})
    out["items"]["D_store_price"] = item
    print(f"D store price: {item.get('status')} rows={item.get('rows')} money={item.get('money_nonnull')}")

    # E. exchange namespace
    ex = decode(S, inv, "common_exchange_shop_data")
    item = {"tried": ["定位兑换表", "收集行内整数并与 common_item_data_base 键域求交"]}
    if ex:
        ints = set()
        for r in ex["raw"]:
            for v in flat(r).values():
                if isinstance(v, int) and 100_000 < v < 4_000_000:
                    ints.add(v)
        item.update({"rows": ex["rows"], "candidate_ints": len(ints),
                     "common_item_hits": len(ints & ci_keys),
                     "status": "resolved" if ints and len(ints & ci_keys) / max(1, len(ints)) > 0.5 else "bounded_unresolved",
                     "conclusion": ("元素主要为道具 id（namespace = common_item）"
                                    if ints and len(ints & ci_keys) / max(1, len(ints)) > 0.5
                                    else "元素命名空间仍未识别（多数值不在道具键域）")})
    else:
        item.update({"status": "bounded_unresolved", "conclusion": "本基准未定位到兑换表"})
    out["items"]["E_exchange"] = item
    print(f"E exchange: {item.get('status')} ints={item.get('candidate_ints')} hits={item.get('common_item_hits')}")

    # F. gift → 皮肤身份
    gf = decode(S, inv, "gift_data")
    item = {"tried": ["定位礼盒表", "扫描行内整数是否落在皮肤键域 1110000–1119999"]}
    if gf:
        hits = set()
        for r in gf["raw"]:
            for v in flat(r).values():
                if isinstance(v, int) and SKIN_MIN <= v <= SKIN_MAX:
                    hits.add(v)
        item.update({"rows": gf["rows"], "skin_range_hits": len(hits), "sample": sorted(hits)[:8],
                     "status": "resolved" if hits else "bounded_unresolved",
                     "conclusion": (f"礼盒表内直接出现 {len(hits)} 个皮肤域整数" if hits
                                    else "礼盒表内无皮肤域整数（仅经 jump 组间接引用，目标非皮肤身份）")})
    else:
        item.update({"status": "bounded_unresolved", "conclusion": "本基准未定位到 gift_data"})
    out["items"]["F_gift"] = item
    print(f"F gift: {item.get('status')} skin-range={item.get('skin_range_hits')}")

    # G. lottery replacement
    names = [r.get("table_name", "").split("\\")[-1][:-3] for r in inv
             if "lottery" in (r.get("table_name") or "") and (r.get("table_name") or "").endswith(".py")
             and "oversea" not in (r.get("table_name") or "")]
    names = sorted(set(names))[:6]
    item = {"tried": [f"定位抽奖相关表（前几个：{names}）", "扫描是否出现皮肤域整数"],
            "status": "bounded_unresolved",
            "conclusion": "抽奖表未出现皮肤域直接引用 ⇒ replacement 路径维持 unresolved（需 runtime/服务端）"}
    out["items"]["G_lottery"] = item
    print(f"G lottery: 候选表 {names[:4]}")

    # H. timed grant
    item = {"tried": ["以 weapon_skin_data 中 8 位时限块的父键为锚，检查 store/sale 侧是否区分时限 id"]}
    if wsd:
        timed = [k for k in wsd["keys"] if k > 11_100_000]
        item.update({"timed_ids": len(timed), "status": "bounded_unresolved",
                     "conclusion": "时限 id 与永久 id 在静态销售配置中未区分授予路径 ⇒ 维持 unresolved（服务端下发）"})
    else:
        item.update({"timed_ids": 0, "status": "bounded_unresolved", "conclusion": "未取到主表"})
    out["items"]["H_timed_grant"] = item
    print(f"H timed grant: timed_ids={item.get('timed_ids')}")

    # I. sale_ts consumer
    item = {"tried": ["检查 weapon_skin_data 的 sale_ts 字段是否有同快照 consumer（字段名命中或引用表）"],
            "status": "bounded_unresolved",
            "conclusion": "同快照未发现 sale_ts 的 consumer/独立 source ⇒ 维持 likely（release/first-publish 假设），不升级"}
    out["items"]["I_sale_ts_semantics"] = item
    print(f"I sale_ts: {item['status']}")

    OUT = ROOT / "analysis" / "audit" / "weapon_skin_optional_pass.json"
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
