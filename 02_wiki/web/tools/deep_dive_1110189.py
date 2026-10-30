# -*- coding: utf-8 -*-
"""1110189 全量档案：主表 / 行为资源 / sfx / 特效名 / 模型 / 其他表引用。"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

ROOT = pathlib.Path("E:/la拆包项目")
CD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
OUT = ROOT / "01_索引与产物/30_分析"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402

SID = 1110189


def dec(name: str, resolve: bool = False):
    try:
        return _dec(name, resolve)
    except Exception:
        return None


def _dec(name: str, resolve: bool = False):
    p = CD / (name + ".py")
    if not p.is_file():
        return None
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    chs = CD / (name + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else []
    rows, _ = decode_table_rows(raw[at + 6:at + 6 + n], pool, resolve_jumps=resolve, lenient=True)
    return rows


def val(v):
    return v[1] if isinstance(v, tuple) and len(v) == 2 else v


def dump_row(rows, key, label):
    if not rows:
        print("   （表缺失）")
        return None
    for r in rows:
        if r.get("key") == key:
            v = {k: val(x) for k, x in (r.get("values") or {}).items()}
            print("   %s：" % label)
            for k in sorted(v):
                print("     %-32s %s" % (k, json.dumps(v[k], ensure_ascii=False)[:110]))
            return v
    print("   %s：未命中" % label)
    return None


def main() -> int:
    print("== 1. weapon_skin_data 主行")
    wsd = dump_row(dec("weapon_skin_data"), SID, "主行")

    print("\n== 2. weapon_skin_behavior_res_data（行为资源）")
    brd = dump_row(dec("weapon_skin_behavior_res_data"), SID, "行为行")

    print("\n== 3. weapon_skin_sfx_function_data（按 skin_id 过滤）")
    sfd = dec("weapon_skin_sfx_function_data") or []
    hits = []
    for r in sfd:
        v = {k: val(x) for k, x in (r.get("values") or {}).items()}
        if v.get("skin_id") == SID:
            hits.append((r["key"], v))
    print("   命中 %d 条" % len(hits))
    for k, v in hits:
        print("     key=%-10s type=%-3s type_label=%-8s name=%-14s params=%s"
              % (k, v.get("sfx_type"), v.get("type_label"), str(v.get("display_name"))[:14],
                 str(v.get("sfx_params"))[:60]))

    print("\n== 4. weapon_skin_effect_show_data（正式特效名）")
    sys.path.insert(0, str(ROOT / "02_wiki/web"))
    from pipelines.parsing import effect_show_names as E
    es, _st = E.parse(CD)
    for e in es.get(str(SID)) or []:
        print("     %-8s %s" % (e["slot"], e["name"]))

    print("\n== 5. 模型文件")
    for p in sorted((ROOT / "01_索引与产物/41_还原树/pe/资源").rglob("skin_1013_010*")):
        print("     %s %.1f KB" % (p.relative_to(ROOT), p.stat().st_size / 1024))

    print("\n== 6. 其他表里出现 %d 的表（限量扫描）" % SID)
    names = ["gift_data", "store_v2_data", "common_exchange_shop_data", "lottery_pool_data",
             "activity_data", "shop_data", "item_store_data", "weapon_skin_replace_nucleus_conf",
             "weapon_kind_to_skin_item_data", "skin_2_sfx_function_map"]
    for nm in names:
        rows = dec(nm)
        if not rows:
            continue
        cnt = 0
        for r in rows:
            v = {k: val(x) for k, x in (r.get("values") or {}).items()}
            if str(SID) in json.dumps(v, ensure_ascii=False):
                cnt += 1
        if cnt:
            print("     %-34s %d 行命中" % (nm, cnt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
