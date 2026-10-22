# -*- coding: utf-8 -*-
r"""PE 全量索引 CLI —— 只读 gpk 表建全局 fid 索引，按 UI 清单回填名字，按需出图。

用法：
  python 命令行/pe全量索引.py build  <包目录> [--db PATH] [--jobs N]
  python 命令行/pe全量索引.py name   <清单txt...> [--db PATH]
  python 命令行/pe全量索引.py stats  [--db PATH]
  python 命令行/pe全量索引.py export [--db PATH] [--like 'item_icon/%'] [--out DIR] [--limit N]

设计：build 只读表不解压；export 才解码，且多进程并行。
"""
from __future__ import annotations

import argparse
import pathlib
import sys

PROJ = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import pe_index as PI   # noqa: E402

DEFAULT_DB = PROJ / "01_索引与产物/30_分析/热更检测/pe_index.sqlite3"


def cmd_build(a):
    r = PI.build(a.dir, a.db, jobs=a.jobs)
    print("完成：%d 包 / %d 行 / %.1fs → %s" % (r["packs"], r["rows"], r["seconds"], r["db"]))


def load_paths(files):
    out, seen = [], set()
    for f in files:
        p = pathlib.Path(f)
        if not p.is_file():
            print("缺文件:", f)
            continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            q = line.split()[0] if line.strip() else ""
            if q and q not in seen:
                seen.add(q)
                out.append(q)
    return out


def cmd_name(a):
    paths = load_paths(a.files)
    print("候选路径:", len(paths))
    r = PI.name_from_paths(a.db, paths)
    print("尝试 %d ｜ 新命中 %d ｜ 已命名 %d/%d (%.2f%%)"
          % (r["tried"], r["hit"], r["named"], r["total"], r["coverage"]))


def cmd_stats(a):
    s = PI.stats(a.db)
    print("包 %d ｜ 行 %d ｜ 有名字 %d (%.2f%%)" % (s["packs"], s["rows"], s["named"], s["coverage"]))


def cmd_export(a):
    import sqlite3
    con = sqlite3.connect(str(a.db))
    q = "select pack,row,name from rows where name is not null"
    args = []
    if a.like:
        q += " and name like ?"
        args.append(a.like)
    q += " order by pack,row"
    if a.limit:
        q += " limit %d" % int(a.limit)
    rows = con.execute(q, args).fetchall()
    con.close()
    print("待导出:", len(rows))
    print("导出需按包聚合后并行解码；先用 `--limit` 小批量验证。")

    from collections import defaultdict
    by_pack = defaultdict(list)
    for pack, row, name in rows:
        by_pack[pack].append((row, name))
    pack_dir = a.pack_dir or str(DEFAULT_DB.parent)
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    from toolkit_core import android_gpk as AG
    done = 0
    for pack, items in by_pack.items():
        p = pathlib.Path(pack_dir) / pack
        if not p.is_file():
            print("  缺包:", p)
            continue
        want = dict(items)
        for e in AG.iter_entries(str(p), verify=True):
            if e["row"] not in want:
                continue
            try:
                img = AG.decode_image(e)
            except Exception:
                continue
            name = want[e["row"]].replace("/", "_")
            img.convert("RGB").save(out / (name + ".png"))
            done += 1
    print("导出完成:", done)


def cmd_pull(a):
    """从设备并行拉包（su cp 到 Download → adb pull → 删远端副本）。"""
    import subprocess
    from concurrent.futures import ThreadPoolExecutor, as_completed
    ADB = r"E:/leidian/LDPlayer14/adb.exe"
    SERIAL = "emulator-5554"
    DEV = "/sdcard/Android/data/com.netease.mrzh/files/netease/g66/Documents/gres"
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    def list_packs():
        p = subprocess.run([ADB, "-s", SERIAL, "shell", "su -c 'ls %s'" % DEV],
                           capture_output=True)
        return [x.strip() for x in p.stdout.decode().split() if x.strip().endswith(".gpk")]

    packs = list_packs()
    if a.limit:
        packs = packs[: a.limit]
    todo = [n for n in packs if not (out / n).exists()]
    print("设备上 %d 个包 ｜ 待拉 %d" % (len(packs), len(todo)))

    def one(name):
        dst = out / name
        # ★ adb.exe 不认中文路径：先拉到纯 ASCII 临时目录，再本地移动
        tmp_dir = pathlib.Path(r"C:/Users/Administrator/AppData/Local/hermes/cache/scratch/pe_pull")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_file = tmp_dir / name
        src = "%s/%s" % (DEV, name)
        # ★ 直接 chmod 原文件后 pull，省掉 260MB 的 cp 往返
        subprocess.run([ADB, "-s", SERIAL, "shell", "su -c 'chmod 644 %s'" % src],
                       capture_output=True)
        r = subprocess.run([ADB, "-s", SERIAL, "pull", src, str(tmp_file)], capture_output=True)
        subprocess.run([ADB, "-s", SERIAL, "shell", "su -c 'chmod 600 %s'" % src],
                       capture_output=True)
        if r.returncode != 0 or not tmp_file.is_file():
            return name, -1
        import shutil
        shutil.move(str(tmp_file), str(dst))
        return name, dst.stat().st_size if dst.is_file() else -1

    done = fail = 0
    with ThreadPoolExecutor(max_workers=a.jobs or 4) as pool:
        futs = {pool.submit(one, n): n for n in todo}
        for i, f in enumerate(as_completed(futs), 1):
            n, sz = f.result()
            if sz > 0:
                done += 1
            else:
                fail += 1
                print("  失败:", n)
            if i % 10 == 0 or i == len(todo):
                print("  进度 %d/%d ｜ 成功 %d 失败 %d" % (i, len(todo), done, fail), flush=True)
    print("拉包完成：成功 %d 失败 %d → %s" % (done, fail, out))


def main():
    ap = argparse.ArgumentParser(description="PE 全量索引 / 命名 / 导出")
    ap.add_argument("--db", default=str(DEFAULT_DB))
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build")
    b.add_argument("dir")
    b.add_argument("--jobs", type=int, default=None)
    b.set_defaults(func=cmd_build)

    n = sub.add_parser("name")
    n.add_argument("files", nargs="+")
    n.set_defaults(func=cmd_name)

    s = sub.add_parser("stats")
    s.set_defaults(func=cmd_stats)

    e = sub.add_parser("export")
    e.add_argument("--like", default=None)
    e.add_argument("--out", default=str(PROJ / "01_索引与产物/30_分析/热更检测/pe_export"))
    e.add_argument("--limit", type=int, default=0)
    e.add_argument("--pack-dir", default=None)
    e.set_defaults(func=cmd_export)

    pl = sub.add_parser("pull")
    pl.add_argument("--out", default=str(PROJ / "01_索引与产物/30_分析/热更检测/pe_packs"))
    pl.add_argument("--jobs", type=int, default=4)
    pl.add_argument("--limit", type=int, default=0)
    pl.set_defaults(func=cmd_pull)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
