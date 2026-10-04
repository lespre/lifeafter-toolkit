# -*- coding: utf-8 -*-
"""env_t6_final.py — T6 最终受控实验：固定布局 + 硬件 WebGL 后端 + A/B/C/D 各 2 次。

关键事实（env_t6_probe2/3 已证，见 E1p_steps.json / E1q_isolate.json）：
  * 在 SwiftShader（--disable-gpu）下，只要 UnrealBloomPass 处于 enabled=true，
    且 7 个链材质可见，整块 canvas 变全黑（strength=0 / threshold=0 也一样）；
    UnrealBloomPass.enabled=false 或绕过 composer 才出图。
  * snapshot()（RT readback，绕过 composer）在任何 bloom 设置下逐像素相同 → 完全看不到 bloom。
因此本实验改用**硬件 GL 后端**（不传 --disable-gpu/--enable-unsafe-swiftshader），并记录实际 GL renderer 字符串。

组定义（固定布局 __hidePanels(true)，窗口 1400x1000 不变）：
  A  = composer 保留 + UnrealBloomPass.enabled=false            （真正的“bloom 关”）
  B  = A 基础上 enabled=true, strength=0.55/radius=0.55/thr=0.8 （viewer.json 标定值）
  C  = B + renderer.toneMapping=NoToneMapping(0)                （判断是否 tone mapping 的锅）
  D  = 绕过 composer（直接 renderer.render）                     （判断 composer 通道本身改了什么）
每组 2 次；掩码在 A 组构建（weapon-only = prim0 ∪ prim4，口径同 neox_weapon_region.py）。
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
PORT = 9924
EVENTS, TOTAL = [], [0]

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

JS_GLINFO = r"""(function(){ try{ var r=window.__envRenderer; var gl=r.getContext();
  var dbg=gl.getExtension('WEBGL_debug_renderer_info');
  return JSON.stringify({version:gl.getParameter(gl.VERSION),vendor:gl.getParameter(gl.VENDOR),
    renderer:gl.getParameter(gl.RENDERER), unmasked:(dbg?gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL):null),
    dpr:r.getPixelRatio(), toneMapping:r.toneMapping, exposure:r.toneMappingExposure,
    passes:(window.__composer?window.__composer.passes.map(function(p){return {ctor:(p.constructor&&p.constructor.name)||'?',enabled:p.enabled,strength:(p.strength===undefined?null:p.strength)};}):null)}); }catch(e){ return 'EXC '+String(e&&e.message||e); } })()"""

JS_APPLY = r"""(function(mode){
  /* mode: 'A' | 'B' | 'C' | 'D' | 'D_off' */
  var EC=window.__ECMod, c=window.__composer, bp=window.__bloomPass, r=window.__envRenderer;
  if(!c) return 'no composer';
  if(window.__t6OrigRender===undefined){ window.__t6OrigRender=EC.EffectComposer.prototype.render; }
  EC.EffectComposer.prototype.render=window.__t6OrigRender;      // 先还原
  if(mode==='D'){ EC.EffectComposer.prototype.render=function(){ this.renderer.render(window.__envScene,window.__envCamera); }; }
  if(mode==='A'||mode==='D'){ if(bp){ bp.enabled=false; } }
  if(mode==='B'||mode==='C'||mode==='D'){ if(bp){ bp.enabled=true; bp.strength=0.55; bp.radius=0.55; bp.threshold=0.8; } }
  r.toneMapping=(mode==='C')?0:4;
  var passes=c.passes.map(function(p){ return {ctor:(p.constructor&&p.constructor.name)||'?',enabled:p.enabled,strength:(p.strength===undefined?null:p.strength),threshold:(p.threshold===undefined?null:p.threshold)}; });
  window.WikiWeaponViewer.canvasShot(2);
  return JSON.stringify({mode:mode, toneMapping:r.toneMapping, bypass:(mode==='D'), passes:passes});
})()"""


def lum_stats(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(float)
    lum = (0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]) / 255.0
    f = np.sort(lum.reshape(-1))
    n = len(f)
    return {'mean': round(float(f.mean()), 4), 'p50': round(float(f[int(.5 * (n - 1))]), 4),
            'p95': round(float(f[int(.95 * (n - 1))]), 4), 'max': round(float(f[-1]), 4),
            'pct_lt_002': round(float(100 * (f < 0.02).mean()), 2)}


def region_stats(path, mask):
    a = np.asarray(Image.open(path).convert('RGB')).astype(int)
    sel = a[mask]
    if len(sel) == 0:
        return {'n': 0}
    gold = silv = viol = 0
    L = []
    for (r, g, b) in sel:
        h, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
        deg = h * 360
        lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.
        L.append(lum)
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
    prof = os.path.join(OUT, '_profT6f')
    shutil.rmtree(prof, ignore_errors=True)
    args = [CHROME, '--headless=new', '--no-first-run', '--hide-scrollbars',
            '--force-device-scale-factor=1', '--window-size=1400,1000',
            '--use-angle=d3d11', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader',
            '--remote-debugging-port=%d' % PORT, '--user-data-dir=%s' % prof, 'about:blank']
    res['chrome_args'] = args[1:]
    pr = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(5)
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0
            pending = {}

            def on_event(m):
                TOTAL[0] += 1
                me = m.get('method'); p = m.get('params') or {}
                if me == 'Runtime.consoleAPICalled':
                    txt = ' '.join(str((a or {}).get('value', (a or {}).get('description', '')))[:1500] for a in (p.get('args') or []))
                    if 'ReadPixels' not in txt:
                        EVENTS.append({'t': p.get('type'), 'text': txt[:1500]})
                elif me == 'Log.entryAdded':
                    e = p.get('entry') or {}
                    if 'ReadPixels' not in str(e.get('text')):
                        EVENTS.append({'t': 'log/' + str(e.get('level')), 'text': str(e.get('text'))[:800]})

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
                    else:
                        on_event(m)
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
                """容错版本：解析失败时把原始返回值放进 _raw，不中断整轮。"""
                v = await ev(expr, wait)
                if isinstance(v, str):
                    try:
                        return json.loads(v)
                    except Exception:
                        return {'_raw': v[:300]}
                if isinstance(v, dict):
                    return v
                return {'_raw': repr(v)}

            async def rect():
                s = await ev("(function(){var c=window.__envRenderer&&window.__envRenderer.domElement;if(!c)return 'null';var r=c.getBoundingClientRect();return JSON.stringify({x:r.left,y:r.top,w:r.width,h:r.height,bw:c.width,bh:c.height});})()")
                try:
                    return json.loads(s)
                except Exception:
                    return None

            async def grab(tag):
                c = await rect()
                s = await send('Page.captureScreenshot', format='png',
                               clip={'x': c['x'], 'y': c['y'], 'width': c['w'], 'height': c['h'], 'scale': 1},
                               captureBeyondViewport=False)
                raw = base64.b64decode(s.get('data', ''))
                name = 'E1_%s_canvas.png' % tag
                open(os.path.join(OUT, name), 'wb').write(raw)
                return {'tag': tag, 'file': name, 'sha256_16': hashlib.sha256(raw).hexdigest()[:16], 'rect': c,
                        'lum': lum_stats(os.path.join(OUT, name))}

            async def snap(tag):
                d = await ev("JSON.stringify(window.WikiWeaponViewer.snapshot())")
                if not isinstance(d, str) or not d.startswith('{'):
                    return {'tag': tag, 'error': str(d)[:200]}
                sj = json.loads(d)
                raw = base64.b64decode(sj['png'].split(',', 1)[-1])
                name = 'E1_%s_snap.png' % tag
                open(os.path.join(OUT, name), 'wb').write(raw)
                sj.pop('png', None)
                return {'tag': tag, 'file': name, 'lum': lum_stats(os.path.join(OUT, name)), 'mean_rgb': sj.get('mean')}

            await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable')
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
            res['glinfo_before_hide'] = await evj(JS_GLINFO)
            await ev("window.WikiWeaponViewer.__hidePanels(true)", wait=2.0)
            for _ in range(20):
                a, b = await rect(), None
                await asyncio.sleep(0.5)
                b = await rect()
                if a == b:
                    break
            res['canvas_settled'] = await rect()

            # 掩码在 A 组（bloom off）下构建
            res['A_apply_masks'] = await evj(JS_APPLY + "('A')")
            await asyncio.sleep(1.0)
            await ev("window.__primOnly(-1)", wait=1.0)
            bg = await grab('MASK_bg')
            masks = {}
            for p in (0, 4):
                await ev("window.__primOnly(%d)" % p, wait=1.0)
                masks[p] = await grab('MASK_prim%d' % p)
            await ev("window.__primOnly(null)", wait=1.0)

            plan = ['A', 'B', 'C', 'D']
            caps = []
            for mode in plan:
                res['apply_%s' % mode] = await evj(JS_APPLY + "('%s')" % mode)
                await asyncio.sleep(1.2)
                for k in (1, 2):
                    await ev("window.WikiWeaponViewer.canvasShot(2)")
                    await asyncio.sleep(0.9)
                    g = await grab('%s_r%d' % (mode, k))
                    g['mode'] = mode
                    g['state'] = await evj(JS_GLINFO)
                    caps.append(g)
                    s = await snap('%s_r%d' % (mode, k))
                    s['mode'] = mode
                    caps.append(s)
            res['captures'] = caps
            res['events'] = EVENTS[:30]
            res['events_total'] = TOTAL[0]
    finally:
        try:
            pr.terminate()
        except Exception:
            pass

    # ---- 分析
    m_weapon = None
    try:
        bgimg = np.asarray(Image.open(os.path.join(OUT, bg['file'])).convert('RGB')).astype(int)
        m_weapon = np.zeros(bgimg.shape[:2], bool)
        for p in (0, 4):
            md = np.asarray(Image.open(os.path.join(OUT, masks[p]['file'])).convert('RGB')).astype(int)
            m_weapon |= (np.abs(md - bgimg).max(axis=2) > 24)
    except Exception as e:
        res['mask_error'] = str(e)
    ana = {'weapon_mask_px': int(m_weapon.sum()) if m_weapon is not None else 0}
    for c in res.get('captures', []):
        if not c.get('file') or not c.get('lum'):
            ana['%s_bad' % c.get('tag')] = {'_raw': str(c)[:220]}
            continue
        f = os.path.join(OUT, c['file'])
        row = {'file': c['file'], 'sha16': c.get('sha256_16') or c.get('sha'), 'lum': c.get('lum')}
        if m_weapon is not None and c['file'].endswith('_canvas.png'):
            try:
                row['weapon_only'] = region_stats(f, m_weapon)
            except Exception as e:
                row['weapon_only_error'] = str(e)
        ana['%s_%s' % (c.get('mode'), c.get('tag'))] = row
    res['analysis'] = ana
    res['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(OUT, 'E1_t6_final.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('viewer.js sha256', res['anchor']['viewer_js_sha256'])
    print('chrome args', ' '.join(res['chrome_args']))
    print('GL before hide:', json.dumps(res.get('glinfo_before_hide'), ensure_ascii=False))
    print('canvas settled:', json.dumps(res.get('canvas_settled'), ensure_ascii=False))
    print('weapon mask px =', ana.get('weapon_mask_px'))
    print()
    for c in res.get('captures', []):
        l = c.get('lum') or {}
        if not l:
            print('%-14s BAD %s' % (c.get('tag'), str(c)[:160])); continue
        print('%-14s %-6s %.4f/%.4f/%.4f  black%%=%.1f' % (c.get('tag'), 'canvas' if c['file'].endswith('_canvas.png') else 'snap',
              l['mean'], l['p50'], l['p95'], l['pct_lt_002']))
    print()
    print('== 组内均值（canvas 通道）')
    for mode in ('A', 'B', 'C', 'D'):
        rows = [ana[k] for k in ana if k.startswith(mode + '_') and 'weapon_only' in ana[k]]
        if not rows:
            continue
        print('  %-3s %s' % (mode, json.dumps(res.get('apply_%s' % mode, {}).get('passes'), ensure_ascii=False), ))
        for r in rows:
            w = r['weapon_only']
            print('      %-16s px=%-6d gold=%-6s silver=%-6s violet=%-6s p50=%-7s p95=%-7s meanL=%-7s | canvasMean=%.4f' % (
                r['file'].split('_')[-2], w['n'], w['gold'], w['silver'], w['violet'], w['p50'], w['p95'], w['meanL'], r['lum']['mean']))
    for mode in ('A', 'B', 'C', 'D'):
        sn = [c for c in res.get('captures', []) if c['mode'] == mode and c['file'].endswith('_snap.png')]
        if sn:
            print('  snapshot(%s):' % mode, ['%.4f/%.4f/%.4f' % (x['lum']['mean'], x['lum']['p50'], x['lum']['p95']) for x in sn])
    print('events:', res['events_total'], json.dumps(res.get('events')[:8], ensure_ascii=False)[:600])
    print('json:', os.path.join(OUT, 'E1_t6_final.json'), 'elapsed', res['elapsed_s'])


asyncio.run(main())
