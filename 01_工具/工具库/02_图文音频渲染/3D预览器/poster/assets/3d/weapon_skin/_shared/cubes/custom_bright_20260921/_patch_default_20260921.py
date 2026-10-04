# -*- coding: utf-8 -*-
u"""_patch_default_20260921.py —— 把 1110025 的**环境 cube 默认档**切到自造 `custom_bright_20260921`。

为什么落在 neox_material.json（而不是改 viewer.js）：
  实测（读代码，非推测）：真正被 loader 消费的 IBL 声明在 **neox_material.json** 的
  `primitives[*].textures.t_custom_ibl`（viewer.js L1435 fetch 的就是它；`T=pr.textures`），
  而 viewer.json **根本没有 t_custom_ibl**（已实测 walk 全文件：0 处）。
  ⇒ 只改这一个字段就能「不点任何控件即使用它」，**完全不用碰 weapon_skin_viewer.js / board.html**，
     也就不会与并发写手冲突、不会动 board 的缓存键（3/3 不受影响）。这是最小改动面。

改哪两个字段、为什么必须改两个：
  · `local_file`：viewer.js L1934-1939 从它的**基名**派生 `iblName`，而 `iblName` 是
    `state.__srcCubeCache` / `state.__iblGate` 的**缓存键**。若基名仍是 `qiangpi`，
    则 `__cubeAB('qiangpi')` 会命中本 cube 的缓存 ⇒ 取证选择器会被污染。
    ⇒ 必须换成不同基名 `src_cube/custom_bright_20260921.dds`（该 .dds **不被 fetch**，
      只作基名载体：L1923-1939 只用它派生 iblName，六面 URL 全部来自 faces_glob）。
  · `faces_glob`：viewer.js L1966-1971 只信任**以 `src_cube/` 开头**的 glob（其余会被压成
    `base+'src_cube/faces/'+basename`）。故用 `src_cube/../../_shared/...` 相对回 _shared/，
    命中既有分支 `base + t`，浏览器按相对 URL 规范化 ⇒ 落到
    `assets/3d/weapon_skin/_shared/cubes/custom_bright_20260921/rgbm/…`。
  ⇒ 两处都改，且**不改任何查看器代码**。

诚实标注：源侧**没有**选择器决定预览用哪套 cube（Lead 裁决 C10 = unresolved）。
  本切换是 **authority=product_choice_20260921 / fidelity=not_source_determined**，
  用的是**自造近似、非游戏资产**的 cube。原声明逐字保留在 `_product_default_override`
  与 `*.bak_brightcube_20260921` 里，可一键回退。

用法：$env:PYTHONIOENCODING='utf-8'; & <venv>\python.exe _patch_default_20260921.py [--apply]
      不加 --apply = 干跑（只打印将要做的事）。
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

CUBE = 'custom_bright_20260921'
REL_FACES = 'src_cube/../../_shared/cubes/%s/rgbm/%s_f{i}_m0.png' % (CUBE, CUBE)
NEW_LOCAL = 'src_cube/%s.dds' % CUBE
SRC_LOCAL = 'src_cube/qiangpi.dds'
SRC_GLOB = 'src_cube/faces/qiangpi_f{i}_m0.png'

SELECTION = {
    'cube': CUBE,
    'authority': 'product_choice_20260921',
    'fidelity': 'not_source_determined',
    'note': ('源无选择器；为消除金属镜面纯黑而改用自造亮环境'
             '（基于 gdansk_shipyard_buildings02 增强 RGBM 辐射）。非源数据。'),
}


def backup(path):
    b = path + BAK
    if os.path.exists(b):
        print('  备份已存在，保持不变（避免用已打补丁的内容覆盖好备份）: %s' % os.path.basename(b))
        return b
    shutil.copy2(path, b)
    print('  备份: %s (%d bytes)' % (os.path.basename(b), os.path.getsize(b)))
    return b


def main():
    apply = '--apply' in sys.argv
    print('=== 目标 ===')
    print('  skin      : 1110025')
    print('  功能绑定  : %s' % NEOX)
    print('  声明记录  : %s' % VJSON)
    print('  cube      : %s (self_authored_approximate, 非游戏资产)' % CUBE)
    print('  模式      : %s' % ('APPLY' if apply else 'DRY-RUN（加 --apply 才写）'))
    print()

    neox = json.load(open(NEOX, encoding='utf-8'))
    vjson = json.load(open(VJSON, encoding='utf-8'))

    print('=== viewer.json：写声明记录 cube_default_selection ===')
    vjson['cube_default_selection'] = dict(SELECTION)
    print('  %s' % json.dumps(SELECTION, ensure_ascii=False))

    print()
    print('=== neox_material.json：逐 prim 覆盖 t_custom_ibl ===')
    n = 0
    for pr in neox.get('primitives', []):
        t = (pr.get('textures') or {}).get('t_custom_ibl')
        if not t:
            print('  prim %s: 无 t_custom_ibl，跳过' % pr.get('prim'))
            continue
        ov = t.get('_product_default_override') or {}
        t['local_file'] = NEW_LOCAL
        t['faces_glob'] = REL_FACES
        t['_product_default_override'] = {
            'changed_fields': ['local_file', 'faces_glob'],
            'local_file_source_declared': ov.get('local_file_source_declared', t.get('local_file_source_declared', SRC_LOCAL)),
            'faces_glob_source_declared': ov.get('faces_glob_source_declared', t.get('faces_glob_source_declared', SRC_GLOB)),
            'cube': CUBE,
            'authority': SELECTION['authority'],
            'fidelity': SELECTION['fidelity'],
            'status': 'self_authored_approximate',
            'is_game_asset': False,
            'note': SELECTION['note'],
            'logical_path_left_as_source_declared': t.get('logical_path'),
            'why_local_file_renamed': ('viewer.js L1934-1939 由 local_file 基名派生 iblName，'
                                       '而 iblName 是 __srcCubeCache/__iblGate 的缓存键；'
                                       '基名若仍为 qiangpi 会让 __cubeAB(\'qiangpi\') 命中本 cube 缓存'),
            'why_relative_src_cube_dotdot': ('viewer.js L1966-1971 只信任以 src_cube/ 开头的 faces_glob '
                                             '⇒ 用 src_cube/../../ 相对回 _shared/，不改查看器代码'),
            'revert': '还原 %s 即可回到源绑定（qiangpi），或删掉本覆盖块' % os.path.basename(NEOX + BAK),
        }
        n += 1
        print('  prim %-2s local_file: %s -> %s' % (pr.get('prim'), SRC_LOCAL, NEW_LOCAL))
        print('           faces_glob: %s' % REL_FACES)
    print('  覆盖 %d 个 prim' % n)

    if not apply:
        print('\nDRY-RUN：未写任何文件。')
        return 0

    print('\n=== 写入 ===')
    backup(NEOX)
    backup(VJSON)
    tmp = NEOX + '.tmp'
    json.dump(neox, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, NEOX)
    tmp = VJSON + '.tmp'
    json.dump(vjson, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, VJSON)

    # 回读校验（硬门）
    a = json.load(open(NEOX, encoding='utf-8'))
    b = json.load(open(VJSON, encoding='utf-8'))
    ok = 0
    for pr in a['primitives']:
        t = (pr.get('textures') or {}).get('t_custom_ibl') or {}
        good = (t.get('local_file') == NEW_LOCAL and t.get('faces_glob') == REL_FACES
                and t.get('_product_default_override', {}).get('cube') == CUBE
                and t.get('logical_path') == 'common\\env_map\\qiangpi.cube')
        ok += 1 if good else 0
        print('  prim %-2s 回读 %s' % (pr.get('prim'), 'OK' if good else 'FAIL'))
    print('  viewer.json.cube_default_selection = %s'
          % json.dumps(b.get('cube_default_selection'), ensure_ascii=False))
    print('  源声明 logical_path 仍为 common\\env_map\\qiangpi.cube：%s'
          % (b.get('cube_default_selection', {}).get('cube') == CUBE))
    print('\n回读 OK %d/%d' % (ok, len(a['primitives'])))
    return 0 if ok == len(a['primitives']) else 1


if __name__ == '__main__':
    sys.exit(main())
