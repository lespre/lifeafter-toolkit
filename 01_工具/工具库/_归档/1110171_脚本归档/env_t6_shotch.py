# -*- coding: utf-8 -*-
"""env_t6_shotch.py — 判定 bloom 输出到底该用哪条通道量（只读）。

背景：
  * CDP Page.captureScreenshot 在 SwiftShader 下：bloom pass enabled=true + 链材质可见 → canvas 全黑；
    enabled=false → 正常。硬件后端(ANGLE/D3D11, RTX5080)下：所有状态都黑（截图通道本身不可用）。
  * snapshot()（RT readback，绕过 composer）在任何 bloom 设置下逐像素相同 → 量不到 bloom。
本轮测第三条通道：项目自带 canvasShot()（= 渲染后立刻 canvas.toDataURL），它是 composer 的最终输出，
  且不经 CDP 合成器。若它在 bloom 打开时仍有内容，即可用它完成 A/B/C 度量。

输出：E1c_*.png（canvasShot 图与被裁切截图对照）+ E1c_shotch.json
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib, colorsys, time
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PAGE = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1'
BASE = 'http://127.0.0.1:8765/assets/'
THREE_URL = BASE + 'vendor/three/three.module.min.js'
PP = BASE + 'vendor/three/addons/postprocessing/'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9925

JS_HOOK = r"""(async()=>{
  if(window.__t6Hooked) return 'already';
  const THREE=await import('%s');
  const O=THREE.Object3D.prototype, ob=O.onBeforeRender;
  O.onBeforeRender=function(r,s,c){ if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envCamera=c; window.__envScene=s; } return ob.apply(this,arguments); };
  const tv=O.traverse; O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
  const [EC,UBP]=await Promise.all([import('%sEffectComposer.js'),import('%sUnrealBloomPass.js')]);
  window.__ECMod=EC;
  const oc=EC.EffectComposer.prototype.render;
  EC.EffectComposer.prototype.render=function(){ window.__composer=this; return oc.apply(this,arguments); };
  const ob2=UBP.UnrealBloomPass.prototype.render;
  UBP.UnrealBloomPass.prototype.render=function(){ window.__bloomPass=this; return ob2.apply(this,arguments); };
  window.__envTHREE=THREE; window.__t6Hooked=true; return 'hooked'; })()""" % (THREE_URL, PP, PP)

JS_APPLY = r"""(function(mode){
  var c=window.__composer, bp=window.__bloomPass, r=window.__envRenderer;
  if(!c) return 'no composer';
  if(bp){ bp.enabled=(mode!=='A'); if(mode!=='A'){ bp.strength=0.55; bp.radius=0.55; bp.threshold=0.8; } }
  r.toneMapping=(mode==='C')?0:4;
  window.WikiWeaponViewer.canvasShot(2);
  return JSON.stringify({mode:mode, toneMapping:r.toneMapping,
    passes:c.passes.map(function(p){return {ctor:(p.constructor&&p.constructor.name)||'?',enabled:p.enabled,strength:(p.strength===undefined?null:p.strength)};})}); })"""


def lum(path_or_bytes):
    a = np.asarray(Image.open(path_or_bytes).convert('RGB')).astype(float)
    l = (0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]) / 255.0
    f = np.sort(l.reshape(-1))
    n = len(f)
    return {'h': a.shape[0], 'w': a.shape[1], 'mean': round(float(f.mean()), 4), 'p50': round(float(f[int(.5 * (n - 1))]), 4),
            'p95': round(float(f[int(.95 * (n - 1))]), 4), 'max': round(float(f[-1]), 4),
            'pct_lt_002': round(float(100 * (f < 0.02).mean()), 2)}


def region(path, mask):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    m = mask
    if a.shape[:2] != m.shape[:2]:
        h = min(a.shape[0], m.shape[0]); w = min(a.shape[1], m.shape[1])
        a = a[:h, :w]; m = m[:h, :w]
    sel = a[m]
    if len(sel) == 0:
        return {'n': 0}
    gold = silv = viol = 0
    L = []
    for (r, g, b) in sel:
        hh, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
        deg = hh * 360
        lumv = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.
        L.append(lumv)
        if 20 <= deg <= 70 and s > 0.20 and v > 0.12:
            gold += 1
        elif 225 <= deg <= 300 and s > 0.18 and v > 0.12:
            viol += 1
        elif s < 0.13 and v > 0.18:
            silv += 1
    n = len(sel)
    L.sort()
    return dict(n=n, gold=round(100 * gold / n, 2), silver=round(100 * silv / n, 2),
                violet=round(100 * viol / n, 2), p50=round(L[int(.5 * (n - 1))], 3),
                p95=round(L[int(.95 * (n - 1))], 3), p99=round(L[int(.99 * (n - 1))], 3),
                meanL=round(float(np.mean(L)), 3))


async def main():
    t0 = time.time()
    res = {'anchor': {'viewer_js_sha256': hashlib.sha256(urllib.request.urlopen(BASE + 'weapon_skin_viewer.js', timeout=20).read()).hexdigest()}}
    prof = os.path.join(OUT, '_profT6s')
    shutil.rmtree(prof, ignore_errors=True)
    args = [CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
            '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1400,1000',
            '--remote-debugging-port=%d' % PORT, '--user-data-dir=%s' % prof, 'about:blank']
    res['chrome_args'] = args[1:]
    pr = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
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

            async def evj(expr, wait=0.0):
                v = await ev(expr, wait)
                if isinstance(v, str):
                    try:
                        return json.loads(v)
                    except Exception:
                        return {'_raw': v[:200]}
                return v if isinstance(v, dict) else {'_raw': repr(v)}

            async def rect():
                s = await ev("(function(){var c=window.__envRenderer&&window.__envRenderer.domElement;if(!c)return 'null';var r=c.getBoundingClientRect();return JSON.stringify({x:r.left,y:r.top,w:r.width,h:r.height});})()")
                try:
                    return json.loads(s)
                except Exception:
                    return None

            async def shot_canvas(tag):
                """canvasShot() = 渲染后立刻 canvas.toDataURL（composer 的最终输出，不经 CDP 合成器）"""
                d = await ev("window.WikiWeaponViewer.canvasShot(2)")
                if not isinstance(d, str) or not d.startswith('data:image'):
                    return {'tag': tag, 'error': str(d)[:200]}
                raw = base64.b64decode(d.split(',', 1)[1])
                name = 'E1c_%s_toDataURL.png' % tag
                open(os.path.join(OUT, name), 'wb').write(raw)
                return {'tag': tag, 'file': name, 'sha16': hashlib.sha256(raw).hexdigest()[:16], **lum(os.path.join(OUT, name))}

            async def shot_cdp(tag):
                c = await rect()
                s = await send('Page.captureScreenshot', format='png',
                               clip={'x': c['x'], 'y': c['y'], 'width': c['w'], 'height': c['h'], 'scale': 1},
                               captureBeyondViewport=False)
                raw = base64.b64decode(s.get('data', ''))
                name = 'E1c_%s_cdpshot.png' % tag
                open(os.path.join(OUT, name), 'wb').write(raw)
                return {'tag': tag, 'file': name, 'sha16': hashlib.sha256(raw).hexdigest()[:16], **lum(os.path.join(OUT, name))}

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
            res['apply_A'] = await evj(JS_APPLY + "('A')")

            # 掩码：A 状态（bloom 关）下的 canvasShot 通道
            res['caps'] = []
            await ev("window.__primOnly(-1)", wait=1.0)
            bg = await shot_canvas('MASK_bg')
            res['caps'].append(bg)
            masks = {}
            for p in (0, 4):
                await ev("window.__primOnly(%d)" % p, wait=1.0)
                masks[p] = await shot_canvas('MASK_prim%d' % p)
                res['caps'].append(masks[p])
            await ev("window.__primOnly(null)", wait=1.0)

            for mode in ('A', 'B', 'C'):
                res['apply_' + mode] = await evj(JS_APPLY + "('%s')" % mode)
                await asyncio.sleep(1.0)
                for k in (1, 2):
                    res['caps'].append(await shot_canvas('%s_r%d' % (mode, k)))
                    res['caps'].append(await shot_cdp('%s_r%d' % (mode, k)))
                    await asyncio.sleep(0.3)
            # 每组再取一次 snapshot() 作对照
            for mode in ('A', 'B', 'C'):
                d = await ev("JSON.stringify(window.WikiWeaponViewer.snapshot())")
                if isinstance(d, str) and d.startswith('{'):
                    sj = json.loads(d)
                    raw = base64.b64decode(sj['png'].split(',', 1)[1])
                    n = 'E1c_%s_snapshot.png' % mode
                    open(os.path.join(OUT, n), 'wb').write(raw)
                    res['caps'].append({'tag': '%s_snapshot' % mode, 'file': n, 'sha16': hashlib.sha256(raw).hexdigest()[:16], **lum(os.path.join(OUT, n))})
    finally:
        try:
            pr.terminate()
        except Exception:
            pass

    # ---- 掩码与组内统计（统一口径：weapon-only = prim0 ∪ prim4）
    try:
        bgimg = np.asarray(Image.open(os.path.join(OUT, bg['file'])).convert('RGB')).astype(int)
        mask = np.zeros(bgimg.shape[:2], bool)
        for p in (0, 4):
            md = np.asarray(Image.open(os.path.join(OUT, masks[p]['file'])).convert('RGB')).astype(int)
            mask |= (np.abs(md - bgimg).max(axis=2) > 24)
        res['mask_px'] = int(mask.sum())
        for c in res['caps']:
            if c.get('file') and not c['file'].endswith('MASK_prim0_toDataURL.png'):
                try:
                    c['weapon_only'] = region(os.path.join(OUT, c['file']), mask)
                except Exception as e:
                    c['weapon_only_error'] = str(e)
    except Exception as e:
        res['mask_error'] = str(e)
    res['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(OUT, 'E1c_shotch.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('viewer.js sha', res['anchor']['viewer_js_sha256'], '| applied', res.get('applied'), '| hook', res.get('hook'))
    print('mask_px =', res.get('mask_px'), res.get('mask_error', ''))
    print('%-34s %-8s %-8s %-8s %-8s %-8s' % ('capture', 'mean', 'p50', 'p95', 'max', 'black%'))
    for c in res['caps']:
        if 'mean' in c:
            print('%-34s %-8s %-8s %-8s %-8s %-8s %s' % (c['tag'], c['mean'], c['p50'], c['p95'], c['max'], c['pct_lt_002'],
                  ('wpx=%d gold=%s silver=%s violet=%s p50=%s p95=%s' % (c['weapon_only']['n'], c['weapon_only']['gold'], c['weapon_only']['silver'], c['weapon_only']['violet'], c['weapon_only']['p50'], c['weapon_only']['p95'])) if c.get('weapon_only') else (c.get('error') or c.get('weapon_only_error') or '')))
        else:
            print('%-34s ERR %s' % (c.get('tag'), c.get('error')))
    for m in ('A', 'B', 'C'):
        print('apply_%s =' % m, json.dumps(res.get('apply_' + m), ensure_ascii=False))
    print('json:', os.path.join(OUT, 'E1c_shotch.json'), 'elapsed', res['elapsed_s'])


asyncio.run(main())
