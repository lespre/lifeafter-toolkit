# -*- coding: utf-8 -*-
"""lighting_defuse.py — Deferred 光照 PS 的 gbuffer 语义追踪（外审 v6 令 · 优先项 #2）

方法: 对反汇编文本做简化 def-use 传播（寄存器 → 来源集合 {t#/cb/v#/l(常量)}），
      再在四类语义模式处报告该值实际来源于哪个 t_gbufferN：

  P1 F0 lerp      : add rX.xyz, rY.xyzx, l(-0.079956…)  + mad rX.xyz, rZ.W, rX.xyzx, l(0.079956…)
                    → 反照率来源 = rY 的 t#；金属标量来源 = rZ.w 的 t#
  P2 八面体法线    : mad rX.xy, rY.xyxx, l(2,2,…), l(-1,-1,…) (+ lt/movc 修正)
                    → 法线来源 = rY 的 t#
  P3 位包解码      : mul rX.y, rY.ZWZZ, l(255…) / mul rX.xy, rY.zwzz, l(255…)
                    → 位包字段来源 = rY 的 t#
  P4 粗糙度→LOD    : log rX.z, rX.z … sample_l(texturecubearray) …, t13, s0, rX.z
                    → LOD 输入来源 = rX 的 t#
用法: python lighting_defuse.py <ps.asm> [--max-report 40]
"""
import re, sys

REG = r'(?:r\d+|v\d+|cb\d+\[\d+\]|o\d+|l\([^)]*\)|t\d+|s\d+)'
COMPS = 'xyzw'

def parse(lines):
    ins = []
    for i, l in enumerate(lines):
        s = l.strip()
        if not s or s.startswith('//') or s.startswith('dcl_'):
            continue
        # 支持 sample_*_indexable(texture2d)(float,...) 这类带括号类型说明的指令
        m = re.match(r'^([a-z_0-9]+)((?:\([^)]*\))*)\s+(.*)$', s)
        if not m:
            continue
        op, rest = m.group(1), m.group(3)
        # 目标 = 第一个操作数
        parts = [p.strip() for p in rest.split(',')]
        dst = parts[0] if parts else ''
        srcs = parts[1:]
        ins.append(dict(i=i, op=op, dst=dst, srcs=srcs, text=s))
    return ins

def reg_name(tok):
    m = re.match(r'^([rovcb]\d+|cb\d+\[\d+\]|l\([^)]*\)|t\d+|s\d+)', tok.strip())
    return m.group(1) if m else None

def propagate(ins):
    """按**分量**追踪 寄存器.通道 → 来源集合（避免 r1.xy 与 r1.w 混桶）。"""
    origins = {}
    snaps = []
    for k, it in enumerate(ins):
        dst = it['dst']
        sset = set()
        for s in it['srcs']:
            s = s.strip().lstrip('-|!')
            r = reg_name(s)
            if not r or r.startswith('l('):
                continue
            if re.match(r'^t\d+$', r):
                sset.add(r)
            elif re.match(r'^(cb\d+|v\d+)', r):
                sset.add(r)
            else:
                comps = s.split('.')[1] if '.' in s else ''
                if not comps:
                    for c in COMPS:
                        sset |= origins.get('%s.%s' % (r, c), set())
                else:
                    for c in comps:
                        if c in COMPS:
                            sset |= origins.get('%s.%s' % (r, c), set())
        if dst:
            r = reg_name(dst)
            comps = dst.split('.')[1] if '.' in dst and reg_name(dst) else ''
            if not r:
                pass
            elif not comps:
                for c in COMPS:
                    origins['%s.%s' % (r, c)] = set(sset)
            else:
                for c in comps:
                    if c in COMPS:
                        origins['%s.%s' % (r, c)] = set(sset)
        snaps.append(dict(origins=dict(origins), text=it['text'], op=it['op'], i=it['i']))
    return snaps

def src_of_snap(snaps, k, reg, swizzle=''):
    """按分量子集查来源；返回 {t#}"""
    out = set()
    comps = swizzle if swizzle else COMPS
    for c in comps:
        if c in COMPS:
            out |= snaps[k]['origins'].get('%s.%s' % (reg, c), set())
    return sorted(x for x in out if re.match(r'^t\d+$', x))


def main():
    path = sys.argv[1]
    lines = open(path, encoding='utf-8', errors='replace').read().splitlines()
    ins = parse(lines)
    snaps = propagate(ins)
    def src_of(reg, k, swz=''):
        return src_of_snap(snaps, k, reg, swz)
    print('== %s ==' % path)
    print('== GBuffer 采样（纹理→寄存器）==')
    for k, it in enumerate(ins):
        if 'sample' in it['op'] and len(it['srcs']) > 1 and re.match(r'^t\d+$', reg_name(it['srcs'][1]) or ''):
            print('   [%4d] %s' % (it['i'], it['text'][:120]))
    print()
    print('== P1 F0 lerp（金属/F0）==')
    for k, it in enumerate(ins):
        if it['op'] == 'add' and '-0.079956' in it['text']:
            reg = reg_name(it['dst'])
            araw = it['srcs'][0]
            albedo = reg_name(araw)
            aswz = araw.split('.')[1] if '.' in araw else ''
            print('   [%4d] %s' % (it['i'], it['text'][:120]))
            print('         反照率来源 %s -> 纹理 %s' % (araw, src_of(albedo, k, aswz)))
            base = reg.split('.')[0] if reg else None
            # 找随后的 mad rX.xyz, rZ.W, ... 0.079956
            for k2 in range(k + 1, min(k + 4, len(ins))):
                if ins[k2]['op'] == 'mad' and '0.079956' in ins[k2]['text'] and reg_name(ins[k2]['dst']).split('.')[0] == base:
                    scal = reg_name(ins[k2]['srcs'][0])
                    if scal and '.' in scal:
                        sreg = scal.split('.')[0]
                        sswz = scal.split('.')[1]
                        print('   [%4d] %s' % (ins[k2]['i'], ins[k2]['text'][:120]))
                        print('         金属标量 = %s -> 纹理 %s' % (scal, src_of(sreg, k2, sswz)))
                    break
    print()
    print('== P2 八面体法线解码 ==')
    for k, it in enumerate(ins):
        if it['op'] == 'mad' and re.search(r'l\(2\.000000, 2\.000000', it['text']) and re.search(r'l\(-1\.000000', it['text']):
            raw = it['srcs'][0]
            r = reg_name(raw)
            if r and '.' in raw:
                print('   [%4d] %s | 输入 %s -> 纹理 %s' % (it['i'], it['text'][:110], raw, src_of(r, k, raw.split('.')[1])))
    print()
    print('== P3 位包解码（×255 取字节）==')
    for k, it in enumerate(ins):
        if it['op'] == 'mul' and '255.000000' in it['text'] and re.search(r'\.\w{2,4},', it['text']):
            raw = it['srcs'][0]
            r = reg_name(raw)
            if r and '.' in raw:
                print('   [%4d] %s | 字段来源 %s -> 纹理 %s' % (it['i'], it['text'][:110], raw, src_of(r, k, raw.split('.')[1])))
    print()
    print('== P4 粗糙度→环境 LOD ==')
    for k, it in enumerate(ins):
        if 'sample_l_indexable(texturecubearray)' in it['text']:
            lod = reg_name(it['srcs'][-1])
            print('   [%4d] %s' % (it['i'], it['text'][:120]))
            if lod:
                base = lod.split('.')[0]
                raw = it['srcs'][-1]
                print('         LOD 操作数 %s -> 来源 %s' % (raw, src_of(base, k, raw.split('.')[1] if '.' in raw else '')))
    for k, it in enumerate(ins):
        if it['op'] == 'log' and re.search(r'^\s*log\s+r\d+\.\w,\s*r\d+\.\w', it['text']):
            raw = it['srcs'][0]
            r = reg_name(raw)
            if r:
                print('   [%4d] %s | 输入 %s -> 来源 %s' % (it['i'], it['text'][:110], raw,
                      src_of(r, k, raw.split('.')[1] if '.' in raw else '')))

if __name__ == '__main__':
    main()
