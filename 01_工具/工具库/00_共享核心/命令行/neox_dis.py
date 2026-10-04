#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""neox_dis.py —— NeoX 客户端脚本反汇编器（带【名字表/常量表索引解析】）

用法：
  python neox_dis.py <file.py> --tables                 列出所有名字表/常量表
  python neox_dis.py <file.py> --blob <off>             反汇编指定码段（带解析 ✓）
  python neox_dis.py <file.py> --grep <kw> [--context 6] 按关键词搜解析后的指令
  python neox_dis.py <file.py> --dump <out.txt>         全量反汇编（带解析）到文件

★ 结构（实测 2026-10-03 ✓）：
  · 名字表：连续的 `D3 <len1> <str>`（len1==0xFF 时后跟 4 字节长度）
    例：D3 08 "ui_scene" D3 10 "cur_active_items" D3 0D "scene_handler" …
  · 常量表：`2E <count>` 后跟 count 项（项 = D3/F3/DA/FA 短串 或 BE+u32 整数）
  · 码段：tag 0xFB 或 0x7B，其后 4 字节长度，再 2 字节魔数 80 00，再 payload
  · 关联规则：表按偏移排列，某条指令的索引表取【其码段之前最近的那张对应表】
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r'E:\la拆包项目\01_工具\工具库\00_共享核心')))
try:
    import toolkit_core.script_decode as sd
except Exception as e:                                    # 允许独立运行
    print('需要 toolkit_core.script_decode：%s' % e)
    raise

NAME_TAGS = (0xD3, 0xF3, 0xDA, 0xFA)                      # 字符串 marshal 标签
CONST_TAG = 0xBE                                          # 整数 marshal 标签


def read_str(buf, j, hi):
    """读一个 marshal 字符串，返回 (str, 新偏移) 或 (None, j)"""
    t = buf[j]
    if t not in NAME_TAGS:
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
    for enc in ('utf-8', 'latin1'):
        try:
            return raw.decode(enc), st + ln
        except Exception:
            pass
    return raw.decode('latin1', 'replace'), st + ln


def scan_name_tables(buf, min_run=4):
    """扫【连续 D3<len><str>】区块 → [(offset, [names])]
    ★ 名字表没有计数头 ⇒ 靠「连续串」识别；min_run 控制最短长度 ✓
    """
    out = []
    n = len(buf)
    i = 0
    while i < n - 3:
        if buf[i] in NAME_TAGS:
            names = []
            j = i
            while j < n - 3:
                s, nj = read_str(buf, j, n)
                if s is None or nj == j:
                    break
                names.append(s)
                j = nj
            if len(names) >= min_run:
                out.append((i, names))
                i = j
                continue
        i += 1
    return out


def scan_const_tables(buf):
    """`2E <count>` + count 项 → [(offset, count, [items])]（与现有解码器一致 ✓）"""
    return sd.const_tables(buf)


def blobs(buf):
    return [(o, b) for o, b in sd.blobs(buf) if isinstance(b, (bytes, bytearray))]


def pick(table_list, off):
    """取 offset 之前最近的一张表（表在码段之前 ✓）"""
    pre = [t for t in table_list if t[0] < off]
    return pre[-1] if pre else None


def dis_resolved(buf, seg_off, body, nts, cts):
    """反汇编 + 名字/常量索引解析"""
    nt = pick(nts, seg_off)
    ct = pick(cts, seg_off)
    names = nt[1] if nt else []
    consts = ct[2] if ct else []
    out = []
    for ins in sd.dis_code(bytes(body)):
        val = None
        src = None
        if ins.name in ('LOAD_CONST',):
            if 0 <= ins.arg < len(consts):
                val, src = consts[ins.arg], 'const'
            elif 0 <= ins.arg < len(names):
                val, src = names[ins.arg], 'name'
        elif ins.name in ('STORE_ATTR', 'LOAD_ATTR', 'STORE_NAME', 'LOAD_NAME',
                          'LOAD_GLOBAL', 'IMPORT_NAME', 'IMPORT_FROM'):
            if 0 <= ins.arg < len(names):
                val, src = names[ins.arg], 'name'
        out.append((ins, val, src))
    return out, (nt[0] if nt else None, len(names)), (ct[0] if ct else None, len(consts))


def main():
    ap = argparse.ArgumentParser(description='NeoX 客户端脚本反汇编器（带索引解析）')
    ap.add_argument('module')
    ap.add_argument('--tables', action='store_true', help='列出名字表/常量表')
    ap.add_argument('--blob', type=int, help='只反汇编该偏移的码段')
    ap.add_argument('--grep', help='按关键词搜（在解析后的指令上）')
    ap.add_argument('--context', type=int, default=4, help='grep 前后行数（默认 4）')
    ap.add_argument('--dump', help='全量写出到文件')
    ap.add_argument('--min-run', type=int, default=4, help='名字表最短串数（默认 4）')
    a = ap.parse_args()

    buf = Path(a.module).read_bytes()
    nts = scan_name_tables(buf, a.min_run)
    cts = scan_const_tables(buf)
    bs = blobs(buf)
    print('★ %s ｜ %d B ｜ 码段 %d ｜ 名字表 %d ｜ 常量表 %d'
          % (Path(a.module).name, len(buf), len(bs), len(nts), len(cts)))

    if a.tables:
        print('\n── 名字表 ──')
        for off, names in nts:
            print('  @%-8d %3d 串  %s' % (off, len(names), str(names[:12])[:150]))
        print('\n── 常量表 ──')
        for off, cnt, items in cts:
            print('  @%-8d %3d 项  %s' % (off, cnt, str(items[:10])[:150]))
        return

    dump = open(a.dump, 'w', encoding='utf-8') if a.dump else None
    lines = []

    def emit(s):
        lines.append(s)
        if dump:
            dump.write(s + '\n')

    for off, body in bs:
        if a.blob is not None and off != a.blob:
            continue
        ins_list, (noff, ncnt), (coff, ccnt) = dis_resolved(buf, off, body, nts, cts)
        emit('\n══ 码段 @%d（%d B）· 名字表@%s(%d) · 常量表@%s(%d) ══'
             % (off, len(body), noff, ncnt, coff, ccnt))
        for ins, val, src in ins_list:
            if val is not None:
                emit('  %6d  %-28s %-6s → %r' % (ins.off, ins.name, ins.arg, val))
            else:
                emit('  %6d  %-28s %s' % (ins.off, ins.name, ins.arg))

    if a.grep:
        kw = a.grep.lower()
        idxs = [i for i, l in enumerate(lines) if kw in l.lower()]
        print('\n══ grep %r：命中 %d 行 ══' % (a.grep, len(idxs)))
        shown = set()
        for i in idxs:
            for j in range(max(0, i - a.context), min(len(lines), i + a.context + 1)):
                if j in shown:
                    continue
                shown.add(j)
                print('   %s%s' % ('>>' if j == i else '  ', lines[j][:160]))
            print('   ──')
    else:
        for l in lines:
            print(l)
    if dump:
        dump.close()
        print('\n写出 %s' % a.dump)


if __name__ == '__main__':
    main()
