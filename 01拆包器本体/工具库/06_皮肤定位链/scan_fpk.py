# -*- coding: utf-8 -*-
"""scan_fpk.py — 在 FPK 包内搜索字符串 (逐帧解压 + 内容匹配)
用法: python scan_fpk.py <package.fpk> <pattern> [--extract-dir <dir>] [--max-hits 40]
输出: 命中帧列表 (index/offset/size/magic), 可选提取命中内容。
"""
import sys, os
from pathlib import Path
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\10_应用核心')
from toolkit_core.fpk_frames import iter_fpk_frames

def main():
    pkg = sys.argv[1]
    pat = sys.argv[2].encode('latin1')
    exdir = None
    if '--extract-dir' in sys.argv:
        exdir = sys.argv[sys.argv.index('--extract-dir') + 1]
        os.makedirs(exdir, exist_ok=True)
    maxh = int(sys.argv[sys.argv.index('--max-hits') + 1]) if '--max-hits' in sys.argv else 40
    n = 0; hits = []
    for fr, payload in iter_fpk_frames(Path(pkg)):
        n += 1
        if pat in payload:
            hits.append(fr)
            print('HIT frame=%d off=%d size=%d magic=%s' % (fr.index, fr.offset, fr.output_size, fr.output_magic))
            if exdir and len(hits) <= maxh:
                fp = os.path.join(exdir, 'frame_%06d.bin' % fr.index)
                open(fp, 'wb').write(payload)
                print('   saved', fp)
            if len(hits) >= maxh:
                break
        if n % 2000 == 0:
            print('... scanned %d frames, hits %d' % (n, len(hits)))
    print('DONE: scanned %d frames, hits %d' % (n, len(hits)))

if __name__ == '__main__':
    main()
