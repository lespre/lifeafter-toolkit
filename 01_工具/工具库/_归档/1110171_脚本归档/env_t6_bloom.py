# -*- coding: utf-8 -*-
"""env_t6_bloom.py — T6 bloom 受控复核（只读项目文件，全部运行时改状态）

目的：在**固定布局**下重做 A/B/C 三组（各重复 2 次），回答“bloom 是否让高光向参考 p95=0.579 靠近”。

布局固定手段（整组一致）：
  1) Chrome 固定 --window-size=1400,1000 + --force-device-scale-factor=1；
  2) 取帧前调用项目自带的 `WikiWeaponViewer.__hidePanels(true)` 隐藏 .wv-params 与 .wv-tools；
  3) 每次取帧记录 canvas 的 CSS 尺寸 / 绘制缓冲尺寸，若不一致则整组作废（脚本会打印断言）。

bloom 控制：three r180 的 postprocessing 是 class + prototype 方法，用 import() 取同一模块实例
  后钩 UnrealBloomPass.prototype.render / EffectComposer.prototype.render 拿到真实实例，
  再运行时改 strength/radius/threshold 与 renderer.toneMapping（不写任何文件）。

口径（与 06_皮肤定位链\\neox_weapon_region.py 一致）：
  遮罩 = |__primOnly(0) 白模帧 − 背景帧| ∪ |__primOnly(4) 白模帧 − 背景帧|（weapon-only，prim0/4）
  判据 = HSV: gold 20-70°,silver s<0.13&v>0.18,violet 225-300°；亮度 Rec.709；p50/p95 为线性插值前的整序取值

输出：03拆包产物\\_target_1110171\\E1_*.png + E1_t6_bloom.json
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib, colorsys, io as _io, time
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PAGE = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1'
BASE = 'http://127.0.0.1:8765/assets/'
THREE_URL = BASE + 'vendor/three/three.module.min.js'
PP = BASE + 'vendor/three/addons/postprocessing/'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
REF = r'E:\la拆包项目\03拆包产物\render_1003_010\_ref_game_x7.png'
PORT = 9921
EVENTS, TOTAL = [], [0]


def stats(a, mask):
    """与 neox_weapon_region.py 完全一致的口径。"""
    sel = a[mask]
    if len(sel) == 0:
        return dict(n=0)
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
                p95=round(L[int(.95 * (n - 1))], 3),
                p99=round(L[int(.99 * (n - 1))], 3), lum_mean=round(float(np.mean(L)), 3))


JS_HOOK = r"""(async()=>{
  if(window.__t6Hooked) return 'already';
  const THREE=await import('%s');
  const O=THREE.Object3D.prototype, ob=O.onBeforeRender;
  O.onBeforeRender=function(r,s,c){ if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envCamera=c; window.__envScene=s; } return ob.apply(this,arguments); };
  const tv=O.traverse;
  O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
  const [EC,UBP,OP]=await Promise.all([import('%sEffectComposer.js'),import('%sUnrealBloomPass.js'),import('%sOutputPass.js')]);
  window.__ECMod=EC; window.__UBPMod=UBP;
  const oc=EC.EffectComposer.prototype.render;
  EC.EffectComposer.prototype.render=function(){ window.__composer=this; return oc.apply(this,arguments); };
  const ob2=UBP.UnrealBloomPass.prototype.render;
  UBP.UnrealBloomPass.prototype.render=function(){ window.__bloomPass=this; return ob2.apply(this,arguments); };
  const oo=OP.OutputPass.prototype.render;
  OP.OutputPass.prototype.render=function(){ window.__outputPass=this; return oo.apply(this,arguments); };
  window.__envTHREE=THREE; window.__t6Hooked=true; return 'hooked';
})()""" % (THREE_URL, PP, PP, PP)

JS_STATE = r"""(function(){
  var out={composer:!!window.__composer, bloomPass:!!window.__bloomPass,
           toneMapping:(window.__envRenderer?window.__envRenderer.toneMapping:null),
           exposure:(window.__envRenderer?window.__envRenderer.toneMappingExposure:null),
           passes:[]};
  if(window.__composer&&window.__composer.passes){ window.__composer.passes.forEach(function(p){
    out.passes.push({ctor:(p&&p.constructor&&p.constructor.name)||'?', enabled:(p?p.enabled:null),
      strength:(p&&p.strength!==undefined?p.strength:null), radius:(p&&p.radius!==undefined?p.radius:null),
      threshold:(p&&p.threshold!==undefined?p.threshold:null)}); }); }
  var cv=(window.__envRenderer?window.__envRenderer.domElement:null);
  if(cv){ var rc=cv.getBoundingClientRect();
    out.canvas={css:[Math.round(rc.left),Math.round(rc.top),Math.round(rc.width),Math.round(rc.height)],buffer:[cv.width,cv.height],dpr:window.devicePixelRatio}; }
  out.infoRender=(window.__envRenderer?JSON.parse(JSON.stringify(window.__envRenderer.info.render)):null);
  return JSON.stringify(out); })()"""

JS_SETBLOOM = r"""(function(s,r,t){ var c=window.__composer; if(!c) return 'no composer';
  var n=0,info=[]; c.passes.forEach(function(p){ if(p&&p.strength!==undefined){ p.strength=s;
      if(r!==null&&p.radius!==undefined)p.radius=r; if(t!==null&&p.threshold!==undefined)p.threshold=t; n++;
      info.push({ctor:(p.constructor&&p.constructor.name)||'?',strength:p.strength,radius:p.radius,threshold:p.threshold}); }
    else { info.push({ctor:(p&&p.constructor&&p.constructor.name)||'?',type:'no-strength-prop'}); } });
  return JSON.stringify({touched:n,passes:info}); })"""

JS_SETTONEMAP = r"""(function(v){ var r=window.__envRenderer; if(!r) return 'no renderer';
  if(window.__t6OrigTM===undefined) window.__t6OrigTM=r.toneMapping;
  r.toneMapping=v; return 'toneMapping='+r.toneMapping; })"""

def set_bloom(s, r, t):
    return JS_SETBLOOM + '(%s,%s,%s)' % (s, 'null' if r is None else r, 'null' if t is None else t)


def set_tonemap(v):
    return JS_SETTONEMAP + '(%d)' % v


def set_bypass(on):
    return JS_BYPASS + '(%s)' % ('true' if on else 'false')


JS_BYPASS = r"""(function(on){ var EC=window.__ECMod; if(!EC) return 'no module';
  if(on){ if(!window.__t6OrigComposerRender){ window.__t6OrigComposerRender=EC.EffectComposer.prototype.render; }
    EC.EffectComposer.prototype.render=function(){ this.renderer.render(window.__envScene,window.__envCamera); };
    return 'bypass-on'; }
  if(window.__t6OrigComposerRender){ EC.EffectComposer.prototype.render=window.__t6OrigComposerRender; return 'bypass-off'; }
  return 'noop'; })"""


async def main():
    t0 = time.time()
    viewer_js = urllib.request.urlopen(BASE + 'weapon_skin_viewer.js', timeout=20).read()
    viewer_json = urllib.request.urlopen(BASE + '3d/weapon_skin/1110171/viewer.json', timeout=20).read()
    res = {'anchor': {'viewer_js_sha256': hashlib.sha256(viewer_js).hexdigest(),
                      'viewer_json_sha256': hashlib.sha256(viewer_json).hexdigest(),
                      'viewer_json_bloom': json.loads(viewer_json.decode('utf-8')).get('material_layers', {}).get('global_rig', {}).get('bloom')},
           'captures': []}
    prof = os.path.join(OUT, '_profT6')
    shutil.rmtree(prof, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                           '--window-size=1400,1000', '--remote-debugging-port=%d' % PORT,
                           '--user-data-dir=%s' % prof, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0
            pending = {}

            def on_event(m):
                TOTAL[0] += 1
                me = m.get('method'); p = m.get('params') or {}
                if me == 'Runtime.consoleAPICalled':
                    txt = ' '.join(str((a or {}).get('value', (a or {}).get('description', '')))[:2000] for a in (p.get('args') or []))
                    EVENTS.append({'t': p.get('type'), 'text': txt[:2000]})
                elif me == 'Log.entryAdded':
                    e = p.get('entry') or {}
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
                    return 'EXC ' + str(r['exceptionDetails'].get('text'))[:300]
                if wait:
                    await asyncio.sleep(wait)
                return (r.get('result', {}) or {}).get('value')

            async def canvas_rect():
                s = await ev("(function(){var c=window.__envRenderer&&window.__envRenderer.domElement;"
                             "if(!c)return null;var r=c.getBoundingClientRect();"
                             "return JSON.stringify({x:r.left,y:r.top,w:r.width,h:r.height,bw:c.width,bh:c.height,dpr:window.devicePixelRatio});})()")
                return json.loads(s) if isinstance(s, str) and s.startswith('{') else None

            async def grab(tag, full=False):
                """canvas 裁切截图（度量用）；full=True 时另存整页图（留档）"""
                rect = await canvas_rect()
                clip = {'x': max(0.0, rect['x']), 'y': max(0.0, rect['y']), 'width': rect['w'], 'height': rect['h'], 'scale': 1}
                s = await send('Page.captureScreenshot', format='png', clip=clip, captureBeyondViewport=False)
                raw = base64.b64decode(s.get('data', ''))
                name = 'E1_%s_canvas.png' % tag
                open(os.path.join(OUT, name), 'wb').write(raw)
                rec = {'tag': tag, 'file': name, 'rect': rect, 'sha256_16': hashlib.sha256(raw).hexdigest()[:16],
                       'bytes': len(raw), 'state': json.loads(await ev(JS_STATE) or '{}')}
                if full:
                    s2 = await send('Page.captureScreenshot', format='png')
                    raw2 = base64.b64decode(s2.get('data', ''))
                    n2 = 'E1_%s_page.png' % tag
                    open(os.path.join(OUT, n2), 'wb').write(raw2)
                    rec['page_file'] = n2
                    rec['page_sha256_16'] = hashlib.sha256(raw2).hexdigest()[:16]
                res['captures'].append(rec)
                return rec

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
                            res['neox_applied'] = json.loads(st)['report']['applied']
                            break
                    except Exception:
                        pass
                await asyncio.sleep(2)
            await asyncio.sleep(5)

            # ---- hook（必须在 composer 首次 render 之前尽早钩；此处 composer 可能已存在，钩后仍能拿到实例）
            res['hook'] = await ev(JS_HOOK)
            await ev("window.WikiWeaponViewer.canvasShot(2)")
            await asyncio.sleep(1)
            res['post_true'] = await ev("JSON.stringify(window.WikiWeaponViewer.__post(true))", wait=2.5)
            await ev("window.WikiWeaponViewer.canvasShot(2)")
            await asyncio.sleep(1.0)
            res['default_state'] = json.loads(await ev(JS_STATE) or '{}')
            res['canvas_before_hide'] = await canvas_rect()

            # ---- 固定布局
            res['hide_panels'] = await ev("window.WikiWeaponViewer.__hidePanels ? window.WikiWeaponViewer.__hidePanels(true) : (window.__hidePanels?window.__hidePanels(true):'no api')")
            await asyncio.sleep(2.0)
            res['canvas_after_hide'] = await canvas_rect()
            for _ in range(20):
                r1 = await canvas_rect()
                await asyncio.sleep(0.5)
                r2 = await canvas_rect()
                if r1 == r2:
                    break
            res['canvas_settled'] = await canvas_rect()
            canvas_key = (res['canvas_settled']['bw'], res['canvas_settled']['bh'])

            # ---- 掩码（在 A 组强度 0 下建，避免 bloom 溢光污染遮罩）
            res['mask_setup'] = await ev(set_bloom(0, None, None))
            await ev("window.WikiWeaponViewer.canvasShot(2)")
            await asyncio.sleep(1.0)
            await ev("window.__primOnly(-1)")
            await ev("window.WikiWeaponViewer.canvasShot(2)")
            await asyncio.sleep(1.0)
            bg = await grab('MASK_bg')
            masks = {}
            for p in (0, 4):
                await ev("window.__primOnly(%d)" % p)
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                await asyncio.sleep(1.0)
                masks[p] = await grab('MASK_prim%d' % p)
            await ev("window.__primOnly(null)")
            await ev("window.WikiWeaponViewer.canvasShot(2)")
            await asyncio.sleep(1.0)

            # ---- A/B/C/D 三组（各 2 次）
            plan = [
                ('A_bloom0', 0.0, 4, False),
                ('B_bloom055', 0.55, 4, False),
                ('C_bloom055_noTM', 0.55, 0, False),
                ('D_nocomposer', 0.55, 4, True),
            ]
            for label, strength, tm, bypass in plan:
                if bypass:
                    res[label + '_bypass'] = await ev(set_bypass(True))
                else:
                    await ev(set_bypass(False))
                res[label + '_setbloom'] = json.loads(await ev(set_bloom(strength, 0.55 if strength > 0 else None, 0.8 if strength > 0 else None)))
                res[label + '_tonemap'] = await ev(set_tonemap(tm))
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                await asyncio.sleep(1.2)
                for k in (1, 2):
                    await ev("window.WikiWeaponViewer.canvasShot(2)")
                    await asyncio.sleep(0.8)
                    await grab('%s_r%d' % (label, k), full=(k == 1))
                res[label + '_state'] = json.loads(await ev(JS_STATE) or '{}')

            # ---- 还原
            res['restore_bypass'] = await ev(set_bypass(False))
            res['restore_bloom'] = await ev(set_bloom(0.55, 0.55, 0.8))
            res['restore_tonemap'] = await ev("(function(){var r=window.__envRenderer;var o=(window.__t6OrigTM===undefined?4:window.__t6OrigTM);r.toneMapping=o;return 'toneMapping='+r.toneMapping;})()")
            res['restore_hide'] = await ev("window.WikiWeaponViewer.__hidePanels ? window.WikiWeaponViewer.__hidePanels(false) : 'n/a'")
            res['events'] = [e for e in EVENTS if 'ReadPixels' not in str(e.get('text'))][:40]
            res['events_total'] = TOTAL[0]
    finally:
        try:
            pr.terminate()
        except Exception:
            pass

    # ---------------------------------------------------------------- 分析
    def load(n):
        return np.asarray(Image.open(os.path.join(OUT, n)).convert('RGB')).astype(int)

    ana = {}
    try:
        bgimg = load(bg['file'])
        m_weapon = np.zeros(bgimg.shape[:2], bool)
        for p in (0, 4):
            md = load(masks[p]['file'])
            m_weapon |= (np.abs(md - bgimg).max(axis=2) > 24)
        chain = [c for c in res['captures'] if c['tag'].startswith('A_bloom0_r')][0]
        chainimg = load(chain['file'])
        m_all = (np.abs(chainimg - bgimg).max(axis=2) > 24)
        ana['mask_px'] = {'weapon_only_prim0_4': int(m_weapon.sum()), 'all_prims': int(m_all.sum()),
                          'canvas_hw': list(bgimg.shape[:2])}
        sizes = {}
        for c in res['captures']:
            if not c['tag'].startswith('MASK_'):
                sizes[c['tag']] = [c['rect']['bw'], c['rect']['bh'], round(c['rect']['w']), round(c['rect']['h'])]
        ana['canvas_size_per_capture'] = sizes
        ana['canvas_size_identical'] = len(set(tuple(v) for v in sizes.values())) == 1
        for c in res['captures']:
            if c['tag'].startswith('MASK_'):
                continue
            img = load(c['file'])
            ana[c['tag']] = {'weapon_only': stats(img, m_weapon), 'all_prims': stats(img, m_all)}
        if os.path.exists(REF):
            ra = load(os.path.basename(REF)) if os.path.dirname(REF) == OUT else np.asarray(Image.open(REF).convert('RGB')).astype(int)
            ana['_ref_game_x7_whole_frame'] = stats(ra, np.ones(ra.shape[:2], bool))
        res['analysis'] = ana
    except Exception as e:
        res['analysis'] = {'error': str(e)}
    res['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(OUT, 'E1_t6_bloom.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---------------------------------------------------------------- 打印
    print('viewer.js sha256 =', res['anchor']['viewer_js_sha256'])
    print('viewer.json sha256 =', res['anchor']['viewer_json_sha256'], 'bloom =', json.dumps(res['anchor']['viewer_json_bloom'], ensure_ascii=False))
    print('neox applied =', res.get('neox_applied'), '| hook =', res.get('hook'), '| events', res.get('events_total'))
    print('默认状态 =', json.dumps(res.get('default_state'), ensure_ascii=False))
    print('canvas before hide =', json.dumps(res.get('canvas_before_hide'), ensure_ascii=False))
    print('canvas after hide  =', json.dumps(res.get('canvas_settled'), ensure_ascii=False))
    ana = res.get('analysis') or {}
    print('canvas 尺寸一致性 =', ana.get('canvas_size_identical'), json.dumps(ana.get('canvas_size_per_capture'), ensure_ascii=False))
    print('遮罩 =', json.dumps(ana.get('mask_px'), ensure_ascii=False))
    print()
    hdr = '%-22s %-6s %-7s %-8s %-8s %-8s %-7s %-7s %-7s' % ('capture', 'px', 'gold%', 'silver%', 'violet%', 'p50', 'p95', 'p99', 'meanL')
    for scope, key in (('weapon-only(prim0/4)', 'weapon_only'), ('all-prims', 'all_prims')):
        print('---', scope)
        print(hdr)
        for tag in sorted([k for k in ana if not k.startswith('_') and k not in ('mask_px', 'canvas_size_per_capture', 'canvas_size_identical')]):
            s = ana[tag].get(key) or {}
            if not s.get('n'):
                continue
            print('%-22s %-6d %-7s %-8s %-8s %-8s %-7s %-7s %-7s' % (tag, s['n'], s['gold'], s['silver'], s['violet'], s['p50'], s['p95'], s.get('p99'), s.get('lum_mean')))
    print('--- 参考图(png, 整帧):', json.dumps(ana.get('_ref_game_x7_whole_frame'), ensure_ascii=False))
    print('--- 每组状态')
    for label in ('A_bloom0', 'B_bloom055', 'C_bloom055_noTM', 'D_nocomposer'):
        print(' ', label, 'set=', json.dumps(res.get(label + '_setbloom'), ensure_ascii=False),
              '| tm=', res.get(label + '_tonemap'), '| bypass=', res.get(label + '_bypass'),
              '| passes=', json.dumps((res.get(label + '_state') or {}).get('passes'), ensure_ascii=False),
              '| info=', json.dumps((res.get(label + '_state') or {}).get('infoRender'), ensure_ascii=False))
    print('--- 控制台')
    for e in res.get('events') or []:
        print('  [%s] %s' % (e.get('t'), str(e.get('text'))[:300].replace('\n', ' | ')))
    print('--- json:', os.path.join(OUT, 'E1_t6_bloom.json'), 'elapsed', res['elapsed_s'])


asyncio.run(main())
