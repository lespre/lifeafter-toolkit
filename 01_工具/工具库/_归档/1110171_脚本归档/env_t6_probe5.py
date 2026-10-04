# -*- coding: utf-8 -*-
"""env_t6_probe5.py — 黑屏是否为 _forceRender(setSize) 人为造成？（只读，最后一问）

前面所有取帧都先调用 canvasShot(2)（内部先 r.setSize(...) 再 composer.render()）。
本轮在 bloom 开启时**不调用任何 _forceRender/canvasShot**，只靠页面自身 RAF 循环渲染，等 4s 后
直接 CDP 截图；再对比「先 canvasShot 再截图」。用来判定“bloom 全黑”是真实现象还是取帧 API 的副作用。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PAGE = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1'
BASE = 'http://127.0.0.1:8765/assets/'
THREE_URL = BASE + 'vendor/three/three.module.min.js'
PP = BASE + 'vendor/three/addons/postprocessing/'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9927

JS_HOOK = r"""(async()=>{
  if(window.__t6Hooked) return 'already';
  const THREE=await import('%s');
  const O=THREE.Object3D.prototype, ob=O.onBeforeRender;
  O.onBeforeRender=function(r,s,c){ if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envCamera=c; window.__envScene=s; } return ob.apply(this,arguments); };
  const tv=O.traverse; O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
  const [EC,UBP]=await Promise.all([import('%sEffectComposer.js'),import('%sUnrealBloomPass.js')]);
  const oc=EC.EffectComposer.prototype.render;
  EC.EffectComposer.prototype.render=function(){ window.__composer=this; return oc.apply(this,arguments); };
  const ob2=UBP.UnrealBloomPass.prototype.render;
  UBP.UnrealBloomPass.prototype.render=function(){ window.__bloomPass=this; return ob2.apply(this,arguments); };
  window.__envTHREE=THREE; window.__t6Hooked=true; return 'hooked'; })()""" % (THREE_URL, PP, PP)


def lum(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(float)
    l = (0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]) / 255.0
    f = np.sort(l.reshape(-1))
    n = len(f)
    return {'mean': round(float(f.mean()), 4), 'p50': round(float(f[int(.5 * (n - 1))]), 4),
            'p95': round(float(f[int(.95 * (n - 1))]), 4), 'pct_black': round(float(100 * (f < 0.02).mean()), 2)}


async def main():
    prof = os.path.join(OUT, '_profT6e')
    shutil.rmtree(prof, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
                           '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1400,1000',
                           '--remote-debugging-port=%d' % PORT, '--user-data-dir=%s' % prof, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    res = {'steps': []}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0
            pending = {}

            async def pump():
                while True:
                    try:
                        raw = await ws.recv()
                    except Exception:
                        return
                    m = json.loads(raw)
                    if 'id' in m:
                        f = pending.pop(m['id'], None)
                        if f and not f.done():
                            f.set_result(m)
            task = asyncio.create_task(pump())

            async def send(method, **params):
                nonlocal _i
                _i += 1
                fut = asyncio.get_event_loop().create_future()
                pending[_i] = fut
                await ws.send(json.dumps({'id': _i, 'method': method, 'params': params}))
                r = await asyncio.wait_for(fut, timeout=240)
                if 'error' in r:
                    raise RuntimeError('CDP %s -> %s' % (method, r['error']))
                return r.get('result', {})

            async def ev(expr, wait=0.0):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True, timeout=180000)
                if r.get('exceptionDetails'):
                    return 'EXC ' + str(r['exceptionDetails']['text'])[:200]
                if wait:
                    await asyncio.sleep(wait)
                return (r.get('result', {}) or {}).get('value')

            async def rect():
                s = await ev("(function(){var c=window.__envRenderer&&window.__envRenderer.domElement;if(!c)return 'null';var r=c.getBoundingClientRect();return JSON.stringify({x:r.left,y:r.top,w:r.width,h:r.height});})()")
                try:
                    return json.loads(s)
                except Exception:
                    return None

            async def shot(tag, force):
                if force:
                    await ev("window.WikiWeaponViewer.canvasShot(2)")
                await asyncio.sleep(MAXWAIT)   # 让页面自身 RAF 循环出帧
                c = await rect()
                s = await send('Page.captureScreenshot', format='png',
                               clip={'x': c['x'], 'y': c['y'], 'width': c['w'], 'height': c['h'], 'scale': 1},
                               captureBeyondViewport=False)
                raw = base64.b64decode(s.get('data', ''))
                n = 'E1e_%s_%s.png' % (tag, 'force' if force else 'nofore')
                open(os.path.join(OUT, n), 'wb').write(raw)
                rec = {'step': tag, 'forceRender': force, 'file': n, 'sha16': hashlib.sha256(raw).hexdigest()[:16], **lum(os.path.join(OUT, n))}
                res['steps'].append(rec)
                return rec

            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=PAGE)
            await asyncio.sleep(10)
            rel = 'assets/3d/weapon_skin/1110171'
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110171',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'});return 1;})()" % (rel, rel))
            for _ in range(45):
                st = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                if st and '"applied"' in st:
                    try:
                        if (json.loads(st).get('report') or {}).get('applied'):
                            res['applied'] = json.loads(st)['report']['applied']; break
                    except Exception:
                        pass
                await asyncio.sleep(2)
            await asyncio.sleep(5)
            res['hook'] = await ev(JS_HOOK)
            await ev("window.WikiWeaponViewer.__post(true)", wait=2.5)
            await ev("window.WikiWeaponViewer.__hidePanels(true)", wait=2.0)
            await ev("(function(){var bp=window.__bloomPass;if(bp){bp.enabled=true;bp.strength=0.55;bp.radius=0.55;bp.threshold=0.8;}return 'bloomON';})()", wait=1.0)

            MAXWAIT = 4.0
            await shot('bloomON', True)
            await shot('bloomON', False)
            await ev("(function(){window.__bloomPass.enabled=false;return 'bloomOFF';})()", wait=1.0)
            await shot('bloomOFF', False)
            await shot('bloomOFF', True)
            await ev("(function(){window.__bloomPass.enabled=true;return 'bloomON2';})()", wait=1.0)
            await shot('bloomON2', False)
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'E1e_forcetest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('applied', res.get('applied'), 'hook', res.get('hook'))
    print('%-14s %-6s %-8s %-8s %-8s %-9s %s' % ('step', 'force', 'mean', 'p50', 'p95', 'black%', 'file'))
    for s in res['steps']:
        print('%-14s %-6s %-8s %-8s %-8s %-9s %s' % (s['step'], s['forceRender'], s['mean'], s['p50'], s['p95'], s['pct_black'], s['file']))
    print('json:', os.path.join(OUT, 'E1e_forcetest.json'))


asyncio.run(main())
