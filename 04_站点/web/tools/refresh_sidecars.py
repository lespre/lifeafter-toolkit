# -*- coding: utf-8 -*-
r"""refresh_sidecars.py — 给主页生成「重活」sidecar。

主页是 15 秒轮询，扛不住现算这些；所以它们落到 sidecar，主页只读。

产出两个：
  ① 03_执行/10_索引/names/coverage_latest.json
       dict_size · covered_rows · total_rows · coverage_pct
  ② 03_执行/10_索引/patch_manifests/delta_latest.json
       = `run_all.py delta diff` 的完整报告（release 正式服 vs playertest 测试服）

用法：
  python 04_站点/web/tools/refresh_sidecars.py            # 两个都刷
  python 04_站点/web/tools/refresh_sidecars.py --names    # 只刷名字
  python 04_站点/web/tools/refresh_sidecars.py --delta    # 只刷增量
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

PROJECT = Path(r"E:/la拆包项目")
CORE = PROJECT / "01_工具" / "工具库" / "00_共享核心"
sys.path.insert(0, str(CORE))

INDEX_DB = PROJECT / "03_执行" / "10_索引" / "indexes" / "lifeafter_files.sqlite3"
def _latest_names_dict():
    """★ 取最新版字典（v13 > v12 > v11 …）。写死版本号会在字典迭代后读到旧版，
    让主页显示的覆盖率永远停在过去（实测：v13 已 +3,204 条但主页仍报 v11）。"""
    root = PROJECT / "03_执行" / "10_索引" / "names"
    vs = []
    for p in root.glob("names_dict_v*.json"):
        d = "".join(c for c in p.stem.split("_v")[-1] if c.isdigit())
        if d:
            vs.append((int(d), p))
    vs.sort()
    if vs:
        return vs[-1][1]
    return root / "names_dict.json"


NAMES_DICT = _latest_names_dict()
NAMES_OUT = PROJECT / "03_执行" / "10_索引" / "names" / "coverage_latest.json"
DELTA_DIR = PROJECT / "03_执行" / "10_索引" / "patch_manifests"
DELTA_OUT = DELTA_DIR / "delta_latest.json"


def refresh_names() -> dict:
    if not NAMES_DICT.is_file():
        print("  ✗ 字典不存在：%s" % NAMES_DICT, file=sys.stderr)
        return {}
    d = json.loads(NAMES_DICT.read_text(encoding="utf-8"))
    print("  字典 %d 条，开始对账…" % len(d), flush=True)
    db = sqlite3.connect(str(INDEX_DB))
    total = db.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    covered = 0
    for (f,) in db.execute("SELECT fid_hex FROM entries"):
        if d.get(f):
            covered += 1
    rep = {
        "dict_path": str(NAMES_DICT),
        "dict_size": len(d),
        "total_rows": total,
        "covered_rows": covered,
        "coverage_pct": round(100.0 * covered / total, 4) if total else 0.0,
    }
    NAMES_OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("  ✓ 字典 {:,} 条 · 覆盖 {:,}/{:,} = {:.2f}%".format(
        len(d), covered, total, rep["coverage_pct"]))
    print("    → %s" % NAMES_OUT)
    return rep


def refresh_delta() -> dict:
    from toolkit_core import patch_delta as PD
    docs = {}
    for name in PD.DEFAULT_PAIR:
        cached = PD.load_cached(DELTA_DIR, name)
        if cached is None:
            print("  拉取 %s …" % name, flush=True)
            cached = PD.fetch(name)
            DELTA_DIR.mkdir(parents=True, exist_ok=True)
            (DELTA_DIR / ("%s.json" % name)).write_text(
                json.dumps(cached, ensure_ascii=False, indent=1), encoding="utf-8")
        docs[name] = cached
    a, b = PD.DEFAULT_PAIR
    rep = PD.diff(docs[a], docs[b], keys="ext")
    DELTA_OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    t = rep["totals"]
    print("  ✓ 增量 %s → %s：新增 %d · 删除 %d · 变更 %d" % (
        a, b, t["added"], t["removed"], t["changed"]))
    print("    → %s" % DELTA_OUT)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", action="store_true", help="只刷名字覆盖率")
    ap.add_argument("--delta", action="store_true", help="只刷热更增量")
    args = ap.parse_args()
    do_all = not (args.names or args.delta)

    if do_all or args.names:
        print("① 名字覆盖率 sidecar")
        refresh_names()
        print()
    if do_all or args.delta:
        print("② 热更增量 sidecar")
        refresh_delta()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
