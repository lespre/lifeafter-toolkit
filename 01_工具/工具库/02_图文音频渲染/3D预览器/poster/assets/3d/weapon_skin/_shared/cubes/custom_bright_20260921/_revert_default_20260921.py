# -*- coding: utf-8 -*-
u"""_revert_default_20260921.py —— 一键回退 1110025 的环境 cube 默认档到源绑定（qiangpi）。

回退语义（两条路，任选）：
  ① 完全回退（推荐）：把 `*.bak_brightcube_20260921` 覆盖回原文件
     ⇒ neox_material.json 的 t_custom_ibl 逐字回到 `src_cube/qiangpi.dds` +
       `src_cube/faces/qiangpi_f{i}_m0.png`，viewer.json 不再有 cube_default_selection。
  ② 仅注销产品档（保留声明记录、保留备份）：把 prim 的 local_file/faces_glob 还原为
     `_product_default_override` 里记的 `*_source_declared` 值，并删掉覆盖块。

用法：
  $env:PYTHONIOENCODING='utf-8'
  & <venv>\python.exe _revert_default_20260921.py --mode restore-bak --apply   # ① 完全回退
  & <venv>\python.exe _revert_default_20260921.py --mode unset-override --apply # ② 仅注销
  不加 --apply = 干跑。
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..', '..'))
SKIN = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110025')
NEOX = os.path.join(SKIN, 'neox_material.json')
VJSON = os.path.join(SKIN, 'viewer.json')
BAK = '.bak_brightcube_20260921'


def main():
    apply = '--apply' in sys.argv
    mode = 'restore-bak'
    if '--mode' in sys.argv:
        mode = sys.argv[sys.argv.index('--mode') + 1]
    print('模式 = %s   %s' % (mode, 'APPLY' if apply else 'DRY-RUN'))

    if mode == 'restore-bak':
        for p in (NEOX, VJSON):
            b = p + BAK
            if not os.path.exists(b):
                print('  缺备份，无法完全回退: %s' % b)
                return 1
            print('  %s  <-  %s' % (os.path.basename(p), os.path.basename(b)))
            if apply:
                shutil.copy2(b, p)
        if apply:
            a = json.load(open(NEOX, encoding='utf-8'))
            for pr in a['primitives']:
                t = (pr.get('textures') or {}).get('t_custom_ibl') or {}
                print('  prim %-2s local_file=%s faces_glob=%s'
                      % (pr.get('prim'), t.get('local_file'), t.get('faces_glob')))
            print('  viewer.json.cube_default_selection = %s'
                  % (json.dumps(json.load(open(VJSON, encoding='utf-8')).get('cube_default_selection'),
                                ensure_ascii=False)))
        return 0

    if mode == 'unset-override':
        a = json.load(open(NEOX, encoding='utf-8'))
        n = 0
        for pr in a['primitives']:
            t = (pr.get('textures') or {}).get('t_custom_ibl') or {}
            ov = t.get('_product_default_override')
            if not ov:
                continue
            t['local_file'] = ov.get('local_file_source_declared')
            t['faces_glob'] = ov.get('faces_glob_source_declared')
            t.pop('_product_default_override', None)
            n += 1
            print('  prim %-2s -> local_file=%s faces_glob=%s'
                  % (pr.get('prim'), t['local_file'], t['faces_glob']))
        if n and apply:
            json.dump(a, open(NEOX, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('  还原 %d 个 prim（声明记录保留在 viewer.json）' % n)
        return 0

    print('未知 --mode：%s' % mode)
    return 1


if __name__ == '__main__':
    sys.exit(main())
