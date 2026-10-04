# -*- coding: utf-8 -*-
r"""快照 2026-09-29 热更的**资源层**（我们之前只存了脚本层）。

背景（实测）：
  · 客户端 2026-09-29 20:31–21:33 落了 52 个文件 / 1.75 GB
    - gres/0000.gpk                1.43 GB（整包重写）
    - res/*.wpk 12 个             ≈300 MB（character3/4、scene_bw4 各 64 MB 等）
    - res/*.idx  9 个            （重写的索引）
    - res/{character,model,building}/<32hex> ≈30 个（内容寻址的新增资源，20:33–20:48）
  · 我们只快照了 script.py314.lc.npk（脚本层）⇒ **资源层热更整层没进树**
★ E:\mrzh 全程只读：这里只 copy，不写回、不删除客户端任何东西。
★ 源快照一律记 sha256 + md5（SKILL 铁律）。
"""
from __future__ import annotations
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

SRC = Path(r"E:\mrzh\Documents")
DST = Path(r"E:\la拆包项目\02_资料\源包\post_update_20260929_2031_res\raw")
MANIFEST = DST.parent / "SHA256.json"
SINCE = "2026-09-29 18:00"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    cutoff = time.mktime(time.strptime(SINCE, "%Y-%m-%d %H:%M"))
    todo = []
    for sub in ("gres", "res"):
        d = SRC / sub
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if not p.is_file():
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            if st.st_mtime >= cutoff:
                todo.append(p)
    todo.sort()
    total = sum(p.stat().st_size for p in todo)
    print("★ 待快照 %d 个文件 · %.2f GB" % (len(todo), total / 1073741824))
    DST.mkdir(parents=True, exist_ok=True)
    recs, done, copied = [], 0, 0
    t0 = time.time()
    for p in todo:
        rel = p.relative_to(SRC)
        tgt = DST / rel
        tgt.parent.mkdir(parents=True, exist_ok=True)
        if not tgt.exists() or tgt.stat().st_size != p.stat().st_size:
            shutil.copy2(p, tgt)
            copied += 1
        recs.append({"rel": str(rel), "bytes": p.stat().st_size,
                     "sha256": sha256(tgt), "md5": md5(tgt),
                     "src_mtime": time.strftime("%Y-%m-%d %H:%M:%S",
                                                time.localtime(p.stat().st_mtime))})
        done += 1
        if done % 10 == 0 or done == len(todo):
            print("   %d/%d（%.0fs · 新拷 %d）" % (done, len(todo), time.time() - t0, copied))
    MANIFEST.write_text(json.dumps(
        {"schema": "source-snapshot/v1", "source": str(SRC),
         "why": "2026-09-29 热更的【资源层】—— 之前只存了脚本层，树里缺这一层",
         "since": SINCE, "count": len(recs),
         "bytes": sum(r["bytes"] for r in recs), "files": recs},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print("★ 清单 → %s" % MANIFEST)
    ok = all((DST / r["rel"]).is_file() for r in recs)
    print("★ 回验：全部落地 = %s" % ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
