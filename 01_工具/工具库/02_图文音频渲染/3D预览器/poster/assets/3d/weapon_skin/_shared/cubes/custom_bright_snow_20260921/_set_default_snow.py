# -*- coding: utf-8 -*-
u"""_set_default_snow.py —— 把 viewer.json 的 `cube_default_selection` 写成本任务书给定的**逐字**值。

只替换这一个 JSON 节点；写前/写后都做「其它键完全不变」的自检。
（本脚本专为"另有一路写手在 12:29:38 把默认改成了 night_clearsky02"这一步而写：
 本任务书明确要求默认 = custom_bright_snow_20260921，故按任务书写入并如实记录"已被取代"。）

用法：& '<venv>\python.exe' _set_default_snow.py [--dry-run]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..', '..'))
VIEWER = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110025', 'viewer.json')
NEW = 'custom_bright_snow_20260921'

WANT = {
    'cube': NEW,
    'authority': 'product_choice_20260921',
    'fidelity': 'not_source_determined',
    'note': ('源侧无 cube 选择器；为消除金属镜面发黑改用自造亮环境'
             '（基于 snow 并补全其全黑朝下面）。非源数据。'),
}


def main():
    dry = '--dry-run' in sys.argv
    text = open(VIEWER, encoding='utf-8').read()
    a = json.loads(text)
    old = a.get('cube_default_selection')
    want = json.dumps(WANT, ensure_ascii=False)
    if json.dumps(old, ensure_ascii=False) == want:
        print('默认已是 %s ⇒ 无需改动' % NEW)
        return 0
    m = re.search(r'"cube_default_selection"\s*:\s*\{', text)
    if not m:
        raise SystemExit('FAIL: 找不到 cube_default_selection')
    i = m.end() - 1
    depth, j = 0, i
    while j < len(text):
        ch = text[j]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                break
        elif ch == '"':
            j += 1
            while j < len(text) and text[j] != '"':
                j += 2 if text[j] == '\\' else 1
        j += 1
    out = text[:i] + want + text[j + 1:]
    b = json.loads(out)
    b2, a2 = dict(b), dict(a)
    b2.pop('cube_default_selection', None)
    a2.pop('cube_default_selection', None)
    if a2 != b2:
        raise SystemExit('FAIL: 替换影响了其它键')
    if b['cube_default_selection'] != WANT:
        raise SystemExit('FAIL: 替换结果不是期望值')
    print('默认: %s → %s' % ((old or {}).get('cube'), NEW))
    if old:
        print('（被取代的旧默认 authority=%s fidelity=%s）'
              % (old.get('authority'), old.get('fidelity')))
    if dry:
        print('--dry-run：未写文件')
        return 0
    open(VIEWER, 'w', encoding='utf-8').write(out)
    print('写了 %s' % VIEWER)
    return 0


if __name__ == '__main__':
    sys.exit(main())
