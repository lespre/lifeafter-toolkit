# -*- coding: utf-8 -*-
"""dxbc_inspect.py — DXBC 容器 + RDEF 反射解析 (v2: 支持偏移表 + 多 DXBC blob)
用法: python dxbc_inspect.py <file.pipe> [--strings]
"""
import sys, os, struct, re

def u32(b, o): return struct.unpack_from('<I', b, o)[0]

def S(b, pool, end, noff):
    if noff in (0xFFFFFFFF, None): return ''
    e = b.find(b'\x00', pool + noff, end)
    return b[pool + noff:e].decode('latin1', 'replace')

def parse_blob(b, i, tag):
    total = u32(b, i + 24); nch = u32(b, i + 28)
    offs = [u32(b, i + 32 + 4 * k) for k in range(nch)]
    print('== BLOB %s @%d total=%d chunks=%d' % (tag, i, total, nch))
    for k, o in enumerate(offs):
        cc = b[i + o:i + o + 4].decode('latin1')
        sz = u32(b, i + o + 4)
        print('   [%d] %s size=%d' % (k, cc, sz))
        st = i + o + 8
        if cc == 'RDEF':
            parse_rdef(b, st, sz)
        elif cc in ('ISGN', 'OSGN', 'PSGN'):
            cnt = u32(b, st)
            names = []
            for q in range(cnt):
                p = st + 4 + q * 28
                no = u32(b, p); idx = u32(b, p + 4); reg = u32(b, p + 20)
                nm = S(b, st, st + sz, no)
                names.append('%s(reg%d)' % (nm, reg))
            print('      sig: ' + ', '.join(names))

def parse_rdef(b, st, sz):
    end = st + sz
    cbCount = u32(b, st)
    p = st + 4
    cbs = []
    for k in range(cbCount):
        cbs.append(struct.unpack_from('<IIIII', b, p)); p += 20
    bindCount = u32(b, p); p += 4
    binds = []
    for k in range(bindCount):
        binds.append(struct.unpack_from('<IIIII', b, p)); p += 20
    varCount = u32(b, p); p += 4
    vars_ = [struct.unpack_from('<IIIIIIIIII', b, p + 40 * k) for k in range(varCount)]
    p += varCount * 40
    typeCount = u32(b, p); p += 4
    p += typeCount * 36
    memberCount = u32(b, p); p += 4
    p += memberCount * 8
    pool = p
    print('   RDEF: cbs=%d binds=%d vars=%d types=%d members=%d poolOff=+%d' % (cbCount, bindCount, varCount, typeCount, memberCount, pool - st))
    print('   -- cbuffers:')
    for name, varc, size, flags, typ in cbs:
        print('      [%s] vars=%d size=%d' % (S(b, pool, end, name), varc, size))
    print('   -- bindings (t/s/b slots):')
    for name, typ, bp, bc, fl in binds:
        print('      %-30s type=%d bindPoint=%d count=%d' % (S(b, pool, end, name), typ, bp, bc))
    print('   -- variables:')
    for f in vars_:
        print('      %-38s start=%d size=%d' % (S(b, pool, end, f[0]), f[1], f[2]))

def parse(path, dump_strings=False):
    b = open(path, 'rb').read()
    offs = [m.start() for m in re.finditer(b'DXBC', b)]
    print('file=%s size=%d blobs=%d' % (os.path.basename(path), len(b), len(offs)))
    for k, i in enumerate(offs):
        try:
            parse_blob(b, i, 'VS' if k == 0 else 'PS')
        except Exception as e:
            print('   !! blob parse fail:', repr(e)[:200])

if __name__ == '__main__':
    parse(sys.argv[1], '--strings' in sys.argv)
