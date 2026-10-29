# -*- coding: utf-8 -*-
"""全量 PE 还原树：把 176 个 gpk 逐条解出来，落成文件树（配置 + 资源一视同仁）。

- 输入：01_索引与产物/源包/pe_gres_android/*.gpk
- 命名：优先用 names_join 里的真实路径；没有就用 unnamed/<包>/<行号>.<ext>
- 内容：写**原始解压字节**（ktx 就是 ktx、gim 就是 gim），不做二次转换，保证可复现
- 断点：进度记在 41_还原树/pe/资源/extract_progress.sqlite3，可重入；已完成的包跳过
- 用法：python tools/extract_pe_full_tree.py [--packs 0181.gpk,0003.gpk] [--limit N]
"""
from __future__ import annotations

import argparse
import pathlib
import sqlite3
import sys
import time


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG  # noqa: E402

PKGDIR = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = PROJ / "01_索引与产物/41_还原树/pe/资源"
DB = OUT / "extract_progress.sqlite3"
NAMES = PROJ / "01_索引与产物/10_索引/热更检测/names_join.sqlite3"


def ext_of(data: bytes) -> str:
    if data.startswith(b"\xabKTX"):
        return "ktx"
    if data.startswith(b"DDS "):
        return "dds"
    if data.startswith(b"\x89PNG"):
        return "png"
    if data.startswith(b"GIM\x01") or data[:4] == b"GIM\x01":
        return "gim"
    if data.startswith(b"<?xml"):
        return "xml"
    if data.startswith(b"{") or data.startswith(b"["):
        return "json"
    if data.startswith(b"x{"):
        return "marshal"
    return "bin"


def open_db() -> sqlite3.Connection:
    OUT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("""create table if not exists packs(
        pack text primary key, files int, bytes int, seconds real, done_at text)""")
    con.commit()
    return con


def name_map(fids: list[str]) -> dict[str, str]:
    if not fids:
        return {}
    out: dict[str, str] = {}
    src = sqlite3.connect("file:%s?mode=ro" % str(NAMES).replace("\\", "/"), uri=True)
    for i in range(0, len(fids), 900):
        chunk = fids[i:i + 900]
        q = "select fid,name from nm where fid in (%s)" % ",".join("?" * len(chunk))
        for fid, name in src.execute(q, chunk):
            out[fid] = name
    src.close()
    return out


def do_pack(pkg: pathlib.Path, con: sqlite3.Connection, limit: int | None) -> tuple[int, int, float]:
    t0 = time.time()
    nbytes = nfiles = 0
    pending = []
    for i, e in enumerate(AG.iter_entries(str(pkg), include_empty=False)):
        pending.append(e)
        if len(pending) >= 4000 or (limit and i + 1 >= limit):
            nfiles += _write(pending, pkg, con)
            nbytes += sum(len(e.get("payload") or b"") for e in pending)
            pending.clear()
            print("   %s 进度 %d" % (pkg.name, i + 1), flush=True)
            if limit and i + 1 >= limit:
                break
    if pending:
        nfiles += _write(pending, pkg, con)
        nbytes += sum(len(e.get("payload") or b"") for e in pending)
    return nfiles, nbytes, time.time() - t0


def _write(entries, pkg: pathlib.Path, con) -> int:
    fids = ["%016X" % e["fid"] for e in entries]
    nm = name_map(fids)
    n = 0
    for e, fid in zip(entries, fids):
        data = e.get("payload")
        if not data:
            continue
        rel = nm.get(fid)
        if rel:
            rel = rel.replace("\\", "/")
            # 只接受真实资源路径；`.gpk/`、`_未命名` 这类是历史提取产物，丢弃
            if ".gpk/" in rel or "_未命名" in rel or rel.endswith(".bin"):
                rel = None
        if not rel:
            rel = "unnamed/%s/%06d.%s" % (pkg.stem, e["row"], ext_of(data))
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            dst.write_bytes(data)
            n += 1
        except OSError:
            continue
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", default="")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    con = open_db()
    done = {r[0] for r in con.execute("select pack from packs")}
    pkgs = ([PKGDIR / p for p in a.packs.split(",") if p] if a.packs
            else sorted(PKGDIR.glob("*.gpk")))
    todo = [p for p in pkgs if p.name not in done]
    print("待解包 %d 个（已完成 %d）" % (len(todo), len(done)))
    total_f = total_b = 0
    for pkg in todo:
        if not pkg.exists():
            print("缺包", pkg.name); continue
        print("== %s %.0f MB" % (pkg.name, pkg.stat().st_size / 1048576), flush=True)
        nf, nb, sec = do_pack(pkg, con, a.limit)
        con.execute("insert or replace into packs values(?,?,?,?,datetime('now'))",
                    (pkg.name, nf, nb, sec))
        con.commit()
        total_f += nf
        total_b += nb
        print("   完成 %s：%d 文件，%.0f MB，%.0fs" % (pkg.name, nf, nb / 1048576, sec), flush=True)
    print("本轮合计 %d 文件 %.1f GB" % (total_f, total_b / 1073741824))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
