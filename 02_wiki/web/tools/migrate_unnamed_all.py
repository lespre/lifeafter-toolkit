"""把还原树 unnamed/<包>/<行号>.ext 全量搬到真实路径（用 pe_index 的最新名字）。

  python migrate_unnamed_all.py            # 只统计
  python migrate_unnamed_all.py --apply    # 实际移动
"""
import argparse
import os
import sqlite3
import sys
import time

ROOT = r"E:/la拆包项目"
TREE = ROOT + r"/01_索引与产物/41_还原树/pe/资源"
DB = ROOT + r"/01_索引与产物/10_索引/热更检测/pe_index.sqlite3"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    con = sqlite3.connect(DB)
    mapping = {}
    for pack, row, name in con.execute("select pack,row,name from rows where name is not null"):
        mapping[(pack, int(row))] = str(name).replace("\\", "/")
    con.close()
    print(f"索引里有名字的条目 {len(mapping):,}", flush=True)
    if a.limit:
        print(f"⚠ 只处理前 {a.limit} 个包（试跑）", flush=True)

    base = os.path.join(TREE, "unnamed")
    packs = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))
    if a.limit:
        packs = packs[: a.limit]

    moved = have = noname = err = 0
    t0 = time.time()
    for i, pk in enumerate(packs, 1):
        pack = pk + ".gpk"
        d = os.path.join(base, pk)
        try:
            files = os.listdir(d)
        except Exception:
            continue
        for fn in files:
            src = os.path.join(d, fn)
            if not os.path.isfile(src):
                continue
            stem, dot, ext = fn.partition(".")
            try:
                row = int(stem)
            except ValueError:
                continue
            name = mapping.get((pack, row))
            if not name:
                noname += 1
                continue
            if not name.lower().endswith("." + ext.lower()):
                # 扩展名不一致也要按索引名字落（索引的名字才是权威）
                pass
            dst = os.path.join(TREE, name)
            if os.path.exists(dst):
                have += 1
                continue
            if a.apply:
                try:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    os.replace(src, dst)
                    moved += 1
                except Exception:
                    err += 1
            else:
                moved += 1
        if i % 20 == 0:
            print(f"  [{i}/{len(packs)}] 可移动 {moved:,} 目标已存在 {have:,} 无名 {noname:,} "
                  f"错 {err}  {time.time()-t0:.0f}s", flush=True)

    verb = "已移动" if a.apply else "可移动"
    print(f"\n{verb} {moved:,} ｜ 目标已存在(跳过) {have:,} ｜ 仍无名 {noname:,} ｜ 失败 {err}  "
          f"｜ {time.time()-t0:.0f}s", flush=True)
    if not a.apply:
        print("（这是试跑；加 --apply 才真移动）", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
