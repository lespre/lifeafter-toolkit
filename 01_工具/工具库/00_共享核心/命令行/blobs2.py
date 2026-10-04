"""blobs2.py —— 修正版码段扫描（★ 2026-10-03 实测）
原 blobs() 要求 `tag + u32len + 80 00` ⇒ 会漏掉魔数为其他值的 code 段 ✗
实测示例：`d3 13 "ColorItem.on_loaded" 47 00 00 00 7b 64 00 00 00 f8 80 00 <payload>`
  ⇒ tag=0x7B ✓ len=100 ✓ 魔数 = f8 80 00（3 字节 ✗）
⇒ 修正：tag + u32len 后允许 1-3 字节任意前缀，只校验【长度可读且 payload 像字节码】
"""
import struct
from pathlib import Path

TAGS = (0xFB, 0x7B)


def scan_blobs(buf, min_len=8):
    """返回 [(tag_off, payload_off, payload_len)]（放宽魔数校验 ✓）"""
    out = []
    n = len(buf)
    i = 0
    while i < n - 8:
        if buf[i] in TAGS:
            ln = struct.unpack_from('<I', buf, i + 1)[0]
            if 8 <= ln <= n - i - 5:
                # 试 3 种魔数前缀长度（2/3 字节 ✓）
                for mag in (2, 3, 4):
                    p = i + 5 + mag
                    if p + ln <= n:
                        body = buf[p:p + ln]
                        score = _bytecode_score(body)
                        if score > 0.55:
                            out.append((i, p, ln, body, score))
                            i = p + ln
                            break
                else:
                    i += 1
                    continue
                continue
        i += 1
    return out


def _bytecode_score(b):
    """粗判这段像不像字节码（opcode 分布 ✓）"""
    if not b:
        return 0.0
    n = len(b)
    good = 0
    # 已知 opcode 号（客户端方言 ✓ 抽样）
    known = set()
    try:
        import sys
        sys.path.insert(0, r'E:\la拆包项目\01_工具\工具库\00_共享核心')
        import toolkit_core.script_decode as sd
        known = set(sd.OPS.keys())
    except Exception:
        pass
    for c in b:
        if c in known:
            good += 1
    return good / max(n, 1)


if __name__ == '__main__':
    import sys
    F = Path(sys.argv[1] if len(sys.argv) > 1 else
             r'E:\la拆包项目\03_执行\41_还原树\Documents\script.py314.lc.npk\ui\PanelFashionPreview.py')
    buf = F.read_bytes()
    bl = scan_blobs(buf)
    print('★ %s ｜ %d B ｜ 码段 %d 个（修正版 ✓）' % (F.name, len(buf), len(bl)))
    tot = 0
    for tag_off, p, ln, body, sc in bl[:40]:
        print('   tag@%-7d payload@%-7d %5d B  像字节码 %.2f' % (tag_off, p, ln, sc))
        tot += ln
    print('   （前 40 个；总 payload %d B，文件 %d B）' % (tot, len(buf)))
