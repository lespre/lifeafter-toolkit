# -*- coding: utf-8 -*-
"""players2021.layers.*.npk 条目表按 fid 定位（整文件 AES-ECB，header[8:12]=NXPK）。"""
import sys, struct, pathlib
PROJ = pathlib.Path(r"E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
import la_unpack_core as LC
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of

ENTRY = 48
LAYERS = PROJ / "01_索引与产物/源包/players2021_layers"


def head_table(f: pathlib.Path):
    with f.open("rb") as h:
        hd = LC.aes_ecb_decrypt(h.read(48))
        if hd[8:12] != b"NXPK":
            return None, {"err": "no NXPK", "head": hd[:16].hex()}
        ver = struct.unpack_from("<i", hd, 12)[0]
        off = struct.unpack_from("<I", hd, 16)[0]
        cnt = struct.unpack_from("<I", hd, 20)[0]
        h.seek(off)
        need = cnt * ENTRY
        tb = LC.aes_ecb_decrypt(h.read(need + 16))
    return (ver, off, cnt, tb[:need]), {"ver": ver, "table_off": off, "count": cnt,
                                        "size": f.stat().st_size}


def main():
    want = {}
    for m in ("3327", "3328"):
        for sex in ("f", "m"):
            for stem in (f"bag_{sex}_{m}_high", f"bag_{sex}_{m}", f"bag_{sex}_{m}_high001",
                         f"bag_{sex}_{m}001"):
                for ext in (".mesh", ".mtg"):
                    rel = f"character\\players2021\\bag_{sex}_{m}\\{stem}{ext}"
                    want["%016X" % fid_of(rel)] = stem + ext
    print("目标 fid:", len(want))
    for f in sorted(LAYERS.glob("*.npk")):
        res, info = head_table(f)
        if not res:
            print(f.name, "失败", info); continue
        ver, off, cnt, tb = res
        print("%s ver=%s entries=%s size=%.2fGB" % (f.name, ver, cnt, info["size"] / 1e9))
        hits = []
        for i in range(min(cnt, len(tb) // ENTRY)):
            base = i * ENTRY
            fid_u64 = struct.unpack_from("<Q", tb, base)[0]
            k = "%016X" % fid_u64
            if k in want:
                o, pk, dc = struct.unpack_from("<III", tb, base + 8)
                fl = struct.unpack_from("<i", tb, base + 28)[0]
                hits.append((want[k], k, i, o, pk, dc, fl))
        print("   命中:", len(hits))
        for x in hits:
            print("    ", x)


if __name__ == "__main__":
    main()
