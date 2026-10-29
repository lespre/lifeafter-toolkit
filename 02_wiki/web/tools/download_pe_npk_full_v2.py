# -*- coding: utf-8 -*-
"""全量下载 PE 客户端 npk（CDN 直链，8 并发，断点续传 + 尺寸校验）。

清单：01_索引与产物/10_索引/pl_npk_version_android4_playertest.json
直链：https://g66.gph.netease.com/<version>/<相对路径>
落盘：01_索引与产物/源包/pe_npk_full/<相对路径>
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

MAN = PROJ / "01_索引与产物/10_索引/pl_npk_version_android4_playertest.json"
OUT = PROJ / "01_索引与产物/源包/pe_npk_full"
HOST = "https://g66.gph.netease.com"
LOG = PROJ / "01_索引与产物/源包/pe_npk_full_下载日志.txt"
WORKERS = 8


def one(ver: str, rel: str, size: int):
    dst = OUT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_file() and dst.stat().st_size == size:
        return rel, size, size, 0
    url = "%s/%s/%s" % (HOST, ver, rel)
    r = subprocess.run([
        "curl", "-s", "--fail", "-C", "-", "-o", str(dst), "-m", "2400",
        "-A", "Orbit/1.0", "-H", "X-NTES-PROJECT: 66", url,
    ], capture_output=True)
    got = dst.stat().st_size if dst.is_file() else 0
    return rel, size, got, r.returncode


def main() -> int:
    d = json.loads(MAN.read_text(encoding="utf-8"))
    ver = d["version"]
    files = d.get("files10") or {}
    if len(sys.argv) > 1 and sys.argv[1] == "--ui":
        files = {k: v for k, v in files.items() if k.startswith("res/ui")}
    todo = []
    for rel, meta in files.items():
        size = int(meta.get("size") or 0)
        dst = OUT / rel
        if dst.is_file() and dst.stat().st_size == size:
            continue
        todo.append((rel, size))
    total = sum(s for _, s in todo)
    print("已完成 %d 个 ｜ 待下 %d 个 / %.1f GB ｜ 并发 %d"
          % (len(files) - len(todo), len(todo), total / 2 ** 30, WORKERS), flush=True)

    ok = bad = 0
    got_bytes = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(one, ver, rel, size) for rel, size in todo]
        for i, fu in enumerate(as_completed(futs), 1):
            rel, size, got, rc = fu.result()
            if rc == 0 and got == size:
                ok += 1
                got_bytes += got
            else:
                bad += 1
                with LOG.open("a", encoding="utf-8") as f:
                    f.write("%s\tgot=%d\texpect=%d\trc=%d\n" % (rel, got, size, rc))
            if i % 25 == 0 or i == len(todo):
                el = max(time.time() - t0, 1)
                print("[%d/%d] ok=%d bad=%d ｜ 本轮 %.1f GB ｜ %.0fs ｜ %.1f MB/s"
                      % (i, len(todo), ok, bad, got_bytes / 2 ** 30, el, got_bytes / 2 ** 20 / el),
                      flush=True)
    print("完成 ok=%d bad=%d ｜ 累计 %.1f GB" % (ok, bad, got_bytes / 2 ** 30))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
