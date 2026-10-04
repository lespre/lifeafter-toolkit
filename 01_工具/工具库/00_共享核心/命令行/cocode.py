"""cocode.py —— 按锚点切出每个函数的 co_code（★ 2026-10-03 实测结构）
结构（逐字实测 ✓）：
    `D3 <len1> "<QualName>"`            ← 全限定名（如 ColorItem.on_loaded ✓）
    <u32>                                ← 未知计数（实测 0x47=71 ✓）
    `7B <u32 len>`                       ← code 段 tag + co_code 长度
    <3 字节魔数>（实测 f8 80 00 ✓）      ← 也可能 2 字节 80 00
    <co_code: len 字节>
之后紧跟 `D3 <len> "<name>"` = co_names 表项 ✓
"""
import re, struct
from pathlib import Path

TAG_STR = (0xD3, 0xF3, 0xDA, 0xFA)


def read_str(buf, j, n):
    t = buf[j]
    if t not in TAG_STR:
        return None, j
    ln = buf[j + 1]
    st = j + 2
    if ln == 0xFF:
        if j + 6 > n:
            return None, j
        ln = struct.unpack_from('<I', buf, j + 2)[0]
        st = j + 6
    if not (0 < ln <= 4096) or st + ln > n:
        return None, j
    raw = buf[st:st + ln]
    try:
        return raw.decode('utf-8'), st + ln
    except Exception:
        return raw.decode('latin1'), st + ln


def extract(buf):
    """→ [(qualname, code_off, code_len, code_bytes)]"""
    n = len(buf)
    out = []
    seen = set()
    for m in re.finditer(rb'[\xd3\xf3\xda\xfa]', buf):
        i = m.start()
        if i in seen:
            continue
        s, j = read_str(buf, i, n)
        if not s or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]*', s):
            continue
        seen.add(i)
        # s 之后：u32 + tag(7B/FB) + u32 len + 魔数
        k = j
        if k + 9 > n:
            continue
        u32a = struct.unpack_from('<I', buf, k)[0]
        if buf[k + 4] not in (0x7B, 0xFB):
            continue
        ln = struct.unpack_from('<I', buf, k + 5)[0]
        if not (8 <= ln <= n - k - 9):
            continue
        for mag in (2, 3, 4):
            p = k + 9 + mag - 2
            if p + ln <= n:
                code = buf[p:p + ln]
                if len(code) >= 8:
                    out.append((s, p, ln, code, u32a, mag))
                    break
    return out


if __name__ == '__main__':
    import sys
    F = Path(sys.argv[1] if len(sys.argv) > 1 else
             r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\ui\PanelFashionPreview.py')
    buf = F.read_bytes()
    funcs = extract(buf)
    print('★ %s ｜ %d B ｜ 切出函数 %d 个' % (F.name, len(buf), len(funcs)))
    kw = sys.argv[2] if len(sys.argv) > 2 else None
    for s, p, ln, code, u, mag in funcs:
        if kw and kw.lower() not in s.lower():
            continue
        print('   %-52s code@%-7d %5d B  魔数%dB' % (s[:52], p, ln, mag))
