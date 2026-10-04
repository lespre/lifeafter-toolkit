# -*- coding: utf-8 -*-
"""dxbc_rdef.py — DXBC(sm5) 资源定义(RDEF)解析器 + 从容器里挖 DXBC 块。

为什么需要它
------------
PC 侧 NeoX 用 DXBC(D3D) 着色器；「cb0/cb1 常量布局 + t0..tN / s0..sN 槽位 ↔ 参数名」
这件事的**权威来源是 shader 自己**（RDEF chunk = 编译器产出的反射数据），
不是猜的，也不是引擎二进制里的字符串。

RDEF 布局（实测对齐 DXBC 规范）：
  header(28B)  = cbCount, cbOffset, boundCount, boundOffset, minor, major, progType(u16), flags, creatorOffset
  cbuffer(24B) = nameOff, varCount, varOff, size, flags, type
  variable(24B)= nameOff, startOff, size, flags, defaultOff, typeOff
  type(16B)    = class(u16), type(u16), rows, cols, elements, memberCount(u16), memberOff(u32)
  boundres(32B)= nameOff, type, returnType, dimension, sampleCount, bindPoint, bindCount, flags
所有偏移都是**相对 RDEF chunk 数据起点**。

用法：
  python dxbc_rdef.py <file.dxbc> [--json out.json]     # 解析单个
  python dxbc_rdef.py --scan <container> [--limit N]    # 在容器里挖 DXBC 并逐个解析
"""
from __future__ import annotations
import argparse, json, os, struct, sys

BOUND_TYPES = {0: 'cbuffer', 1: 'tbuffer', 2: 'texture', 3: 'sampler', 4: 'uav', 5: 'structbuf'}
DIM = {0: 'unknown', 1: 'buffer', 2: 'tex1d', 3: 'tex2d', 4: 'tex3d', 5: 'texcube',
       6: 'tex1darray', 7: 'tex2darray', 8: 'tex2dms', 9: 'tex2dmsarray', 10: 'texcubeArray'}


def _s(buf, off):
    if off is None or off < 0 or off >= len(buf):
        return None
    e = buf.find(b'\0', off)
    if e < 0:
        e = len(buf)
    return buf[off:e].decode('utf-8', 'replace')


def split_ccaa5566(data):
    """切 NeoX .pipe 容器（魔数 'ccaa5566'）。

    实测布局（与 03_执行/30_分析/ccaa5566调研_20260928/ccaa_lib.py 一致，该实现已与 fxc 交叉验证 11/11）：
      +0x00 char[4] "ccaa5566"
      +0x04 u32 版本 = 2
      +0x08 u32 blob 个数 (1..2)
      +0x0C..0x1F 全零
      +0x20 起，每 blob: u64 阶段标志(0=VS 1=PS 2=CS) + u64 长度 + char[长度] = 标准 DXBC
    返回 [(stage, dxbc_bytes), ...]；非该容器返回 None。
    """
    if data[:4] != bytes.fromhex('ccaa5566'):
        return None
    n = struct.unpack_from('<I', data, 8)[0]
    if n < 1 or n > 8:
        return None
    out, off = [], 0x20
    for _ in range(n):
        if off + 16 > len(data):
            return None
        mark, ln = struct.unpack_from('<QQ', data, off)
        j = off + 16
        if data[j:j + 4] != b'DXBC' or j + ln > len(data):
            return None
        out.append((mark, data[j:j + ln]))
        off = j + ln
    return out


def parse_dxbc(b):
    """返回 dict(chunks=[...], rdef=..., isgn=..., osgn=...)；无 DXBC 头则抛 ValueError"""
    if b[:4] != b'DXBC':
        raise ValueError('不是 DXBC（首 4 字节=%r）' % b[:4])
    total = struct.unpack_from('<I', b, 0x18)[0]
    nch = struct.unpack_from('<I', b, 0x1C)[0]
    if nch > 32 or 0x20 + 4 * nch > len(b):
        raise ValueError('chunk 数异常 %d' % nch)
    chunks = []
    for i in range(nch):
        o = struct.unpack_from('<I', b, 0x20 + 4 * i)[0]
        if o + 8 > len(b):
            continue
        fourcc = b[o:o + 4].decode('latin1')
        sz = struct.unpack_from('<I', b, o + 4)[0]
        if o + 8 + sz > len(b):
            sz = len(b) - o - 8
        chunks.append(dict(fourcc=fourcc, off=o, size=sz))
    out = dict(total_size=total, chunk_count=nch, chunks=chunks)
    for c in chunks:
        if c['fourcc'] == 'RDEF':
            out['rdef'] = parse_rdef(b[c['off'] + 8:c['off'] + 8 + c['size']])
    return out


def _valid_name(buf, off):
    s = _s(buf, off)
    if not s or not s.isascii() or not s[0].isalpha() or len(s) > 64:
        return None
    return s


def _pick_stride(buf, var_off, var_cnt, cb_size):
    """★ 变量记录步长不是固定 24：实测 targetVersion=0x0500 的 blob 是 40 字节
    （24 字节 {nameOff,startOff,size,flags,defOff,typeOff} + 16 字节类型内联）。
    用「多少条能解出合法 ASCII 成员名」自证，避免写死步长后取到半条记录。
    判据非平凡：要求 >=80% 的记录同时满足「名字合法」且「start <= cbuffer 大小」。
    """
    if var_cnt <= 0:
        return None
    best = None
    for stride in range(16, 73, 4):
        good = 0
        for k in range(var_cnt):
            q = var_off + k * stride
            if q + 24 > len(buf):
                break
            nm_off, start = struct.unpack_from('<II', buf, q)
            if _valid_name(buf, nm_off) and start <= cb_size:
                good += 1
        if good >= var_cnt * 0.8:
            if best is None or good > best[1]:
                best = (stride, good)
    return best[0] if best else None


def parse_rdef(buf):
    if len(buf) < 28:
        return dict(error='RDEF 过短 %d' % len(buf))
    cb_cnt, cb_off, br_cnt, br_off = struct.unpack_from('<IIII', buf, 0)
    minor, major, prog = struct.unpack_from('<BBH', buf, 16)
    flags, creator_off = struct.unpack_from('<II', buf, 20)
    r = dict(major=major, minor=minor, program_type='0x%04x' % prog, flags=flags,
             creator=_s(buf, creator_off), cbuffers=[], resources=[])
    for i in range(min(cb_cnt, 64)):
        o = cb_off + 24 * i
        if o + 24 > len(buf):
            break
        name_off, var_cnt, var_off, size, cbflags, cbtype = struct.unpack_from('<IIIIII', buf, o)
        cb = dict(index=i, name=_s(buf, name_off), size=size, var_count=var_cnt, flags=cbflags, vars=[])
        stride = _pick_stride(buf, var_off, var_cnt, size)
        cb['var_stride'] = stride
        for j in range(min(var_cnt, 512)):
            if stride is None:
                break
            vo = var_off + j * stride
            if vo + 24 > len(buf):
                break
            vname, vstart, vsize, vflags, vdef, vtype = struct.unpack_from('<IIIIII', buf, vo)
            # ★ type 字段：本工具对 40 字节记录里内联的 16 字节类型结构**未验证**
            #   （实测 rows/cols 会读出恒等于变量序号的垃圾值），故只留原始偏移，
            #   不对外声称 rows/cols/elements 语义。name/start/size 三项已与 fxc 直出逐条对齐。
            cb['vars'].append(dict(name=_s(buf, vname), start=vstart, size=vsize,
                                   flags=vflags, type_offset=vtype))
        r['cbuffers'].append(cb)
    for i in range(min(br_cnt, 256)):
        o = br_off + 32 * i
        if o + 32 > len(buf):
            break
        nm, ty, rty, dim, sc, bp, bc, fl = struct.unpack_from('<IIIIIIII', buf, o)
        r['resources'].append(dict(name=_s(buf, nm), type=BOUND_TYPES.get(ty, ty), raw_type=ty,
                                   dimension=DIM.get(dim, dim), bind_point=bp, bind_count=bc,
                                   sample_count=sc, flags=fl))
    return r


def find_dxbc(data, start=0, limit=None):
    out, i, n = [], 0, len(data)
    while True:
        j = data.find(b'DXBC', i)
        if j < 0:
            break
        out.append(j)
        i = j + 4
        if limit and len(out) >= limit:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--json')
    ap.add_argument('--scan', action='store_true')
    ap.add_argument('--limit', type=int, default=12)
    ap.add_argument('--dump', help='把挖到的 DXBC 写到该目录')
    a = ap.parse_args()
    if a.scan:
        data = open(a.file, 'rb').read()
        report = []
        ok = 0
        blobs = split_ccaa5566(data)
        if blobs is not None:
            print('%s  %d B  NeoX .pipe(ccaa5566) 容器, blob 数 = %d' % (a.file, len(data), len(blobs)))
            stage_name = {0: 'vertex', 1: 'pixel', 2: 'compute'}
            items = [(i, m, d) for i, (m, d) in enumerate(blobs)]
        else:
            offs = find_dxbc(data)
            print('%s  %d B  非 ccaa5566 容器；按标准 DXBC 头搜到 %d 处 "DXBC"' % (a.file, len(data), len(offs)))
            print('  提示：在 effect_cache.gpk 原始字节里这样搜到的 "DXBC" **解析不出标准头**'
                  '（chunkCount 为垃圾值，已实测反证）⇒ 该容器要先按 gpk 行切出 .ccaa5566 子容器。')
            items = []
            for k, o in enumerate(offs[:a.limit]):
                if o + 0x20 > len(data):
                    continue
                ts = struct.unpack_from('<I', data, o + 0x18)[0]
                # ★ 护栏：非标准容器时 total_size 会是垃圾值（实测见过 ~7.3 亿），
                #   直接切片会写出几百 MB~GB 的假 blob（本轮踩过：16 个 ~730MB ≈ 11GB）。
                if ts < 0x40 or ts > 64 << 20 or o + ts > len(data):
                    print('  #%-3d @0x%-9x 疑似非标准 DXBC（total_size=%d 不合理），跳过' % (k, o, ts))
                    continue
                items.append((k, o, data[o:o + ts]))
        stage_name = {0: 'vertex', 1: 'pixel', 2: 'compute'}
        for k, mark, blob in items[:a.limit]:
            try:
                d = parse_dxbc(blob)
                rd = d.get('rdef') or {}
                cls = [c['fourcc'] for c in d['chunks']]
                st = stage_name.get(mark, mark)
                print('  #%-3d %-8s size=%-7d chunks=%-30s cb=%d res=%d  creator=%s' %
                      (k, st, d['total_size'], ','.join(cls), len(rd.get('cbuffers', [])),
                       len(rd.get('resources', [])), rd.get('creator')))
                for cb in rd.get('cbuffers', []):
                    print('        cb%-2d %-24s size=%-6d vars=%d' % (cb['index'], cb['name'], cb['size'], cb['var_count']))
                for rs in rd.get('resources', []):
                    if rs['type'] != 'cbuffer':
                        print('        %-8s reg=%-3d %s' % (rs['type'], rs['bind_point'], rs['name']))
                report.append(dict(blob_index=k, stage=st, **d))
                ok += 1
            except Exception as e:
                print('  #%-3d 解析失败 %r' % (k, e))
        if a.dump:
            os.makedirs(a.dump, exist_ok=True)
            for k, mark, blob in items[:a.limit]:
                open(os.path.join(a.dump, 'shader_%03d.dxbc' % k), 'wb').write(blob)
            print('→ 已 dump %d 个到 %s' % (len(items[:a.limit]), a.dump))
        if a.json:
            os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
            json.dump(report, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('→', a.json)
        return 0
    b = open(a.file, 'rb').read()
    d = parse_dxbc(b)
    print('chunks:', [(c['fourcc'], c['size']) for c in d['chunks']])
    rd = d.get('rdef')
    if not rd:
        print('无 RDEF'); return 1
    print('creator=%s  program_type=%s' % (rd['creator'], rd['program_type']))
    for cb in rd['cbuffers']:
        print('  cbuffer[%d] %-22s size=%-5d vars=%d (stride=%s)' %
              (cb['index'], cb['name'], cb['size'], cb['var_count'], cb.get('var_stride')))
        for v in cb['vars']:
            print('      +0x%03x %-30s size=%d' % (v['start'], v['name'], v['size']))
    for rs in rd['resources']:
        print('  %-8s reg=%-3d %s' % (rs['type'], rs['bind_point'], rs['name']))
    if a.json:
        json.dump(d, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
