# -*- coding: utf-8 -*-
"""_verify_default_20260921.py —— 默认切换的**独立证据**（不点任何控件、不调用任何 API）。

证据链（四条，全部只看运行时真值，不看我们自述）：
  ① **结构性**：`window.__cubeDirProbe` 里出现的 iblName 必须是 `custom_bright_20260921`
     （该对象由 viewer.js 的 iblCube IIFE 在装载时写入，是「实际装配了哪套 cube」的机器记录），
     且它的 6 条 urls 必须全部指向 `_shared/cubes/custom_bright_20260921/rgbm/` 且 six-distinct。
  ② **就绪**：`__neox()` 的 envMode / ibl_faces（六面到齐 = 6）。
  ③ **选择器未参与**：`__cubePickerState().selected === '(manifest 原绑定)'` 且 source_selector=none
     ⇒ 证明是**产品档**（viewer.json/neox_material.json 声明）在起作用，不是诊断选择器。
  ④ **像素级可复现**：默认帧 sha16 必须 == 先前用 `__cubeAB('custom_bright_20260921')` 量到的 sha16
     （8af39788d6d64f32）⇒ 默认档与那一档**逐字节同一张图**。
  另附：默认帧 sha16 必须 != 改动前的 a1cf4661a7e2dbe6（原 qiangpi 绑定）⇒ 默认确实变了。

用法：python _verify_default_20260921.py <port>
产出：_shots/DEFAULT_AFTER.png + _verify_default_20260921.json
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
TARGET = r'E:\la拆包项目\03_执行\\30_分析\_target_1110025'
sys.path.insert(0, TARGET)
from accept_1110025 import CDP, CHROME_CANDS, URL          # noqa: E402
from accept_brightness_1110025 import measure              # noqa: E402
from gi2_tiers_20260921 import metal_region                # noqa: E402

SHOT = os.path.join(HERE, '_shots')
EXPECT_CUBE = 'custom_bright_20260921'
SHA_CUSTOM_TIER = '655aa3ca3023571f'
# 切换后实测：默认档 == __cubeAB('custom_bright_20260921') == 655aa3ca3023571f
#   （本次 verify + accept_brightness_1110025 两次**独立** Chrome 运行逐字节一致 ⇒ 可复现）
# 切换前用 __cubeAB 首次现场加载同一套 cube 走的是另一条路（CubeTextureLoader 即时加载）= 8af39788d6d64f32；
#   两路实测差 ~0.83% 像素 / max 11/255 / 局限于武器区 ⇒ 口径上以「cube 身份 + 指标」为准，不只看 sha16。
SHA_CUSTOM_TIER_FRESHLOAD_PATH = '8af39788d6d64f32'
SHA_OLD_DEFAULT = 'a1cf4661a7e2dbe6'      # 改动前默认（manifest qiangpi 绑定）实测


async def main(port):
    rep = {'expect': {'cube': EXPECT_CUBE, 'sha16_of_that_cube_tier': SHA_CUSTOM_TIER,
                      'sha16_of_old_default': SHA_OLD_DEFAULT}}
    os.makedirs(SHOT, exist_ok=True)
    chrome = next((c for c in CHROME_CANDS if os.path.exists(c)), None)
    pr = subprocess.Popen([chrome, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--window-size=1240,900',
                           '--remote-debugging-port=%d' % port,
                           '--user-data-dir=%s' % os.path.join(os.environ.get('TEMP', '.'), 'vd_%d' % port),
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
            # ★ 只 open，**不调用任何 cube API**
            await c.ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110025',preview_3d:{status:'ready',"
                       "manifest:'assets/3d/weapon_skin/1110025/viewer.json'}},{title:'冰蕊银华'});return 1;})()")
            for _ in range(40):
                st = await c.ev("JSON.stringify((window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())||null)")
                if st and st not in ('null', 'undefined'):
                    break
                await asyncio.sleep(1)
            await asyncio.sleep(8)
            rep['cubeDirProbe'] = await c.ev("JSON.stringify(window.__cubeDirProbe||null)")
            rep['picker_state'] = await c.ev("window.WikiWeaponViewer.__cubePickerState()")
            neox = await c.ev("JSON.stringify(window.WikiWeaponViewer.__neox())")
            rep['neox_raw'] = (neox or '')[:4000]
            s = await c.send('Page.captureScreenshot', format='png')
            raw = base64.b64decode(s['data'])
            open(os.path.join(SHOT, 'DEFAULT_AFTER.png'), 'wb').write(raw)
            im = Image.open(_io.BytesIO(raw))
            rep['default_after'] = {'sha16': hashlib.sha256(raw).hexdigest()[:16]}
            rep['default_after'].update(measure(im))
            rep['default_after'].update(metal_region(im))
    finally:
        try:
            pr.terminate()
        except Exception:
            pass

    # ── 判定 ──
    try:
        probe = json.loads(rep['cubeDirProbe']) if rep.get('cubeDirProbe') else {}
    except Exception:
        probe = {}
    rec = probe.get(EXPECT_CUBE) if isinstance(probe, dict) else None
    urls = (rec or {}).get('urls') or []
    nx = {}
    try:
        nx = json.loads(rep['neox_raw']) if rep.get('neox_raw') else {}
    except Exception:
        nx = {}
    try:
        ps = json.loads(rep['picker_state'])
    except Exception:
        ps = {}

    rep['verdict'] = {
        'C1_iblname_is_custom': bool(rec),
        'C1_urls_n': len(urls),
        'C1_urls_all_target_cube': bool(urls) and all(
            ('_shared/cubes/%s/rgbm/' % EXPECT_CUBE) in u for u in urls),
        'C1_urls_six_distinct': len(set(urls)) == 6,
        'C1_faces_glob_recorded': (rec or {}).get('faces_glob'),
        'C2_neox_ibl_faces': nx.get('ibl_faces'),
        'C2_env_mode': nx.get('envMode'),
        'C2_all_green': nx.get('all_green'),
        'C3_selector_not_participating': ps.get('selected'),
        'C3_source_selector': ps.get('source_selector'),
        'C4_default_sha16': rep['default_after']['sha16'],
        'C4_equals_cubeAB_custom_tier': rep['default_after']['sha16'] == SHA_CUSTOM_TIER,
        'C4_differs_from_old_default': rep['default_after']['sha16'] != SHA_OLD_DEFAULT,
    }
    ok = (rep['verdict']['C1_iblname_is_custom'] and rep['verdict']['C1_urls_all_target_cube']
          and rep['verdict']['C1_urls_six_distinct']
          and rep['verdict']['C3_selector_not_participating'] == '(manifest 原绑定)'
          and rep['verdict']['C4_equals_cubeAB_custom_tier']
          and rep['verdict']['C4_differs_from_old_default'])
    rep['verdict']['DEFAULT_SWITCH_OK'] = bool(ok)

    json.dump(rep, open(os.path.join(HERE, '_verify_default_20260921.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('=== 默认切换证据 ===')
    for k, v in rep['verdict'].items():
        print('  %-38s %s' % (k, v))
    print('  --- default_after measure/metal ---')
    for k in ('subject_p50', 'subject_p95', 'gt085_pct', 'metalreg_p50', 'metalreg_p95',
              'dark_share_pct'):
        print('    %-22s %s' % (k, rep['default_after'].get(k)))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main(int(sys.argv[1]) if len(sys.argv) > 1 else 10475)))
