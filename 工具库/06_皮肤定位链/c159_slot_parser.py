#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""c159_slot_parser.py — .c159 属性记录解析器：把「槽位类名」与「明文引用路径」逐槽配对（只读）

为什么需要它
------------
现有 `c159_pair.py` 只把**数值槽(u_*)**与数值块配对（`pair_block` 显式跳过字符串槽，
见其 L173 `slots=[v for v in group if not _is_str_slot(names,v)]`），
所以「哪个槽位类(t_basecolor/ParamMap/t_surfacemap/Tex0/NormalMap/...)绑定哪个明文文件」
一直没有机器可读的逐槽记录 —— 这正是 ParamMap/t_basecolor/t_surfacemap 三处悬案的根源。

本解析器做三件事
----------------
1) **稳健名字表**：修 c159_pair.read_names 的两个硬伤
   · 名字前缀字节可能是任意可打印字符（实测 '/AnimParam' '4AnimParam' ':AnimParam' '16AnimParam'），
     原实现只 `lstrip('0123456789')` ⇒ 001386/000654 等直接抛 ValueError。
     这里统一剥掉首个字母/下划线之前的全部字符。
   · 无 `t_basecolor` 的变体（000334/002731 等）回退到首个 `t_*`/`u_*`。
2) **槽序提取**：复用 c159_pair 的组发现，取出每组的**字符串槽序列（按组内顺序）**。
3) **逐槽配对 + 双路判定**：
   · 路 A（槽序）：组内字符串槽[k] ↔ 该材料明文串[k]
   · 路 B（文件名语义）：`*_b_m`→Tex0 / `*_a`→t_basecolor / `*_n`→NormalMap /
     `*_m`→ParamMap / `*_s_m`→t_surfacemap / `*.cube`→t_custom_ibl / `bump`→DetailMap /
     `caustic`→t_caustic_tex / `reflection*`→t_reflection_tex / `refraction*`→t_refraction_tex
   两路一致的槽 = **双路直证**；不一致 = 明确记为 conflict（不硬凑）。

用法
----
  python c159_slot_parser.py <file.c159> [--json out.json]
  python c159_slot_parser.py --skins            # 跑 6 个皮肤的材料 c159 并汇总
  库: parse(path) -> dict ; SELF_CHECKS -> 已知对照
"""
from __future__ import annotations
import argparse, json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c159_pair as CP  # noqa: E402  复用 组发现/条目解析

W = r'E:\la拆包项目\03拆包产物\weapon'
STR_SLOT = ('Tex0', 'NormalMap', 'DetailMap', 'ParamMap')
SEM = [  # 路 B：文件名语义（按优先级）
    ('t_refraction_tex', r'refraction'),
    ('t_reflection_tex', r'reflection'),
    ('t_caustic_tex', r'caustic'),
    ('t_surfacemap', r'_s_m'),
    ('t_basecolor', r'_a$'),
    ('Tex0', r'_b_m'),
    ('NormalMap', r'_n$'),
    ('ParamMap', r'_m$'),
    ('DetailMap', r'bump'),
    ('t_custom_ibl', r'\.cube$'),
]

SKIN_FILES = {  # skin_item_id -> material c159（来自各皮肤 neox_material.json 的 material_c159）
    '1110024': '001386.c159',
    '1110129': '000334.c159',
    '1110145': '000654.c159',
    '1110152': '002731.c159',
    '1110165': '001631.c159',
    '1110171_dual': '001265.c159',
    '1110171_single': '001223.c159',
    '1110177': '003996.c159',
}


def read_names_robust(b: bytes):
    """稳健名字表：剥掉首个 [A-Za-z_] 之前的任意字符（修 c159_pair 的前缀字节硬伤）。"""
    runs = [(m.start(), m.group().decode('latin1')) for m in re.finditer(rb'[\x20-\x7e]{2,}', b)]
    norm = []
    for off, s in runs:
        t = re.sub(r'^[^A-Za-z_]+', '', s)
        if t:
            norm.append((off, t))
    i0 = next((k for k, (_, s) in enumerate(norm) if s == 'AnimParam'), None)
    prefixed = [s for _, s in runs if 'AnimParam' in s]
    if i0 is None:
        # 没有 AnimParam：退化为「首个 t_/u_/Tex0 之前的组件段」
        i0 = next((k for k, (_, s) in enumerate(norm) if s.startswith(('t_', 'u_')) or s == 'Tex0'), None)
        if i0 is None:
            raise ValueError('名字表: 未找到 AnimParam / t_ 起点')
        i0 = max(0, i0 - 6)   # 往前补组件段（DetailMap/NormalMap/Tex0/ParamMap/Material* 等）
    comp, j = [], i0
    while j < len(norm):
        s = norm[j][1]
        if s == 't_basecolor' or s.startswith(('t_', 'u_')):
            break
        comp.append(s); j += 1
    params = []
    while j < len(norm):
        s = norm[j][1]
        if re.search(r'[\\]|::|\.fx$', s) or s.startswith(('skim', 'skin_', 'shader')):
            break
        params.append(s)
        if s in ('AlphaRef', 'Version'):
            break
        j += 1
    full = comp + params
    idx = {}
    for k, n in enumerate(full):
        idx.setdefault(n, k)
    return dict(comp=comp, params=params, full=full, idx=idx, max_index=len(full) - 1,
                prefix_chars=sorted({s[0] for s in prefixed} or []))


def is_pathstr(e):
    v = e['value']
    return ('\\' in v or '/' in v) and v.lower().endswith(('.tga', '.cube', '.dds', '.png'))


def string_slots(names, group):
    """组内字符串槽（按组序），跳过 Macro*/TransparentMode 等非资源槽。"""
    out = []
    for v in group:
        nm = names['full'][v] if 0 <= v < len(names['full']) else '?'
        if nm in STR_SLOT or nm.startswith('t_'):
            out.append((v, nm))
    return out


def semantic_class(path):
    base = os.path.basename(path).lower()
    for cls, pat in SEM:
        if re.search(pat, base):
            return cls
    return None


def parse(path: str) -> dict:
    b = open(path, 'rb').read()
    if b[:4] != bytes([0xC1, 0x59, 0x41, 0x0D]):
        return dict(file=os.path.basename(path), error='magic 非 c1 59 41 0d', magic=b[:4].hex(' '))
    declared = struct.unpack_from('<I', b, 4)[0]
    names = read_names_robust(b)
    groups = CP.find_groups(b, names)
    entries = CP.parse_entries(b)
    strings = [e for e in entries if e['type'] == 'str' and is_pathstr(e)]
    # 材料组 = 含 >=4 个字符串槽的组（其余是 0/1 槽的算法噪声段）
    mags = [g for g in groups if len(string_slots(names, g)) >= 4]
    # 字符串串流按文件顺序切分（每个材料组按自己的槽数领走 N 个）
    rows, si = [], 0
    for gi, g in enumerate(mags):
        ss = string_slots(names, g)
        take = strings[si:si + len(ss)]
        si += len(ss)
        for k, (v, nm) in enumerate(ss):
            p = take[k]['value'] if k < len(take) else None
            sem = semantic_class(p) if p else None
            rows.append(dict(material_block=gi, slot_index=v, slot_class=nm,
                             ref=os.path.basename(p) if p else None, ref_full=p,
                             off=take[k]['off'] if k < len(take) else None,
                             semantic_class=sem,
                             agree_by_order_only=(sem is not None and sem != nm),
                             dual_proof=(sem == nm)))
    return dict(file=os.path.basename(path), size=len(b), declared=declared,
                name_prefix_chars=names['prefix_chars'], comp=names['comp'], params=names['params'],
                materials=len(mags), strings_total=len(strings), strings_consumed=si,
                rows=rows,
                conflicts=[r for r in rows if r['agree_by_order_only']])


def summarize(d: dict) -> dict:
    dual = sum(1 for r in d.get('rows', []) if r['dual_proof'])
    conf = d.get('conflicts', [])
    return dict(file=d['file'], materials=d.get('materials'), rows=len(d.get('rows', [])),
                dual=dual, conflict=len(conf), unparsed_strings=d.get('strings_total', 0) - d.get('strings_consumed', 0),
                errors=d.get('error'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='?')
    ap.add_argument('--json')
    ap.add_argument('--skins', action='store_true')
    a = ap.parse_args()
    if a.skins:
        out = {}
        for sid, fn in SKIN_FILES.items():
            p = os.path.join(W, fn)
            if not os.path.exists(p):
                out[sid] = dict(file=fn, error='missing'); continue
            try:
                d = parse(p); out[sid] = d
                s = summarize(d)
                print('%-16s %-14s mats=%s rows=%s dual=%s conflict=%s 余串=%s' %
                      (sid, fn, s['materials'], s['rows'], s['dual'], s['conflict'], s['unparsed_strings']))
                for r in d['conflicts']:
                    print('    ⚠ conflict: %-18s ↔ %-28s (按槽序) / 文件名语义=%s' %
                          (r['slot_class'], r['ref'], r['semantic_class']))
            except Exception as e:
                out[sid] = dict(file=fn, error=repr(e)); print('%-16s %-14s FAIL %r' % (sid, fn, e))
        if a.json:
            os.makedirs(os.path.dirname(a.json), exist_ok=True)
            json.dump(out, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('→', a.json)
        return 0
    if not a.file:
        ap.error('需要 <file.c159> 或 --skins')
    d = parse(a.file)
    if d.get('error'):
        print('ERR', d); return 2
    print('%s  %dB  materials=%d  prefix_chars=%s' % (d['file'], d['size'], d['materials'], d['name_prefix_chars']))
    print('%-4s %-18s %-30s %-18s %s' % ('blk', 'slot_class', 'ref', '语义类', '判定'))
    for r in d['rows']:
        verdict = '双路一致' if r['dual_proof'] else ('槽序≠语义 ⚠' if r['agree_by_order_only'] else '无语义可比')
        print('%-4d %-18s %-30s %-18s %s' % (r['material_block'], r['slot_class'], r['ref'], r['semantic_class'] or '-', verdict))
    print('materials=%d rows=%d dual=%d conflict=%d 未消费串=%d' %
          (d['materials'], len(d['rows']), sum(1 for r in d['rows'] if r['dual_proof']),
           len(d['conflicts']), d['strings_total'] - d['strings_consumed']))
    if a.json:
        os.makedirs(os.path.dirname(a.json), exist_ok=True)
        json.dump(d, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('→', a.json)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
