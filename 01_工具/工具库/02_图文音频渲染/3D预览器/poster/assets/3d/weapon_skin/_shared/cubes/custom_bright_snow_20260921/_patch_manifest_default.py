# -*- coding: utf-8 -*-
u"""_patch_manifest_default.py —— 两件事，一次做完（幂等）：

  ① 把 `custom_bright_snow_20260921` 登记进 data/media/weapon_skin_cubes_custom.js
     （**只插入，不重写整个文件** ⇒ 不踩另一路写手的并发改动）；
  ② 把 assets/3d/weapon_skin/1110025/viewer.json 的 `cube_default_selection`
     从旧基底 `custom_bright_20260921` **替换为** `custom_bright_snow_20260921`，
     并在旧自造条目上如实标注 `superseded_by`（"已被取代"）。

用法：
  $env:PYTHONIOENCODING='utf-8'
  & '<venv>\python.exe' _patch_manifest_default.py [--dry-run]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = <wiki>/assets/3d/weapon_skin/_shared/cubes/<NAME>  ⇒ 上溯 6 层到 wiki 根
WIKI = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..', '..'))
NAME = 'custom_bright_snow_20260921'
OLD = 'custom_bright_20260921'
MANIFEST = os.path.join(WIKI, 'data', 'media', 'weapon_skin_cubes_custom.js')
VIEWER = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110025', 'viewer.json')
REL = 'assets/3d/weapon_skin/_shared/cubes/' + NAME


def build_entry(prov):
    """从 provenance.json 生成清册条目（faces 指向 rgbm/ 档）。"""
    faces = ['%s/rgbm/%s_f%d_m0.png' % (REL, NAME, i) for i in range(6)]
    faces_srgb = ['%s/faces/%s_f%d_m0.png' % (REL, NAME, i) for i in range(6)]
    sh_rgbm = [f['sha256'] for f in prov['rgbm_faces']]
    sh_srgb = [f['sha256'] for f in prov['faces']]
    src_sha = [f['source']['sha256'] for f in prov['faces']]
    d = prov['derived_from'][0]
    cal = prov['radiance_calibration']
    s = prov['summary']
    per_face = []
    for i, f in enumerate(prov['faces']):
        r = prov['rgbm_faces'][i]
        per_face.append({
            'axis': f['axis'], 'face': f['face'],
            'is_self_authored_fill': f['is_filled_face'],
            'alpha_M_min': r['alpha_M']['min'], 'alpha_M_p50': r['alpha_M']['p50'],
            'alpha_M_max': r['alpha_M']['max'],
            'alpha_M_byte_min': r['alpha_M_byte']['min'],
            'alpha_M_byte_p50': r['alpha_M_byte']['p50'],
            'alpha_M_byte_max': r['alpha_M_byte']['max'],
            'decoded_L_min': f['decoded_L_min'],
            'decoded_L_p50': f['decoded_L']['p50'],
            'dark_L_lt_0.05_pct': f['dark_L_lt_0.05_pct'],
            'gt1_pct': f['gt1_pct'],
            'gt085_pct': f['gt085_pct'],
            'source_face_sha256': f['source']['sha256'],
            'source_decoded_L_p50': f['source']['src_decoded_L']['p50'],
            'source_dark_L_lt_0.05_pct': f['source']['src_dark_L_lt_0.05_pct'],
            'source_gt1_pct': f['source']['src_gt1_pct'],
            'source_is_all_black': f['source']['src_is_all_black'],
        })
    return {
        'name': NAME,
        'status': 'self_authored_approximate',
        'authority': 'user_authorized_manual_20260921',
        'fidelity': 'approximate',
        'is_game_asset': False,
        'derived_from': [
            ('assets/3d/weapon_skin/_shared/cubes/snow (cube sha256:%s, sha16:%s, logical %s, '
             'container %s row %s, %s) 的 **f0/f1/f2/f4/f5 五面** mip0 PNG 为像素基底；'
             '**f3(−Y) 面由本写手用 +Y(f2) 天花垂直镜像 + 高斯 σ=10 + 压暗 ×0.85 自造补出**'
             '（该面在源容器里全黑：maxRGB=0 / maxA=1 ⇒ 解码 100%% 近黑）。'
             % (d['cube_sha256'], d['cube_sha16'], d.get('logical'), d.get('container'),
                d.get('row'), d.get('dims')))
        ],
        'method': (
            '逐面：源解码辐射 L_src = (rgb_src * a_src * 16)^2（asm 542-544，已由游戏 DXBC 逐指令证实）'
            ' → 自造软抬底 L_new = sqrt(L_src^2 + a^2)，**增益恒为 1.0（不加任何增益）**，a=0.0505'
            '（由「逐面近黑 L<0.05 占比 == 0」反解；因 luma 是各通道凸组合，min_channel(L_new)=a，'
            '再留 8bit 量化余量）'
            ' → 反解 RGBM：q=sqrt(L_new), s=q/16, M=ceil_8bit(max_c s_c), rgb_out=s/M。'
            'f3(−Y)：+Y 天花**垂直镜像** → 逐通道高斯模糊 σ=10 → 均匀压暗 ×0.85（保留 HDR 感，不做平灰箱）。'
            '未混任何其它 cube 的像素；未做任何图像域增益/对比度/裁剪整形（唯一整形是 f3 的模糊与压暗）。'),
        'note': (
            '**自造近似、非游戏资产**；源侧**无选择器** ⇒ 默认改用它属**产品选择**'
            '（authority=product_choice_20260921）；目的 = **消除武器金属镜面发黑**。'
            '像素基底取自游戏资产 snow 的 f0/f1/f2/f4/f5 五面，**f3(−Y) 面是自造的**'
            '（源该面全黑 ⇒ 用 +Y 天花镜像补出），并逐像素加了软抬底 a=0.0505（反解 RGBM 的 M）。'
            '**不得**作为「游戏实际使用该环境」的证据，**不得**标成 source_verified，'
            '**不得**顶替源资产，也不得计入「源数据驱动」目标。'
            '本项**取代**上一版自造基底 custom_bright_20260921（基于 gdansk、只抬底、会削弱 HDR 亮点、'
            '对金属帮助有限）。'),
        'supersedes': OLD,
        'logical': 'self_authored://' + NAME,
        'container': None, 'row': None, 'sha16': None,
        'dims': '128x128',
        'format': 'PNG RGBA RGBM(a=multiplier) — 与源 B8G8R8A8_UNORM + asm542-544 解码约定对齐',
        'n_faces': 6,
        'resolve': 'self_authored',
        'in_skin': False,
        'identity_basis': 'self_authored_approximate — 无容器/无哈希命中，**不是**源 cube',
        'selectable': True,
        'group': 'self_authored（自造近似，非游戏资产）',
        'requires_status_whitelist_extend': True,
        'cubemap_order': ['+X', '-X', '+Y', '-Y', '+Z', '-Z'],
        'faces': faces,
        'faces_srgb': faces_srgb,
        'faces_encoding': 'rgbm',
        'face_sha256_rgbm': sh_rgbm,
        'face_sha256_srgb': sh_srgb,
        'source_face_sha256': src_sha,
        'source_face_sha256_note': ('f0/f1/f2/f4/f5 = snow 源面原件哈希；f3 = 源 snow_f3 的哈希'
                                    '（该面全黑，本项的 f3 是自造补面，见 per_face[3].is_self_authored_fill）'),
        'rgbm_encoding': {
            'decode_in_viewer': 'q_L = pow(rgb * a * 16.0, 2.0)   /* asm 542-544 */',
            'texture_colorSpace': 'NoColorSpace (viewer L2001/L5106/L5223)',
            'encode': 'q = sqrt(L_new) ; s = q/16 ; M = ceil_8bit(max_c s_c) ; rgb_out = s / M',
            'alpha_is_rgbm_multiplier': True,
            'ceil_not_round_why': ('M 取 ceil 到 8bit 网格 ⇒ M ≥ max_c s_c 恒成立 ⇒ rgb_out ≤ 1 '
                                   '**无需裁剪**，回读误差只剩 rgb_out 的 8bit 量化。'),
            'why_alpha_matters': ('源 IBL 分支解码 pow(rgb*a*16,2)，alpha 就是 RGBM 乘子 M。'
                                  '实测 qiangpi alpha≈0.015 ⇒ 解码辐射≈0.05 ⇒ 金属镜面发黑。'),
        },
        'radiance_calibration': {
            'is_self_authored': True,
            'formula': 'L_new = sqrt( L_src^2 + a^2 )   逐通道；L_src = (rgb_src * a_src * 16)^2',
            'GAIN': cal['GAIN'],
            'GAIN_rule': cal['GAIN_rule'],
            'L_FLOOR_A': cal['L_FLOOR_A'],
            'L_FLOOR_A_rule': cal['L_FLOOR_A_rule'],
            'f3_fill': {'method': '+Y(f2) 垂直镜像 → 逐通道高斯 σ=10.0 → 均匀压暗 ×0.85',
                        'sigma': 10.0, 'dim': 0.85,
                        'src_f3_sha256': s['f3_fill']['src_f3_sha256'],
                        'src_f3_all_black': True,
                        'built_f3_L_min': s['f3_fill']['built_f3_L_min'],
                        'built_f3_L_p50': s['f3_fill']['built_f3_L_p50'],
                        'built_f3_gt1_pct': s['f3_fill']['built_f3_gt1_pct']},
            'no_image_domain_gain': cal['no_image_domain_gain'],
            'forbidden_touched': cal['forbidden_touched'],
        },
        'per_face_alpha': per_face,
        'summary': {
            'decoded_L_p50_per_face': s['decoded_L_p50_per_face'],
            'decoded_L_min_per_face': s['decoded_L_min_per_face'],
            'dark_L_lt_0.05_pct_per_face': s['dark_L_lt_0.05_pct_per_face'],
            'gt1_pct_per_face': s['gt1_pct_per_face'],
            'gt1_pct_cube': s['gt1_pct_cube'],
            'gt1_pct_cube_source_snow': s['source_snow']['gt1_pct_cube'],
            'gt1_ge_source_snow': s['gt1_ge_source_snow'],
            'decoded_L_mean_cube': s['decoded_L_mean_cube'],
            'decoded_L_mean_cube_source_snow': s['source_snow']['decoded_L_mean_cube'],
            'decoded_L_min_over_all_faces': s['decoded_L_min_over_all_faces'],
            'dark_L_lt_0.05_pct_worst_face': s['dark_L_lt_0.05_pct_worst_face'],
            'all_faces_dark_zero': s['all_faces_dark_zero'],
            'all_faces_min_gt_0.05': s['all_faces_min_gt_0.05'],
            'source_snow_f3_all_black': True,
        },
        'limitations': prov['limitations'],
        'builder_script': '_shared/cubes/%s/_build_snow_cube.py' % NAME,
    }


def insert_entry(text, entry_json):
    """把条目插入 CUSTOM_CUBES 数组末尾（在最后的 `  }\\n];` 之前）。只插入指定文本。"""
    m = re.search(r'\n\];\n', text)
    if not m:
        raise SystemExit('FAIL: 找不到 CUSTOM_CUBES 数组结尾')
    ins = ',\n' + entry_json
    return text[:m.start()] + ins + text[m.start():]


def main():
    dry = '--dry-run' in sys.argv
    prov = json.load(open(os.path.join(HERE, 'provenance.json'), encoding='utf-8'))
    entry = build_entry(prov)

    # ── ① 清册 ──
    mtext = open(MANIFEST, encoding='utf-8').read()
    if '"%s"' % NAME in mtext:
        print('[①] 清册已含 %s ⇒ 跳过插入' % NAME)
        mtext_new = mtext
    else:
        # 旧条目补 superseded_by（如实记录"已被取代"）
        if '"superseded_by"' not in mtext:
            anchor = '"name": "%s",' % OLD
            if anchor in mtext:
                mtext = mtext.replace(
                    anchor,
                    anchor + '\n    "superseded_by": "%s",' % NAME
                    + '\n    "superseded_note": "已被 custom_bright_snow_20260921 取代：'
                      '实测金属区发黑由 cube 中 L>1 纹素占比决定，本项（基于 gdansk_shipyard_buildings02、'
                      '只抬底、会削弱 HDR 亮点）对金属帮助有限。保留仅为可比对，不再是默认。",',
                    1)
        entry_json = json.dumps(entry, ensure_ascii=False, indent=2)
        entry_json = '\n'.join('  ' + ln if ln else ln for ln in entry_json.split('\n'))
        mtext_new = insert_entry(mtext, entry_json)
        print('[①] 清册：插入 %s（%d → %d 字符）' % (NAME, len(mtext), len(mtext_new)))

    # ── ② viewer.json 默认 ──
    vtext = open(VIEWER, encoding='utf-8').read()
    v = json.loads(vtext)
    old_sel = (v.get('cube_default_selection') or {}).get('cube')
    new_sel = {
        'cube': NAME,
        'authority': 'product_choice_20260921',
        'fidelity': 'not_source_determined',
        'note': ('源侧无 cube 选择器；为消除金属镜面发黑改用自造亮环境'
                 '（基于 snow 并补全其全黑朝下面）。非源数据。'),
    }
    want = json.dumps(new_sel, ensure_ascii=False)
    have = json.dumps(v.get('cube_default_selection'), ensure_ascii=False)
    if have == want:
        print('[②] viewer.json 默认已是 %s ⇒ 跳过' % NAME)
        vtext_new = vtext
    else:
        # 定位并整段替换 cube_default_selection 的值（保持其它字段逐字不动）
        m = re.search(r'"cube_default_selection"\s*:\s*\{', vtext)
        if not m:
            raise SystemExit('FAIL: viewer.json 找不到 cube_default_selection')
        i = m.end() - 1
        depth, j = 0, i
        while j < len(vtext):
            if vtext[j] == '{':
                depth += 1
            elif vtext[j] == '}':
                depth -= 1
                if depth == 0:
                    break
            elif vtext[j] == '"':          # 跳过字符串
                j += 1
                while j < len(vtext) and vtext[j] != '"':
                    j += 2 if vtext[j] == '\\' else 1
            j += 1
        vtext_new = vtext[:i] + want + vtext[j + 1:]
        print('[②] viewer.json 默认：%s → %s' % (old_sel, NAME))
        # 写前自检：替换后仍是合法 JSON 且只改了这一个键
        a, b = json.loads(vtext), json.loads(vtext_new)
        b2 = dict(b)
        b2.pop('cube_default_selection', None)
        a2 = dict(a)
        a2.pop('cube_default_selection', None)
        assert a2 == b2, 'FAIL: 替换影响了其它键'
        assert b['cube_default_selection'] == new_sel

    if dry:
        print('--dry-run：未写任何文件')
        return 0
    open(MANIFEST, 'w', encoding='utf-8').write(mtext_new)
    open(VIEWER, 'w', encoding='utf-8').write(vtext_new)
    print('写了 %s' % MANIFEST)
    print('写了 %s' % VIEWER)
    return 0


if __name__ == '__main__':
    sys.exit(main())
