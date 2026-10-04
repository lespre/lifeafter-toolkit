# -*- coding: utf-8 -*-
"""[已由 c159_pair.py v3 取代 — 本文件保留作历史/条目级调试用]
c159_pair.py v3 = 通用解析器: 名字表/槽位组/数值块自动识别 + 评分配对 + 003997 绑定解析 + 跨LOD/跨资产测试。

c159_parser.py — NeoX .c159 材质/对象文件解析器 (可复用, v1 条目级)
序列化格式(实测 2026-09, 029): 流式条目序列, 条目 = [magic 01 00 01 13] [type] [payload]
  type: 01=字符串(\\0结尾)  02=int32  03=uint32?  05=float32
        06=float32数组(=uint32 count + N*float, 颜色=count 4)  07/08=待定
  另见变体 magic [01 00 01 0f](尾部), 以及 [01 01 00 01 13] 开头的第一条目。
用法:
  python c159_parser.py <file.c159>            # 打印结构化条目表
  python c159_parser.py <file.c159> --json out.json
"""
import sys, struct, json

MAGIC = b'\x01\x00\x01\x13'

def parse_entries(b):
    """返回条目列表: dict(off, tag, type, raw, value)"""
    out = []
    i = 0
    n = len(b)
    while i < n - 6:
        j = b.find(MAGIC, i)
        if j < 0: break
        # 若 magic 前一字节=0x01 且形成 [01 01 00 01 13], 归并到前一条目(payload 尾部)
        t = b[j+4]
        st = j + 5
        try:
            if t == 0x01:  # 字符串
                k = b.find(b'\x00', st)
                if k < 0: i = j + 5; continue
                raw = b[st:k]
                s = raw.decode('utf-8', 'replace')
                if not all(32 <= ord(c) < 127 for c in s):  # 非可打印=不是字符串类型, 跳过
                    i = j + 5; continue
                out.append(dict(off=j, type='str', raw=raw.hex(), value=s))
                i = k + 1
            elif t == 0x02:
                v = struct.unpack_from('<i', b, st)[0]
                out.append(dict(off=j, type='i32', raw=b[st:st+4].hex(), value=v))
                i = st + 4
            elif t == 0x03:
                v = struct.unpack_from('<I', b, st)[0]
                out.append(dict(off=j, type='u32', raw=b[st:st+4].hex(), value=v))
                i = st + 4
            elif t == 0x05:
                v = struct.unpack_from('<f', b, st)[0]
                out.append(dict(off=j, type='f32', raw=b[st:st+4].hex(), value=round(float(v), 5)))
                i = st + 4
            elif t == 0x06:
                cnt = struct.unpack_from('<I', b, st)[0]
                if cnt < 64:
                    vals = struct.unpack_from('<%df' % cnt, b, st+4)
                    out.append(dict(off=j, type='f32[%d]' % cnt, raw=b[st:st+4+cnt*4].hex(),
                                    value=[round(float(v), 5) for v in vals]))
                    i = st + 4 + cnt * 4
                else:
                    i = j + 5
            else:
                i = j + 5
                continue
        except Exception:
            i = j + 5
    return out

def main():
    path = sys.argv[1]
    b = open(path, 'rb').read()
    entries = parse_entries(b)
    # 顶部自由字符串(非条目): 收集所有可打印串并标注是否已被条目覆盖
    import re
    covered = set()
    for e in entries:
        if e['type'] == 'str':
            covered.add(e['off'])
    frees = [(m.start(), m.group().decode('latin1')) for m in re.finditer(rb'[\x20-\x7e]{3,}', b)]
    print(f'== {path}  {len(b)}B  条目={len(entries)}  自由串={len(frees)} ==')
    print('--- 自由字符串(名字区等) ---')
    for off, s in frees:
        print('%5d  %s' % (off, s[:90]))
    print('--- 条目序列 ---')
    for e in entries:
        v = e['value']
        vs = str(v)
        if len(vs) > 90: vs = vs[:90] + '...'
        print('%5d  %-8s %s' % (e['off'], e['type'], vs))
    if '--json' in sys.argv:
        out = sys.argv[sys.argv.index('--json')+1]
        json.dump(dict(file=path, size=len(b), entries=entries,
                       free_strings=[dict(off=o, s=s) for o, s in frees]),
                  open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('JSON ->', out)

if __name__ == '__main__':
    main()
