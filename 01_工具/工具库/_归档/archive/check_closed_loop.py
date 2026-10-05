# -*- coding: utf-8 -*-
import os, json, subprocess

out = r'E:\提取成果\filename_restore_output'
files = os.listdir(out)
closed_loop = [f for f in files if 'closed_loop' in f]

if closed_loop:
    print('闭环脚本已完成！')
    for f in closed_loop:
        full = os.path.join(out, f)
        print(f'  {os.path.getsize(full):>10}B  {f}')

    report_path = os.path.join(out, 'filename_restore_closed_loop.json')
    if os.path.exists(report_path):
        report = json.load(open(report_path, 'r', encoding='utf-8'))
        print(f'\n  条目数: {report.get("entry_count")}')
        print(f'  提取到路径的条目: {report.get("extracted_entries")}')
        print(f'  唯一路径: {report.get("unique_paths")}')
        print(f'  匹配成功: {report.get("matched")}')
        print(f'  未匹配路径: {report.get("unmatched_paths")}')
        print(f'\n  匹配结果（前30条）:')
        for m in report.get('matched_entries', [])[:30]:
            print(f"    [{m['entry_index']:5d}] {m['logical_path']}")
else:
    print('闭环脚本还在运行中...')
    r = subprocess.run(['powershell', '-Command',
                        'Get-Process -Id 35924 -ErrorAction SilentlyContinue | Select-Object Id, CPU, WorkingSet'],
                       capture_output=True, text=True)
    print(r.stdout.strip())
