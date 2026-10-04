# -*- coding: utf-8 -*-
"""_probe_envreach_20260921.py —— **环境可达性**判定（诊断用，不改任何文件、不是交付改动）。

问题：三档实测 dark% 只降 3.74pp（qiangpi→自造），而环境辐射抬了 ≈6×。
      是「6× 还不够」，还是「那批暗像素根本不由 cube 驱动」？
做法：固定 cube = custom_bright_20260921，用**既有**诊断 API `__cubeBrightApprox(k)`
      （源 `u_cube_brightness` 的近似接线，**默认关**、只乘在 radiance 出口）把环境辐射
      再放大到 k = 1 / 5 / 20 / 60 倍，看 dark% / MRp50 动不动。
判据：若 20×（乃至 60×）下 dark% 仍几乎不动 ⇒ 代理指标的暗分子**不由环境驱动**，
      换 cube 在结构上不可能达成「dark% 降 30pp」。
⚠ 本脚本的 k 只是**诊断探针**，不写文件、不进交付；交付档一律 k=1（= 不调用该 API）。
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

from PIL import Image
import websockets

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = r'E:\la拆包項目\03_执行\\30_分析\_target_1110025'.replace('項', '项')
sys.path.insert(0, TARGET)
from accept_1110025 import CDP, CHROME_CANDS, URL            # noqa: E402
from accept_brightness_1110025 import measure                # noqa: E402
from gi2_tiers_20260921 import metal_region                  # noqa: E402

SHOT = os.path.join(HERE, '_shots')
CUBE = 'custom_bright_20260921'
KS = [1.0, 5.0, 20.0, 60.0]


async def main(port):
    rep = {'cube': CUBE, 'note': 'diagnostic only; 交付档 k=1（不调用 __cubeBrightApprox）', 'rows': []}
    os.makedirs(SHOT, exist_ok=True)
    chrome = next((c for c in CHROME_CANDS if os.path.exists(c)), None)
    pr = subprocess.Popen([chrome, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--window-size=1240,900',
                           '--remote-debugging-port=%d' % port,
                           '--user-data-dir=%s' % os.path.join(os.environ.get('TEMP', '.'), 'er_%d' % port),
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
            await c.ev("window.WikiWeaponViewer.__cubeAB(%s)" % json.dumps(CUBE))
            await asyncio.sleep(3.5)
            for k in KS:
                if k <= 1.0:
                    await c.ev("window.WikiWeaponViewer.__cubeBrightApprox(null)")
                else:
                    await c.ev("window.WikiWeaponViewer.__cubeBrightApprox(%s)" % k)
                await asyncio.sleep(2.5)
                s = await c.send('Page.captureScreenshot', format='png')
                raw = base64.b64decode(s['data'])
                open(os.path.join(SHOT, 'ENVREACH_k%g.png' % k), 'wb').write(raw)
                im = Image.open(_io.BytesIO(raw))
                row = {'k': k, 'sha16': hashlib.sha256(raw).hexdigest()[:16]}
                row.update(measure(im))
                row.update(metal_region(im))
                rep['rows'].append(row)
                print('k=%-5g subj p50=%-7s MRp50=%-7s MRp95=%-7s dark%%=%-7s MR>085=%-6s sha16=%s'
                      % (k, row['subject_p50'], row.get('metalreg_p50'), row.get('metalreg_p95'),
                         row.get('dark_share_pct'), row.get('metalreg_gt085_pct'), row['sha16']), flush=True)
            await c.ev("window.WikiWeaponViewer.__cubeBrightApprox(null)")
            await asyncio.sleep(1.5)
        d = [r['dark_share_pct'] for r in rep['rows']]
        rep['verdict'] = {
            'dark_pct_by_k': d,
            'dark_pct_span_k1_to_kmax_pp': round(max(d) - min(d), 2),
            'env_drives_dark_pct': bool(max(d) - min(d) >= 5.0),
            'MRp50_by_k': [r.get('metalreg_p50') for r in rep['rows']],
            'subject_p50_by_k': [r['subject_p50'] for r in rep['rows']],
            'reading': ('span 很小 ⇒ 那批暗像素**不由环境驱动** ⇒ 「dark% 降 30pp」无法靠换 cube 达成'
                        if max(d) - min(d) < 5.0 else
                        'span 明显 ⇒ 环境可达，6× 不够是量的问题'),
        }
        print('\n=== 环境可达性 ===')
        for kk, vv in rep['verdict'].items():
            print('  %-34s %s' % (kk, vv))
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(rep, open(os.path.join(HERE, '_envreach_20260921.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('\nwrote _envreach_20260921.json')
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 10473)))
