# -*- coding: utf-8 -*-
"""test_provenance_e2e.py — 端到端 provenance 测试: 实际启动主管线, 逐项注入, 读 provenance 验证。
运行: python test_provenance_e2e.py  (exit 0 = 全过; 预计 3-5 分钟)
案例: 干净(源模式+c159参数) / v19 / tint / face / band / post / 哈希替换(同名贴图被改)
"""
import sys, os, json, shutil, subprocess
from PIL import Image
import numpy as np

PY = sys.executable
SD = os.path.dirname(os.path.abspath(__file__))
PIPE = os.path.join(SD, 'weapon_skin_pipeline.py')
W = r'E:\la拆包项目\03拆包产物\weapon'
TEX = r'E:\la拆包项目\03拆包产物\render_jiguangjian'
OUT = os.path.join(TEX, '_e2e_prov')
MESH = os.path.join(W, '003995.mesh')
C159 = os.path.join(W, '003996.c159')

def run_case(name, extra, tex_dir=TEX):
    od = os.path.join(OUT, name)
    shutil.rmtree(od, ignore_errors=True); os.makedirs(od, exist_ok=True)
    cmd = [PY, PIPE, MESH, tex_dir, od, '--profile', 'jiguangjian', '--source'] + extra
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    pj = os.path.join(od, 'provenance.json')
    if not os.path.exists(pj):
        return None, 'no provenance.json; rc=%s; out=%s' % (p.returncode, (p.stdout or '')[-300:] + (p.stderr or '')[-300:])
    d = json.load(open(pj, encoding='utf-8'))
    return d, None

def main():
    os.makedirs(OUT, exist_ok=True)
    # 准备: v19 改色贴图(缺失才建)
    v19 = os.path.join(TEX, 'tex_4011_v19.png')
    if not os.path.exists(v19):
        a = np.asarray(Image.open(os.path.join(TEX, 'tex_4011.png')).convert('RGBA'), np.int16)
        a[..., 1] = np.clip(a[..., 1] * 0.7, 0, 255); a[..., 2] = np.clip(a[..., 2] * 0.7, 0, 255)
        Image.fromarray(a.astype(np.uint8)).save(v19)
        print('*(创建 tex_4011_v19.png 改色版)')
    # 准备: 哈希替换贴图目录 (tex_4011.png 内容被改, 名称不变)
    SWAP = os.path.join(OUT, '_tex_hashswap')
    shutil.rmtree(SWAP, ignore_errors=True); os.makedirs(SWAP)
    for f in ('tex_4009.png', 'tex_4012.png', 'tex_4013.png'):
        shutil.copy2(os.path.join(TEX, f), os.path.join(SWAP, f))
    a = np.asarray(Image.open(os.path.join(TEX, 'tex_4011.png')).convert('RGBA'), np.int16)
    a[..., 0] = np.clip(a[..., 0] + 20, 0, 255)   # 细微改动
    Image.fromarray(a.astype(np.uint8)).save(os.path.join(SWAP, 'tex_4011.png'))

    CASES = [
        ('01_clean', ['--params-c159', C159], TEX, True, None),
        ('02_inject_v19', ['--params-c159', C159, '--inject', 'v19'], TEX, False, 'v19'),
        ('03_inject_tint', ['--params-c159', C159, '--inject', 'tint'], TEX, False, '染色'),
        ('04_inject_face', ['--params-c159', C159, '--inject', 'face'], TEX, False, 'face_overrides'),
        ('05_inject_band', ['--params-c159', C159, '--inject', 'band'], TEX, False, 'band'),
        ('06_inject_post', ['--params-c159', C159, '--inject', 'post'], TEX, False, '后处理'),
        ('07_hashswap', ['--params-c159', C159], SWAP, False, '锚定'),
    ]
    allok = True
    for name, extra, texdir, want_pass, kw in CASES:
        d, err = run_case(name, extra, texdir)
        if d is None:
            allok = False; print('FAIL | %-15s | %s' % (name, err)); continue
        sdi = d.get('source_data_integrity', {})
        ok = bool(sdi.get('pass'))
        reasons = sdi.get('reasons', [])
        fid = d.get('shader_fidelity', {}).get('status')
        good = (ok == want_pass) and (want_pass or any(kw in r for r in reasons))
        allok = allok and good
        print(('PASS' if good else 'FAIL'), '| %-15s | integrity=%s fidelity=%s | %s' % (name, ok, fid, '; '.join(reasons)[:110]))
    print('==== 端到端 provenance 测试', '全部通过' if allok else '存在失败', '====')
    sys.exit(0 if allok else 1)

if __name__ == '__main__':
    main()
