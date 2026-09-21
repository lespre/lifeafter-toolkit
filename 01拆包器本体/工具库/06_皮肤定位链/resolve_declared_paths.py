# -*- coding: utf-8 -*-
"""resolve_declared_paths.py — 从声明类文件里抽出资产路径，并按容器索引逐条判 HIT/MISS

解决的问题
----------
`*.c159`（材质/参数块）、`*.sfx`（特效轨道）、以及任意文本/二进制配置里写的是**逻辑路径**
（如 `common\\env_map\\qiangpi.cube`、`res\\ui\\xxx.dds`），但容器（.gpk/.fpk/.npk）里
**只存路径的 murmur3 哈希、不存名字**。所以"声明了却没生效"这类缺陷，必须靠
"候选名 → 哈希 → 去容器表里查行"来判定，而不能靠字符串搜索。

本工具做三件事：
  1. **抽路径**：从输入文件里扫出所有像路径的字符串（按扩展名白名单过滤），带字节偏移；
  2. **逐条解析**：算 fid（高低 32 位 = murmur3 seed 0x77777777 / 0x66666666），
     在全部容器条目表里查；支持 `--variants` 展开候选名（分隔符/大小写/去一层目录/换扩展名）；
  3. **汇总矩阵**：按「顶层目录 × 扩展名」给出 声明数 / HIT / MISS / 命中率，并输出逐条明细。

用法
----
    # 1) 直接解析一批声明文件（自带索引扫描，无需预建）
    python resolve_declared_paths.py "E:\\la拆包项目\\03拆包产物\\weapon\\*.c159" \\
        --json "E:\\la拆包项目\\03拆包产物\\_target_1110171\\BUGFIX_declared_paths.json"

    # 2) 复用已建 TSV 索引（反复查更快）
    python resolve_declared_paths.py a.sfx b.c159 --index ALL_index.tsv

    # 3) 展开候选名（查 MISS 时先试变体，避免把"名字写法不同"误判成"资产缺失"）
    python resolve_declared_paths.py x.c159 --variants

    # 4) 只看汇总矩阵，不看逐条
    python resolve_declared_paths.py x.c159 --no-detail

    # 5) 也把抽到的路径原样 dump 出来（不解析），用于检查抽取质量
    python resolve_declared_paths.py x.c159 --dump-strings

退出码
------
    0 全部解析完成（是否有 MISS 不影响退出码；MISS 是数据结论不是工具故障）
    1 用法/参数错误
    2 一个输入文件都读不到
    3 写盘 IO 失败
    4 索引完全不可用（容器一个都解析不出来，且未给 --index）

边界（明确不做的事）
--------------------
  * **不改任何被检文件**（本工具纯只读；发现的问题由调用方决定是否修）；
  * 不理解 `.c159` / `.sfx` 的语法：只做"像路径的字符串"抽取 ⇒ 抽到的东西可能包含注释、
    拼接片段或非资产路径，逐条都会带上原始字节偏移供人工复核；
  * MISS 只证明"这些候选名的哈希不在容器表里"，**不证明资产不存在**（可能进的是匿名容器、
    或名字在打包时被改写）；判据请配合 `--variants` 与同族资产对照使用。
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import os
import re
import sys
import time
from collections import defaultdict

# ── UTF-8 强制：用 reconfigure（不替换 sys.stdout，避免 import 时关掉调用方 buffer）
for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
for _p in (os.path.join(_HERE, "..", "01_核心解包器"),):
    _p = os.path.abspath(_p)
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

try:
    from gpk_npk_index import (DEFAULT_FPK_INDEX, DEFAULT_RES, _gpk_blockchain, candidates,
                               parse_npk, path_id_raw, scan_containers)
except Exception as _exc:  # pragma: no cover
    sys.stderr.write("无法导入同目录的 gpk_npk_index.py：%r\n"
                     "本工具依赖它的容器解析与候选名逻辑。\n" % (_exc,))
    raise SystemExit(1)

# 资产扩展名白名单（决定"什么算路径"）
ASSET_EXTS = {
    ".dds", ".tga", ".png", ".jpg", ".jpeg", ".bmp", ".ktx", ".hdr",
    ".cube", ".mesh", ".gim", ".anim", ".skeleton", ".skel", ".mtl", ".mtlidx", ".material",
    ".sfx", ".json", ".xml", ".txt", ".bin", ".nxs", ".py", ".lua", ".fx", ".shader", ".hlsl",
    ".wav", ".ogg", ".mp3", ".bnk", ".ttf", ".fnt", ".atlas", ".prefab", ".scene",
}
# 像路径的可打印串
_PATH_RUN = re.compile(rb"[\x20-\x7e]{3,260}")
_HAS_SEP = re.compile(rb"[\\/]")


def file_sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()[:16]


def extract_paths(path, exts=ASSET_EXTS, min_len=4):
    """从任意文件里抽出"像资产路径"的字符串。

    做法：先取所有 ≥3 字符的可打印 ASCII 连续段，再在其中筛出含分隔符且扩展名在白名单里的。
    **带原始字节偏移**，便于人工回原文件复核。返回 [(str, byte_offset)]，按出现顺序去重。
    """
    data = open(path, "rb").read()
    out, seen = [], set()
    for m in _PATH_RUN.finditer(data):
        s = m.group(0)
        if not _HAS_SEP.search(s):
            continue
        for piece in re.split(rb"[^\x20-\x7e]+", s):
            if len(piece) < min_len:
                continue
            txt = piece.decode("ascii", "replace").strip()
            if not _HAS_SEP.search(txt.encode("ascii", "replace")):
                continue
            ext = os.path.splitext(txt)[1].lower()
            if exts and ext not in exts:
                continue
            # 去掉可能粘到的引号/括号
            txt = txt.strip("\"'()[]{},;:")
            if len(txt) < min_len:
                continue
            key = txt.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append((txt, m.start()))
    return out


def top_dir(p):
    q = p.replace("\\", "/").lstrip("/")
    return q.split("/", 1)[0] if "/" in q else "(根)"


def resolve(paths, res_root, fpk_index, variants, deep, index_tsv, verbose=True):
    """返回 {fid: [locations]}；先把查询集压缩成哈希集合，再对容器表做一遍流式匹配。"""
    want = {}
    for p in paths:
        for cand in candidates(p, variants, deep):
            for enc in ("utf-8", "latin1"):
                want.setdefault(path_id_raw(cand, enc), set()).add(cand)
    hits = defaultdict(list)
    stats = {"streamed_containers": 0, "tsv_rows": 0, "failed_containers": []}
    if index_tsv and os.path.isfile(index_tsv):
        with open(index_tsv, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#"):
                    continue
                q = line.rstrip("\n").split("\t")
                fid = int(q[3], 16)
                stats["tsv_rows"] += 1
                if fid in want:
                    hits[fid].append({"container": q[0], "kind": q[1], "row": int(q[2]),
                                      "offset": int(q[4]), "packed": int(q[5]), "decoded": int(q[6]),
                                      "flag": int(q[7]), "via": "tsv"})
    else:
        for c in scan_containers(res_root, "all"):
            if c["kind_hint"] == "fpk":
                continue
            p = c["path"]
            rec = rows_iter = None
            last = None
            try:
                if c["kind_hint"] == "gpk":
                    rec, rows_iter, _bl = _gpk_blockchain(p)
                else:
                    rec, rows_iter = parse_npk(p)
            except Exception as exc:
                last = exc
                rec = rows_iter = None
                stats["failed_containers"].append({"container": os.path.relpath(p, res_root),
                                                   "reason": str(last)})
                continue
            stats["streamed_containers"] += 1
            rel = os.path.relpath(p, res_root)
            try:
                for i, fid, off, ps, ds, fl in rows_iter():
                    if fid in want:
                        hits[fid].append({"container": rel, "kind": rec["kind"], "row": i, "offset": off,
                                          "packed": ps, "decoded": ds, "flag": fl, "via": "stream"})
            except Exception as exc:
                stats["failed_containers"].append({"container": rel, "reason": "row_iter:%r" % (exc,)})
        if fpk_index and os.path.isfile(fpk_index):
            d = json.load(open(fpk_index, encoding="utf-8"))
            for fid_hex, v in (d.get("fid2info") or {}).items():
                f = int(fid_hex, 16)
                if f in want:
                    hits[f].append({"container": v[0], "kind": "fpk", "row": v[1], "offset": v[2],
                                    "packed": v[3], "decoded": v[4], "flag": v[7], "via": "fpk_fid_index"})
    return hits, want, stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="resolve_declared_paths.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="抽出 .c159/.sfx/任意文件里的资产路径，按容器索引逐条判 HIT/MISS，并给顶层目录×扩展名命中矩阵。",
        epilog="退出码：0 完成 / 1 参数错 / 2 输入不可读 / 3 写盘失败 / 4 索引不可用")
    ap.add_argument("inputs", nargs="*", help="声明文件（支持通配符），如 *.c159、*.sfx")
    ap.add_argument("--res-root", default=DEFAULT_RES, help="游戏资源根（默认 %s）" % DEFAULT_RES)
    ap.add_argument("--fpk-index", default=DEFAULT_FPK_INDEX, help="既有 fpk 索引 JSON")
    ap.add_argument("--index", metavar="TSV", help="复用 gpk_npk_index.py --tsv 产出的紧凑索引")
    ap.add_argument("--variants", action="store_true", help="展开分隔符/大小写/去一层目录/换扩展名变体")
    ap.add_argument("--deep-variants", action="store_true", help="再追加 _lod01/_1/_high 等后缀变体")
    ap.add_argument("--ext", action="append", help="追加/覆盖扩展名白名单（可重复；给空串则不过滤）")
    ap.add_argument("--dump-strings", action="store_true", help="只抽路径并打印，不解析")
    ap.add_argument("--no-detail", action="store_true", help="只输出汇总矩阵")
    ap.add_argument("--json", dest="json_out", metavar="PATH", help="把结果写入 JSON")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    v = not args.quiet

    files = []
    for pat in args.inputs:
        hits = glob.glob(pat) if any(ch in pat for ch in "*?[") else ([pat] if os.path.isfile(pat) else [])
        if not hits:
            sys.stderr.write("输入不可读（无匹配 / 不存在）：%s\n" % pat)
        files.extend(hits)
    files = sorted(set(os.path.abspath(f) for f in files))
    if not files:
        sys.stderr.write("一个输入文件都读不到。\n")
        return 2

    exts = ASSET_EXTS
    if args.ext:
        exts = set()
        for e in args.ext:
            if e == "":
                exts = None
                break
            exts.add(e if e.startswith(".") else "." + e)

    per_file = {}
    all_paths = []
    for f in files:
        got = extract_paths(f, exts)
        per_file[os.path.basename(f)] = {"path": f, "bytes": os.path.getsize(f),
                                         "sha16": file_sha16(f), "paths": len(got)}
        if v:
            print("%-24s %8d B  sha16=%s  抽出路径 %d 条" % (os.path.basename(f), os.path.getsize(f),
                                                        per_file[os.path.basename(f)]["sha16"], len(got)))
        for txt, off in got:
            all_paths.append((f, txt, off))
    if args.dump_strings:
        for f, txt, off in all_paths:
            print("%s\t%d\t%s" % (os.path.basename(f), off, txt))
        return 0
    if not all_paths:
        print("\n未抽出任何路径（检查 --ext 白名单）。")
        return 0

    uniq = sorted({t for _f, t, _o in all_paths})
    if v:
        print("\n去重后待解析路径 %d 条（原始出现 %d 次）" % (len(uniq), len(all_paths)))

    hits, want, stats = resolve(uniq, args.res_root, args.fpk_index, args.variants,
                               args.deep_variants, args.index, v)
    if stats["streamed_containers"] == 0 and not args.index:
        sys.stderr.write("容器一个都没解析出来 ⇒ 索引不可用。\n")
        return 4

    # 逐条判定
    detail = []
    for txt in uniq:
        cands = candidates(txt, args.variants, args.deep_variants)
        fids = {path_id_raw(c, e) for c in cands for e in ("utf-8", "latin1")}
        locs = [h for fid in fids for h in hits.get(fid, [])]
        detail.append({"路径": txt, "顶层目录": top_dir(txt), "扩展名": os.path.splitext(txt)[1].lower(),
                       "结果": "HIT" if locs else "MISS", "候选名数": len(cands),
                       "fid_hex": ["%016X" % f for f in sorted(fids)][:4],
                       "位置": sorted(locs, key=lambda x: (x["container"], x["row"]))[:8],
                       "位置数": len(locs),
                       "出现": [{"文件": os.path.basename(f), "字节偏移": o} for f, t, o in all_paths if t == txt]})

    # 汇总矩阵：顶层目录 × 扩展名
    mat = defaultdict(lambda: {"声明": 0, "HIT": 0, "MISS": 0})
    for d in detail:
        k = (d["顶层目录"], d["扩展名"] or "(无扩展名)")
        mat[k]["声明"] += 1
        mat[k][d["结果"]] += 1
    matrix = [{"顶层目录": k[0], "扩展名": k[1], **val,
               "命中率": round(val["HIT"] / max(1, val["声明"]), 4)} for k, val in sorted(mat.items())]

    n_hit = sum(1 for d in detail if d["结果"] == "HIT")
    print("\n== 命中矩阵（顶层目录 × 扩展名）==")
    print("%-24s %-12s %6s %6s %6s %8s" % ("顶层目录", "扩展名", "声明", "HIT", "MISS", "命中率"))
    for r in matrix:
        print("%-24s %-12s %6d %6d %6d %7.1f%%" % (r["顶层目录"], r["扩展名"], r["声明"], r["HIT"],
                                                 r["MISS"], r["命中率"] * 100))
    print("\n合计：声明 %d 条，HIT %d，MISS %d，命中率 %.1f%%"
          % (len(detail), n_hit, len(detail) - n_hit, 100.0 * n_hit / max(1, len(detail))))
    print("索引：流式扫过 %d 个容器，失败 %d 个%s"
          % (stats["streamed_containers"], len(stats["failed_containers"]),
             "；TSV 行 %d" % stats["tsv_rows"] if stats["tsv_rows"] else ""))
    for f in stats["failed_containers"]:
        print("  ! %s : %s" % (f["container"], f["reason"]))

    if not args.no_detail:
        print("\n== 逐条 ==")
        for d in detail:
            tag = "HIT " if d["结果"] == "HIT" else "MISS"
            loc = ""
            if d["位置"]:
                h = d["位置"][0]
                loc = " %s#row%d off=%d packed=%d decoded=%d flag=%d" % (h["container"], h["row"], h["offset"],
                                                                       h["packed"], h["decoded"], h["flag"])
            print("%s %-58s %s%s" % (tag, d["路径"], "候选%d" % d["候选名数"], loc))

    if args.json_out:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
            payload = {"tool": "resolve_declared_paths.py", "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                       "res_root": args.res_root, "variants": args.variants,
                       "index_tsv": args.index, "inputs": per_file, "stats": stats,
                       "summary": {"声明": len(detail), "HIT": n_hit, "MISS": len(detail) - n_hit,
                                   "命中率": round(n_hit / max(1, len(detail)), 4)},
                       "matrix": matrix, "detail": detail}
            json.dump(payload, open(args.json_out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print("\n结果 JSON：%s (%d B)" % (args.json_out, os.path.getsize(args.json_out)))
        except OSError as exc:
            sys.stderr.write("写盘失败：%r\n" % (exc,))
            return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
