#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""neox_marshal.py —— NeoX（网易自研 Python 3.14 方言）marshal 解码器。

用法：
  python neox_marshal.py <file.py>                  # 解出模块结构与数据字面量
  python neox_marshal.py <file.py> --dump out.json  # 结果写 JSON
  python neox_marshal.py <file.py> --tables         # 只列名字表/对象表
  python neox_marshal.py <file.py> --entries N      # 打印前 N 个条目（默认 5）
  python neox_marshal.py <file.py> --dis            # 反汇编模块码段

结构（2026-10-03 实测；与标准 CPython 3.14 的 functools.py 对拍验证）：
  文件头        : 21 字节（`73 00 00 00` + 计数/保留区）
  code 对象     : tag 0xFB + u32 长度 + 魔数 `80 00` + co_code
  bytes 对象    : tag 0x7B + u32 长度 + 原始字节        ← 数据字面量就是它
  表(名字/常量) : `2E <u8 n>` + n 项（项=字符串/`5A`·`BE`·`3E` u32/`3C` u8/
                  `7A` i32/嵌套 `2E`）
  字符串        : `D3 <u8 len>`（len==0xFF 时后跟 u32 长度）
  None          : 0x4E
  数据字面量编码 : NeoX bindict 值编解码（tag 低半字节=类型，高半字节=宽度/标志）
                  0x12 float32 · 0x22 float64 · 0x07 混合列表 · 0x27 同型列表
                  (随后 1 字节公共类型) · 0x05 共享引用 · 0x0b 缓冲偏移引用
                  0x03 bool · 0x4e None · 0x01 LEB128 整数 · 0x96 行标记
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r'E:\la拆包项目\01_工具\工具库\00_共享核心')))
try:
    from toolkit_core import script_decode as sd
except Exception:                                          # pragma: no cover
    sd = None

HEADER = 21
CODE_TAG = 0xFB
BYTES_TAG = 0x7B
STR_TAGS = (0xD3, 0xF3, 0xDA, 0xFA, 0x79, 0x74, 0x75, 0x61, 0x41)
INT_U32 = (0x5A, 0xBE, 0x3E)
INT_I32 = (0x7A,)
INT_U8 = (0x3C,)
NONE_TAG = 0x4E
TUPLE_U8 = 0x2E

RESYNC = [bytes.fromhex(h) for h in
          ('070312', '070322', '070a22', '070a12', '272203', '271e03',
           '967e2a04', '0b05', '0502')]

# 表结构前导块（全文件唯一）：`0a 03 00 00 06 07 08 09 04 01 0c` 起，
# 描述字段类型/槽位；其后才是真正的条目。
PROLOGUE_SIG = bytes.fromhex('0a0300000607080904010c')


# ───────────────────────── marshal 层 ─────────────────────────
def read_str(b, p):
    if p >= len(b) or b[p] not in STR_TAGS:
        return None, p
    ln = b[p + 1]; st = p + 2
    if ln == 0xFF:
        if p + 6 > len(b):
            return None, p
        ln = struct.unpack_from('<I', b, p + 2)[0]; st = p + 6
    if not (0 <= ln <= 1 << 20) or st + ln > len(b):
        return None, p
    return b[st:st + ln].decode('utf-8', 'replace'), st + ln


def read_value(b, p):
    """marshal 层单值：字符串 / 整数 / None / 元组。"""
    if p >= len(b):
        raise ValueError('越界')
    t = b[p]
    if t in STR_TAGS:
        s, q = read_str(b, p)
        if s is None:
            raise ValueError('字符串标签 %02x 解析失败' % t)
        return s, q
    if t in INT_U32:
        return struct.unpack_from('<I', b, p + 1)[0], p + 5
    if t in INT_I32:
        return struct.unpack_from('<i', b, p + 1)[0], p + 5
    if t in INT_U8:
        return b[p + 1], p + 2
    if t == NONE_TAG or t == 0x78:
        return None, p + 1
    if t == BYTES_TAG:                                # bytes（u32 长）
        ln = struct.unpack_from('<I', b, p + 1)[0]
        return {'__bytes__': ln}, p + 5 + ln
    if t == CODE_TAG:                                 # co_code/bytes（u32 长；有 80 00 魔数则含魔数）
        ln = struct.unpack_from('<I', b, p + 1)[0]
        if b[p + 5:p + 7] == b'\x80\x00':
            return {'__code__': ln}, p + 7 + ln
        return {'__bytes__': ln}, p + 5 + ln
    if t in (TUPLE_U8, 0xAE):                         # SMALL_TUPLE（u8 元素数）
        n = b[p + 1]; items = []; q = p + 2
        for _ in range(n):
            v, q = read_value(b, q)
            items.append(v)
        return items, q
    raise ValueError('未知 marshal 标签 0x%02x @%d' % (t, p))


def scan_objects(buf):
    i, n, out = 0, len(buf), []
    while i < n - 7:
        t = buf[i]
        if t == CODE_TAG and buf[i + 5:i + 7] == b'\x80\x00':
            ln = struct.unpack_from('<I', buf, i + 1)[0]
            if 0 < ln <= n - i - 7:
                out.append(('code', i, buf[i + 7:i + 7 + ln])); i += 7 + ln; continue
        if t == BYTES_TAG:
            ln = struct.unpack_from('<I', buf, i + 1)[0]
            if ln == 0 or ln <= n - i - 5:
                out.append(('bytes', i, buf[i + 5:i + 5 + ln])); i += 5 + ln; continue
        i += 1
    return out


# ─────────────────── bindict 值编解码（数据字面量） ───────────────────
class BindictError(Exception):
    pass


def _uleb(b, p):
    v = 0; sh = 0
    while True:
        if p >= len(b):
            raise BindictError('varint 越界')
        c = b[p]; p += 1
        v |= (c & 0x7F) << sh
        if not (c & 0x80):
            return v, p
        sh += 7
        if sh > 63:
            raise BindictError('varint 过长')


class Bindict:
    """NeoX 数据字面量值编解码。tag 低半字节=类型，高半字节=宽度/标志。"""

    def __init__(self, buf, base=0):
        self.b = buf
        self.base = base
        self.shared = []

    def value(self, p, tag=None, depth=0):
        if depth > 64:
            raise BindictError('嵌套过深')
        if tag is None:
            tag = self.b[p]; p += 1
        t, w = tag & 0x0F, tag & 0xF0

        if t == 0:                                    # 小整数（值内联于高半字节）
            return w, p
        if t == 1:                                    # LEB128 整数
            v, p = _uleb(self.b, p)
            return ((-(v & 1) ^ (v >> 1)) if w == 0x10 else v), p
        if t == 2:                                    # 浮点
            if w == 0x10:
                return struct.unpack_from('<f', self.b, p)[0], p + 4
            if w in (0x20, 0x00):
                return struct.unpack_from('<d', self.b, p)[0], p + 8
            raise BindictError('浮点宽度 0x%02x' % tag)
        if t == 3:                                    # 布尔
            return bool(self.b[p]), p + 1
        if t == 4:                                    # None
            return None, p
        if t == 5:                                    # 共享节点引用
            i, p = _uleb(self.b, p)
            if i >= len(self.shared):
                raise BindictError('共享引用越界 %d' % i)
            return self.shared[i], p
        if self.b[p - 1:p + 2] == b'\x96\x7e\x2a':    # 行标记：`96 7e 2a <kind> <a> <b> <f64>`
            kind = self.b[p + 2]
            a, q = _uleb(self.b, p + 3)
            b_, q = _uleb(self.b, q)
            val = struct.unpack_from('<d', self.b, q)[0]
            return {'__row__': {'kind': kind, 'a': a, 'b': b_, 'value': val}}, q + 8
        if t == 6:                                    # 位宽打包数组 / 行
            bits, p = _uleb(self.b, p)
            cnt, p = _uleb(self.b, p)
            nb = (bits * cnt + 7) // 8 if bits and cnt else 0
            if nb > 8192 or cnt > 1 << 20:
                raise BindictError('位宽打包数组过大（疑似解偏移）')
            raw = self.b[p:p + nb]; p += nb
            vals = []
            if bits:
                acc = int.from_bytes(raw, 'little'); m = (1 << bits) - 1
                vals = [(acc >> (k * bits)) & m for k in range(cnt)]
            node = {'__bitpack__': bits, 'count': cnt, 'values': vals[:24]}
            self.shared.append(node)
            return node, p
        if t == 11:                                   # 缓冲区偏移引用
            off, p = _uleb(self.b, p)
            node, _ = self.value(self.base + off, depth=depth + 1)
            return node, p
        if tag == 0x0A and self.b[p] == 0x03:         # `0a 03 <kind>` 记录/结构标记
            kind = self.b[p + 1]
            return {'__marker__': kind}, p + 2
        if t in (7, 8, 9, 10, 12, 13, 14, 15):        # 列表 / 容器
            if tag & 0x40:                            # 省略 → 共享表占位
                c, p = _uleb(self.b, p)
                node = {'__omitted__': c}; self.shared.append(node); return node, p
            common = None
            if tag & 0x20:                            # 同型列表：1 字节公共类型
                common = self.b[p]; p += 1
            cnt, p = _uleb(self.b, p)
            items = []
            self.shared.append(items)
            for _ in range(cnt):
                if common is None:
                    sub = self.b[p]; p += 1
                else:
                    sub = common
                v, p = self.value(p, sub, depth + 1)
                items.append(v)
            return items, p
        raise BindictError('未知类型 %d (tag=0x%02x) @%d' % (t, tag, p - 1))


def decode_payload(payload, start=56, limit=0, resync=True):
    """把数据字面量解成条目列表；解不动时跳到下一个重同步锚。
    返回 (entries, offsets, consumed, skipped)。"""
    bd = Bindict(payload, base=start)
    entries, offsets, p, skipped = [], [], start, []
    n = len(payload)
    while p < n:
        if limit and len(entries) >= limit:
            break
        if payload[p:p + len(PROLOGUE_SIG)] == PROLOGUE_SIG:
            # 表结构前导块：记下原始字节，跳到第一个真实条目锚
            # （条目模板：同型/混合向量列表）
            nxt = None
            for hint in (b'\x07\x03\x12', b'\x07\x03\x22', b'\x27\x22\x03',
                         b'\x07\x0a\x22', b'\x27\x12\x0a', b'\x27\x1e\x03'):
                k = payload.find(hint, p + len(PROLOGUE_SIG))
                if k != -1 and k > p and (nxt is None or k < nxt):
                    nxt = k
            end = nxt if nxt is not None else n
            entries.append({'__table_schema__': True, 'offset': p,
                            'hex': payload[p:end].hex()})
            offsets.append(p)
            p = end
            continue
        try:
            v, q = bd.value(p)
            if q <= p:
                raise BindictError('no progress')
        except Exception as e:
            if not resync:
                entries.append({'__error__': str(e), 'offset': p}); offsets.append(p); break
            nxt = None
            for hint in RESYNC:
                k = payload.find(hint, p + 1)
                if k != -1 and k > p and (nxt is None or k < nxt):
                    nxt = k
            if nxt is None or nxt <= p:
                skipped.append({'offset': p, 'length': n - p, 'reason': str(e)})
                break
            skipped.append({'offset': p, 'length': nxt - p, 'reason': str(e)})
            p = nxt
            continue
        entries.append(v); offsets.append(p); p = q
    return entries, offsets, p, skipped


# ───────────────────────── 模块解析 ─────────────────────────
def parse_module(buf):
    info = {'size': len(buf), 'objects': []}
    if buf[:4] == b'\x73\x00\x00\x00':
        info['magic'] = '0x73'
    info['header_hex'] = buf[:HEADER].hex()
    for kind, off, body in scan_objects(buf):
        info['objects'].append({'kind': kind, 'offset': off, 'length': len(body)})
    best = None
    n = len(buf)
    for start in range(HEADER, n - 2):
        if buf[start] != TUPLE_U8:
            continue
        cnt = buf[start + 1]
        if not (1 <= cnt <= 255):
            continue
        try:
            items = []; q = start + 2
            for _ in range(cnt):
                v, q = read_value(buf, q)
                items.append(v)
            if all(isinstance(x, str) for x in items) and (best is None or cnt > best[1]):
                best = (start, cnt, items, q)
        except Exception:
            continue
    if best:
        info['names_table'] = {'offset': best[0], 'count': best[1], 'names': best[2]}
        q = best[3]; meta = []
        while q < n - 1:
            try:
                v, q2 = read_value(buf, q)
            except Exception:
                break
            if q2 <= q:
                break
            meta.append(v); q = q2
        strs = [x for x in meta if isinstance(x, str)]
        nums = [x for x in meta if isinstance(x, int)]
        if strs:
            info['filename'] = strs[0]
        if len(strs) > 1:
            info['qualname'] = strs[1]
        if nums:
            info['trailing_ints'] = nums[:8]
    return info


def main():
    ap = argparse.ArgumentParser(description='NeoX marshal 解码器')
    ap.add_argument('module')
    ap.add_argument('--dump', help='结果写 JSON')
    ap.add_argument('--tables', action='store_true', help='只列名字表/对象表')
    ap.add_argument('--entries', type=int, default=5, help='打印前 N 个条目')
    ap.add_argument('--start', type=int, default=56, help='数据体解码起点（默认 56）')
    ap.add_argument('--no-resync', action='store_true', help='不做重同步')
    ap.add_argument('--dis', action='store_true', help='反汇编模块码段')
    a = ap.parse_args()

    buf = Path(a.module).read_bytes()
    info = parse_module(buf)
    print('★ %s ｜ %d B ｜ code %d ｜ bytes %d'
          % (Path(a.module).name, info['size'],
             sum(1 for o in info['objects'] if o['kind'] == 'code'),
             sum(1 for o in info['objects'] if o['kind'] == 'bytes')))

    if a.tables:
        nt = info.get('names_table')
        if nt:
            print('── 名字表 @%d（%d 项）' % (nt['offset'], nt['count']))
            for i, s in enumerate(nt['names']):
                print('   [%2d] %s' % (i, s))
        print('── filename = %r ｜ qualname = %r ｜ trailing_ints = %s'
              % (info.get('filename'), info.get('qualname'), info.get('trailing_ints')))
        for o in info['objects']:
            print('   对象 %-5s @%-8d len=%d' % (o['kind'], o['offset'], o['length']))
        return

    if a.dis and sd is not None:
        for o in info['objects']:
            if o['kind'] != 'code':
                continue
            body = buf[o['offset'] + 7:o['offset'] + 7 + o['length']]
            print('══ 码段 @%d（%d B）' % (o['offset'], o['length']))
            for ins in sd.dis_code(body):
                print('   %5d  %-32s %s' % (ins.off, ins.name, ins.arg))
        return

    blobs = [o for o in info['objects'] if o['kind'] == 'bytes']
    if not blobs:
        print('（无 bytes 数据体）'); return
    # 数据体 = 能解出最多条目的 bytes 对象（同尺寸取大者）
    cand = sorted(blobs, key=lambda x: -x['length'])[:12]
    best_pick = None
    for o in cand:
        b = buf[o['offset'] + 5:o['offset'] + 5 + o['length']]
        if len(b) < 64:
            continue
        ent, offs, cons, skip = decode_payload(b, a.start, 40, True)
        score = (sum(1 for e in ent if isinstance(e, list)), len(ent), o['length'])
        if best_pick is None or score > best_pick[0]:
            best_pick = (score, o, b)
    big, payload = best_pick[1], best_pick[2]
    print('── 数据体 @%d ｜ %d B' % (big['offset'], len(payload)))

    entries, offsets, consumed, skipped = decode_payload(payload, a.start, 0, not a.no_resync)
    print('── 顶层：list ｜ 条目 %d ｜ 消费 %d/%d B ｜ 跳过 %d 段'
          % (len(entries), consumed, len(payload), len(skipped)))
    for i, e in enumerate(entries[:a.entries]):
        off = offsets[i] if i < len(offsets) else -1
        if isinstance(e, list):
            print('   条目 %-3d @%-7d = list[%d] = %s' % (i, off, len(e), str(e)[:200]))
        else:
            print('   条目 %-3d @%-7d = %r' % (i, off, e))

    result = {'file': str(a.module), 'size': info['size'],
              'header_hex': info['header_hex'], 'objects': info['objects'],
              'names': info.get('names_table', {}).get('names'),
              'filename': info.get('filename'), 'qualname': info.get('qualname'),
              'payload': {'offset': big['offset'], 'size': len(payload),
                          'top_level': 'list', 'entry_count': len(entries),
                          'consumed': consumed, 'skipped': skipped,
                          'entry_offsets': offsets, 'entries': entries}}
    if a.dump:
        Path(a.dump).write_text(json.dumps(result, ensure_ascii=False, indent=1,
                                           default=str), encoding='utf-8')
        print('写出 %s' % a.dump)


if __name__ == '__main__':
    main()
