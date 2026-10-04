# -*- coding: utf-8 -*-
r"""热更检测器：记基线 / 对比变化。

用法：
  python hotwatch.py base    记基线到 baseline.json
  python hotwatch.py check   对比基线，报变化
"""
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys
import time

SNAP = pathlib.Path(r"E:/la拆包项目/03_执行/30_分析/热更检测")
SNAP.mkdir(parents=True, exist_ok=True)
BASE = SNAP / "baseline.json"
CLIENT = pathlib.Path(r"E:/mrzh")

# 关键文件（小、变动就说明有热更）
WATCH = [
    "Documents/fo_version",
    "Documents/local_state_314_lc",
    "Documents/file_hash_pack.bin",
    "Documents/pkg_left_files",
    "Documents/fpk_history_res",
    "Documents/local_finfo_314_lc",
    "Documents/obstruct_record.txt",
    "Documents/last_region_code",
    "Documents/cfs_prewarm_pos",
    "Documents/history_downloaded_packages",
    "Documents/downloaded_packages",
    "Documents/local_dflag2",
]
# res/ 下的 gpk 只记 mtime（太大不算 hash）
WATCH_DIRS = ["res", "script.py314.lc.npk", "res.gpk"]


def sha8(p: pathlib.Path) -> str:
    try:
        h = hashlib.sha256()
        with p.open("rb") as f:
            while True:
                b = f.read(1 << 20)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()[:16]
    except OSError:
        return ""


def snapshot() -> dict:
    d = {"at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "files": {}, "dirs": {}}
    for rel in WATCH:
        p = CLIENT / rel
        if p.is_file():
            st = p.stat()
            d["files"][rel] = {
                "size": st.st_size,
                "mtime": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "sha8": sha8(p) if st.st_size < 2 * 1024 * 1024 else "",
            }
    r = CLIENT / "res"
    if r.is_dir():
        ent = {}
        for p in r.iterdir():
            if p.is_file():
                ent[p.name] = {
                    "size": p.stat().st_size,
                    "mtime": datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%m-%d %H:%M"),
                }
        d["dirs"]["res"] = ent
    # 最顶层文件的 mtime
    top = {}
    for p in CLIENT.iterdir():
        if p.is_file():
            top[p.name] = datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%m-%d %H:%M")
    d["dirs"]["top"] = top
    return d


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "base":
        d = snapshot()
        BASE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        print("★ 基线已记（%s）→ %s" % (d["at"], BASE))
        print("  监控文件 %d 个 ｜ res/ %d 个 gpk" % (len(d["files"]), len(d["dirs"].get("res", {}))))
        return
    if not BASE.is_file():
        print("没有基线，先跑 base")
        return
    old = json.loads(BASE.read_text("utf-8"))
    new = snapshot()
    print("════ 基线 %s → 现在 %s ════" % (old["at"], new["at"]))
    ch = 0
    print()
    print("── 关键文件 ──")
    for k, v in new["files"].items():
        o = old["files"].get(k)
        if not o:
            print("  ★ 新增 %s  %s" % (k, v))
            ch += 1
        elif o != v:
            print("  ★ 变化 %s" % k)
            for kk in set(list(o) + list(v)):
                if o.get(kk) != v.get(kk):
                    print("       %-6s %s → %s" % (kk, o.get(kk), v.get(kk)))
            ch += 1
        else:
            print("   未变  %s" % k)
    print()
    print("── res/ 目录 ──")
    ores, nres = old["dirs"].get("res", {}), new["dirs"].get("res", {})
    dif = 0
    for k, v in nres.items():
        o = ores.get(k)
        if o != v:
            print("  ★ %s  %s → %s" % (k, o, v))
            dif += 1
    if not dif:
        print("    56 个 gpk 全未变")
    ch += dif
    print()
    print("── 顶层 ──")
    ot, nt = old["dirs"].get("top", {}), new["dirs"].get("top", {})
    for k, v in nt.items():
        if ot.get(k) != v:
            print("  ★ %s  %s → %s" % (k, ot.get(k), v))
            ch += 1
    print()
    print("════ 结论：%s ════" % ("★ 有 %d 处变化 ⇒ 可能触发了热更" % ch if ch else "★ 0 处变化 ⇒ 没有热更"))
    print("  （新基线已存，下次直接 check）")
    BASE.write_text(json.dumps(new, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
