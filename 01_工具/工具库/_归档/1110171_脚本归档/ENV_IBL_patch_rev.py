# -*- coding: utf-8 -*-
"""ENV_IBL_patch_rev.py — 把两份交付更新到并发更新后的 viewer 修订 a846f104（只改这两份交付）。
   113692f0(4149 行) → a846f104(4191 行)：IBL 段行号未变；仅 2187→2229、2307→2349、2363→2405、3735+/3822+→3796+ 发生位移。"""
import io, json, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
J = os.path.join(OUT, 'ENV_IBL_diff.json')
M = os.path.join(OUT, 'ENV_IBL_spec_1110171_1110177_20260919.md')
REPL = [('L2187-2190', 'L2229-2232'), ('L2187', 'L2229'), ('L2363', 'L2405'), ('L2307', 'L2349'),
        ('L2308', 'L2350'), ('L2311-2318', 'L2352-2359'), ('L3735-3764', 'L3796'), ('L3822-3844', 'L3796/3804/3862-3867/3864/3887'),
        ('L1208-1218', 'L1208-1218'), ('L1219-1245', 'L1219-1245')]
NEWREV = {'sha256': 'a846f1043e5e687839dcfcd054f4af8263b25c112a1cb0318e29ed5f1b12578f',
          'bytes': 301919, 'lines': 4191, 'file': r'08Lifeafter wiki\assets\weapon_skin_viewer.js',
          'audited_revision_note': '审计起始修订 113692f0（298,329 B / 4149 行）；审计期间被并发更新为 a846f104（301,919 B / 4191 行），'
                                   'IBL 相关行号已逐条复核：L1168/L1193/L1208-1218/L1219-1245/L1254-1257/L1288/L1316/L1339-1376 未变；'
                                   'L2187→L2229、L2307→L2349、L2308→L2350、L2311-2318→L2352-2359、L2363→L2405、L3735+/L3822+→L3796/L3804/L3862-3867 已位移。'}


def fix(s):
    for a, b in REPL:
        s = s.replace(a, b)
    return s


d = json.load(open(J, encoding='utf-8'))
d['viewer_revision'] = NEWREV
d['facts']['manifest_revisions'] = {'1110171/neox_material.json': '80526e54c42d19b1（09-18 21:38）',
                                    '1110177/neox_material.json': '3b32c0e350fa60ea（09-18 21:38）',
                                    'note': '1110177 prim2 的 faces_glob=null（prim0/1 为 {0..5}）⇒ 链按 iblName 回落到 fashion_qiangpi_f{i}_m0.png，可工作；属 manifest 内部不一致，非缺陷'}
for it in d['items']:
    it['source_evidence'] = fix(it['source_evidence'])
    it['current_code'] = fix(it['current_code'])
    for skin, pv in it['per_prim'].items():
        for pid, rec in pv.items():
            rec['source_evidence'] = fix(rec['source_evidence'])
            rec['current_code'] = fix(rec['current_code'])
d['generated_from'] = [fix(x) for x in d['generated_from']]
json.dump(d, open(J, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

md = open(M, encoding='utf-8').read()
md = fix(md)
md = md.replace('**读用的代码修订**：`08Lifeafter wiki\\assets\\weapon_skin_viewer.js` sha256 `113692f0f38362c483b1f65fa695665bf7b619f1a6edf7bd2c285fdaaa22b6ef`（298,329 B / 4149 行）。下文所有 viewer 行号均指该修订；该文件正被并发编辑，行号复核时请以该 sha 为准。',
                '**读用的代码修订**：`08Lifeafter wiki\\assets\\weapon_skin_viewer.js` sha256 **`a846f1043e5e687839dcfcd054f4af8263b25c112a1cb0318e29ed5f1b12578f`**（301,919 B / 4191 行，09-18 22:18）。'
                '⚠ **并发更新披露**：审计起始修订为 `113692f0…`（298,329 B / 4149 行）；审计期间该文件被他方更新为 `a846f104…`。'
                'IBL 相关行号已逐条复核：`L1168 / L1193 / L1208-1218 / L1219-1245 / L1254-1257 / L1288 / L1316 / L1339-1376` **两版一致**；'
                '`L2187→L2229`、`L2307→L2349`、`L2308→L2350`、`L2311-2318→L2352-2359`、`L2363→L2405`、`L3735+ / L3822+ → L3796 / L3804 / L3862-3867` 已位移。下表均按 **a846f104** 标注。')
md = md.replace('⇒ **1110177 三 prim 声明与绑定 3/3 相符**',
                '⇒ **1110177 三 prim 声明与绑定 3/3 相符**（附：`1110177/neox_material.json` 的 prim2 `faces_glob=null`（prim0/1 为 `{0..5}`）'
                '⇒ 链按 `iblName` 回落到 `fashion_qiangpi_f{i}_m0.png`，可工作；属 manifest 内部不一致，非声明/绑定错误）')
md = md.replace('**只读声明**：', '**只读声明**：')
open(M, 'w', encoding='utf-8').write(md)
print('patched:', J, os.path.getsize(J), '|', M, os.path.getsize(M))
