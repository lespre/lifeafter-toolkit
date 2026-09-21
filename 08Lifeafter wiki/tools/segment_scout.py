# -*- coding: utf-8 -*-
"""
segment_scout.py —— id 段侦察器：名册段 dump / jump 组引用收集 / 缺口对照

三类侦察一次完成（2026-09-06 芯片轮沉淀：曾因手写脚本配错 CHS 池（002131 漂移池）
解出杂物名假数据——本工具强制正源配对+漂移防呆）。

用法：
  1) 段名册：python tools/segment_scout.py roster 018005 --range 330000-331999
       → 自动配对正源 chs（同变体/校验条数）+ 段内 id/name/desc 行
  2) 引用收集：python tools/segment_scout.py refs 009729 --fields up_chips,active_pool_ids
       --seg 330000-332000
       → 每行指定 jump 组解出的 id（过滤在段内的）
  3) 缺口对照：python tools/segment_scout.py compare --refs <refs.json> --roster <roster.json>
       → refs 有而 roster 无的 id 清单（=名册缺口/板未收录）
  roster/refs 都支持 --out <file.json> 落盘供 compare。

正源 chs 自动配对逻辑（scan_table_family 同款）：
  同变体段名 chs → 漂移防呆（池条数 ≠ base 期望值=警告）；roster 缺省自动找族内 chs。
"""
import argparse
import json
import struct
import sys
from pathlib import Path

BA8_ENTRIES = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
sys.path[:0] = [str(Path(__file__).resolve().parent),
                str(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")]
from bindict_provenance import decode_table_rows_with_chs_slots
from toolkit_core.bindict_table import parse_legacy_chs_pool
from toolkit_core.bindict_rows import uleb


def resolve(fn):
    fn = str(fn)
    if not fn.endswith(".bin"):
        fn = f"{int(fn):06d}.bin"
    p = Path(fn)
    return p if p.exists() else BA8_ENTRIES / fn


def xbody_at(data):
    at = data.find(b"x{")
    if at < 0:
        return None, None
    n = struct.unpack_from("<I", data, at + 2)[0]
    return at, n


def find_chs_for(base_name, expect_pool_n=None):
    """同变体段 chs 配对：xxx_auto_oversea_data_ykxq.py ↔ xxx_..._ykxq_chs.py"""
    stem = base_name.replace("_chs.py", "").replace(".py", "")
    for p in sorted(BA8_ENTRIES.glob("*.bin")):
        data = p.read_bytes()[:8192]
        if b"\\" not in data and b"chs" not in data.lower():
            continue
        tail = data[-4096:]
        import re
        names = {m.decode("ascii", "replace").split("\\")[-1]
                 for m in re.findall(rb"[A-Za-z0-9_\\]{8,}\.py", tail)}
        for n in names:
            if n.replace("_chs.py", "") == stem and n.endswith("_chs.py"):
                return p.name
    return None


def load_table(fname):
    path = resolve(fname)
    data = path.read_bytes()
    at, xl = xbody_at(data)
    if at is None:
        raise SystemExit(f"{path.name}: 无 x{{ 容器")
    body = data[at + 6: at + 6 + xl]
    return path.name, data, at, body


def load_pool(chs_file):
    if not chs_file:
        return {}, None
    pool = parse_legacy_chs_pool((resolve(chs_file)).read_bytes())
    return pool, chs_file


def flat(row):
    return {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v)
            for k, v in row["values"].items()}


def read_jump_group(body, jump_ref):
    """解 jump 组（组起点 0x27）；失败返回 []"""
    tgt = int(str(jump_ref).split(":")[1])
    try:
        count, pos = uleb(body, tgt + 2, len(body))
        vals = []
        for _ in range(min(count, 500)):
            v, pos = uleb(body, pos, len(body))
            vals.append(v)
        return vals
    except Exception:
        return []


def parse_range(s):
    if "-" in s:
        a, b = s.split("-", 1)
        return int(a), int(b)
    a = int(s)
    return a, a + 9999


def cmd_roster(args):
    fname, data, at, body = load_table(args.table)
    expect = None
    try:
        expect = struct.unpack_from("<I", data, at + 6)[0]
    except Exception:
        pass
    chs = args.chs
    if not chs:
        # 尾名同变体配对
        import re
        names = {m.decode("ascii", "replace").split("\\")[-1]
                 for m in re.findall(rb"[A-Za-z0-9_\\]{8,}\.py", data[-8192:])}
        chs = find_chs_for(sorted(names)[0] if names else fname, expect)
    pool, chs_used = load_pool(chs)
    if expect and pool and len(pool) != expect:
        print(f"⚠ 漂移池警告：{chs_used} 池 {len(pool)} 条 ≠ base 期望 {expect}——名字槽会错位，换正源 chs！")
    rows, un = decode_table_rows_with_chs_slots(body, pool)
    lo, hi = parse_range(args.range)
    out = []
    for r in rows:
        if lo <= r["key"] <= hi:
            f = flat(r)
            out.append({"id": r["key"], "name": str(f.get("name") or "")[:80],
                        "desc": str(f.get("desc") or "")[:60]})
    print(f"{fname}（chs {chs_used or '无'}）rows={len(rows)} unbound={len(un)} | 段 {lo}-{hi} 命中 {len(out)} 行")
    for o in out[: args.limit]:
        print(f"  {o['id']} | {o['name'][:44]}")
    if len(out) > args.limit:
        print(f"  …（共 {len(out)} 行，--limit 增加可见）")
    if args.out:
        json.dump({"table": fname, "chs": chs_used, "segment": [lo, hi], "rows": out},
                  open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"已存 {args.out}（{len(out)} 行）")


def cmd_refs(args):
    fname, data, at, body = load_table(args.table)
    pool, chs_used = load_pool(args.chs)
    rows, un = decode_table_rows_with_chs_slots(body, pool)
    lo, hi = parse_range(args.seg) if args.seg else (0, 10 ** 12)
    out = {}
    for r in rows:
        f = flat(r)
        got = {}
        for fd in args.fields.split(","):
            v = f.get(fd.strip())
            if isinstance(v, str) and v.startswith("jump:"):
                g = read_jump_group(body, v)
                ins = sorted(x for x in g if lo <= x <= hi)
                if ins:
                    got[fd.strip()] = ins
        if got:
            out[str(r["key"])] = got
    print(f"{fname} 行 {len(rows)} | 段 {lo}-{hi} 内引用: {len(out)} 行命中")
    for k, g in list(out.items())[: args.limit]:
        print(f"  key={k}: " + " ".join(f"{fd}={v}" for fd, v in g.items()))
    if args.out:
        json.dump({"table": fname, "segment": [lo, hi], "rows": out},
                  open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"已存 {args.out}")


def cmd_compare(args):
    refs = {}
    for rf in args.refs.split(","):
        d = json.load(open(rf, encoding="utf-8"))
        for k, g in d.get("rows", {}).items():
            for fd, vals in g.items():
                for v in vals:
                    refs.setdefault(v, []).append(f"{d.get('table','?')}:{k}.{fd}")
    if args.roster:
        rd = json.load(open(args.roster, encoding="utf-8"))
        have = {r["id"] for r in rd.get("rows", [])}
        missing = sorted(i for i in refs if i not in have)
        print(f"roster {args.roster} 收录 {len(have)} | refs 引用 {len(refs)} 唯一 id")
        print(f"→ refs 有而 roster 无（{len(missing)} 个）：")
        for i in missing:
            print(f"    {i}  ← {refs[i][:3]}")
    else:
        print(f"refs 唯一 id {len(refs)} 个:")
        for i in sorted(refs):
            print(f"  {i}  ← {refs[i][:2]}")


def main():
    ap = argparse.ArgumentParser(description="id 段侦察器")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("roster", help="段名册 dump")
    p1.add_argument("table")
    p1.add_argument("--range", required=True, help="如 330000-331999")
    p1.add_argument("--chs", default=None)
    p1.add_argument("--limit", type=int, default=60)
    p1.add_argument("--out", default=None)
    p2 = sub.add_parser("refs", help="jump 组引用收集")
    p2.add_argument("table")
    p2.add_argument("--fields", required=True, help="逗号分隔字段名")
    p2.add_argument("--chs", default=None)
    p2.add_argument("--seg", default=None, help="id 段过滤 如 330000-332000")
    p2.add_argument("--limit", type=int, default=30)
    p2.add_argument("--out", default=None)
    p3 = sub.add_parser("compare", help="引用 vs 名册 缺口")
    p3.add_argument("--refs", required=True, help="refs 输出 json（逗号可多份）")
    p3.add_argument("--roster", default=None, help="roster 输出 json")
    args = ap.parse_args()
    if args.cmd == "roster":
        cmd_roster(args)
    elif args.cmd == "refs":
        cmd_refs(args)
    elif args.cmd == "compare":
        cmd_compare(args)


if __name__ == "__main__":
    main()
