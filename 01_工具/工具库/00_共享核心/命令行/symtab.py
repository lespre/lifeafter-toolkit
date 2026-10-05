"""symtab.py —— NeoX 符号/调试名表解析（★ 2026-10-03 实测破译 ✓）
格式（逐字实测）：
  `D3 <len1> <name>` 后跟 `2E`（'.' 分隔符）或另一条 `D3`
  name 形如 "PanelFashionPreview.update_model_light"（全限定名 ✓）
  条目之间夹元数据：`05` · `5A <u32>` · `3E <u32>` 等
⇒ 解出来就是【类.方法】的完整符号表 ✓ 可用于定位函数体归属 ✓
"""
import re, struct
from pathlib import Path

TAG_STR = (0xD3, 0xF3, 0xDA, 0xFA)


def read_str(buf, j, hi):
    t = buf[j]
    if t not in TAG_STR:
        return None, j
    ln = buf[j + 1]
    st = j + 2
    if ln == 0xFF:
        if j + 6 > hi:
            return None, j
        ln = struct.unpack_from('<I', buf, j + 2)[0]
        st = j + 6
    if not (0 < ln <= 4096) or st + ln > hi:
        return None, j
    raw = buf[st:st + ln]
    try:
        return raw.decode('utf-8'), st + ln
    except Exception:
        return raw.decode('latin1'), st + ln


def scan_symbols(buf, min_len=3):
    """扫全部 `D3<len><str>`（允许 2E 分隔 ✓）→ [(offset, name)]"""
    out = []
    n = len(buf)
    i = 0
    while i < n - 3:
        if buf[i] in TAG_STR:
            s, nj = read_str(buf, i, n)
            if s and len(s) >= min_len and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]*', s):
                out.append((i, s))
                i = nj
                # 跳过紧跟的 2E（'.'）或短元数据
                if i < n and buf[i] == 0x2E:
                    i += 1
                continue
        i += 1
    return out


if __name__ == '__main__':
    import sys
    F = Path(sys.argv[1] if len(sys.argv) > 1 else
             r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\ui\PanelFashionPreview.py')
    buf = F.read_bytes()
    syms = scan_symbols(buf)
    print('★ %s ｜ %d B ｜ 符号 %d 条' % (F.name, len(buf), len(syms)))
    kw = sys.argv[2] if len(sys.argv) > 2 else None
    if kw:
        for off, s in syms:
            if kw.lower() in s.lower():
                print('   @%-7d %s' % (off, s))
    else:
        for off, s in syms[:60]:
            print('   @%-7d %s' % (off, s))
        print('   …')
        for off, s in syms[-30:]:
            print('   @%-7d %s' % (off, s))
