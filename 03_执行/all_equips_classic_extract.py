# -*- coding: utf-8 -*-
"""经典服 all_equips_data 行级提取（PE 测试服客户端安装基线包）— 2026-10-29。

数据源（PE 测试服安卓客户端安装基线，PE 家族源包）：
  01_索引与产物/源包/apk_20261002/mumu_5.0.679/assets/script.py314.lc.npk
    - fid 1F8E9684E1B97CE0 = com/cdata/all_equips_data.py       行表（10,949 行）
    - fid 94AB0B3FD057EF01 = com/cdata/all_equips_data_chs.py   sec1=字段名池(10,949)
  注：PE 还原树 pe/配置/com/cdata/all_equips_data.py 已被增量热更的 808B
      MergedTableData 存根覆盖（同名取高优先级），基线行表只在安装包里。
      base/_inc/_del 分片 fid 在所有留盘 npk 中均不存在 → 安装基线即经典服
      在库内的最新全量行数据（2026-10-02 版），热更增量（inc/del）未留盘。

解码：toolkit_core.bindict_table 结案规则 —— 基址恒为 blob 起点；
  attrs 走 0x0b jump → 0xC6/0x86 嵌套行帧（见 30_分析/子代理产出_20261022/
  all_equips_jump基址_报告.md 结论「通用规则 = 基址恒为 blob 起点 + 帧族分派」）。

输出：
  01_索引与产物/30_分析/all_equips_经典服基线_20261029/all_equips_attrs_classic.json
  字段与 30_分析/子代理产出_20261022/all_equips_attrs_kj1.json 同构
  （key/name/equip_type/weapon_type/attrs/attrs_frame）。
"""
import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
PACK = PROJ / "01_索引与产物/源包/apk_20261002/mumu_5.0.679/assets/script.py314.lc.npk"
OUT_DIR = PROJ / "01_索引与产物/30_分析/all_equips_经典服基线_20261029"
OUT = OUT_DIR / "all_equips_attrs_classic.json"

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import la_unpack_core as L  # noqa: E402
from toolkit_core.bindict_table import (  # noqa: E402
    decode_table_rows, parse_legacy_chs_pool, resolve_jump_target,
)

FID_ROWS = "1F8E9684E1B97CE0"   # all_equips_data.py（行表）
FID_CHS = "94AB0B3FD057EF01"    # all_equips_data_chs.py（sec1=字段名池 10,949）


def extract_entries():
    a = L.NpkArchive(str(PACK))
    got = {}
    for ent in a.iter_entries():
        fid = "%016X" % ent.file_id
        if fid in (FID_ROWS, FID_CHS):
            got[fid] = a.read_entry(entry_index=ent.entry_index)
        if len(got) == 2:
            break
    if len(got) != 2:
        raise SystemExit("源包缺条目：%s" % (set((FID_ROWS, FID_CHS)) - set(got)))
    return got[FID_ROWS], got[FID_CHS]


def sections(raw: bytes):
    """枚举 0x7B 体：[(marker_off, body_len, count)]。"""
    out, i = [], 0
    while i < len(raw) - 9:
        if raw[i] != 0x7B:
            i += 1
            continue
        bl = struct.unpack_from("<I", raw, i + 1)[0]
        if bl < 16 or i + 5 + bl > len(raw):
            i += 1
            continue
        cnt, res = struct.unpack_from("<II", raw, i + 5)
        if res == 0 and cnt < 200000 and 8 + 4 * cnt < bl:
            out.append((i, bl, cnt))
        i += 5 + bl
    return out


def main() -> int:
    raw_rows, raw_chs = extract_entries()
    s_rows = sections(raw_rows)
    s_chs = sections(raw_chs)
    # 行表：单段 10,949（0x73 包装头 278B）；字段池：chs sec1（10,949 与行数同构）
    off_r, ln_r, cnt = next(s for s in s_rows if s[2] == 10949)
    off_p, ln_p, cnt_p = next(s for s in s_chs if s[2] == 10949)
    body = raw_rows[off_r + 5: off_r + 5 + ln_r]
    blob = body[8 + 4 * cnt:]
    pool = parse_legacy_chs_pool(raw_chs[off_p: off_p + 5 + ln_p])
    rows, unbound = decode_table_rows(body, pool)

    out, stats = [], {"rows_index": cnt, "rows_decoded": len(rows),
                      "unbound": len(unbound), "attrs_total": 0, "attrs_ok": 0,
                      "frames": {}}
    for r in rows:
        v = r.get("values") or {}
        g = lambda k: (v.get(k)[1] if isinstance(v.get(k), tuple) else v.get(k))
        rec = {"key": r["key"], "name": g("name"),
               "equip_type": g("equip_type"), "weapon_type": g("weapon_type"),
               "attrs": None, "attrs_frame": None}
        a = v.get("attrs")
        if isinstance(a, tuple) and str(a[1]).startswith("jump:"):
            stats["attrs_total"] += 1
            j = int(str(a[1])[5:])
            res = resolve_jump_target(blob, j, pool)
            rec["attrs_frame"] = res.get("frame")
            fr = res.get("frame")
            stats["frames"][fr] = stats["frames"].get(fr, 0) + 1
            if res.get("error") is None and res.get("values"):
                stats["attrs_ok"] += 1
                rec["attrs"] = res["values"] if fr != "0x27" else {
                    "pairs": res.get("pairs"), "leaves": res.get("leaves")}
        out.append(rec)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"meta": {
        "generated": "2026-10-29",
        "source_package": str(PACK).replace("\\", "/"),
        "package_sha256": L.NpkArchive(str(PACK)).file_hash_used if hasattr(
            L.NpkArchive(str(PACK)), "file_hash_used") else None,
        "entries": {"all_equips_data.py(fid %s)" % FID_ROWS:
                    {"bytes": len(raw_rows), "count": cnt},
                    "all_equips_data_chs.py(fid %s) sec1" % FID_CHS:
                    {"bytes": ln_p, "pool": cnt_p}},
        "decode": "toolkit_core.bindict_table 结案规则；基址=blob 起点；attrs=0xC6/0x86 帧",
        "stats": stats,
    }, "rows": out}
    OUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
