# -*- coding: utf-8 -*-
"""抓 PC 热更（不建全量还原树）：只收 PC 客户端的增量文件 + 变更清单。

收的目录/文件（E:/mrzh）：
  Documents/script.py314.lc.npk   热更脚本包（表都在里面）
  Documents/plcoht_ag             热更清单（加密）
  Documents/plls / patchlock / fo_version / file_hash_pack.bin
  Documents/client_doc@*          客户端文档增量目录（空则跳过）

用法：
  python capture_pc_hotfix.py            # 只对比，不复制
  python capture_pc_hotfix.py --copy     # 把新增/变动的文件复制到 源包/pc_hotfix/<时间戳>/
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import time

PC = pathlib.Path("E:/mrzh")
DOC = PC / "Documents"
OUT = pathlib.Path("E:/la拆包项目/01_索引与产物/源包/pc_hotfix")
STATE = pathlib.Path("E:/la拆包项目/01_索引与产物/30_分析/pc_hotfix_state.json")

FILES = [
    DOC / "script.py314.lc.npk",
    DOC / "plcoht_ag",
    DOC / "plls",
    DOC / "patchlock",
    DOC / "fo_version",
    DOC / "file_hash_pack.bin",
]


def sig(p: pathlib.Path) -> dict:
    st = p.stat()
    d = {"size": st.st_size, "mtime": int(st.st_mtime)}
    if st.st_size <= 20_000_000:
        try:
            h = hashlib.sha256()
            with p.open("rb") as fh:
                for blk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(blk)
            d["sha256"] = h.hexdigest()
        except PermissionError:
            d["locked"] = True
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--copy", action="store_true")
    a = ap.parse_args()

    cur = {}
    for p in FILES:
        if p.is_file():
            cur[str(p.relative_to(PC)).replace("\\", "/")] = sig(p)

    old = json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}
    changed = [k for k in cur if old.get(k) != cur[k]]
    gone = [k for k in old if k not in cur]

    print("监控文件 %d ｜ 变化 %d ｜ 消失 %d" % (len(cur), len(changed), len(gone)))
    for k in changed:
        print("  变动", k, cur[k].get("size"), time.strftime("%m-%d %H:%M", time.localtime(cur[k]["mtime"])))

    if a.copy and changed:
        stamp = time.strftime("%Y%m%d_%H%M")
        dst = OUT / stamp
        dst.mkdir(parents=True, exist_ok=True)
        for k in changed:
            src = PC / k
            tgt = dst / pathlib.Path(k).name
            try:
                shutil.copy2(src, tgt)
                print("  复制", src, "→", tgt, "%.1f MB" % (tgt.stat().st_size / 1e6))
            except PermissionError:
                print("  复制失败（被占用）", src)
                if tgt.exists():
                    tgt.unlink()
        (dst / "manifest.json").write_text(
            json.dumps({"at": stamp, "files": {k: cur[k] for k in changed}}, ensure_ascii=False, indent=1),
            encoding="utf-8")
        print("落盘目录", dst)

    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
    print("状态已更新", STATE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
