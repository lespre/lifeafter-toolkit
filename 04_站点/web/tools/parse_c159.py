#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""解析 .c159 文档（明日之后 NeoX 资源描述符）为可读 JSON。

格式（2026-09-13 实证）：
  +0   magic c1 59 41 0d
  +4   u32  文件总长
  +8   u32  0
  +12  字段名表：连续 <u8 名长><ASCII 名>  '\x00' ... 直到某个字节不是合法"名长"
       例：05 "NeoX" 00 | 04 "Sub0" 00 | 09 "AnimAccumEnable" 00 ...
  然后  数据区：带 tag 的值流
       tag 0x03 -> 后跟 <u8 子tag=01> + ASCII 字符串（如 "(0.33,1.26,2.47)"）
       tag 0x06 -> 后跟 <u8> 计数 + <u8 03> + 每项 <u32 0> + float32×3
       tag 0x08 -> 后跟 <u8 01> + "true"/"false"
       tag 0x07 -> 后跟 <u8 01> + ASCII 名（子网格名等）
       tag 0x01/0x02/0x04/0x05 -> 结构标记（保留原样）
  值按字段顺序与字段名一一对应（位置解码见下）。

用法: python tools/parse_c159.py <file.c159> [--json out.json]
"""
from __future__ import annotations
import argparse, json, pathlib, struct, sys


def parse_names(d: bytes, off: int = 12):
    """字段名表 = 连续 <tag 可选><ASCII 名>\\x00；tag 值如 0x05/0x09。
    稳健做法：在头部区（前 512B）抓「首字母大写的标识符」，按出现顺序返回。"""
    import re
    head = d[off:off + 512]
    names = []
    for mm in re.finditer(rb'[A-Za-z][A-Za-z0-9_]{2,40}', head):
        s = mm.group(0)
        # 名字表在数据区之前；遇到 'true'/'(0.' 这类值就停
        if s in (b'true', b'false') or b'.' in s:
            break
        names.append(s.decode('latin1'))
    # 数据区起点 = 最后一个名字的 NUL 之后
    last = names[-1].encode('latin1') if names else b''
    idx = d.find(last + b'\x00', off) if last else -1
    end = idx + len(last) + 1 if idx >= 0 else off
    return names, end


def walk_values(d: bytes, off: int):
    """尽力解码值流；未知 tag 原样跳过 1 字节。"""
    vals, i = [], off
    while i < len(d):
        tag = d[i]
        try:
            if tag == 0x03 and i + 2 < len(d):
                j = d.find(b'\x00', i + 2)
                if j < 0:
                    break
                s = d[i + 2:j]
                if all(32 <= c < 127 for c in s):
                    vals.append(('str', s.decode('latin1'))); i = j + 1; continue
            if tag == 0x06 and i + 2 < len(d):
                cnt = d[i + 1]
                if cnt <= 8 and d[i + 2] == 0x03:
                    p = i + 3
                    vs = []
                    for _ in range(cnt):
                        if p + 4 + 12 > len(d):
                            break
                        vs.append(struct.unpack_from('<fff', d, p + 4))
                        p += 4 + 12
                    if vs:
                        vals.append(('vec3[]', [[round(v, 5) for v in t] for t in vs])); i = p; continue
            if tag == 0x07 and i + 2 < len(d):
                j = d.find(b'\x00', i + 2)
                if j > 0:
                    s = d[i + 2:j]
                    if all(32 <= c < 127 for c in s):
                        vals.append(('name', s.decode('latin1'))); i = j + 1; continue
            if tag == 0x08 and i + 2 < len(d):
                j = d.find(b'\x00', i + 2)
                if j > 0:
                    s = d[i + 2:j]
                    if s in (b'true', b'false'):
                        vals.append(('bool', s.decode())); i = j + 1; continue
        except struct.error:
            break
        vals.append(('raw', f'0x{tag:02x}'))
        i += 1
    return vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--json')
    a = ap.parse_args()
    p = pathlib.Path(a.file)
    d = p.read_bytes()
    if d[:4] != bytes([0xC1, 0x59, 0x41, 0x0D]):
        print('!! magic 不是 c1 59 41 0d:', d[:4].hex(' ')); sys.exit(2)
    size = struct.unpack_from('<I', d, 4)[0]
    names, off = parse_names(d)
    vals = walk_values(d, off)
    print(f'文件 {p.name}  {len(d)}B  声明长度={size}')
    print(f'字段名 {len(names)} 个: {names}')
    print(f'数据区 @{off}  解出值 {len(vals)} 个:')
    for k, (t, v) in enumerate(vals):
        nm = names[k] if k < len(names) else '?'
        print(f'   [{k:>2}] {nm:<20} {t:<8} {v}')
    if a.json:
        o = pathlib.Path(a.json); o.parent.mkdir(parents=True, exist_ok=True)
        o.write_text(json.dumps({'file': p.name, 'size': len(d), 'declared': size,
                                 'names': names, 'values': [{'type': t, 'value': v} for t, v in vals]},
                                ensure_ascii=False, indent=2), encoding='utf-8')
        print('→', o)


if __name__ == '__main__':
    main()
