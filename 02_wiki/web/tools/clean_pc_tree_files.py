# -*- coding: utf-8 -*-
"""只清理 PC 树里的解压文件，保留目录骨架 + .gitkeep；索引库不动。"""
import os
import pathlib
import shutil
import sys

ROOT = pathlib.Path("E:/la拆包项目/01_索引与产物/41_还原树/pc")
GUARD = ("41_还原树/pe/资源", "源包", "pe_20261020")


def main() -> int:
    if not ROOT.is_dir():
        print("目录不存在", ROOT)
        return 1
    assert not any(g in str(ROOT).replace("\\", "/") for g in GUARD), "守卫命中，停止"

    files = 0
    bytes_ = 0
    dirs = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirs.append(dirpath)
        for n in filenames:
            p = os.path.join(dirpath, n)
            try:
                bytes_ += os.path.getsize(p)
                os.remove(p)
                files += 1
            except OSError:
                pass
    for d in dirs:
        try:
            pathlib.Path(d, ".gitkeep").touch()
        except OSError:
            pass
    print("删除文件 %d 个，释放 %.1f GB；保留目录 %d 个" % (files, bytes_ / 1073741824, len(dirs)))
    left = sum(len(fs) for _, _, fs in os.walk(ROOT))
    print("剩余文件 %d（应为 .gitkeep 数量）" % left)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
