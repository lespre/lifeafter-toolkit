# -*- coding: utf-8 -*-
"""all_equips 家族三表全量提取（node 索引法）— 2026-10-29。

★ 2026-10-29 结案：0x7B 行表索引尾结构补全 ——
  旧 parse_index 只回收 bucket 数组直连节点，漏掉 node 溢出区的完整键链。
  实际结构（kj1/yk/经典服三表逐一验证）：
    索引尾 = 76 01 0b + uleb(bucket_count) + bucket_count×8B 桶数组(hash, node_off)
             + node 溢出区：连续 (uleb key, uleb row_start) 对 —— 这才是全量行索引
  「0x7B 头 cnt」是扩容声明容量（含墓碑/空槽），≠ 物理行数：
    经典服 10,949 槽 = 3,287 活跃 + 7,662 空槽
    kj1     5,248 槽 = 1,553 活跃 + 1,238 墓碑(段后 3e 流) + 2,457 空槽
    yk      9,483 槽 = 2,228 活跃 + …
  物理活跃行 100% 解出（lenient=True 回收行尾 inline list variant）：
    经典服 3,287（旧法 2,721+516 失败） / kj1 1,553（旧 1,226+326） / yk 2,228（旧 1,637+591）

琥珀护臂家族（仿生/典藏/雨战/雪地/典藏体验版）名字在热更池（还原树 chs 池
11,632 串）中，但三张表活跃行均无其行数据 —— 行数值在热更 inc 分片
（all_equips_data_base/_inc/_del）内，该分片在库内所有留盘 npk 中均不存在，
判定为数据源硬缺口（2026-10-02 基线之后的 PE 热更内容未落盘）。

数据源：
  经典服 base  01_索引与产物/源包/apk_20261002/mumu_5.0.679/assets/script.py314.lc.npk
    fid 1F8E9684E1B97CE0 行表 + fid 94AB0B3FD057EF01 池
  kj1 / yk     01_索引与产物/源包/pe_20261020/script.py314.lc.npk（PE 最新快照）
    kj1: fid 3D123F2BEE73ED47 行表(com/cdata/oversea/all_equips_data_auto_oversea_data_kj1.py)
         + fid 9B6BE39D902BD6D6 池(…_kj1_chs.py)
    yk : fid 5790A7683EB6AAA8 行表(…_yk.py) + fid D1D2E03CF2901EBC 池(…_yk_chs.py)

输出：01_索引与产物/30_分析/all_equips_全量_node索引_20261029/
  all_equips_attrs_classic.json / _kj1.json / _yk.json
  行结构 key/name/equip_type/weapon_type/attrs/attrs_frame（与 20261022/20261029 冻结同构）
"""
import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import la_unpack_core as L  # noqa: E402
from toolkit_core.bindict_table import (  # noqa: E402
    decode_table_rows, parse_legacy_chs_pool, resolve_jump_target,
)

PACK_APK = PROJ / "01_索引与产物/源包/apk_20261002/mumu_5.0.679/assets/script.py314.lc.npk"
PACK_PE20 = PROJ / "01_索引与产物/源包/pe_20261020/script.py314.lc.npk"
OUT_DIR = PROJ / "01_索引与产物/30_分析/all_equips_全量_node索引_20261029"

TABLES = {
    "classic": {
        "pack": PACK_APK, "fid_rows": "1F8E9684E1B97CE0", "fid_pool": "94AB0B3FD057EF01",
        "label": "经典服 all_equips_data（apk_20261002 安装基线）",
    },
    "kj1": {
        "pack": PACK_PE20, "fid_rows": "3D123F2BEE73ED47", "fid_pool": "9B6BE39D902BD6D6",
        "label": "简单生存服 oversea_data_kj1（pe_20261020 快照）",
    },
    "yk": {
        "pack": PACK_PE20, "fid_rows": "5790A7683EB6AAA8", "fid_pool": "D1D2E03CF2901EBC",
        "label": "悠客服 oversea_data_yk（pe_20261020 快照）",
    },
}


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


def uleb(b: bytes, p: int):
    r, s = 0, 0
    while True:
        x = b[p]
        p += 1
        r |= (x & 0x7F) << s
        if not x & 0x80:
            return r, p
        s += 7


def node_index(blob: bytes) -> tuple[int, list[tuple[int, int]], int]:
    """★ 结案规则：索引尾 = 76 01 0b + uleb(bc) + bc×8B 桶数组 + node 溢出区键对。

    返回 (bucket_count, [(key, row_start)], tombstone 数暂 0)。
    桶数组每条 8B = (hash, node_off)；node 区从数组尾开始，连续 (k, v) uleb 对。
    """
    de = struct.unpack_from("<I", blob, 0)[0]
    tail = blob[de:]
    if not (len(tail) >= 4 and tail[0] == 0x76 and tail[1] == 0x01 and tail[2] == 0x0B):
        raise ValueError("index tail head not 76 01 0b: %s" % tail[:4].hex())
    bc, p = uleb(tail, 3)
    arr_end = p + 8 * bc
    if arr_end > len(tail):
        raise ValueError("bucket array out of tail")
    pairs = []
    q = arr_end
    while q < len(tail):
        k, q = uleb(tail, q)
        v, q = uleb(tail, q)
        pairs.append((k, v))
    return bc, pairs, arr_end


def extract(tag: str, cfg: dict) -> dict:
    a = L.NpkArchive(str(cfg["pack"]))
    got = {}
    for ent in a.iter_entries():
        fid = "%016X" % ent.file_id
        if fid in (cfg["fid_rows"], cfg["fid_pool"]):
            got[fid] = a.read_entry(entry_index=ent.entry_index)
    raw_rows, raw_pool = got[cfg["fid_rows"]], got[cfg["fid_pool"]]

    soff, sbl, scnt = sections(raw_rows)[0]
    body = raw_rows[soff + 5: soff + 5 + sbl]
    blob = body[8 + 4 * scnt:]
    bc, pairs, _arr_end = node_index(blob)

    psoff, psbl, _pcnt = sections(raw_pool)[0]
    pool = parse_legacy_chs_pool(raw_pool[psoff: psoff + 5 + psbl])

    rows, unbound = decode_table_rows(body, pool, index_rows=pairs, lenient=True)

    stats = {"slots_declared": scnt, "buckets": bc, "index_pairs": len(pairs),
             "rows_decoded": len(rows), "unbound": len(unbound),
             "pool_strings": len(pool), "attrs_total": 0, "attrs_ok": 0,
             "frames": {}}
    out = []
    for r in rows:
        v = r.get("values") or {}
        g = lambda k: (v.get(k)[1] if isinstance(v.get(k), tuple) else v.get(k))
        rec = {"key": r["key"], "name": g("name"),
               "equip_type": g("equip_type"), "weapon_type": g("weapon_type"),
               "attrs": None, "attrs_frame": None}
        aattr = v.get("attrs")
        if isinstance(aattr, tuple) and str(aattr[1]).startswith("jump:"):
            stats["attrs_total"] += 1
            j = int(str(aattr[1])[5:])
            res = resolve_jump_target(blob, j, pool)
            fr = res.get("frame")
            rec["attrs_frame"] = fr
            stats["frames"][fr] = stats["frames"].get(fr, 0) + 1
            if res.get("error") is None and res.get("values"):
                stats["attrs_ok"] += 1
                rec["attrs"] = res["values"] if fr != "0x27" else {
                    "pairs": res.get("pairs"), "leaves": res.get("leaves")}
        out.append(rec)

    payload = {"meta": {
        "generated": "2026-10-29",
        "table": tag,
        "label": cfg["label"],
        "source_package": str(cfg["pack"]).replace("\\", "/"),
        "entries": {
            "rows(fid %s)" % cfg["fid_rows"]: {"bytes": len(raw_rows), "slots": scnt},
            "pool(fid %s)" % cfg["fid_pool"]: {"bytes": len(raw_pool), "strings": len(pool)},
        },
        "decode": ("node 索引法（76 01 0b + 桶数组 + node 溢出区键对，2026-10-29 结案）；"
                   "lenient=True 回收行尾 inline list variant；attrs=0xC6/0x86 帧"),
        "stats": stats,
    }, "rows": out}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / ("all_equips_attrs_%s.json" % tag)
    out_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(tag, json.dumps(stats, ensure_ascii=False))
    print("  wrote", out_path)
    return payload


def main() -> int:
    for tag, cfg in TABLES.items():
        extract(tag, cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
