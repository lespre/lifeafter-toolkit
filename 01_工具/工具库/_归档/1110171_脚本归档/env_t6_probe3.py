# -*- coding: utf-8 -*-
"""env_t6_probe3.py — 隔离「composer 通道全黑」的责任 pass（只读，运行时开关）。

已在 env_t6_probe2 观测：
  * 全部 7 个链材质可见 + composer → canvas 全黑（lum_mean 1.58, 93.7% near-black）
  * __primOnly(-1)/__primOnly(0)（白模）→ composer 正常出图
  * 绕过 composer 直渲 → 正常出图
  * bloom strength 0/0.55、toneMapping 0/4 都不影响“黑”
本轮逐个禁用 pass（UnrealBloomPass.enabled=false / OutputPass.enabled=false / RenderPass 保留），
并用 snapshot()（绕过 composer 的 RT readback）作对照，判定责任环节，并确认 A/B 度量该用哪条通道。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib, colorsys
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PAGE = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1'
BASE = 'http://127.0.0.1:8765/assets/'
THREE_URL = BASE + 'vendor/three/three.module.min.js'
PP = BASE + 'vendor/three/addons/postprocessing/'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9923

JS_HOOK = r"""(async()=>{
  if(window.__t6Hooked) return 'already';
  const THREE=await import('%s');
  const O=THREE.Object3D.prototype, ob=O.onBeforeRender;
  O.onBeforeRender=function(r,s,c){ if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envCamera=c; window.__envScene=s; } return ob.apply(this,arguments); };
  const tv=O.traverse; O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
  const [EC,UBP,RP,OP]=await Promise.all([import('%sEffectComposer.js'),import('%sUnrealBloomPass.js'),import('%sRenderPass.js'),import('%sOutputPass.js')]);
  window.__ECMod=EC;
  const oc=EC.EffectComposer.prototype.render;
  EC.EffectComposer.prototype.render=function(){ window.__composer=this; return oc.apply(this,arguments); };
  const ob2=UBP.UnrealBloomPass.prototype.render;
  UBP.UnrealBloomPass.prototype.render=function(){ window.__bloomPass=this; return ob2.apply(this,arguments); };
  const orr=RP.RenderPass.prototype.render;
  RP.RenderPass.prototype.render=function(){ window.__renderPass=this; return orr.apply(this,arguments); };
  const oo=OP.OutputPass.prototype.render;
  OP.OutputPass.prototype.render=function(){ window.__outputPass=this; return oo.apply(this,arguments); };
  window.__envTHREE=THREE; window.__t6Hooked=true; return 'hooked'; })()""" % (THREE_URL, PP, PP, PP, PP)

JS_STATE = r"""(function(){
  window.WikiWeaponViewer.canvasShot(2);
  var r=window.__envRenderer; if(!r) return 'no renderer';
  var c=r.domElement, rc=c.getBoundingClientRect();
  var out={canvas:{x:rc.left,y:rc.top,w:rc.width,h:rc.height},
    toneMapping:r.toneMapping, exposure:r.toneMappingExposure,
    info:JSON.parse(JSON.stringify(r.info.render)),
    passes:(window.__composer?window.__composer.passes.map(function(p){return {ctor:(p.constructor&&p.constructor.name)||'?',enabled:p.enabled,strength:(p.strength===undefined?null:p.strength),threshold:(p.threshold===undefined?null:p.threshold)};}):null)};
  return JSON.stringify(out); })()"""

JS_TOGGLE = r"""(function(which,on){
  var map={bloom:window.__bloomPass, output:window.__outputPass, render:window.__renderPass};
  var p=map[which]; if(!p) return 'no '+which;
  p.enabled=!!on; return which+'='+p.enabled; })"""

JS_SETSTRENGTH = r"""(function(v){ var p=window.__bloomPass; if(!p) return 'no bloomPass'; p.strength=v; return 'strength='+p.strength; })"""
JS_SETTHRESHOLD = r"""(function(v){ var p=window.__bloomPass; if(!p) return 'no bloomPass'; p.threshold=v; return 'threshold='+p.threshold; })"""


def lum_stats(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(float)
    lum = (0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]) / 255.0
    f = lum.reshape(-1)
    f.sort()
    n = len(f)
    return {'mean': round(float(f.mean()), 4), 'p50': round(float(f[int(.5 * (n - 1))]), 4),
            'p95': round(float(f[int(.95 * (n - 1))]), 4), 'max': round(float(f[-1]), 4),
            'pct_lt_002': round(float(100 * (f < 0.02).mean()), 2)}


async def main():
    prof = os.path.join(OUT, '_profT6c')
    shutil.rmtree(prof, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                           '--window-size=1400,1000', '--remote-debugging-port=%d' % PORT,
                           '--user-data-dir=%s' % prof, 'about:blank'],
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
                    return 'EXC ' + str(r['exceptionDetails']['text'])[:250]
                if wait:
                    await asyncio.sleep(wait)
                return (r.get('result', {}) or {}).get('value')

            async def step(label, js=None):
                if js:
                    await ev(js)
                st = json.loads(await ev(JS_STATE) or '{}')
                rec = {'step': label, 'state': st}
                c = st.get('canvas')
                if c:
                    s = await send('Page.captureScreenshot', format='png',
                                   clip={'x': c['x'], 'y': c['y'], 'width': c['w'], 'height': c['h'], 'scale': 1},
                                   captureBeyondViewport=False)
                    raw = base64.b64decode(s.get('data', ''))
                    n1 = 'E1q_%s_canvas.png' % label
                    open(os.path.join(OUT, n1), 'wb').write(raw)
                    rec['canvas_file'], rec['canvas_stats'] = n1, lum_stats(os.path.join(OUT, n1))
                # snapshot() 通道（绕过 composer 的 RT readback）
                d = await ev("JSON.stringify(window.WikiWeaponViewer.snapshot())")
                if isinstance(d, str) and d.startswith('{'):
                    sj = json.loads(d)
                    raw = base64.b64decode(sj['png'].split(',', 1)[-1])
                    n2 = 'E1q_%s_snap.png' % label
                    open(os.path.join(OUT, n2), 'wb').write(raw)
                    sj.pop('png', None)
                    rec['snap_file'], rec['snap'] = n2, dict(sj, **{'lum': lum_stats(os.path.join(OUT, n2))})
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
            await asyncio.sleep(1.5)

            await step('00_default')
            await step('01_bloom_off_enabled_false', JS_TOGGLE + "(('bloom'),false)")
            await step('02_bloom_on_strength0', JS_TOGGLE + "(('bloom'),true)" )
            rec = await step('03_strength0', JS_SETSTRENGTH + '(0)')
            await step('04_strength055', JS_SETSTRENGTH + '(0.55)')
            await step('05_threshold0', JS_SETTHRESHOLD + '(0)')
            await step('06_output_off', JS_TOGGLE + "(('output'),false)")
            await step('07_bloom_off_again', JS_TOGGLE + "(('bloom'),false)")
            await step('08_all_on_restore', JS_TOGGLE + "(('output'),true)")
            await ev(JS_TOGGLE + "(('bloom'),true)")
            await ev(JS_SETSTRENGTH + '(0.55)')
            await ev(JS_SETTHRESHOLD + '(0.8)')
            await step('09_restored_default')
            await ev("window.__primOnly(-1)", wait=1.0)
            await step('10_allmeshes_hidden')
            await ev("window.__primOnly(null)", wait=1.0)
            await step('11_allmeshes_visible')
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'E1q_isolate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('applied', res.get('applied'), 'hook', res.get('hook'))
    print('%-26s %-34s %-34s %s' % ('step', 'canvas(lum mean/p50/p95)', 'snapshot(lum mean/p50/p95)', 'passes'))
    for s in res['steps']:
        c = s.get('canvas_stats') or {}
        sn = (s.get('snap') or {}).get('lum') or {}
        ps = s['state'].get('passes')
        ps = '|'.join('%s%s%s' % (p['ctor'][:6], '' if p['enabled'] else '!OFF', ('/%.2f' % p['strength']) if p['strength'] is not None else '') for p in (ps or []))
        print('%-26s %-34s %-34s %s' % (s['step'],
              '%.3f/%.3f/%.3f' % (c.get('mean', -1), c.get('p50', -1), c.get('p95', -1)),
              '%.3f/%.3f/%.3f' % (sn.get('mean', -1), sn.get('p50', -1), sn.get('p95', -1)), ps))
    print('json:', os.path.join(OUT, 'E1q_isolate.json'))


asyncio.run(main())
