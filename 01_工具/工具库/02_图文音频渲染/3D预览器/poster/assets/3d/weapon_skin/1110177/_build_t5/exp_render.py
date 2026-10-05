# -*- coding: utf-8 -*-
"""T5-fix 渲染/度量：加载 1110177，截图 + 全局色彩度量 + __chainMats 证据。

用法：python exp_render.py <tag>
输出：_target_1110171\\S177_<tag>.png（线索指定的截图位置）
      <skin>/_build_t5/S177_<tag>.png（副本）+ _t5_exp_<tag>.json
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib, sys
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1'
SHOTDIR = r'E:\la拆包项目\03_执行\\30_分析\_target_1110171'
HERE = os.path.dirname(os.path.abspath(__file__))
REL = 'assets/3d/weapon_skin/1110177'
PORT = 9876


def metrics(a):
    a = a.astype(np.int16)
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    n = a.shape[0] * a.shape[1]
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    blue = int(((B > R + 30) & (B > G + 20) & (B > 110)).sum())
    warm = int(((R > B + 30) & (R > 120)).sum())
    red = int(((R > 110) & (R > G + 50) & (R > B + 50)).sum())
    silver = int(((abs(R - G) < 25) & (abs(G - B) < 25) & (lum > 120)).sum())
    return {'mean': [round(float(x), 1) for x in a.reshape(-1, 3).mean(0)],
            'blue_frac': round(100.0 * blue / n, 2), 'warm_frac': round(100.0 * warm / n, 2),
            'red_frac': round(100.0 * red / n, 2), 'silver_frac': round(100.0 * silver / n, 2),
            'bright_frac': round(100.0 * float((lum > 100).mean()), 2)}


async def main(tag):
    prof = os.path.join(HERE, '_profcam')
    shutil.rmtree(prof, ignore_errors=True)
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                          '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                          '--window-size=1400,950', '--remote-debugging-port=%d' % PORT,
                          '--user-data-dir=%s' % prof, 'about:blank'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    out = {'tag': tag}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            i = {'n': 0}; pend = {}

            async def rd():
                try:
                    async for raw in ws:
                        m = json.loads(raw)
                        if 'id' in m: pend[m['id']] = m
                except Exception: pass
            t = asyncio.create_task(rd())

            async def send(method, **pp):
                i['n'] += 1; k = i['n']
                await ws.send(json.dumps(dict(id=k, method=method, params=pp)))
                for _ in range(900):
                    if k in pend: return pend.pop(k).get('result', {})
                    await asyncio.sleep(0.02)
                return {}

            async def ev(e):
                r = await send('Runtime.evaluate', expression=e, returnByValue=True, awaitPromise=True)
                if r.get('exceptionDetails'): return 'EXC ' + str(r['exceptionDetails'].get('text'))[:300]
                return (r.get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=URL); await asyncio.sleep(10)
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110177',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'极光剑'});return 1;})()" % (REL, REL))
            nx = None
            for _ in range(45):
                nx = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                if nx and 'applied' in str(nx): break
                await asyncio.sleep(2)
            await asyncio.sleep(16)
            out['neox'] = str(nx)[:120]
            out['chainMats'] = await ev("JSON.stringify(window.__chainMats&&window.__chainMats())")
            out['crystalOBC'] = await ev("JSON.stringify(window.__crystalOBCInfo||null)")
            out['useDetail'] = await ev("String(window.WikiWeaponViewer.__useDetailFlag||'')")
            await ev("(()=>{document.querySelectorAll('.wv-poster,.wv-loading,.wv-status,.wv-tools,.wv-params,.wv-tabs,.wv-cam').forEach(e=>e.style.display='none');return 1;})()")
            await asyncio.sleep(1)
            # 首选 snapshot()：渲染进 WebGLRenderTarget 后 readPixels，与 headless 合成器无关
            await ev("try{window.WikiWeaponViewer.canvasShot(3);}catch(e){}")
            await asyncio.sleep(1)
            raw = None
            sh = await ev("JSON.stringify(window.WikiWeaponViewer.snapshot&&window.WikiWeaponViewer.snapshot())")
            try:
                sd = json.loads(sh or '{}')
            except Exception:
                sd = {}
            out['snapshot_meta'] = {k: sd.get(k) for k in ('w', 'h', 'mean', 'magenta_pct', 'gray_pct', 'error')}
            if sd.get('png'):
                raw = base64.b64decode(sd['png'].split(',', 1)[-1])
            if raw is None:
                s = await send('Page.captureScreenshot', format='png',
                               clip=dict(x=100, y=90, width=1190, height=740, scale=1))
                if 'data' in s:
                    raw = base64.b64decode(s['data'])
                else:
                    out['shot_error'] = str(s)[:200]
            if raw is not None:
                a = np.asarray(Image.open(__import__('io').BytesIO(raw)).convert('RGB'))
                name = 'S177_%s.png' % tag
                open(os.path.join(SHOTDIR, name), 'wb').write(raw)
                if os.path.isdir(HERE):
                    open(os.path.join(HERE, name), 'wb').write(raw)
                out['shot'] = {'file': name, 'sha16': hashlib.sha256(raw).hexdigest()[:16],
                               'shape': list(a.shape), 'bytes': len(raw)}
                out['metrics'] = metrics(a)
            # 每 prim 隔离取值（判据：各 prim 的可见材质/是否注入）
            out['chainMats2'] = await ev("JSON.stringify(window.__chainMats&&window.__chainMats())")
            t.cancel()
    finally:
        try: p.terminate()
        except Exception: pass
    json.dump(out, open(os.path.join(HERE, '_t5_exp_%s.json' % tag), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'chainMats'}, ensure_ascii=False, indent=1))
    print('chainMats head:', str(out.get('chainMats'))[:900])


asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'v1'))
