# -*- coding: utf-8 -*-
"""只解 NXPK 头 + 条目表（不整文件解密），按 fid 查条目。
CDN 包结构：raw[0:8] 明文前缀 + 从 offset 8 起 AES-ECB(块对齐) 的 NXPK 流。
"""
import sys, struct, pathlib
PROJ = pathlib.Path(r"E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
import la_unpack_core as LC
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of

SKIP = 8
ENTRY = 48


def read_table(f: pathlib.Path):
    with f.open("rb") as h:
        raw = h.read(SKIP + 48 + 16)
        body = raw[SKIP:SKIP + 48]
        head = LC.aes_ecb_decrypt(body)
        if head[:4] != b"NXPK":
            return None, {"error": "not NXPK after aes", "head": head[:16].hex()}
        ver = struct.unpack_from("<i", head, 4)[0]
        table_off = struct.unpack_from("<I", head, 8)[0]
        count = struct.unpack_from("<I", head, 12)[0]
        if count > 4_000_000 or table_off <= 0:
            return None, {"error": "bad header", "ver": ver, "off": table_off, "count": count}
        h.seek(SKIP + table_off)
        need = count * ENTRY
        tb = h.read(need + 16)
    tb = tb[:need + (16 - need % 16) % 16]
    plain = LC.aes_ecb_decrypt(tb)[:need]
    info = {"ver": ver, "table_off": table_off, "count": count, "size": f.stat().st_size}
    return (plain, count, table_off, info), info


def main():
    pkgs = sorted(pathlib.Path(r"E:/la拆包项目/01_索引与产物/源包/players2021_layers").glob("*.npk"))
    targets = {}
    for rel in ("bag_f_3328_high.mesh", "bag_f_3328.mesh", "bag_m_3328_high.mesh",
                "bag_f_3327_high.mesh", "bag_m_3327_high.mesh"):
        for sex in ("f", "m"):
            pass
    want = {}
    for m, sex in (("3327", "f"), ("3327", "m"), ("3328", "f"), ("3328", "m")):
        for stem in (f"bag_{sex}_{m}_high", f"bag_{sex}_{m}"):
            rel = f"character\\players2021\\bag_{sex}_{m}\\{stem}.mesh"
            want["%016X" % fid_of(rel)] = rel
    print("目标 fid 数:", len(want))
    for p in pkgs:
        res = read_table(p)
        if not res[0]:
            print(p.name, "解析失败:", res[1]); continue
        plain, count, _off, info = res[0]
        print(p.name, "ver=%s entries=%s size=%.1fMB" % (info["ver"], count, info["size"] / 1e6))
        hit = 0
        for i in range(count):
            base = i * ENTRY
            a = struct.unpack_from("<HHI", plain, base)      # 常见布局：u16 flag + u16 ? + u32 ?
            pass
        # 两种可能布局都试：<QIII..> 与 <IHHI..>
        found = []
        for i in range(count):
            base = i * ENTRY
            fid_u64 = struct.unpack_from("<Q", plain, base)[0]
            key = "%016X" % fid_u64
            if key in want:
                off, packed, dec, = struct.unpack_from("<III", plain, base + 8)
                found.append((want[key], key, i, off, packed, dec))
        print("   u64@0 命中:", len(found))
        for f_ in found:
            print("   ", f_)


if __name__ == "__main__":
    main()
