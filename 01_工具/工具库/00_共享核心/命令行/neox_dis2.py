#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""neox_dis2.py —— NeoX py314 字节码【带常量解析】的反汇编 CLI
（基于 toolkit_core.script_decode 的结构化读取器）

用法
  python neox_dis2.py <file.py>                 总览：函数清单 + 每个函数的名字/常量表 + 字段赋值
  python neox_dis2.py <file.py> --funcs         只要函数清单（名字 + co_code 起止偏移）
  python neox_dis2.py <file.py> --consts        只要常量/名字池的字符串值
  python neox_dis2.py <file.py> --names         只要名字表（co_names / co_varnames）
  python neox_dis2.py <file.py> --fields        只要 LOAD_CONST↔STORE_ATTR 字段赋值配对
  python neox_dis2.py <file.py> --dis 3         反汇编第 3 个函数（带解析）；--dis all 全部
  python neox_dis2.py <file.py> --grep kb       在解析后的反汇编里按关键词搜
  python neox_dis2.py <file.py> --dump out.txt  全量写出到文件（同时打印摘要）
  python neox_dis2.py <file.py> --scan          强制用特征扫描路径列函数（递归解析失步时）

★ 已实测的结构（详见 toolkit_core/script_decode.py 文件头）：
  code object = 73 | 5×u32 | co_code(7b|fb+u32 len) | co_consts | co_names |
                co_localsplusnames | co_localspluskinds | filename | name | qualname |
                firstlineno(裸 u32) | linetable | exceptiontable
  验证：解析终点与文件长度逐字节吻合才算「结构解通」。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r'E:\la拆包项目\01_工具\工具库\00_共享核心')))
try:
    from toolkit_core import script_decode as sd
except Exception as e:                                        # pragma: no cover
    print('需要 toolkit_core.script_decode：%s' % e)
    raise

OUT: list[str] = []


def emit(s: str = ''):
    OUT.append(s)
    print(s)


def human(n: int) -> str:
    return '{:,}'.format(n)


# ── 报告块 ───────────────────────────────────────────────────────────────────
def report_overview(path, buf, root, codes, end, reader, used_scan=False):
    ok = (end == len(buf))
    emit('★ %s ｜ %s B ｜ 解析终点 %d %s' % (Path(path).name, human(len(buf)), end,
                                            '✓ 与文件长度逐字节吻合' if ok else '✗ 未到文件末尾'))
    if used_scan:
        emit('  ⚠ 递归结构解析未走通，函数清单来自【特征扫描】路径（见下方告警）')
    if root is not None:
        emit('  顶层 code：name=%s  qualname=%s  firstlineno=%d' %
             (_q(root.name_str), _q(root.qualname_str), root.firstlineno))
        emit('  文件名：%s' % _q(root.filename_str))
    emit('  code 对象 %d 个 ｜ 引用表 %d 项 ｜ 结构告警 %d 条 ｜ 引用类型失配 %d 条' %
         (len(codes), len(reader.refs), len(reader.anomalies), len(reader.ref_mismatch)))
    for a in reader.anomalies[:5]:
        emit('    ⚠ %s' % a)
    if len(reader.anomalies) > 5:
        emit('    …（其余 %d 条同类告警略）' % (len(reader.anomalies) - 5))
    for row in reader.ref_mismatch[:3]:
        parts = list(row) + ['?'] * (4 - len(row))
        emit('    ⚠ 引用类型失配：@%s 引用 #%s → %s（已按未解析显示）'
             % (parts[0], parts[1], parts[2]))
    if len(reader.ref_mismatch) > 3:
        emit('    …（其余 %d 条引用失配略）' % (len(reader.ref_mismatch) - 3))


def _q(v):
    return repr(v) if v is not None else '?'


def report_funcs(codes, argcounts=True):
    emit()
    emit('── 函数清单（code objects） ──')
    emit('  %-4s %-42s %-17s %-17s %5s %6s %5s %7s' %
         ('#', '名称 (qualname)', 'code 容器起止', 'co_code(payload)', '长度B', '行号', '参数', '名字/常量'))
    for i, c in enumerate(codes):
        nm = c.display_name
        if c.depth == 0:
            nm += ' [模块体]'
        elif c.parent is not None:
            nm += ' ← %s' % (c.parent.display_name if c.depth > 1 else '模块体')
        emit('  %-4d %-42s %-17s %-17s %5d %6d %5d %7s' %
             (i, nm[:42],
              '%d..%d' % (c.holder_off, c.holder_off + c.holder_len),
              '%d..%d' % (c.code_off, c.code_off + c.code_len),
              c.code_len, c.firstlineno, c.argcount,
              '%d/%d' % (len(c.names), len(c.consts))))
    emit('  （code 容器 = <73 + 5×u32 + tag + u32 len> 整体；co_code(payload) = 真正的字节码区间，'
         '即容器起点+5；名字/常量 = co_names/co_consts 条目数）')


def report_tables(codes, which=('names', 'consts', 'vars')):
    for i, c in enumerate(codes):
        emit()
        emit('── [%d] %s ｜ co_code %d..%d（%d B）｜ firstlineno=%d ｜ stacksize=%d ｜ flags=0x%x ──'
             % (i, c.display_name, c.code_off, c.code_off + c.code_len, c.code_len,
                c.firstlineno, c.stacksize, c.flags))
        emit('   文件：%s' % _q(c.filename_str))
        if c.parent is not None:
            emit('   所属：%s' % c.parent.display_name)
        if 'names' in which:
            emit('   ── co_names（%d）—— 索引 → 实际值 ──' % len(c.names))
            for j, v in enumerate(c.names):
                emit('     [%3d] %s' % (j, v.show(120)))
        if 'consts' in which:
            emit('   ── co_consts（%d）—— 索引 → 实际值 ──' % len(c.consts))
            for j, v in enumerate(c.consts):
                extra = ''
                if v.kind == 'code' and v.code is not None:
                    extra = '   （函数体：%s）' % v.code.display_name
                emit('     [%3d] %s%s' % (j, v.show(160), extra))
        if 'vars' in which:
            emit('   ── co_varnames/localsplusnames（%d，kinds %d 字节）──'
                 % (len(c.localsplusnames), c.nlocals))
            for j, v in enumerate(c.localsplusnames):
                emit('     [%3d] %s' % (j, v.show(80)))
        fa = c.field_assignments(strict=True)
        fl = c.field_assignments(strict=False)
        if fa or fl:
            seen = {(x[0], x[2]) for x in fa}
            emit('   ── ★ LOAD_CONST ↔ STORE_ATTR/STORE_NAME 字段赋值'
                 '（声明块模式 %d 条 ／ 宽松模式共 %d 条）──' % (len(fa), len(fl)))
            for fld, val, off, _m in fa:
                emit('     [声明块] %-32s = %-46s (STORE @%d)' % (fld, val.show(110), off))
            for fld, val, off, _m in fl:
                if (fld, off) in seen:
                    continue
                emit('     [宽松*]  %-32s = %-46s (STORE @%d)' % (fld, val.show(110), off))
            if not fa:
                emit('     （本 code 无「声明块」模式配对；[宽松*] 含 import/调用等噪声，仅参考）')


def report_consts_only(codes, strings=False):
    emit()
    emit('── 常量/名字池里的字符串值 ──')
    total = 0
    for i, c in enumerate(codes):
        strs = []
        for j, v in enumerate(c.consts):
            if v.base_kind == 'str':
                strs.append(('const[%d]' % j, v.v))
            elif v.kind == 'tuple':
                for k, e in enumerate(v.v):
                    if e.base_kind == 'str':
                        strs.append(('const[%d][%d]' % (j, k), e.v))
        if strs:
            emit('  ［%d］%s → 常量串 %d 条' % (i, c.display_name, len(strs)))
            for tag, s in strs:
                emit('     %-14s %s' % (tag, repr(s)))
            total += len(strs)
        nstr = [v.v for v in c.names if v.base_kind == 'str']
        if nstr:
            emit('  ［%d］%s → co_names 串 %d 条' % (i, c.display_name, len(nstr)))
            for j, s in enumerate(nstr):
                emit('     co_names[%d] %s' % (j, repr(s)))
            total += len(nstr)
        if strings:
            nblob = 0
            for v in c.consts:
                if v.base_kind == 'bytes' and len(v.v) >= 16:
                    ss = sd.pool_strings(v.v)
                    if ss:
                        emit('  ［%d］bytes 常量 @%d（%d B）内嵌可读串 %d 条：'
                             % (i, v.off, len(v.v), len(ss)))
                        for off2, s in ss[:200]:
                            emit('     +%-7d %s' % (off2, repr(s)))
                        nblob += len(ss)
            total += nblob
    emit('   合计字符串值 %d 条' % total)


def report_dis(codes, sel, grep=None, context=6):
    if sel == 'all':
        todo = list(enumerate(codes))
    else:
        try:
            k = int(sel)
        except ValueError:
            k = -1
        todo = [(k, codes[k])] if 0 <= k < len(codes) else []
    lines = []
    for i, c in todo:
        lines.append('')
        lines.append('══ [%d] %s ｜ co_code %d..%d（%d B）══'
                     % (i, c.display_name, c.code_off, c.code_off + c.code_len, c.code_len))
        for ins, val, src in c.dis_resolved():
            if val:
                lines.append('  %6d  %-30s %-6s → %s' % (ins.off, ins.name, ins.arg, val))
            else:
                lines.append('  %6d  %-30s %s' % (ins.off, ins.name, ins.arg))
    if grep:
        kw = grep.lower()
        hits = [n for n, l in enumerate(lines) if kw in l.lower()]
        emit()
        emit('── grep %r：命中 %d 行 ──' % (grep, len(hits)))
        shown = set()
        for n in hits:
            for m in range(max(0, n - context), min(len(lines), n + context + 1)):
                if m in shown:
                    continue
                shown.add(m)
                emit('  %s%s' % ('>>' if m == n else '  ', lines[m][:170]))
            emit('  ──')
    else:
        for l in lines:
            emit(l)


def scan_report(buf, scan_codes):
    emit()
    emit('── 特征扫描：候选 code 头（73 + 5×u32 + 7b|fb + u32 len，按 payload 反汇编像码率过滤）──')
    for off, arg, stk, flg, coff, clen, sc in scan_codes:
        rec, err = sd.read_record_at(buf, off)
        nm = rec.display_name if rec is not None else '(字段解析失败：%s)' % (err or '')
        emit('  code@%-8d co_code@%-8d %6dB  arg=%-2d stack=%-2d score=%.2f  %s' %
             (off, coff, clen, arg, stk, sc, nm))


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description='NeoX py314 字节码【带常量解析】反汇编器',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument('module', help='待解析的 .py（NeoX 字节码）')
    ap.add_argument('--funcs', action='store_true', help='只列函数清单')
    ap.add_argument('--consts', action='store_true', help='只列常量/名字池的字符串值')
    ap.add_argument('--names', action='store_true', help='只列名字表')
    ap.add_argument('--fields', action='store_true', help='只列 LOAD_CONST↔STORE_ATTR 字段赋值')
    ap.add_argument('--dis', metavar='N|all', help='反汇编第 N 个函数（或 all）')
    ap.add_argument('--grep', metavar='KW', help='在 --dis 的输出里按关键词过滤（带上下文）')
    ap.add_argument('--context', type=int, default=6, help='--grep 上下文行数（默认 6）')
    ap.add_argument('--dump', metavar='OUT', help='把全部输出写到文件')
    ap.add_argument('--scan', action='store_true', help='强制走特征扫描路径')
    ap.add_argument('--strings', action='store_true', help='额外抽取 bytes 常量里内嵌的可读串')
    a = ap.parse_args()

    p = Path(a.module)
    if not p.exists():
        print('找不到文件：%s' % p)
        return 2
    buf = p.read_bytes()
    reader, root, end = sd.load_module(p)
    used_scan = False
    partial = False
    scan_codes = []

    if root is not None:
        codes = sd.all_codes_from_root(root)
    else:
        used_scan = True
        codes = sd.complete_codes(reader)
        partial = bool(codes)
        # 再补一层特征扫描：把递归没走到的 code 头也列出来
        have = {c.off for c in codes}
        for off, arg, stk, flg, coff, clen, sc in sd.scan_code_headers(buf):
            if off in have:
                continue
            rec, err = sd.read_record_at(buf, off)
            if rec is not None and rec.complete:
                codes.append(rec)
        codes.sort(key=lambda x: x.off)
    if a.scan or used_scan:
        scan_codes = sd.scan_code_headers(buf)

    report_overview(p, buf, root, codes, end, reader, used_scan)
    if reader.error and root is None:
        emit('  ✗ 递归解析在此处中断：%s' % reader.error)
        if partial:
            emit('    （已把中断前【字段完整解析】的 %d 个 code 对象列出，并补以特征扫描）' % len(codes))
        else:
            emit('    （该文件结构与本读取器已知布局不符，函数清单来自特征扫描，可能不全）')

    only = a.funcs or a.consts or a.names or a.fields or a.dis is not None or bool(a.grep)
    if not only:
        if used_scan:
            scan_report(buf, scan_codes)
        report_funcs(codes)
        report_tables(codes)
        if a.strings:
            report_consts_only(codes, strings=True)
        return finish(a)

    if used_scan:
        scan_report(buf, scan_codes)
    if a.funcs or (not (a.consts or a.names or a.fields or a.dis is not None)):
        report_funcs(codes)
    if a.consts:
        report_consts_only(codes, strings=a.strings)
    if a.names:
        report_tables(codes, which=('names', 'vars'))
    if a.fields:
        report_tables(codes, which=())
    if not (a.funcs or a.consts or a.names or a.fields):
        report_tables(codes)
    if a.dis is not None:
        report_dis(codes, a.dis, a.grep, a.context)
    elif a.grep:
        report_dis(codes, 'all', a.grep, a.context)
    return finish(a)


def finish(a):
    if a.dump:
        outp = Path(a.dump)
        outp.write_text('\n'.join(OUT) + '\n', encoding='utf-8')
        print('\n写出 %s（%d 行）' % (outp, len(OUT)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
