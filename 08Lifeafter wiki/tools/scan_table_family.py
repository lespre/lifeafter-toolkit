# -*- coding: utf-8 -*-
"""
scan_table_family.py v2 —— 表族通道侦察器（BA8 工作副本）

v2（2026-09-06）：
  1. 主族/子族分组：变体后缀剥离后按表族名分组输出（huodong_conf 家族、falling_box_* 子族…）
  2. 海外壳收敛：kr/sea/kjhmt/au/kjjp/kjna/kjsea/jp 等 ~0.3KB 变体折叠为一行计数
  3. CHS 配对三级回退：同变体段名配对 → 主族内其它 chs 逐个试解取 unbound 最低
     （实证：main 形态壳 016869 无同名字典 chs，可试 kj1/kjxq chs 配对）
  4. 主通道结论行：ykxq → main-plain → kj1/kjxq(仅覆盖对比) → 壳，给明确行动指令
  5. --rows 空池/错池高 unbound 时输出「疑似 CHS 配对缺失」警示（缺池≠行缺失，27.9x 教训）

用法：
  python tools/scan_table_family.py huodong_conf
  python tools/scan_table_family.py huodong_conf --rows
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

BA8_ENTRIES = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
BA8_MANIFEST = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\manifest.json")
TAIL_PAT = re.compile(rb"[A-Za-z0-9_\\]{8,}\.py")

OVERSEA_REGIONS = ("kr", "sea", "kjsea", "kjhmt", "kjjp", "kjna", "au", "hmt", "jp", "tw", "vn", "th")


def classify(name):
    n = name.lower()
    if n.endswith("_chs.py"):
        return "chs"
    if n.endswith("_auto_oversea_data_ykxq.py"):
        return "ykxq"
    if n.endswith("_auto_oversea_data_yk.py"):
        return "yk"
    if n.endswith("_auto_oversea_data_kjxq.py"):
        return "kjxq"
    if n.endswith("_auto_oversea_data_kj1.py"):
        return "kj1"
    if "_auto_oversea_data_" in n or "_for_export" in n or "_oversea" in n:
        # 海外区域壳（小文件）：命名段=_auto_oversea_data_<region>
        m = re.search(r"_auto_oversea_data_([a-z0-9]+)\.py$", n)
        if m and m.group(1) in OVERSEA_REGIONS:
            return "oversea-shell"
        return "other-oversea"
    if n.endswith(".py"):
        return "main-plain"
    return "other"


def family_of(name):
    """变体后缀剥离 → 表族名：falling_box_huodong_conf_data_auto_oversea_data_ykxq.py
    → falling_box_huodong_conf_data；xxx_kj1_chs.py → xxx。chs 尾与变体段都剥。"""
    n = re.sub(r"_chs\.py$", "", name)                      # xxx_kj1_chs.py → xxx_kj1
    n = re.sub(r"_(?:auto_oversea_data|for_export|auto)(?:_[a-z0-9]+)?$", "", n)  # xxx_kj1 → xxx
    n = re.sub(r"\.py$", "", n)
    return n


PRIORITY = {"ykxq": 0, "main-plain": 1, "yk": 2, "kjxq": 3, "kj1": 4, "chs": 5,
            "other-oversea": 6, "oversea-shell": 7, "other": 8}
LABEL = {
    "ykxq": "ykxq（全量主通道候选）", "main-plain": "主表形态（无变体后缀）",
    "yk": "yk（运营文本/壳）", "kjxq": "kjxq 覆盖（测试服专属·子集）",
    "kj1": "kj1 覆盖（测试服专属·子集）", "chs": "CHS 文本池",
    "other-oversea": "其它 overseas", "oversea-shell": "海外区域壳",
    "other": "其它",
}


def xbody_info(data):
    """找合法 x{ 容器（与 decode_probe 同版，27.104 硬化）：x{ 后 4B=体长；
    体头 8B=count+reserved 校验。二进制里 b"x{" 可巧合出现（后跟段偏移表=假标记，
    如 LifeAfter kj1 base 27423）；老格式 0x73 壳可能无任何合法 x{。返回 mode=ok/no_x/fake_only。"""
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


def load_fids():
    fids = {}
    try:
        m = json.load(open(BA8_MANIFEST, encoding="utf-8"))
        for e in m.get("entries", []):
            fids[Path(e["output_file"]).name] = e.get("file_id")
    except Exception:
        pass
    return fids


# 解码器（模块级导入，decode_file 共用）
sys.path[:0] = [str(Path(__file__).resolve().parent),
                str(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")]
try:
    from bindict_provenance import decode_table_rows_with_chs_slots
    from toolkit_core.bindict_table import parse_legacy_chs_pool
    HAVE_DECODER = True
except Exception as _e:
    decode_table_rows_with_chs_slots = None
    parse_legacy_chs_pool = None
    HAVE_DECODER = False
    print("!! 解码器不可用（仅变体扫描）:", _e)


def decode_file(fname, pool_file=None):
    """解码单表。返回 (rows, unbound, used_pool)；老格式/无合法 x{ 容器返回 (None, None, None)。"""
    data = (BA8_ENTRIES / fname).read_bytes()
    at, n, xmode = xbody_info(data)
    if xmode != "ok":
        return None, None, None
    body = data[at + 6: at + 6 + n]
    pool = {}
    if pool_file:
        pool = parse_legacy_chs_pool((BA8_ENTRIES / pool_file).read_bytes())
    rows, un = decode_table_rows_with_chs_slots(body, pool)
    return len(rows), len(un), pool_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keyword", help="表名关键词，如 huodong_conf / vehicle_proto")
    ap.add_argument("--rows", action="store_true", help="解码候选表验证行数（含 CHS 三级配对回退）")
    ap.add_argument("--no-formal", action="store_true",
                    help="跳过正式服（经典服 npk）FID 对照（默认打开双源整合）")
    ap.add_argument("--json", action="store_true", help="机器可读输出（hits 全字段 + 双源判定）")
    ap.add_argument("--fid", metavar="FID", help="FID 反查模式：给出表族/名字/归属（不扫关键词）")
    args = ap.parse_args()

    if args.fid:
        fid_key = args.fid.upper().replace("0X", "")
        fids = load_fids()
        rev = {}
        for fn, fv in fids.items():
            rev.setdefault(str(fv).upper().replace("0X", ""), []).append(fn)
        found = rev.get(fid_key, [])
        print(f"FID {args.fid.upper()} 反查：")
        if not found:
            print("  BA8 工作副本 manifest 无此 FID（可能为正式服独有/未解包表）。")
            return
        for fn in found:
            data = (BA8_ENTRIES / fn).read_bytes()
            names = {m.decode("ascii", "replace").split("\\")[-1]
                     for m in TAIL_PAT.findall(data[-8192:])}
            cls = classify(sorted(names)[0]) if names else "?"
            fam = family_of(sorted(names)[0]) if names else "?"
            print(f"  {fn}  {len(data):,}B  {cls:<10} {sorted(names)[:2]}  族={fam}")
        return

    # 双源整合：正式服（经典服）npk FID 存在性对照
    formal_fids, formal_err = None, None
    formal_info = ""
    if not args.no_formal:
        try:
            reg = json.load(open(Path(__file__).resolve().parent.parent / "data" / "live_sources.json",
                                 encoding="utf-8"))
            src = next(s for s in reg.get("sources", [])
                       if s.get("source_id") == "lifeafter-classic-current")
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from live_npk_reader import LiveNpkReader
            rd = LiveNpkReader(src["path"], src.get("server_branch", "classic"))
            formal_fids = {f"{e.file_id:016X}": e.entry_index for e in rd._entries}
            formal_info = f"正式服对照：{src['path']}（{len(formal_fids)} entry）"
        except Exception as e:
            formal_err = str(e)
            formal_fids = {}
            formal_info = f"正式服对照不可用：{e}"

    fids = load_fids()
    hits = []
    for path in sorted(BA8_ENTRIES.glob("*.bin")):
        data = path.read_bytes()
        # Small script modules can be the complete ``*_del.py`` side of a
        # split table; filter by recovered logical name, not physical size.
        names = {m.decode("ascii", "replace").split("\\")[-1] for m in TAIL_PAT.findall(data[-8192:])}
        for n in sorted(names):
            if args.keyword.lower() in n.lower():
                at, xl, xmode = xbody_info(data)
                hits.append({"file": path.name, "bytes": len(data),
                             "x": xmode, "_xlen": xl if xmode == "ok" else None, "name": n,
                             "cls": classify(n), "fam": family_of(n)})
    # 同名尾名多文件去重（一个文件多个匹配名只取一个）
    seen_file = {}
    for h in hits:
        if h["file"] not in seen_file:
            seen_file[h["file"]] = h
    hits = list(seen_file.values())

    if not hits:
        print(f"0 命中：BA8 无表名含 '{args.keyword}' 的通道。")
        return

    if args.json:
        fids_map = load_fids()
        core_cls = {"ykxq", "main-plain", "kj1", "kjxq", "yk", "chs"}
        out = {"keyword": args.keyword, "family_hits": []}
        for h in sorted(hits, key=lambda x: (family_of(x["name"]), x["file"])):
            fid = fids_map.get(h["file"], "")
            rec = {"file": h["file"], "bytes": h["bytes"], "class": h["cls"],
                   "family": h["fam"], "name": h["name"], "fid": fid}
            if formal_fids:
                rec["formal_present"] = bool(fid and fid in formal_fids)
            out["family_hits"].append(rec)
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return

    # 分组：主族（hits 最多的族）优先列出，其余子族分组折叠
    fam_count = {}
    for h in hits:
        fam_count[h["fam"]] = fam_count.get(h["fam"], 0) + 1
    main_fam = max(fam_count, key=lambda f: (fam_count[f], f))
    print(f"表族 '{args.keyword}' 命中 {len(hits)} 文件 / {len(fam_count)} 子族：")
    if formal_info:
        print(f"  {formal_info}")
    print()

    def print_group(fam, title):
        gh = [h for h in hits if h["fam"] == fam]
        gh.sort(key=lambda h: (PRIORITY[h["cls"]], h["file"]))
        shells = [h for h in gh if h["cls"] == "oversea-shell"]
        core = [h for h in gh if h["cls"] != "oversea-shell"]
        print(f"  ── {title}：{fam}")
        for h in core:
            fid = fids.get(h["file"], "")
            if fid and formal_fids:
                dual = " 双源共享" if fid in formal_fids else " BA8/测试专属"
            elif fid:
                dual = " 未对照"
            else:
                dual = ""
            xs = f"x{{体 {h['_xlen']:,}B" if h.get("_xlen") else (
                "⚠假x{（老格式壳/索引表，无合法容器）" if h["x"] == "fake_only" else ("无x{（纯池/壳）" if h["x"] == "no_x" else "-"))
            print(f"    {h['file']}  {h['bytes']:>8,}B  {h['cls']:<10} {h['name'][:60]}  FID={fid}{dual}")
        if shells:
            print(f"    （海外区域壳 ×{len(shells)}：{', '.join(h['file'] for h in shells)}）")

    # 主族核心组打印
    print_group(main_fam, "主族")
    for fam in sorted(fam_count):
        if fam != main_fam:
            print_group(fam, "子族")

    print()
    # 主通道结论
    all_f = {h["file"]: h for h in hits}
    by_cls = {}
    for h in hits:
        by_cls.setdefault(h["cls"], []).append(h["file"])
    ykxq = by_cls.get("ykxq") or []
    mainp = by_cls.get("main-plain") or []
    kj = (by_cls.get("kj1") or []) + (by_cls.get("kjxq") or [])
    if ykxq:
        print(f"  ★ 主通道结论：ykxq（{', '.join(ykxq)}）→ 全量主表（{'已含' if not args.rows else '行数见下'}）；kj1/kjxq（{', '.join(kj)}）仅覆盖差异对比。")
    elif mainp:
        print(f"  ★ 主通道结论：主表形态（{', '.join(mainp)}）；{'运行 --rows 验证（main 壳可能需 CHS 回退配对）' if not args.rows else '行数见下'}。")
        if kj:
            print(f"  ⚠ kj1/kjxq（{', '.join(kj)}）=覆盖通道——行数比主表大时先怀疑主表是壳。")
    elif kj:
        print(f"  ⚠ 仅 kj1/kjxq（{', '.join(kj)}）=覆盖通道（kjxq 多为 BA8 专属；kj1 常双源同文件）——确认读取侧重后再解。")
    if by_cls.get("chs"):
        print(f"  · CHS 池：{', '.join(by_cls['chs'])}（按变体段配对，见 --rows）")

    # 双源服务器语义（存在性对照 → 经典/简单服数据层判定）
    if formal_fids is not None:
        core_hits = [h for h in hits if h["cls"] not in ("chs", "oversea-shell", "other")]
        shared = [h["file"] for h in core_hits if fids.get(h["file"]) and fids[h["file"]] in formal_fids]
        only = [h["file"] for h in core_hits if fids.get(h["file"]) and fids[h["file"]] not in formal_fids]
        kj_only = [h["file"] for h in core_hits if h["cls"] in ("kj1", "kjxq")
                   and fids.get(h["file"]) and fids[h["file"]] not in formal_fids]
        print(f"  ◆ 双源判定（{len(shared)} 共享 / {len(only)} 测试服专属）：")
        if shared:
            print(f"     共享（同 FID=同文件，经典服同读）：{', '.join(shared)}")
        if kj_only:
            print(f"     专属覆盖通道（该文件正式 npk 无，如 kjxq=BA8 最新覆盖层；内容启用与否仍看各服读取侧重）：{', '.join(kj_only)}")
        rest_only = [f for f in only if f not in kj_only]
        if rest_only:
            print(f"     专属其它通道（仅 BA8 打包）：{', '.join(rest_only)}")

    # --rows 解码
    if args.rows and HAVE_DECODER:
        print()
        cands = [h for h in hits if h["cls"] in ("ykxq", "main-plain", "kj1", "kjxq")]
        cands.sort(key=lambda h: (PRIORITY[h["cls"]], h["file"]))
        # CHS 候选：按变体段名 → 全族 chs 逐个试解取最优
        for h in cands[:5]:
            base_key = re.sub(r"\.py$", "", h["name"])
            same_variant = [x["file"] for x in hits
                            if x["cls"] == "chs" and x["name"].replace("_chs.py", "") == base_key]
            pool_opts = same_variant or [x["file"] for x in hits if x["cls"] == "chs" and x["fam"] == h["fam"]]
            best = None
            for pf in (pool_opts or [None]):
                try:
                    r = decode_file(h["file"], pf)
                    if best is None or r[1] < best[1]:
                        best = r
                except Exception as e:
                    print(f"    {h['file']} +chs {pf} 解码失败: {e}")
            if best:
                r, un, used = best
                if r is None:
                    print(f"    {h['file']} (+chs {used or '无'}) → ⚠无合法 x{{ 容器（老格式壳/索引表，当前解码器不支持）——标老格式勿硬解")
                    continue
                warn = "  ⚠ 高 unbound：缺池/错池≠行缺失——先怀疑 CHS 配对，别判表空" if un > max(5, r * 0.2) else ""
                print(f"    {h['file']} (+chs {used or '无'}) → rows={r}  unbound={un}{warn}")
            else:
                print(f"    {h['file']} → 全部解码尝试失败")


if __name__ == "__main__":
    main()
