# -*- coding: utf-8 -*-
r"""gres 资源层热更增补：把新 gpk 里【新增行】解出并写进 41_还原树。

## 实测背景（2026-09-29 热更）

```
客户端 Documents/gres/0000.gpk   mtime 20:31 · 1,433,566,606 B
索引记录的旧状态                  1,389,678,714 B · 54,292 行 · sha256 bfe68639…
★ 新容器 = 56 块 · 55,030 条  ⇒ 旧 54,292 条 (packed/decoded/flag) 逐条【完全一致】
                            ⇒ 本次 = 纯尾部【新增 738 条】（+41.85 MB）
```
⇒ 增补是「只写新增行」的，不需要全量重写 —— 与 skill 记的「大 gpk 更新通常是纯尾部追加」吻合。

## 路径从哪来

`row_path_map` 是按【旧】索引建的（只有 0..54291）⇒ 新增行的路径必须另找：
 ① 名字字典 `names_dict_v13.json`（fid_hex → 路径）—— 命中就用真名
 ② 没命中 → `_未命名/0000/<行号>.<ext>`（扩名按内容魔数）

## 纪律

* 默认 **dry-run**；真写要 `--real`（还原树是唯一权威产物）。
* E:\mrzh 全程只读（只解、不写客户端）。
* 落台账 `gres增补台账_<ts>.json`（逐条 row/fid/path/sha256/结果）+ 回验。
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
TREE = PROJ / "03_执行" / "41_还原树"
GPKI = PROJ / "01_工具/工具库/02_图文音频渲染/皮肤链与渲染/gpk_npk_index.py"
UNPACK = PROJ / "01_工具/工具库/01_解码定位复原/解包与扫描"
INDEX = PROJ / "03_执行/10_索引/indexes/lifeafter_files.sqlite3"
ROW_MAP = PROJ / "03_执行/10_索引/indexes/row_path_map.db"
NAMES = PROJ / "03_执行/10_索引/names/names_dict_v13.json"
CONTAINER = r"Documents\gres\0000.gpk"
CLIENT = Path(r"E:\mrzh\Documents\gres\0000.gpk")

MAGIC = ((b"DDS ", ".dds"), (b"\x89PNG", ".png"), (b"\xff\xd8\xff", ".jpg"),
         (b"GIF8", ".gif"), (b"RIFF", ".riff"), (b"FSB5", ".fsb5"),
         (b"OggS", ".ogg"), (b"<?xml", ".xml"), (b"{\x00", ".csb"),
         (b"\x00\x00\x00\x0cftyp", ".mp4"), (b"ftyp", ".mp4"),
         (b"<FxGroup", ".sfx"), (b"PK\x03\x04", ".zip"), (b"\x1f\x8b", ".gz"))


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def ext_of(b: bytes) -> str:
    for magic, ext in MAGIC:
        if b.startswith(magic):
            return ext
    if b[:2] == b"\x73\x00":
        return ".bin"
    return ".bin"


def load_names() -> dict:
    if not NAMES.is_file():
        return {}
    d = json.loads(NAMES.read_text(encoding="utf-8"))
    ent = d.get("entries") if isinstance(d, dict) else None
    if isinstance(ent, dict) and ent:            # 带包装的那种
        return {k: v for k, v in ent.items()}
    return d if isinstance(d, dict) else {}


def main() -> int:
    ap = argparse.ArgumentParser(description="gres 资源层热更增补（默认 dry-run）")
    ap.add_argument("--client", type=Path, default=CLIENT)
    ap.add_argument("--container", default=CONTAINER)
    ap.add_argument("--tree", type=Path, default=TREE)
    ap.add_argument("--names", type=Path, default=NAMES)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--real", action="store_true", help="真写（不加只 dry-run）")
    args = ap.parse_args()

    dry = not args.real
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = args.out or (PROJ / "03_执行" / "30_分析" / "资源层热更_20260930")
    out.mkdir(parents=True, exist_ok=True)

    print("★ gres 资源层增补 —— %s" % ("★ DRY-RUN（不写）" if dry else "★ REAL（真写！）"))
    print("   客户端：%s" % args.client)
    print("   还原树：%s" % args.tree)

    gpki = _load("_gpki_merge", GPKI)
    core = _load("_unpack_core_merge", UNPACK / "la_unpack_core.py")
    t0 = time.time()
    rec, rows_fn, blocks = gpki._gpk_blockchain(str(args.client), with_crc=True)
    new = {}
    for i, fid, poff, packed, decoded, flag, c1, c2 in rows_fn():
        new[i] = (("%016X" % fid), poff, packed, decoded, flag)
    print("   新容器：%d 块 · %d 条（%.1fs）" % (len(blocks), len(new), time.time() - t0))

    con = sqlite3.connect("file:%s?mode=ro" % INDEX.as_posix(), uri=True)
    old = {r for (r,) in con.execute("SELECT row_index FROM entries WHERE container=?",
                                     (args.container,))}
    con.close()
    new_rows = sorted(r for r in new if r not in old)
    print("   旧索引 %d 行 · ★ 新增 %d 行（%s…%s）"
          % (len(old), len(new_rows), new_rows[0] if new_rows else "-",
             new_rows[-1] if new_rows else "-"))
    if not new_rows:
        print("★ 无新增行 —— 容器内容未变（只有 mtime 变了）")
        return 0

    names = load_names()
    print("   名字字典：%d 条" % len(names))

    # ★ 同一批新增行里可能有【同一路径出现两次】（客户端追加式修订：后一行覆盖前一行）。
    #   实测 738 行 → 736 个唯一路径（`ui\liandong_zhanshen_miwu_tansuo_area_boss.csb`
    #   与 `…_main.csb` 各被两行引用）。处理：**高行号胜**（后追加的才是当前版），
    #   低行号那条标 superseded，不重复写 —— 否则会静默丢掉「谁是当前版」这条事实。
    by_path = {}
    for row in new_rows:
        fid = new[row][0]
        rel = names.get(fid) or names.get(fid.upper())
        if rel:
            by_path.setdefault(rel.replace("/", "\\"), []).append(row)
    dup_paths = {p: rows for p, rows in by_path.items() if len(rows) > 1}
    superseded = {r for rows in dup_paths.values() for r in rows[:-1]}
    if dup_paths:
        print("   ★ 新增行里有 %d 个路径被多行引用（高行号胜，低行号标 superseded）："
              % len(dup_paths))
        for p, rows in list(dup_paths.items())[:6]:
            print("      %s ← 行 %s" % (p[:64], rows))

    named = 0
    recs, stats = [], Counter()
    with args.client.open("rb") as fh:
        for row in new_rows:
            fid, poff, packed, decoded, flag = new[row]
            path = names.get(fid) or names.get(fid.upper())
            if path:
                named += 1
            if row in superseded:
                stats["被后行覆盖(跳过写)"] += 1
                recs.append({"row": row, "fid": fid,
                             "path": (path or "").replace("/", "\\"),
                             "result": "superseded",
                             "note": "同路径存在更高行号，未写"})
                continue
            try:
                fh.seek(poff)
                seg = fh.read(packed)
                data = core.npk_decode_entry(seg, decoded, flag)
            except Exception as exc:                                # noqa: BLE001
                stats["解失败"] += 1
                recs.append({"row": row, "fid": fid, "error": "%s: %s"
                             % (type(exc).__name__, str(exc)[:120])})
                continue
            if data is None or len(data) != decoded:
                stats["长度不符"] += 1
                recs.append({"row": row, "fid": fid, "error": "解出 %s B ≠ 声明 %s B"
                             % (0 if data is None else len(data), decoded)})
                continue
            ext = ext_of(data)
            # ★ 2026-09-30 对标 E:\mrzh 层级：落点带容器分区
            cdir = args.container.replace("/", "\\")
            rel = ((cdir + "\\" + path.replace("/", "\\")) if path
                   else "%s\\_未命名\\%08d%s" % (cdir, row, ext))
            dst = args.tree / rel
            sha = hashlib.sha256(data).hexdigest()
            existed = dst.is_file()
            if existed:
                same = dst.stat().st_size == len(data) and \
                    hashlib.sha256(dst.read_bytes()).hexdigest() == sha
                kind = "相同" if same else "覆盖"
            else:
                kind = "新增"
            stats[kind] += 1
            if not dry and kind != "相同":
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists():
                    dst.unlink()
                dst.write_bytes(data)
            recs.append({"row": row, "fid": fid, "path": rel, "ext": ext,
                         "bytes": len(data), "sha256": sha, "result": kind,
                         "named": bool(path)})

    print()
    print("★ 结果：%s" % dict(stats))
    print("   具名 %d / 未具名 %d（%.1f%% 有名字）"
          % (named, len(new_rows) - named, 100.0 * named / max(len(new_rows), 1)))
    print("   按扩展名：%s" % dict(Counter(r.get("ext") for r in recs if r.get("ext")).most_common(12)))
    for r in recs[:10]:
        print("      r%-7s %-58s %s" % (r["row"], (r.get("path") or r.get("error", ""))[:58],
                                        r.get("result", "")))

    led = out / ("gres增补台账_%s.json" % ts)
    led.write_text(json.dumps({
        "schema": "gres-layer-merge/v1", "generated": ts, "dry_run": dry,
        "client": str(args.client), "container": args.container,
        "client_bytes": args.client.stat().st_size,
        "rows_new": len(new_rows), "named": named,
        "stats": dict(stats), "records": recs}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print("★ 台账 → %s" % led)

    if not dry:
        # 把新增行补进 row_path_map，保持「容器+行号 → 路径」可用
        con = sqlite3.connect(str(ROW_MAP))
        n = 0
        for r in recs:
            if not r.get("path"):
                continue
            try:
                con.execute("INSERT OR REPLACE INTO rows VALUES(?,?,?,?,?)",
                            (args.container, r["row"], r["fid"], r["path"], 1))
                n += 1
            except sqlite3.Error:
                pass
        con.commit()
        con.close()
        print("★ row_path_map 补入 %d 行" % n)
        miss = [r for r in recs if r.get("path") and not (args.tree / r["path"]).is_file()]
        print("★ 回验：落地缺失 %d 条" % len(miss))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
