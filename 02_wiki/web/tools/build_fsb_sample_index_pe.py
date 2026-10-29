# -*- coding: utf-8 -*-
"""扫 gpk 里的 FSB5 bank，建/并「样本名 → (包, bank 偏移, 长度, 样本序号)」索引。

用法：
  python build_fsb_sample_index_pe.py 0185.gpk 0186.gpk ...   # 覆盖写
  python build_fsb_sample_index_pe.py --merge 0218.gpk        # 并入已有索引
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

import fsb5

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = PROJ / "01_索引与产物/30_分析/fsb_sample_index_pe.json"


def banks_in(d: bytes):
    start = 0
    while True:
        i = d.find(b"FSB5", start)
        if i < 0:
            return
        try:
            num, sh, nt, ds = struct.unpack_from("<IIII", d, i + 8)
            ln = 0x3C + sh + nt + ds
            if ln <= 0 or i + ln > len(d):
                start = i + 4
                continue
            yield i, ln, num
            start = i + ln
        except Exception:  # noqa: BLE001
            start = i + 4


def main() -> int:
    args = sys.argv[1:]
    merge = "--merge" in args
    packs = [a for a in args if a.endswith(".gpk")]
    index: dict[str, list] = {}
    meta: dict[str, dict] = {}
    if merge and OUT.is_file():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        index = old.get("index", {})
        meta = old.get("meta", {})
        print("并入模式：已有样本名 %d" % len(index))

    for name in packs:
        path = PACKS / name
        if not path.is_file():
            print("缺包", name)
            continue
        d = path.read_bytes()
        nb = ns = 0
        for off, ln, num in banks_in(d):
            try:
                f = fsb5.FSB5(d[off:off + ln])
            except Exception:  # noqa: BLE001
                continue
            nb += 1
            for k, s in enumerate(f.samples):
                nm = getattr(s, "name", None)
                if not nm:
                    continue
                ns += 1
                index.setdefault(nm, []).append([name, off, ln, k])
        meta[name] = {"banks": nb, "samples": ns}
        print("%-12s bank %5d 样本 %6d" % (name, nb, ns))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"meta": meta, "index": index}, ensure_ascii=False), encoding="utf-8")
    print("样本名合计 %d ｜ 写出 %s" % (len(index), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
