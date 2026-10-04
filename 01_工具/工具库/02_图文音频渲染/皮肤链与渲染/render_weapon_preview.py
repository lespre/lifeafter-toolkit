#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""render_weapon_preview.py —— 一条命令：用【游戏相机 + 游戏光照 + 游戏材质】渲染武器皮肤

依据（全部来自拆包真值 ✓ 非推断）：
  · 相机：common_model_show_conf（NeoX marshal 解码）里的 list[10] 预设
          = [posX,posY,posZ, fwdX,fwdY,fwdZ, upX,upY,upZ, FOV]
          武器皮肤预览簇：z≈900-935，FOV 44.3~45
  · 模型世界位置：[18.4, -17.0, 916.29]（list[3][0]）
  · 光照：天气 XML 的 42 个时间轨道（locallight/cube/atmo/exposure/char_*）
  · 材质：c159 + 晶体 shader

用法：
  python render_weapon_preview.py <skin_id> <mesh> <c159> <tex_by_slot> <tex_common> <site> <out_dir>
         [--pct 72]         目标占画面高度百分比（默认 72）
         [--seed 2]         用哪个游戏相机预设（默认 2 = 武器皮肤预览簇）
         [--hour 12.53]     天气时刻（默认 12.53 = 白天）
         [--weather <xml>]  天气 XML（默认 city08/zhanshen01）
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
RENDER = HERE / 'render_game_faithful.py'
PY = r'E:\la拆包项目\.venv\Scripts\python.exe'
CONF = Path(r'E:\la拆包项目\03_执行\90_临时\common_model_show_conf.json')
DEFAULT_WX = (r'E:/la拆包项目/03_执行/41_还原树/Documents/gres/0000.gpk/weather/'
              r'weather_ct_pve_city08_v20_pve_zhanshen01.xml')


def build_cam(seed, pct, out_json):
    """从解出的配置表取游戏相机 + 按目标占比算距离"""
    import numpy as np
    d = json.loads(CONF.read_text('utf-8'))
    es = d['payload']['entries']
    c = es[seed]
    assert isinstance(c, list) and len(c) == 10, 'seed %d 不是 list[10]' % seed
    pos = np.array(c[0:3], float)
    fwd = np.array(c[3:6], float)
    up = np.array(c[6:9], float)
    fov = float(c[9])
    fwd = fwd / (np.linalg.norm(fwd) or 1.0)
    C = np.array([-0.0, 0.2541, 1.4449], float)          # mesh 中心（实测 ✓）
    # 距离：默认相机 dist≈15.0 时武器占高 23.4% ⇒ dist = 15.0×23.4/pct
    dist = 15.0 * 23.4 / float(pct)
    out = {'source': 'game config seed=%d (NeoX marshal) + pct=%.0f' % (seed, pct),
           'camera_presets': [{'seed': seed, 'position': (C - fwd * dist).tolist(),
                               'target': C.tolist(), 'up': up.tolist(),
                               'fov': fov, 'dist': dist}]}
    Path(out_json).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    return {'pos': (C - fwd * dist).tolist(), 'fov': fov, 'dist': dist}


def main():
    a = sys.argv[1:]
    if len(a) < 7:
        print(__doc__)
        raise SystemExit(2)
    skin, mesh, c159, tex_slot, tex_common, site, out_dir = a[:7]

    def opt(k, dflt):
        return a[a.index(k) + 1] if k in a else dflt
    pct = float(opt('--pct', 72))
    seed = int(opt('--seed', 2))
    weather = opt('--weather', DEFAULT_WX)
    _ = float(opt('--hour', 12.53))       # 时刻由天气 XML 在渲染器侧读，这里仅记录

    cam_json = str(Path(out_dir).parent / ('cam_%s_seed%d.json' % (skin, seed)))
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    cam = build_cam(seed, pct, cam_json)
    print('[CAM] seed=%d pos=%s fov=%.1f dist=%.2f（目标占高 %.0f%%）'
          % (seed, [round(x, 3) for x in cam['pos']], cam['fov'], cam['dist'], pct))

    S = site.rstrip('/')
    cmd = [PY, '-X', 'utf8', str(RENDER), mesh, out_dir,
           '--c159', c159,
           '--tex-a',  '%s/../tex_by_slot_%s/a.png' % (tex_slot, skin),
           '--tex-bm', '%s/../tex_by_slot_%s/b_m.png' % (tex_slot, skin),
           '--tex-n',  '%s/../tex_by_slot_%s/n.png' % (tex_slot, skin),
           '--tex-bump', '%s/crystal_bump_n_uvva.png' % tex_common,
           '--tex-caustic', '%s/crystal_caustic_uvva.png' % tex_common,
           '--tex-refr', '%s/src_tex/refraction_envmap_3.png' % S,
           '--ibl', '%s/src_cube/faces' % S, '--ibl-name', 'car_studio01',
           '--cam-json', cam_json]
    print('[RUN] %s' % ' '.join(cmd[:6]) + ' ...')
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    for l in (r.stdout or '').splitlines():
        if any(k in l for k in ('相机', '覆盖', '出图', 'Error', 'Traceback')):
            print('   %s' % l.strip())
    if r.returncode != 0:
        print((r.stderr or '')[-600:])
        raise SystemExit(r.returncode)


if __name__ == '__main__':
    main()
