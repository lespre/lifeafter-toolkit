# -*- coding: utf-8 -*-
"""导出 1110189 的 9 个 .sfx 并抓音效线索（字符串/FSB 引用）。"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG  # noqa: E402

PKG = ROOT / "01_索引与产物/源包/pe_gres_android/0360.gpk"
OUT = ROOT / "01_索引与产物/30_分析/1110189_sfx"
WANT = {4688, 4689, 4684, 8777, 8779, 564, 565, 4678, 8782}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    got = 0
    for i, e in enumerate(AG.iter_entries(str(PKG), include_empty=False)):
        row = int(e.get("row", i))
        if row not in WANT:
            continue
        data = e.get("data")
        if data is None:
            data = e.get("payload")
        if data is None:
            print("row", row, "读取失败（无 read_entry）")
            continue
        got += 1
        dst = OUT / ("%04d.sfx" % row)
        dst.write_bytes(data)
        txt = data.decode("utf-8", "ignore")
        names = re.findall(r"[A-Za-z0-9_./\-]{6,60}\.(?:wav|fsb|ogg|mp3)", txt)
        ev = re.findall(r"[A-Za-z_]{0,20}(?:Sound|sound|Event|event)[A-Za-z_]{0,20}", txt)
        print("row %-5d %.1f KB ｜ 音频引用 %d %s ｜ 事件关键词 %s"
              % (row, len(data) / 1024, len(set(names)), sorted(set(names))[:3], sorted(set(ev))[:3]))
    print("导出", got, "个 →", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
