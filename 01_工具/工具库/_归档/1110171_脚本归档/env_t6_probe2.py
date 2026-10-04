# -*- coding: utf-8 -*-
"""env_t6_probe2.py — 找出「composer 通道输出全黑」的触发步骤（T6 前置诊断，只读）。

env_t6_bloom.py 现象：MASK 阶段（__primOnly 状态）画面正常，A/B/C 阶段（全部 mesh 可见 + composer）
canvas 全黑；D 阶段（绕过 composer 直渲）画面正常。本轮逐步施加每个操作，每步都取
  ① Page.captureScreenshot(clip=canvas)  的均值/最大亮度
  ② canvas 矩形 + renderer.info.render
  ③ 覆盖层体检：elementFromPoint(canvas 中心) 的 selector、.wv-loading/.wv-poster/.wv-params 的 display/opacity
以定位是「画布真的黑」还是「被覆盖层挡住」还是「截图通道问题」。
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
PORT = 9922

JS_HOOK = r"""(async()=>{
  if(window.__t6Hooked) return 'already';
  const THREE=await import('%s');
  const O=THREE.Object3D.prototype, ob=O.onBeforeRender;
  O.onBeforeRender=function(r,s,c){ if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envCamera=c; window.__envScene=s; } return ob.apply(this,arguments); };
  const tv=O.traverse; O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
  const [EC,UBP,OP]=await Promise.all([import('%sEffectComposer.js'),import('%sUnrealBloomPass.js'),import('%sOutputPass.js')]);
  window.__ECMod=EC;
  const oc=EC.EffectComposer.prototype.render;
  EC.EffectComposer.prototype.render=function(){ window.__composer=this; return oc.apply(this,arguments); };
  const ob2=UBP.UnrealBloomPass.prototype.render;
  UBP.UnrealBloomPass.prototype.render=function(){ window.__bloomPass=this; return ob2.apply(this,arguments); };
  window.__envTHREE=THREE; window.__t6Hooked=true; return 'hooked'; })()""" % (THREE_URL, PP, PP, PP)

JS_PROBE = r"""(function(){
  var out={};
  try{ window.WikiWeaponViewer.canvasShot(2); }catch(e){ out.shotErr=String(e&&e.message||e); }
  var r=window.__envRenderer, c=r&&r.domElement;
  if(c){ var rc=c.getBoundingClientRect();
    out.canvas={x:rc.left,y:rc.top,w:rc.width,h:rc.height,bw:c.width,bh:c.height};
    var cx=Math.round(rc.left+rc.width/2), cy=Math.round(rc.top+rc.height/2);
    var el=document.elementFromPoint(cx,cy);
    out.hit={tag:(el&&el.tagName)||null, cls:(el&&el.className)||null, id:(el&&el.id)||null,
             isCanvas:!!(el&&el===c)};
    out.stack=(function(){ var a=[],e=el; while(e&&a.length<5){ a.push((e.tagName||'?')+'.'+String(e.className||'').replace(/\s+/g,'')); e=e.parentElement; } return a; })();
  }
  out.overlays={};
  ['.wv-loading','.wv-poster','.wv-params','.wv-tools','.wv-canvas','.wv-dialog'].forEach(function(sel){
    var e=document.querySelector(sel); if(!e) { out.overlays[sel]=null; return; }
    var s=getComputedStyle(e);
    out.overlays[sel]={display:s.display,visibility:s.visibility,opacity:s.opacity,zIndex:s.zIndex,
      bg:s.backgroundColor,w:Math.round(e.getBoundingClientRect().width),h:Math.round(e.getBoundingClientRect().height),
      rect:[Math.round(e.getBoundingClientRect().left),Math.round(e.getBoundingClientRect().top)]};
  });
  var p=document.querySelector('.wv-poster');
  out.poster={src:(p&&p.getAttribute('src'))||null, complete:(p?p.complete:null), nw:(p?p.naturalWidth:null)};
  out.scrollY=window.scrollY; out.viewport=[window.innerWidth,window.innerHeight];
  out.info=r?JSON.parse(JSON.stringify(r.info.render)):null;
  out.passes=(function(){ if(!window.__composer) return null; return window.__composer.passes.map(function(p){ return {ctor:(p.constructor&&p.constructor.name)||'?', enabled:p.enabled, strength:(p.strength===undefined?null:p.strength)}; }); })();
  out.toneMapping=r?r.toneMapping:null;
  out.glLost=(function(){ try{ return r.getContext().isContextLost(); }catch(e){ return 'err'; } })();
  return JSON.stringify(out); })()"""


def img_stats(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(float)
    lum = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]
    return {'mean': [round(float(x), 1) for x in a.reshape(-1, 3).mean(0)],
            'lum_mean': round(float(lum.mean()), 2), 'lum_max': round(float(lum.max()), 1),
            'pct_near_black': round(float(100 * (lum < 4).mean()), 2),
            'uniq_est': int(len(np.unique(a.reshape(-1, 3)[::17], axis=0)))}


async def main():
    prof = os.path.join(OUT, '_profT6b')
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
                    return 'EXC ' + str(r['exceptionDetails'].get('text'))[:300]
                if wait:
                    await asyncio.sleep(wait)
                return (r.get('result', {}) or {}).get('value')

            async def step(label, extra_js=None):
                if extra_js:
                    await ev(extra_js)
                info = json.loads(await ev(JS_PROBE) or '{}')
                rec = {'step': label, 'probe': info}
                c = info.get('canvas')
                if c:
                    clip = {'x': c['x'], 'y': c['y'], 'width': c['w'], 'height': c['h'], 'scale': 1}
                    s = await send('Page.captureScreenshot', format='png', clip=clip, captureBeyondViewport=False)
                    raw = base64.b64decode(s.get('data', ''))
                    name = 'E1p_%s_canvas.png' % label
                    open(os.path.join(OUT, name), 'wb').write(raw)
                    rec['file'] = name
                    rec['sha'] = hashlib.sha256(raw).hexdigest()[:16]
                    rec['stats'] = img_stats(os.path.join(OUT, name))
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
            await asyncio.sleep(2.0)
            await step('00_default')
            await ev("window.WikiWeaponViewer.__hidePanels(true)", wait=2.0)
            await step('01_hidepanels')
            await step('02_hidepanels_again')
            await ev("window.__primOnly(-1)", wait=1.0)
            await step('03_primOnly_minus1')
            await ev("window.__primOnly(0)", wait=1.0)
            await step('04_primOnly_0')
            await ev("window.__primOnly(null)", wait=1.0)
            await step('05_primOnly_null')
            await ev("(function(){var p=window.__composer;if(!p)return 'nc';p.passes.forEach(function(q){if(q.strength!==undefined)q.strength=0;});return 'set0';})()", wait=1.0)
            await step('06_bloom0')
            await ev("(function(){var p=window.__composer;if(!p)return 'nc';p.passes.forEach(function(q){if(q.strength!==undefined)q.strength=0.55;});return 'set055';})()", wait=1.0)
            await step('07_bloom055')
            await ev("(function(){var r=window.__envRenderer;r.toneMapping=0;return 'tm0';})()", wait=1.5)
            await step('08_nomapping')
            await ev("(function(){var r=window.__envRenderer;r.toneMapping=4;return 'tm4';})()", wait=1.5)
            await step('09_tm4')
            await ev("(function(){var EC=window.__ECMod;window.__t6o=EC.EffectComposer.prototype.render;"
                     "EC.EffectComposer.prototype.render=function(){this.renderer.render(window.__envScene,window.__envCamera);};return 'bypass';})()", wait=1.5)
            await step('10_bypass')
            await ev("(function(){var EC=window.__ECMod;EC.EffectComposer.prototype.render=window.__t6o;return 'restore';})()", wait=1.5)
            await step('11_restore_composer')
            await ev("window.WikiWeaponViewer.__hidePanels(false)", wait=2.0)
            await step('12_showpanels')
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'E1p_steps.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('applied', res.get('applied'), 'hook', res.get('hook'))
    for s in res['steps']:
        p = s['probe']
        print('%-24s canvas=%s hit=%s stack=%s' % (s['step'], json.dumps(p.get('canvas')), json.dumps(p.get('hit'), ensure_ascii=False), json.dumps(p.get('stack'), ensure_ascii=False)))
        print('      stats=%s' % json.dumps(s.get('stats', {}), ensure_ascii=False))
        print('      overlays=%s' % json.dumps(p.get('overlays'), ensure_ascii=False)[:600])
        print('      poster=%s passes=%s tm=%s glLost=%s info=%s' % (json.dumps(p.get('poster'), ensure_ascii=False), json.dumps(p.get('passes'), ensure_ascii=False), p.get('toneMapping'), p.get('glLost'), json.dumps(p.get('info'))))
        if p.get('shotErr'):
            print('      shotErr=%s' % p['shotErr'])
    print('json:', os.path.join(OUT, 'E1p_steps.json'))


asyncio.run(main())
