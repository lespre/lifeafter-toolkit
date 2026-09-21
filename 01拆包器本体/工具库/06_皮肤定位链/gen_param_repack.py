# -*- coding: utf-8 -*-
"""gen_param_repack.py — 武器皮肤 ParamMap 通道重排生成器（可复跑）

源依据（DXBC 直译，非拟合）：
  · metal = sat(ParamMap.G)  ·  rough = clamp(ParamMap.R, 0.02, 1)
    —— 出处：1110165/1110171 材质链反汇编 pbr_weapon 的 ParamMap 采样与 saturate/clamp 语义
       （见 RENDER_RULES.md / C159_PARAM_PAIRING.md 记载的 DXBC 行；本仓库 06_皮肤定位链 已多轮引用）
  · three r180 实读 `material.metalnessMap.B` / `material.roughnessMap.G`
    （three 源码 metalnessmap_pars/roughnessmap_pars：metalness *= texelMetalness.b；roughness *= texelRoughness.g）

输出（就地对每个皮肤 src_tex/ 下的 param_repack_*.png 重写；不动 rough_repack_*）：
  R = 255                                   ← 无消费者（three 不读 R），留白并在本注释说明
  G = round(255 * clamp(ParamMap.R, 0.02, 1))   ← rough
  B = round(255 * sat(ParamMap.G))              ← metal
  A = 255

用法：
  python gen_param_repack.py --check 1110165        # 自检：与现有图逐像素比对（只读，不写）
  python gen_param_repack.py --skin 1110171         # 单皮肤重生成（改前备份到 REPACK_backup/）
  python gen_param_repack.py --all                  # 全部已建皮肤
"""
import os, sys, json, glob, shutil, hashlib, datetime
import numpy as np
from PIL import Image

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
S3D = os.path.join(WIKI, 'assets', '3d', 'weapon_skin')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
BK = os.path.join(OUT, 'REPACK_backup')
os.makedirs(BK, exist_ok=True)


def find_parammap(skin, fam):
    """按 repack 家族号找 ParamMap 源图：优先 src_tex/<fam>_m.png，其次 manifest，其次唯一 *_m.png。"""
    d = os.path.join(S3D, skin, 'src_tex')
    cands = []
    for p in (os.path.join(d, '%s_m.png' % fam),):
        if os.path.isfile(p):
            cands.append(p)
    if not cands:
        for tag in ('ParamMap',):
            mp = os.path.join(S3D, skin, 'neox_material.json')
            if os.path.isfile(mp):
                man = json.load(open(mp, encoding='utf-8'))
                for pr in man.get('primitives', []):
                    t = (pr.get('textures') or {}).get(tag)
                    lf = (t or {}).get('local_file')
                    if lf:
                        p = os.path.join(WIKI, lf)
                        if os.path.isfile(p):
                            cands.append(p)
    if not cands:
        ms = sorted(glob.glob(os.path.join(d, '*_m.png')))
        if len(ms) == 1:
            cands.append(ms[0])
    return cands[0] if cands else None


def build(src_png):
    a = np.asarray(Image.open(src_png).convert('RGBA')).astype(np.float32)
    R = a[:, :, 0] / 255.0
    G = a[:, :, 1] / 255.0
    out = np.zeros_like(a)
    out[:, :, 0] = 255.0
    out[:, :, 1] = np.round(255.0 * np.clip(R, 0.02, 1.0))
    out[:, :, 2] = np.round(255.0 * np.clip(G, 0.0, 1.0))
    out[:, :, 3] = 255.0
    return out.astype(np.uint8)


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def do_skin(skin, write=False):
    d = os.path.join(S3D, skin, 'src_tex')
    reps = sorted(glob.glob(os.path.join(d, 'param_repack_*.png')))
    recs = []
    for rp in reps:
        fam = os.path.basename(rp).replace('param_repack_', '').replace('.png', '')
        src = find_parammap(skin, fam)
        rec = {'skin': skin, 'repack': os.path.basename(rp), 'fam': fam,
               'param_src': (os.path.relpath(src, WIKI).replace('\\', '/') if src else None)}
        if not src:
            rec['status'] = 'absent: 找不到 ParamMap 源图（不改）'
            recs.append(rec)
            continue
        new = build(src)
        old = np.asarray(Image.open(rp).convert('RGBA')).astype(np.uint8)
        rec['old_sha16'] = sha16(rp)
        rec['old_mtime'] = datetime.datetime.fromtimestamp(os.path.getmtime(rp)).isoformat(timespec='seconds')
        rec['same_shape'] = bool(old.shape == new.shape)
        if old.shape == new.shape:
            rec['diff_pixels'] = int((old != new).any(axis=2).sum())
            rec['G_pixel_identical'] = bool((old[:, :, 1] == new[:, :, 1]).all())
            rec['B_pixel_identical'] = bool((old[:, :, 2] == new[:, :, 2]).all())
            rec['old_ch_mean'] = [round(float(old[:, :, i].mean()), 1) for i in range(4)]
            rec['new_ch_mean'] = [round(float(new[:, :, i].mean()), 1) for i in range(4)]
            rec['predicted_rough_mean'] = round(float(new[:, :, 1].mean() / 255.0), 4)
            rec['predicted_metal_mean'] = round(float(new[:, :, 2].mean() / 255.0), 4)
        if write:
            bkp = os.path.join(BK, '%s_%s_%s.png' % (skin, fam, rec['old_sha16']))
            if not os.path.isfile(bkp):
                shutil.copyfile(rp, bkp)
            rec['backup'] = bkp
            Image.fromarray(new, 'RGBA').save(rp)
            rec['new_sha16'] = sha16(rp)
            rec['status'] = 'regenerated'
        else:
            rec['status'] = 'check-only'
        recs.append(rec)
    return recs


mode = sys.argv[1] if len(sys.argv) > 1 else '--all'
report = {'mode': mode, 'rule': {'R': 255, 'G': 'round(255*clamp(ParamMap.R,0.02,1))',
                                 'B': 'round(255*sat(ParamMap.RG... G))', 'A': 255},
          'recs': []}
if mode == '--check':
    report['recs'] = do_skin(sys.argv[2], write=False)
elif mode == '--skin':
    report['recs'] = do_skin(sys.argv[2], write=True)
else:
    for skin in sorted({os.path.basename(p) for p in glob.glob(os.path.join(S3D, '1*')) if os.path.isdir(p)}):
        if skin.endswith('_cand'):
            continue
        report['recs'] += do_skin(skin, write=True)
json.dump(report, open(os.path.join(OUT, 'REPACK_gen_report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('%-10s %-24s %-30s %-22s %s' % ('skin', 'repack', 'param_src', 'old→new G|B 均值', '状态'))
for r in report['recs']:
    if r.get('old_ch_mean'):
        print('%-10s %-24s %-30s G %-6s→%-6s B %-6s→%-6s %s' % (
            r['skin'], r['repack'], r.get('param_src') or '-',
            r['old_ch_mean'][1], r['new_ch_mean'][1], r['old_ch_mean'][2], r['new_ch_mean'][2],
            ('G逐像素一致=%s B逐像素一致=%s diff=%s px' % (r.get('G_pixel_identical'), r.get('B_pixel_identical'), r.get('diff_pixels'))) if 'diff_pixels' in r else r['status']))
    else:
        print('%-10s %-24s %-30s %s' % (r['skin'], r['repack'], r.get('param_src') or '-', r['status']))
print('\njson ->', os.path.join(OUT, 'REPACK_gen_report.json'))
