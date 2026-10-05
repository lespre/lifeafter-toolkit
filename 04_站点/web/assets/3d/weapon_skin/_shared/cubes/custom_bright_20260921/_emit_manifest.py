# -*- coding: utf-8 -*-
u"""_emit_manifest.py —— 把自造 cube `custom_bright_20260921` **幂等**登记进
`04_站点\\web/data/media/weapon_skin_cubes_custom.js`。

设计取舍（为什么不重写整个文件）：
  该文件由 custom_studio_20260920 的生成器产出，头部写明「请勿手改，改生成器」。
  为了**不触碰别人的条目**、又能让本条目可复现，这里只做**单条目 upsert**：
    · 已存在同名条目 ⇒ 用 provenance.json 重新生成并**替换**它；
    · 不存在       ⇒ 插到 `CUSTOM_CUBES` 数组末尾（`];` 之前）。
  其余字节**一律不动**。

诚实标注（规格第 5 条，逐字落到 note）：
  status="self_authored_approximate" / authority="user_authorized_manual_20260921" / fidelity="approximate"
  note = **自造近似、非游戏资产；源侧无选择器 ⇒ 默认改用它属产品选择；目的=消除金属镜面方向的纯黑**

用法：$env:PYTHONIOENCODING='utf-8'; & <venv>\python.exe _emit_manifest.py
只写 data/media/weapon_skin_cubes_custom.js（生成器产出，不手改）。
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = 'custom_bright_20260921'
WIKI = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..', '..'))   # 04_站点\\web
TARGET = os.path.join(WIKI, 'data', 'media', 'weapon_skin_cubes_custom.js')
REL = 'assets/3d/weapon_skin/_shared/cubes/' + NAME

NOTE = ('**自造近似、非游戏资产**；源侧**无选择器** ⇒ 默认改用它属**产品选择**（'
        'authority=product_choice_20260921）；目的 = **消除金属镜面方向的纯黑**。'
        '像素基底取自游戏资产 gdansk_shipyard_buildings02 六面，但**辐射标定（增益 K + 抬底 L_FLOOR '
        '+ RGBM alpha 反解）是本写手自造的** —— 不得作为「游戏实际使用该环境」的证据，'
        '不得标成 source_verified，不得顶替源资产，也不得计入「源数据驱动」目标。')


def build_entry(prov):
    faces_rgbm = [REL + '/rgbm/' + r['file'].split('/')[-1] for r in prov['rgbm_faces']]
    faces_srgb = [REL + '/faces/' + r['file'] for r in prov['faces']]
    per_face_alpha = [{'axis': r['axis'],
                       'alpha_M_min': r['alpha_M']['min'], 'alpha_M_p50': r['alpha_M']['p50'],
                       'alpha_M_max': r['alpha_M']['max'],
                       'alpha_M_byte_min': r['alpha_M_byte']['min'],
                       'alpha_M_byte_p50': r['alpha_M_byte']['p50'],
                       'alpha_M_byte_max': r['alpha_M_byte']['max'],
                       'decoded_L_p50': r['decoded_L']['p50'], 'decoded_L_min': r['decoded_L']['min'],
                       'source_decoded_L_p50': r['source']['src_decoded_L']['p50'],
                       'source_alpha_p50': r['source']['src_alpha']['p50'],
                       'floor_dominated_px_pct': r['floor_dominated_px_pct']}
                      for r in prov['rgbm_faces']]
    return {
        'name': NAME,
        'status': 'self_authored_approximate',
        'authority': 'user_authorized_manual_20260921',
        'fidelity': 'approximate',
        'is_game_asset': False,
        'derived_from': [
            'assets/3d/weapon_skin/_shared/cubes/gdansk_shipyard_buildings02 '
            '(cube sha256:d28948b4cffe512ae170fa142cb28e3e556967466ea25700bf117d1b236571e3, sha16:d28948b4cffe512a, '
            'container 0000.gpk row 11706, B8G8R8A8_UNORM 128x128 mips=8) '
            '六面 mip0 PNG —— **唯一**像素来源（未混任何其它 cube）'
        ],
        'method': ('逐面：源解码辐射 L_src = (rgb_src * a_src * 16)^2（asm 542-544）→ 自造标定 '
                   'L_new = sqrt((K*L_src)^2 + L_FLOOR^2)（K=%.5f 由「六面 p50 ≤ 0.45」反解取最大；'
                   'L_FLOOR=%.2f 为逐像素下界）→ 反解 RGBM：q=sqrt(L_new), s=q/16, '
                   'M=ceil_8bit(max_c s_c), rgb_out=s/M。'
                   '未混其它 cube（实测 gdansk 六面无大面积近黑 ⇒ 规格允许的「补面」不需要）；'
                   '未做任何图像域增益/模糊/裁剪整形。' % (prov['radiance_calibration']['K'],
                                                          prov['radiance_calibration']['L_FLOOR'])),
        'note': NOTE,
        'logical': 'self_authored://' + NAME,
        'container': None, 'row': None, 'sha16': None,
        'dims': '128x128',
        'format': prov['format'],
        'n_faces': 6,
        'resolve': 'self_authored',
        'in_skin': False,
        'identity_basis': 'self_authored_approximate — 无容器/无哈希命中，**不是**源 cube',
        'selectable': True,
        'group': 'self_authored（自造近似，非游戏资产）',
        'requires_status_whitelist_extend': True,
        'cubemap_order': prov['cubemap_order'],
        'faces': faces_rgbm,
        'faces_srgb': faces_srgb,
        'faces_encoding': 'rgbm',
        'face_sha256_rgbm': [r['sha256'] for r in prov['rgbm_faces']],
        'face_sha256_srgb': [r['sha256'] for r in prov['faces']],
        'source_face_sha256': [f['sha256'] for f in prov['derived_from'][0]['faces']],
        'rgbm_encoding': prov['rgbm_encoding'],
        'radiance_calibration': prov['radiance_calibration'],
        'per_face_alpha': per_face_alpha,
        'summary': prov['summary'],
        'limitations': prov['limitations'],
    }


def main():
    prov = json.load(open(os.path.join(HERE, 'provenance.json'), encoding='utf-8'))
    entry = build_entry(prov)
    blob = '  ' + json.dumps(entry, ensure_ascii=False, indent=2).replace('\n', '\n  ')
    # json.dumps 已自带 2 空格缩进；再整体 +2 与数组内既有条目同缩进
    blob = '\n'.join(('  ' + ln) if ln.strip() else ln for ln in
                     json.dumps(entry, ensure_ascii=False, indent=2).split('\n'))
    blob = blob.rstrip()
    assert blob.startswith('  {') and blob.endswith('  }'), 'entry blob 缩进异常'

    s = open(TARGET, encoding='utf-8').read()
    before = s

    # ① 幂等：删掉既有同名条目
    pat = re.compile(r'\n  \{\n    "name": "' + re.escape(NAME) + r'",.*?\n  \}', re.S)
    had = bool(pat.search(s))
    if had:
        s = pat.sub('', s, count=1)

    # ② 插到 CUSTOM_CUBES 数组的 `];` 之前
    a = s.index('var CUSTOM_CUBES = [')
    close = s.index('\n];', a)
    head, tail = s[:close], s[close:]
    # 若数组清空过，前一条目末尾可能没有逗号；统一保证 `},` 再追加
    stripped = head.rstrip()
    if stripped.endswith('}'):
        head = stripped + ','
    s = head + '\n' + blob + tail

    assert NAME in s and s.count('"name": "' + NAME + '"') == 1, '条目数不为 1'
    open(TARGET, 'w', encoding='utf-8', newline='\n').write(s)

    print('%s 既有同名条目：%s ⇒ 数组内条目数 = %d'
          % (NAME, '替换' if had else '无（新增）',
             len(re.findall(r'\n  \{\n    "name": "', s))))
    print('写入 %s（%d → %d 字节）' % (TARGET, len(before.encode('utf-8')), len(s.encode('utf-8'))))

    # ③ node --check（硬门）
    r = subprocess.run(['node', '--check', TARGET], capture_output=True, text=True)
    print('node --check: rc=%d %s' % (r.returncode, ((r.stdout or '') + (r.stderr or '')).strip()))
    if r.returncode != 0:
        print('!! 语法检查失败，回滚')
        open(TARGET, 'w', encoding='utf-8', newline='\n').write(before)
        return 1

    # ④ 真跑一遍 JS，断言 mergeInto / get / viewerFaces 行为
    probe = (
        "global.window={};"
        "require(%s);"
        "var A=window.WikiWeaponSkinCubesCustom;"
        "console.log(JSON.stringify({names:A.names(),"
        "faces:A.viewerFaces('%s').length,"
        "first:A.viewerFaces('%s')[0],"
        "status:A.get('%s').status,"
        "enc:A.get('%s').faces_encoding,"
        "merged:A.mergeInto({cubes:[]}).merged}));"
        % (json.dumps(TARGET), NAME, NAME, NAME, NAME)
    )
    r2 = subprocess.run(['node', '-e', probe], capture_output=True, text=True)
    print('node 运行探针: rc=%d %s' % (r2.returncode, ((r2.stdout or '').strip() + (r2.stderr or '').strip())))
    return 0 if r2.returncode == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
