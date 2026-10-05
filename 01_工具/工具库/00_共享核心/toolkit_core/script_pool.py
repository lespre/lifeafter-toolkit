# -*- coding: utf-8 -*-
r"""script_pool.py — 网易 NeoX Python 方言（=标准 marshal + 改制）的池表解析器。

★ 为什么需要它：客户端 .py 是【网易改制的 marshal 方言】，标准 marshal 不认。
  我们在 lib/functools.py（源码已知）上对拍，把 tag 表推出来了：

    tag            含义                                   载荷
    ─────────────────────────────────────────────────────────────────
    0xd3 / 0xf3    ASCII 串（ref 位变体）                  1B 长度（0xff → u32）
    0xda / 0xfa    Unicode 串                              同上
    0x73           bytes                                    u32 长度 + 数据
    0xfb           code 段                                  u32 长度 + "80 00" + 字节码
    0x5a           ★池序号引用（不是值！）                   u32
    0xbe           ★整型常量（真值容器）                     u32 LE

★ 已验证的锚点（硬证据，不是猜）：
    1) functools.py 里 `be 80 00 00 00`（=128）全文恰出现 1 次，
       与源码 `lru_cache(maxsize=128)` 一一对应；
    2) 池是【自索引】的：`d3 "abc" 5a 6` / `"collections" 5a 7` / `"operator" 5a 8` /
       `"reprlib" 5a 9` —— 与 import 语句顺序完全一致；
    3) const.py 里 `5a 47806` ↔ 池序号 47806 = 'HACK_BAG_TYPE_FOR_COMPARE' ✓。
    4) 覆盖率：functools.py 41,691 B 上已知 tag 覆盖 82.4%。

★ 池的排布（可直接读）：
    <模块名> <类名> <成员名…> <该类码段> <下一个类名> …
    类常量数组 = 一串 `5a <池序号>`，序号指向池里的该常量（整数条目也在池里，如 49→1600）。

用法：
    python script_pool.py <模块路径> [--window N] [--find NAME]
    python script_pool.py <模块路径> --ordinals 47780 47840
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

ASCII_TAGS = (0xD3, 0xF3)
UNI_TAGS = (0xDA, 0xFA)
BYTES_TAG = 0x73
REF_TAG = 0x5A
INT_TAG = 0xBE
CODE_TAG = 0xFB
CODE_MAGIC = b"\x80\x00"


def walk(buf: bytes):
    """按 tag 走文件，返回顶层条目 [(kind, value, offset)]；kind ∈ str/int/code。"""
    out = []
    i, n = 0, len(buf)
    while i < n:
        t = buf[i]
        if t in ASCII_TAGS or t in UNI_TAGS:
            if i + 1 >= n:
                i += 1
                continue
            ln = buf[i + 1]
            st = i + 2
            if ln == 0xFF:
                if i + 6 > n:
                    i += 1
                    continue
                ln = struct.unpack_from("<I", buf, i + 2)[0]
                st = i + 6
            if ln and st + ln <= n:
                raw = buf[st:st + ln]
                # ★ 必须校验「可打印」+ 串长上限，否则 (a) 二进制被当串吞掉
                #   (b) 巨长假长度把整片区域吞掉 —— 两种都会让条目数塌成 1/3
                #   踩过：const.py 54866 → 18107
                if ln <= 512 and all(0x20 <= c < 0x7F for c in raw):
                    out.append(("str", raw.decode("ascii"), i))
                    i = st + ln
                    continue
        elif t == BYTES_TAG and i + 5 <= n:
            ln = struct.unpack_from("<I", buf, i + 1)[0]
            if ln <= n - i - 5:
                # ★ bytes 也占一个槽（v4 规则：槽由 str/int/bytes/code 占，ref 不占）
                out.append(("bytes", ln, i))
                i += 5 + ln
                continue
        elif t == INT_TAG and i + 5 <= n:
            out.append(("int", struct.unpack_from("<I", buf, i + 1)[0], i))
            i += 5
            continue
        elif t == REF_TAG and i + 5 <= n:
            i += 5
            continue
        elif t == CODE_TAG and i + 7 <= n and buf[i + 5:i + 7] == CODE_MAGIC:
            ln = struct.unpack_from("<I", buf, i + 1)[0]
            if 0 < ln <= n - i - 7:
                out.append(("code", ln, i))
                i += 7 + ln
                continue
        i += 1
    return out


def refs(buf: bytes, lo: int, hi: int):
    """区间内所有 `5a <u32>` 引用（含偏移）。"""
    out = []
    i = lo
    while i < hi - 5:
        if buf[i] == REF_TAG:
            out.append((i, struct.unpack_from("<I", buf, i + 1)[0]))
            i += 5
        else:
            i += 1
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("--ordinals", nargs=2, type=int, metavar=("LO", "HI"))
    ap.add_argument("--find", help="按名字找池序号")
    ap.add_argument("--refs", nargs=2, type=int, metavar=("LO", "HI"),
                    help="打印该字节区间里的 5a 引用及其指向")
    a = ap.parse_args()

    p = Path(a.module)
    buf = p.read_bytes()
    ents = walk(buf)
    print("★ %s ｜ %d B ｜ 顶层条目 %d（str %d / int %d / code %d）"
          % (p.name, len(buf), len(ents),
             sum(1 for k, _, _ in ents if k == "str"),
             sum(1 for k, _, _ in ents if k == "int"),
             sum(1 for k, _, _ in ents if k == "code")))

    if a.find:
        hits = [i for i, (k, v, _) in enumerate(ents) if k == "str" and v == a.find]
        print("   '%s' → 池序号 %s" % (a.find, hits))

    if a.ordinals:
        lo, hi = a.ordinals
        print("   池序号 %d..%d：" % (lo, hi))
        for k in range(lo, min(hi + 1, len(ents))):
            kind, v, off = ents[k]
            print("      %-7d %-5s %r  @%d" % (k, kind, v, off))

    if a.refs:
        lo, hi = a.refs
        rs = refs(buf, lo, hi)
        print("   区间 %d..%d 的 5a 引用 %d 个：" % (lo, hi, len(rs)))
        for off, n in rs:
            if n < len(ents):
                kind, v, _ = ents[n]
                print("      @%-8d → 池 %-7d %-5s %r" % (off, n, kind, v))
            else:
                print("      @%-8d → 池 %-7d （越界）" % (off, n))


if __name__ == "__main__":
    main()
