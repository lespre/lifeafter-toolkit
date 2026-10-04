# -*- coding: utf-8 -*-
"""_probe_tiers_20260921.py —— 自造亮 cube 的**三档金属区对照**（不改任何渲染文件）。

为什么现在就能测：查看器已有 diagnostic selector `window.WikiWeaponViewer.__cubeAB(name)`，
它只换 `uSrcIbl`/`uCustomIbl` 的 CubeTexture（同一条既有接线），**不写文件、不改默认**。
⇒ 借它就能在「默认尚未切换」时先量出自造项的金属区读数。

口径（**逐字复用**，不复制公式）：
  · measure()     ← accept_brightness_1110025.measure()     （常规闸门口径）
  · metal_region()← gi2_tiers_20260921.metal_region()       （金属区**代理**：消色差 sat<0.55、不设亮度下限）
        dark_share_pct = 带内消色差且 luma<0.25 的占比  ← 直接对应「发黑」
        metalreg_p50 / p95 / gt085_pct              ← 抬头与否

达标线（规格）：
  · 新自造项 dark% 相对 qiangpi 绝对下降 ≥ 30pp，且 MRp50 明显上升；
  · 同时主体 p50 不得跌破 0.60。

用法：python _probe_tiers_20260921.py <port>
产出：_shots/TIER_<name>.png + _tiers_20260921.json
"""
import asyncio
import base64
import hashlib
import io as _io
import json
import os
import subprocess
import sys
import urllib.request

import numpy as np
from PIL import Image
import websockets

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = r'E:\la拆包项目\03_执行\\30_分析\_target_1110025'
sys.path.insert(0, TARGET)
from accept_1110025 import CDP, CHROME_CANDS, URL          # noqa: E402
from accept_brightness_1110025 import measure              # noqa: E402
from gi2_tiers_20260921 import metal_region                # noqa: E402

SHOT = os.path.join(HERE, '_shots')
BASELINE_SHA16 = 'a1cf4661a7e2dbe6'          # 改动前默认帧 sha16（gi2_tiers 的基线常量）
TIERS = ['qiangpi', 'gdansk_shipyard_buildings02', 'custom_bright_20260921']


def analyze(img):
    a = np.asarray(img.convert('RGB')).astype(float) / 255.0
    H, Wd, _ = a.shape
    band = a[int(H * 0.33):int(H * 0.62), int(Wd * 0.18):int(Wd * 0.85)]
    lum = 0.2126 * band[:, :, 0] + 0.7152 * band[:, :, 1] + 0.0722 * band[:, :, 2]
    sat = band.max(axis=2) - band.min(axis=2)
    ach = sat < 0.55
    out = metal_region(img)
    # 补几个如实标注的诊断量
    out['band_p50_all_px'] = round(float(np.percentile(lum, 50)), 4)
    out['ach_p05'] = round(float(np.percentile(lum[ach], 5)), 4) if ach.sum() else None
    out['ach_lt_010_pct'] = round(float(100.0 * (ach & (lum < 0.10)).mean()), 2)
    out['ach_lt_050_pct'] = round(float(100.0 * (ach & (lum < 0.50)).mean()), 2)
    return out


async def shot(c, tag, rep, extra=None):
    s = await c.send('Page.captureScreenshot', format='png')
    raw = base64.b64decode(s['data'])
    fp = os.path.join(SHOT, 'TIER_%s.png' % tag)
    open(fp, 'wb').write(raw)
    row = {'tag': tag, 'shot': os.path.basename(fp),
           'shot_sha16': hashlib.sha256(raw).hexdigest()[:16]}
    im = Image.open(_io.BytesIO(raw))
    row.update(measure(im))
    row.update(analyze(im))
    if extra:
        row.update(extra)
    rep['tiers'].append(row)
    print('%-30s subj p50=%-7s | MRp50=%-7s MRp95=%-7s MR>085=%-6s dark%%=%-6s | p05=%-7s sha16=%s'
          % (tag, row['subject_p50'], row.get('metalreg_p50'), row.get('metalreg_p95'),
             row.get('metalreg_gt085_pct'), row.get('dark_share_pct'), row.get('ach_p05'),
             row['shot_sha16']), flush=True)
    return row


async def wait_faces(c, name, tries=40):
    for _ in range(tries):
        st = await c.ev("window.WikiWeaponViewer.__cubePickerState()")
        try:
            q = json.loads(st)
        except Exception:
            await asyncio.sleep(0.5)
            continue
        if q.get('selected') == name and (q.get('faces_loaded') or 0) >= 6:
            return q
        await asyncio.sleep(0.5)
    return None


async def main(port):
    rep = {'purpose': '自造亮 cube 三档金属区对照（借既有 __cubeAB，不改默认/不写渲染文件）',
           'baseline_sha16_expected': BASELINE_SHA16, 'tiers': []}
    os.makedirs(SHOT, exist_ok=True)
    chrome = next((c for c in CHROME_CANDS if os.path.exists(c)), None)
    pr = subprocess.Popen([chrome, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--window-size=1240,900',
                           '--remote-debugging-port=%d' % port,
                           '--user-data-dir=%s' % os.path.join(os.environ.get('TEMP', '.'), 'bc_%d' % port),
                           'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(5)
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % port))
                  if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            c = CDP(ws)
            await c.send('Page.enable')
            await c.send('Runtime.enable')
            await c.send('Page.navigate', url=URL)
            await asyncio.sleep(10)
            await c.ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110025',preview_3d:{status:'ready',"
                       "manifest:'assets/3d/weapon_skin/1110025/viewer.json'}},{title:'冰蕊银华'});return 1;})()")
            for _ in range(40):
                st = await c.ev("JSON.stringify((window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())||null)")
                if st and st not in ('null', 'undefined'):
                    break
                await asyncio.sleep(1)
            await asyncio.sleep(8)

            # ① 默认档（不调用任何 API）= 切换前的默认身份
            r0 = await shot(c, 'T0_default_nocall', rep)
            rep['default_identity'] = {
                'picker': await c.ev("window.WikiWeaponViewer.__cubePickerState()"),
                'sha16': r0['shot_sha16'],
                'byte_identical_to_prechange_baseline': (r0['shot_sha16'] == BASELINE_SHA16)}
            print('DEFAULT sha16=%s  == pre-change baseline(%s) ? %s'
                  % (r0['shot_sha16'], BASELINE_SHA16,
                     rep['default_identity']['byte_identical_to_prechange_baseline']), flush=True)

            # ② 三档
            for name in TIERS:
                res = await c.ev("window.WikiWeaponViewer.__cubeAB(%s)" % json.dumps(name))
                q = await wait_faces(c, name)
                await asyncio.sleep(3.0)
                r = await shot(c, name, rep, {'cubeAB_readback': (res or '')[:900],
                                              'picker_after': q})
            # ③ 复位
            await c.ev("window.WikiWeaponViewer.__cubeAB(null)")
            await asyncio.sleep(3.0)

        by = {t['tag']: t for t in rep['tiers'] if t['tag'] in TIERS}
        if 'qiangpi' in by and 'custom_bright_20260921' in by:
            q0, q1 = by['qiangpi'], by['custom_bright_20260921']
            rep['verdict'] = {
                'dark_pct_qiangpi': q0['dark_share_pct'], 'dark_pct_custom': q1['dark_share_pct'],
                'dark_pct_abs_drop_pp': round(q0['dark_share_pct'] - q1['dark_share_pct'], 2),
                'dark_drop_target_30pp': bool(q0['dark_share_pct'] - q1['dark_share_pct'] >= 30.0),
                'MRp50_qiangpi': q0.get('metalreg_p50'), 'MRp50_custom': q1.get('metalreg_p50'),
                'MRp50_rise': round((q1.get('metalreg_p50') or 0) - (q0.get('metalreg_p50') or 0), 4),
                'subject_p50_custom': q1['subject_p50'],
                'subject_p50_ge_060': bool(q1['subject_p50'] >= 0.60),
                'gdansk_dark_pct': by.get('gdansk_shipyard_buildings02', {}).get('dark_share_pct'),
                'gdansk_MRp50': by.get('gdansk_shipyard_buildings02', {}).get('metalreg_p50'),
            }
            print('\n=== 达标线 ===')
            for k, v in rep['verdict'].items():
                print('  %-28s %s' % (k, v))
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(rep, open(os.path.join(HERE, '_tiers_20260921.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\nwrote _tiers_20260921.json')
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 10471)))
