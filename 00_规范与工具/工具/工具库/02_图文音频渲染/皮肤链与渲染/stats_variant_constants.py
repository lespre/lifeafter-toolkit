# -*- coding: utf-8 -*-
"""stats_variant_constants.py — 跨变体统计（外审 v6 令 #3：唯一化依据）

对目标 shader 家族的全部 .pipe：反汇编 PS → 抽取
  · SV_Target3.w 常量（mov o3.xw, l(1.0,0,0,X)）
  · 输出数 / 指令数 / 采样槽集合
  · 特征 uniform 使用情况（emissive / detail / pearl / color_2u / alpha_mtl / custom_ibl / char_virtual_lit）
输出: <out_csv> + 控制台交叉表
用法: python stats_variant_constants.py <pipe_dir_or_root> <substr> <out.csv> [--limit N]
"""
import os, re, sys, csv, subprocess, collections

P = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

def disasm(path, outdir):
    subprocess.run([PY, os.path.join(P, 'dxbc_disasm.py'), path, '--out', outdir],
                   capture_output=True, text=True, timeout=300)
    b = os.path.basename(path)
    txt = ''
    for f in os.listdir(outdir):
        if f.startswith(b):
            txt += open(os.path.join(outdir, f), encoding='utf-8', errors='replace').read()
    return txt

def features(txt):
    ps = [l for l in txt.splitlines()]
    d = {}
    d['target3w'] = None
    for l in ps:
        m = re.search(r'mov o3\.xw,\s*l\(1\.000000,0,0,([0-9.]+)\)', l)
        if m:
            d['target3w'] = float(m.group(1))
    d['n_out'] = len(re.findall(r'dcl_output(?:_siv)?\s+o(\d+)', txt))
    d['ins'] = txt.count('// Approximately')
    for k, pat in [('emissive', 'u_emissive_strength'), ('detail', 'u_detail_intensity'),
                   ('pearl', 'u_pearl_phase'), ('color2u', 'u_color_2u'),
                   ('alpha_mtl', 'u_alpha_mtl'), ('cvl', 'char_virtual_lit')]:
        used = False
        for l in txt.splitlines():
            if pat in l and '[unused]' not in l and l.strip().startswith('//'):
                used = True
                break
        d[k] = used
    d['slots'] = ','.join(sorted(set(re.findall(r'// (s_\w+)\s+sampler', txt))))
    return d

def main():
    root, sub, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    limit = int(sys.argv[sys.argv.index('--limit') + 1]) if '--limit' in sys.argv else 10 ** 9
    outdir = os.path.join(os.path.dirname(outp), '_tmp_disasm')
    os.makedirs(outdir, exist_ok=True)
    rows = []
    n = 0
    for r, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.pipe') or sub not in os.path.relpath(os.path.join(r, f), root).lower():
                continue
            if n >= limit:
                break
            n += 1
            txt = disasm(os.path.join(r, f), outdir)
            d = features(txt)
            d['file'] = f
            rows.append(d)
            if n % 25 == 0:
                print('...%d' % n, flush=True)
    if rows:
        with open(outp, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for x in rows:
                w.writerow(x)
    print('rows=%d -> %s' % (len(rows), outp))
    print('\n=== SV_Target3.w 常量分布 ===')
    c = collections.Counter(x['target3w'] for x in rows)
    for k, v in c.most_common(20):
        print('   %-12s %d' % (k, v))
    print('\n=== 常量 × 特征 交叉表 ===')
    for feat in ['emissive', 'detail', 'pearl', 'color2u', 'alpha_mtl', 'cvl']:
        cc = collections.Counter((x['target3w'], x[feat]) for x in rows)
        print('  [%s]' % feat)
        for k, v in sorted(cc.items(), key=lambda z: (str(z[0][0]), z[0][1])):
            print('     const=%-12s %-5s : %d' % (k[0], k[1], v))

if __name__ == '__main__':
    main()
