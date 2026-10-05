# -*- coding: utf-8 -*-
r"""NeoX 脚本方言（script.py314.lc.npk 的 .py 载荷）—— 字符串/整数抽取。

## 为什么有这个模块
客户端的脚本模块是**网易魔改过的 marshal**（标准 `marshal.loads` 逐偏移 120,000 次
→ 0 个 code 对象；社区那几种 XOR/rotor 变换也全无效）。但我们**实测出了三个 tag**，
足以把「名字/文案/整数常量」从任意模块里抠出来（读字段名、UI key、id、时间戳足够用）：

```
0xd3 / 0xf3 = ASCII 串：1B 长度（0xff ⇒ 接 u32 长度）
0xda / 0xfa = Unicode 串：同长度规则（内容 utf-8，失败退 utf-16le）
0x5a        = 整数 + u32 小端        （实测含纪元时间戳与 6~9 位 id）
```
实测依据（`com/const.py`）：
```
PREORDER_CD         前 = 5a 21 00 00 00 | 5a 22 00 00 00 | d3 0b   ← 0x0b=11=len ✓
AUTO_BUY_INTERVAL   前 = 5a 94 a8 00 00 | d3 11                  ← 0x11=17=len ✓
DOWN_SHELF_INTERVAL 前 = d3 13  · PREORDER_CLAC_TIME 前 = d3 12  · STUB_PREORDER_SUCCESS 前 = d3 15
```

## 能力边界（如实）
- ✅ 抽出全部字符串（含标识符/文案）与整数/偏移
- ❌ **还原不了字节码**（opcode 被换表）⇒ 拿不到「哪个常量属于哪个字段」的绑定
  以及函数级逻辑。要那个需运行时 dump 或 RE 客户端解释器。
"""
from __future__ import annotations

import struct
from pathlib import Path

ASCII_TAGS = (0xD3, 0xF3)
UNI_TAGS = (0xDA, 0xFA)
INT_TAG = 0x5A

#: 串内容可信度判据（防 tag 在二进制里误撞）——实测必须做，否则噪声占多数
_PRINTABLE = frozenset(range(0x20, 0x7F))


def _plausible_ascii(raw: bytes) -> bool:
    return bool(raw) and all(c in _PRINTABLE for c in raw)


def _plausible_uni(raw: bytes) -> str | None:
    try:
        s = raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            s = raw.decode("utf-16le")
        except UnicodeDecodeError:
            return None
    # 至少要有一半是可打印/非控制字符，才算真串
    good = sum(1 for ch in s if ch.isprintable() or ch in " \t")
    if s and good * 2 >= len(s):
        return s
    return None


def scan(buf: bytes, *, max_items: int | None = None, strict: bool = True):
    """→ (strings, ints)。strings: [{off, tag, len, s}]；ints: [{off, v}]。

    strict=True 时只收「内容像真串」的结果（推荐）；False 会带大量二进制噪声。
    """
    strs: list[dict] = []
    ints: list[dict] = []
    i, n = 0, len(buf)
    while i < n:
        t = buf[i]
        if t in ASCII_TAGS or t in UNI_TAGS:
            if i + 1 >= n:
                break
            ln = buf[i + 1]
            start = i + 2
            if ln == 0xFF:
                if i + 6 > n:
                    i += 1
                    continue
                ln = struct.unpack_from("<I", buf, i + 2)[0]
                start = i + 6
            if ln == 0 or start + ln > n:
                i += 1
                continue
            raw = buf[start:start + ln]
            if t in ASCII_TAGS:
                if strict and not _plausible_ascii(raw):
                    i += 1
                    continue
                s = raw.decode("ascii", "replace")
            else:
                s = _plausible_uni(raw)
                if s is None:
                    i += 1
                    continue
                if strict and not s:
                    i += 1
                    continue
            strs.append({"off": i, "tag": "0x%02x" % t, "len": ln, "s": s})
            i = start + ln
            continue
        if t == INT_TAG and i + 5 <= n:
            ints.append({"off": i, "v": struct.unpack_from("<I", buf, i + 1)[0]})
            i += 5
            continue
        i += 1
        if max_items and len(strs) >= max_items:
            break
    return strs, ints


def scan_file(path: Path | str, **kw):
    p = Path(path)
    return scan(p.read_bytes(), **kw)


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:]:
        s, iv = scan_file(arg)
        print("%s：字符串 %d ｜ 整数 %d" % (arg, len(s), len(iv)))
