# -*- coding: utf-8 -*-
import os, json, subprocess

out = r'E:\提取成果\filename_restore_output'
f = os.path.join(out, 'disguised_ui_03.json')

if os.path.exists(f):
    print(f'ui_03.gpk 扫描已完成！结果文件: {os.path.getsize(f)}B')
    data = json.load(open(f, 'r', encoding='utf-8'))
    print(f'  候选数: {len(data.get("candidates", []))}')
    for c in data.get('candidates', [])[:30]:
        print(f"    [{c['index']:6d}] {c['decomp']:>8}B 1DPW={c['is_1dpw']} markers={c['markers']} head={c['head_hex'][:24]}")
else:
    print('ui_03.gpk 扫描还在进行中...')
    r = subprocess.run(['powershell', '-Command',
                        'Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CPU -gt 50} | Select-Object Id, CPU, WorkingSet, StartTime'],
                       capture_output=True, text=True)
    print(r.stdout.strip())
