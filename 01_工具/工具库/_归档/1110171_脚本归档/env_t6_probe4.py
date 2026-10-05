# -*- coding: utf-8 -*-
"""env_t6_probe4.py — 黑屏责任链收口：UnrealBloomPass + 链材质 → 是否由注入的源 IBL 项导致（只读）。

已知：SwiftShader 下 UnrealBloomPass.enabled=true 且 7 个链材质可见 → canvas 100% 黑；
      enabled=false 或全部 mesh 隐藏 → 正常。本轮在 bloom 保持开启的前提下，逐项把
      onBeforeCompile 注入的源 IBL 项清零（运行时改 uniform，不改文件），看画面是否恢复。
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
PORT = 9926

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

JS_SET = r"""(function(what,val){
  var s=window.__envScene; if(!s) return 'no scene';
  var n=0, keys=[];
  s.traverse(function(o){ if(!o.isMesh) return; var m=o.material; if(!m) return;
    if(what==='iblstrength'){ var u=m.userData&&m.userData.__sh&&m.userData.__sh.uniforms;
      if(u&&u.uIblStrength){ u.uIblStrength.value=val; n++; } }
    else if(what==='envmapintensity'){ m.envMapIntensity=val; m.needsUpdate=true; n++; }
    else if(what==='bloom'){ if(window.__bloomPass){ window.__bloomPass.enabled=(val===1); n++; } }
    else if(what==='onbeforecompile'){ if(typeof m.onBeforeCompile==='function'){ m.onBeforeCompile=function(){}; m.customProgramCacheKey=function(){return 'noinj_'+String(m.uuid).slice(0,8);}; m.needsUpdate=true; n++; } }
  });
  window.WikiWeaponViewer.canvasShot(2);
  return JSON.stringify({what:what,val:val,touched:n}); })"""


def lum(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(float)
    l = (0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]) / 255.0
    f = np.sort(l.reshape(-1))
    n = len(f)
    return {'mean': round(float(f.mean()), 4), 'p50': round(float(f[int(.5 * (n - 1))]), 4),
            'p95': round(float(f[int(.95 * (n - 1))]), 4), 'pct_black': round(float(100 * (f < 0.02).mean()), 2)}


async def main():
    prof = os.path.join(OUT, '_profT6d')
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

            async def step(label, js=None):
                applied = None
                if js:
                    applied = await ev(js)
                    await asyncio.sleep(1.2)
                    await ev("window.WikiWeaponViewer.canvasShot(2)")
                    await asyncio.sleep(0.8)
                d = await ev("window.WikiWeaponViewer.canvasShot(2)")
                rec = {'step': label, 'applied': applied}
                if isinstance(d, str) and d.startswith('data:image'):
                    raw = base64.b64decode(d.split(',', 1)[1])
                    n = 'E1d_%s_toDataURL.png' % label
                    open(os.path.join(OUT, n), 'wb').write(raw)
                    rec.update({'file': n, 'sha16': hashlib.sha256(raw).hexdigest()[:16], **lum(os.path.join(OUT, n))})
                else:
                    rec['error'] = str(d)[:200]
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
            await ev("(function(){var bp=window.__bloomPass;if(bp){bp.enabled=true;bp.strength=0.55;bp.radius=0.55;bp.threshold=0.8;}return 'bloom on';})()", wait=1.0)

            await step('00_bloom_on_chain')
            await step('01_iblstrength_0', JS_SET + "(('iblstrength'),0)")
            await step('02_iblstrength_back_1', JS_SET + "(('iblstrength'),1)")
            await step('03_bloom_off', JS_SET + "(('bloom'),0)")
            await step('04_bloom_on_again', JS_SET + "(('bloom'),1)")
            await step('05_no_onbeforecompile', JS_SET + "(('onbeforecompile'),1)")
            await step('06_reshow_iblstrength0', JS_SET + "(('iblstrength'),0)")
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'E1d_ibl_bloom.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('applied', res.get('applied'), 'hook', res.get('hook'))
    print('%-24s %-8s %-8s %-8s %-9s %s' % ('step', 'mean', 'p50', 'p95', 'black%', 'applied'))
    for s in res['steps']:
        if 'mean' in s:
            print('%-24s %-8s %-8s %-8s %-9s %s' % (s['step'], s['mean'], s['p50'], s['p95'], s['pct_black'], str(s.get('applied'))[:80]))
        else:
            print('%-24s ERR %s' % (s['step'], s.get('error')))
    print('json:', os.path.join(OUT, 'E1d_ibl_bloom.json'))


asyncio.run(main())
