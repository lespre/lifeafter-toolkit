# -*- coding: utf-8 -*-
"""v2: 补上「sub flag 高字节==1 → 额外 vc*4 的 u32 重映射块」
并打印逐步 steps 以定位 typ=1 偏差"""
import sys, os, struct, glob
sys.path.insert(0, r"E:\la拆包项目\01_工具\工具库\02_图文音频渲染\皮肤链与渲染")
import mesh_parse2 as M

def locate(d):
    for k in range(1, 11):
        off = 0x0E + 10 * k
        if off + 2 + 8 + 24 > len(d): break
        term = struct.unpack_from('<H', d, off)[0]
        tv, tf = struct.unpack_from('<II', d, off + 2)
        if term != 1 or tv == 0 or tf == 0: continue
        subs = [struct.unpack_from('<IIH', d, 0x0E + 10 * i) for i in range(k)]
        if sum(s[0] for s in subs) == tv and sum(s[1] for s in subs) == tf:
            return (0x0E, subs, tv, tf, 'sub_table_0x0e')
    best = M._scan_sub_table_anywhere(d)
    if best:
        k2, cand, subs2, tv2, tf2 = best
        return (cand - 10*k2, subs2, tv2, tf2, 'full_file_scan')
    return None

def walk(d, trace=False):
    ver = struct.unpack_from('<I', d, 4)[0] & 0xffffff
    flag8 = struct.unpack_from('<I', d, 4)[0] >> 24
    typ = struct.unpack_from('<H', d, 8)[0]
    half = (ver > 0x50003) or (flag8 == 2)
    L = locate(d)
    if L is None: return None, {'err':'no_sub_table'}
    off, subs, tv, tf, variant = L
    k = len(subs); steps=[]; q = off + 10*k
    term = struct.unpack_from('<H', d, q)[0]
    tv2, tf2 = struct.unpack_from('<II', d, q+2)
    steps.append(('subtab', off, 10*k, 'k=%d flags=%s'%(k,[hex(s[2]) for s in subs])))
    steps.append(('term/tv/tf', q, 10, 'term=%d tv=%d tf=%d'%(term,tv2,tf2)))
    if term == 0:
        return q+10, {'note':'term0','steps':steps,'variant':variant}
    q += 10
    if ver >= 0x50004:
        steps.append(('bounds6f', q, 24, '')); q += 24
        steps.append(('pos u16x3', q, tv*6, '')); q += tv*6
        steps.append(('nrm u16x3', q, tv*6, '')); q += tv*6
    else:
        steps.append(('pos f32x3', q, tv*12, '')); q += tv*12
        if half: steps.append(('nrm8', q, tv*8, '')); q += tv*8
        else: steps.append(('nrm f32x3', q, tv*12, '')); q += tv*12
    fl = struct.unpack_from('<H', d, q)[0]
    steps.append(('flag48', q, 2, 'flag=%d'%fl)); q += 2
    if fl != 0:
        if half:
            if ver < 0x50004: steps.append(('stream48 8B', q, tv*8, '')); q += tv*8
            else: steps.append(('stream48 6B', q, tv*6, '')); q += tv*6
        else:
            steps.append(('stream48 f32x3', q, tv*12, '')); q += tv*12
    steps.append(('idx u16x3', q, tf*6, '')); q += tf*6
    for i,(vc,fc,flag) in enumerate(subs):
        n_ex = flag & 0xff; per = vc*(4 if half else 8)
        steps.append(('sub%d extras'%i, q, n_ex*per, 'n=%d vc=%d per=%d'%(n_ex,vc,per))); q += n_ex*per
    # ★ 新增：sub flag 高字节==1 → 额外 vc*4 (u32 重映射)
    for i,(vc,fc,flag) in enumerate(subs):
        if (flag >> 8) == 1:
            steps.append(('sub%d remap u32 vc*4'%i, q, vc*4, '')); q += vc*4
    if typ == 1:
        if ver < 0x50004:
            steps.append(('skin tv*20', q, tv*20, '')); q += tv*20
            if ver >= 0x50003: steps.append(('bitset32', q, 32, '')); q += 32
        else:
            if q < len(d) and d[q] == 1:
                sVar6 = struct.unpack_from('<h', d, q+1)[0]
                cnt = struct.unpack_from('<H', d, q+3)[0]
                steps.append(('skin tag1 pal', q, 5+cnt*4, 'w=%d cnt=%d'%(sVar6,cnt))); q += 5+cnt*4
                idw = 1 if sVar6 == 8 else 2
                steps.append(('skin idx', q, tv*idw, 'w=%d'%idw)); q += tv*idw
                steps.append(('skin w tv*6', q, tv*6, '')); q += tv*6
            else:
                steps.append(('skin tag0 hdr1', q, 1, '')); q += 1
                steps.append(('skin idx tv*4', q, tv*4, '')); q += tv*4
                steps.append(('skin w tv*6', q, tv*6, '')); q += tv*6
            if ver >= 0x50003: steps.append(('bitset32', q, 32, '')); q += 32
    info = {'ver':hex(ver),'flag8':flag8,'typ':typ,'half':half,'k':k,'tv':tv,'tf':tf,
            'variant':variant,'q':q,'len':len(d),'rest':len(d)-q,'steps':steps}
    return q, info

if __name__=='__main__':
    mode = sys.argv[1]
    pats = sys.argv[2:]
    files=[]
    for p in pats: files += glob.glob(p)
    if mode == 'trace':
        for p in files[:6]:
            d=open(p,'rb').read()
            if d[:4]!=b'\x34\x80\xc8\xbb': continue
            q,info=walk(d)
            print("="*70); print(os.path.basename(p), "len",len(d))
            for s in info.get('steps',[]):
                print("   %-22s @%-8d len=%-7d %s"%(s[0],s[1],s[2],s[3]))
            print("   cursor=%s rest=%s"%(info.get('q'),info.get('rest')))
    else:
        from collections import Counter
        c=Counter(); rows=[]
        for p in files:
            d=open(p,'rb').read()
            if d[:4]!=b'\x34\x80\xc8\xbb': continue
            try: q,info=walk(d)
            except Exception as e: c['EXC']+=1; continue
            if q is None: c['ERR']+=1; continue
            c['rest=%d'%info['rest']]+=1
            rows.append((os.path.basename(p),info))
        tot=sum(c.values())
        print("total",tot,"rest=16:",c.get('rest=16',0),"非16:",tot-c.get('rest=16',0))
        print("其他 rest 分布:", {k:v for k,v in c.most_common(12) if k!='rest=16'})
        bad=[(n,i) for n,i in rows if i['rest']!=16][:12]
        for n,i in bad:
            print(" BAD %-14s ver=%s typ=%d half=%d k=%d tv=%d tf=%d flags=%s rest=%d var=%s"%(
                n,i['ver'],i['typ'],i['half'],i['k'],i['tv'],i['tf'],
                [hex(s[2]) for s in M.__dict__ and [] ] if False else '',i['rest'],i['variant']))
