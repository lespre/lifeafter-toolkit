# -*- coding: utf-8 -*-
"""
decode_probe.py —— 解码探针：单表第一眼（表型指纹 + 行级解码 + 字段错位警示）

用法：
  python tools/decode_probe.py 024329 --chs 021919          # 工作副本 entry 号（BA8）
  python tools/decode_probe.py 024329.bin --chs 021919.bin
  python tools/decode_probe.py 1352 --rows 3                # 无 chs：只有指纹+行数估算
  python tools/decode_probe.py <file> --json                # 机器可读

输出：
  1. 文件/容器信息：大小、x{ 偏移、容器体长
  2. 表型指纹：行 marker 分布（0x92/0x96/0xd6…）、index 行数估算、schema 数、
     字段名样本（有 chs 时）
  3. 标准解码：rows/unbound + 前 N 行字段 dump
  4. 字段错位警示：文本值高比例像路径/ui 图标/超长句 → 「字段名可能来自值文本区
     （0x96 宽表模式）或文本槽跨行错位」——下字段语义结论前先看这个
"""
import argparse
import json
import struct
import sys
from pathlib import Path

BA8_ENTRIES = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
sys.path[:0] = [str(Path(__file__).resolve().parent),
                str(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")]
try:
    from bindict_provenance import decode_table_rows_with_chs_slots
    from toolkit_core.bindict_table import (parse_legacy_chs_pool, parse_index,
                                            _collect_schemas, _schema_at)
    HAVE_DECODER = True
except Exception as e:
    HAVE_DECODER = False
    print("!! 解码器不可用:", e)


def resolve(fn):
    fn = str(fn)
    if not fn.endswith(".bin"):
        fn = f"{int(fn):06d}.bin"
    p = Path(fn)
    if p.exists():
        return p
    return BA8_ENTRIES / fn


def xbody_info(data):
    """找合法 x{ 容器：x{ 后 4B=容器体长；体头 8B=count+reserved（reserved 必须 0）。

    27.104 教训：二进制内 b"x{" 序列可巧合出现（如 LifeAfter common_item kj1 base
    27423：x{ 后跟 2300 7e7b 2300…=段偏移表=假标记，单看 find 首个 x{ 会拿错体长超界）；
    老格式 0x73 壳表可能没有任何合法 x{。返回 mode=ok / no_x / fake_only 区分。"""
    pos = 0
    found = 0
    while True:
        at = data.find(b"x{", pos)
        if at < 0:
            return None, None, ("fake_only" if found else "no_x")
        found += 1
        if at + 6 <= len(data):
            n = struct.unpack_from("<I", data, at + 2)[0]
            if 0 < n <= len(data) - at - 6:
                try:
                    cnt, res = struct.unpack_from("<II", data, at + 6)
                    if res == 0 and cnt <= 300000:
                        return at, n, "ok"
                except Exception:
                    pass
        pos = at + 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="entry 号或 .bin 文件名（BA8 工作副本）")
    ap.add_argument("--chs", default=None, help="配对 CHS 池文件（entry 号或 .bin）")
    ap.add_argument("--rows", type=int, default=5, help="dump 前 N 行（默认 5）")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    args = ap.parse_args()

    path = resolve(args.file)
    if not path.is_file():
        print(f"找不到 {path}")
        return
    data = path.read_bytes()
    at, xl, xmode = xbody_info(data)
    if at is None:
        head = data[:64]
        # 模块包装/加载壳：即使无 x{ 容器，也可恢复 com\\cdata\\xxx.py 逻辑路径
        # （实测 common_item_data_del.py=147B、合并壳 common_item_data.py=815B 均为
        # tI 包装的 py 代码模块；旧提示把它们误报成 0x73 纯 CHS 池=扫描缺陷）
        # 模块包装/加载壳探测：tI 包装的 py 代码模块内嵌逻辑路径文本
        dotpy = data.find(b".py")
        if dotpy > 0:
            seg = data[max(0, dotpy - 96): dotpy + 3]
            seg = seg[seg.rfind(b"\\") + 1:] if seg.rfind(b"\\") >= 0 else seg
            logical = seg.decode("utf-8", "replace")
            print(f"{path.name}: 无 x{{ 容器（{len(data)}B）——py 模块加载壳/代码，"
                  f"恢复逻辑路径尾={logical}；非表体，含表体请换 _base 实体。")
        elif xmode == "fake_only" and head[:1] == b"\x73":
            print(f"{path.name}: 无合法 x{{ 容器但发现假 x{{ 序列（{len(data)}B）——头 0x73=老格式壳"
                  f"（段偏移表/索引/覆盖表，如 LifeAfter kj1 base 27423），当前解码器不支持，标老格式勿硬解。")
        elif xmode == "no_x" and head[:1] == b"\x73":
            print(f"{path.name}: 无 x{{ 容器（{len(data)}B）——0x73 纯 CHS 池/壳（0x73+段偏移表），换 base 表。")
        else:
            print(f"{path.name}: 无合法 x{{ 容器（{len(data)}B）——纯 CHS 池、py 壳或老格式覆盖表，换 base 表。")
        return
    body = data[at + 6: at + 6 + xl]

    out = {"file": path.name, "bytes": len(data), "x_offset": at, "x_body_len": xl}

    # CHS 池
    pool = {}
    if args.chs:
        cpath = resolve(args.chs)
        if cpath.is_file():
            pool = parse_legacy_chs_pool(cpath.read_bytes())
            out["chs"] = cpath.name
            out["pool_texts"] = len(pool)
            # 漂移池防呆：base 内嵌期望池条数（x{ 容器体前 8B 结构区）vs 传入池条数
            # 实证：common_item 正源 023928=55141 条；旧漂移 002131=55085（少 56）=名字槽错位
            try:
                expect = struct.unpack_from("<I", data, at + 6)[0]
                if expect and expect != len(pool):
                    out["pool_mismatch_warning"] = (
                        f"CHS 池条数 {len(pool)} ≠ base 期望 {expect}——疑似旧漂移池配对！"
                        f"（实证：002131 旧池=55085 vs 正源 023928=55141=名字槽错位解出杂物名）"
                        f"先核对正源 chs（skill：common_item 正源=023928/EF3A；通用=同变体段 chs）。")
            except Exception:
                pass

    # 表型指纹
    marker_counts = {}
    for b in body[: min(len(body), 65536)]:
        if b in (0x73, 0x76, 0x92, 0x96, 0xD6):
            marker_counts.setdefault(b, 0)
            marker_counts[b] += 1
    out["head_marker_counts"] = {f"{k:02X}": v for k, v in sorted(marker_counts.items())}
    # 0x96 宽表：标准行 marker 0x92 几乎为零 + 0x96/0x76 密集才提示（普通表数据区含 0x96 字节=常态，勿误报）
    is_wide96 = marker_counts.get(0x96, 0) > 400 and marker_counts.get(0x92, 0) < 20
    if is_wide96:
        out["table_type_warning"] = "疑似 0x96 宽表形态：字段名可能来自池值文本区（chip_type/nucleus_entry 同族）——解出的文本字段语义需先验键域，勿直接当列名/品级。"

    index_rows = {}
    try:
        index_rows = parse_index(body)
    except Exception as e:
        out["index_error"] = str(e)
    out["index_row_estimate"] = len(index_rows)

    schema_n = 0
    field_names = []
    try:
        if index_rows and HAVE_DECODER:
            schemas = _collect_schemas(body, index_rows)
            schema_n = len(schemas)
            ref0 = next(iter(schemas))
            try:
                _, fields, _ = _schema_at(body, ref0, pool)
                field_names = [f[2] for f in fields[:14]]
            except Exception:
                pass
    except Exception as e:
        out["schema_error"] = str(e)
    out["schema_count"] = schema_n
    if field_names:
        out["field_name_sample"] = field_names

    # 标准解码
    if HAVE_DECODER and not (is_wide96 and not args.chs):
        try:
            rows, unbound = decode_table_rows_with_chs_slots(body, pool)
            out["rows"] = len(rows)
            out["unbound"] = len(unbound)

            # 键域提示：中文字段名=池值文本误升为键（行列式/无名槽，如 chip_type 芯片名列组）
            # 或 0x96 宽表形态；正常 schema 字段名=英文（name/hd_class/effect_label…）
            if rows and pool:
                all_keys = set()
                for r in rows[:200]:
                    all_keys.update(k for k in r["values"])
                has_cjk_keys = any(k and ord(k[0]) > 0x2E7F for k in all_keys)
                if is_wide96 or has_cjk_keys:
                    out["keydomain"] = {
                        "field_keys_sample": sorted(all_keys)[:30],
                        "note": (f"{'0x96 形态；' if is_wide96 else ''}字段名含中文字段"
                                 f"{'（池值文本误升为键=行列式/无名槽设计，如 chip_type 芯片名列组）' if has_cjk_keys else ''}"
                                 f"——此类列语义=行×列关联位；真字段列以 effect_label 类已知英文字段为锚人工对齐，"
                                 f"勿把同名列当普通字段下结论。"),
                    }
            # 重复/幽灵行检测（27.104：chip huodong 行 30 key=200002=2023-07-13 与行 2 同窗
            # =「期2/3重复」元凶；key>=200000=测试/占位幽灵段，行序对齐前必须剔除）
            try:
                from collections import Counter
                ghost = [r["key"] for r in rows if isinstance(r.get("key"), int) and r["key"] >= 200000]
                if ghost:
                    out["ghost_row_warning"] = {
                        "ghost_keys": ghost[:10], "count": len(ghost),
                        "note": "key>=200000=测试/占位幽灵行（实例：chip huodong key200002=2023-07-13 与正常行"
                                "同窗=用户口径「期2/3重复」根因）——行序对齐/期次统计前剔除，勿当真实期。",
                    }
                start_fields = set()
                for r in rows[:300]:
                    start_fields.update(k for k in r["values"] if any(
                        s in k.lower() for s in ("start", "begin", "open_time")))
                dups = {}
                for sf in sorted(start_fields)[:3]:
                    cnt = Counter()
                    for r in rows[:1500]:
                        v = r["values"].get(sf)
                        if isinstance(v, tuple):
                            v = v[1]
                        if isinstance(v, int) and v > 1000000000:  # 时间戳形态
                            cnt[v // 86400] += 1  # 日期级（同日不同秒也可见）
                    d = {ts: c for ts, c in sorted(cnt.items()) if c > 1}
                    if d:
                        dups[sf] = d
                if dups:
                    out["dup_start_warning"] = {
                        "fields": list(start_fields)[:3],
                        "same_day_row_counts": dups,
                        "note": "同日起始多行=重复登记（幽灵/并行场次）——按行序做期次对齐前先剔除 key>=200000"
                                "幽灵行并人工核对；实例 chip huodong：2130 与 200002 同 2023-07-13=用户「期2/3重复」。",
                    }
            except Exception:
                pass
            # 文本值形态抽查（错位警示）
            texts = []
            for r in rows[:80]:
                for k, v in r["values"].items():
                    if isinstance(v, tuple) and len(v) == 2 and isinstance(v[1], str) and v[1]:
                        texts.append(v[1])
                    elif isinstance(v, str) and v:
                        texts.append(v)
            pathy = sum(1 for t in texts if "/" in t or t.startswith(("ui/", "icon", "effect", "mesh", "animator")))
            longy = sum(1 for t in texts if len(t) > 30)
            if texts:
                out["text_samples"] = texts[:6]
                out["text_path_ratio"] = round(pathy / len(texts), 2)
                out["text_long_ratio"] = round(longy / len(texts), 2)
                if pathy / len(texts) > 0.3:
                    out["text_warning"] = (f"文本槽 {pathy}/{len(texts)} 像路径/图标引用——"
                                           f"文本字段可能跨行错位（如 all_equips desc 模式），数值字段才可信。")
            # 行 dump
            out["row_dump"] = []
            for r in rows[: max(0, args.rows)]:
                flat = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v)
                        for k, v in r["values"].items()}
                short = {k: (str(v)[:60] if not isinstance(v, (int, float)) else v)
                         for k, v in flat.items() if v not in (None, "", 0)}
                out["row_dump"].append({"key": r["key"], "fields": short})
        except Exception as e:
            out["decode_error"] = str(e)

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return

    print(f"文件 {path.name}  {len(data):,}B | x{{ @{at} 体 {xl:,}B")
    if out.get("chs"):
        print(f"CHS {out['chs']}  池 {out['pool_texts']} 条")
    print(f"头部 marker 分布: " + " ".join(f"{k}=x{v}" for k, v in out.get("head_marker_counts", {}).items()))
    print(f"index 行数估算: {out.get('index_row_estimate')}   schema 数: {out.get('schema_count')}")
    if out.get("field_name_sample"):
        print(f"字段名样本: {' / '.join(out['field_name_sample'][:12])}")
    if out.get("table_type_warning"):
        print(f"⚠ {out['table_type_warning']}")
    if "rows" in out:
        print(f"解码: rows={out['rows']}  unbound={out['unbound']}")
        if out.get("ghost_row_warning"):
            g = out["ghost_row_warning"]
            print(f"⚠ {g['note']}  幽灵行: {g['ghost_keys']}")
        if out.get("dup_start_warning"):
            print(f"⚠ {out['dup_start_warning']['note']}  字段={out['dup_start_warning']['fields']}")
        if out.get("text_warning"):
            print(f"⚠ {out['text_warning']}  (路径占比 {out.get('text_path_ratio')})")
        for rd in out.get("row_dump", []):
            print(f"  key={rd['key']}: " + json.dumps(rd["fields"], ensure_ascii=False)[:340])


if __name__ == "__main__":
    main()
