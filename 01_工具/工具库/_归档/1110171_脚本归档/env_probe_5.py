# -*- coding: utf-8 -*-
"""env_probe_5.py — 只读诊断（task-4 / env-auditor）：对**当前**viewer.js 修订做一次干净复核。

背景：viewer.js 于 2026-09-16 23:41:53 被其他成员改写（L950 起 __x → q_x、补声明 uIblStrength），
      env_probe_1/2/3 测的是改前修订（控制台含 '__rough' 保留标识符 ERROR），env_probe_4 测到的是改后。
      本轮从零启动，不做任何前置注入，只做一次干净读数 + 取证截图，并记录 viewer.js 的 sha256 作为修订锚点。

产出：env5_*.png + env_probe_5.json（含控制台事件、直渲 triangles、逐 prim 掩码与差异百分比）。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PAGE = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1'
VIEWER_URL = 'http://127.0.0.1:8765/assets/weapon_skin_viewer.js'
THREE_URL = 'http://127.0.0.1:8765/assets/vendor/three/three.module.min.js'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9915
EVENTS, TOTAL = [], [0]

JS_HOOK = r"""(async()=>{
  if(window.__envHooked) return 'already';
  const THREE=await import('%s');
  const O=THREE.Object3D.prototype, ob=O.onBeforeRender;
  O.onBeforeRender=function(r,s,c){ if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envCamera=c; window.__envScene=s; } return ob.apply(this,arguments); };
  const tv=O.traverse;
  O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
  window.__envTHREE=THREE; window.__envHooked=true; return 'hooked'; })()""" % THREE_URL

JS_DIRECT = r"""(function(){ var r=window.__envRenderer,s=window.__envScene,c=window.__envCamera; if(!r) return 'no r';
  try{ r.render(s,c); }catch(e){ return 'EXC '+e; } return JSON.stringify(JSON.parse(JSON.stringify(r.info.render))); })()"""

JS_FRAGINFO = r"""(function(){ var s=window.__envScene; if(!s) return JSON.stringify({error:'no scene'}); var out=[];
  s.traverse(function(o){ if(!o.isMesh) return; var m=o.material,u=(m.userData||{}); if(!u.__frag) return;
    var prim=(u.chain?u.chain.prim:null); if(out.some(function(x){return x.prim===prim;})) return;
    var f=u.__frag.split('\n'); var idx=-1; for(var i=0;i<f.length;i++){ if(f[i].indexOf('rough = max')>=0){ idx=i; break; } }
    out.push({prim:prim,totalLines:f.length,blockLine_1based:(idx>=0?idx+1:null),
      dunder:(f.join('\n').match(/__[A-Za-z_][A-Za-z0-9_]*/g)||[]).filter(function(v,i,a){return a.indexOf(v)===i;}),
      qvars:(f.join('\n').match(/\bq_[A-Za-z0-9_]*/g)||[]).filter(function(v,i,a){return a.indexOf(v)===i;}),
      declares_uIblStrength:/uniform float uIblStrength;/.test(f.join('\n')),
      block:(idx>=0?f.slice(idx,idx+12).join('\n'):null)}); });
  return JSON.stringify(out); })()"""

JS_ENVUNI = r"""(function(){ var s=window.__envScene; if(!s) return JSON.stringify({error:'no scene'}); var out=[];
  s.traverse(function(o){ if(!o.isMesh) return; var m=o.material,u=(m.userData||{}); var U=(u.__sh&&u.__sh.uniforms)||{};
    out.push({prim:(u.chain?u.chain.prim:null),matType:m.type,color:(m.color?'#'+m.color.getHexString():null),
      metalness:m.metalness,roughness:m.roughness,envMapIntensity:(m.envMapIntensity===undefined?null:m.envMapIntensity),
      mat_envMap:(m.envMap?(m.envMap.isCubeTexture?('CUBE '+String(m.envMap.uuid).slice(0,8)+' n='+(m.envMap.image&&m.envMap.image.length)):String(m.envMap.type)):null),
      map:(m.map?((m.map.image&&m.map.image.width)+'x'+(m.map.image&&m.map.image.height)+' '+(m.map.image&&m.map.image.currentSrc||'').split('/').slice(-1)[0]):null),
      metalnessMap:(m.metalnessMap?((m.metalnessMap.image&&m.metalnessMap.image.width)+'x'+(m.metalnessMap.image&&m.metalnessMap.image.height)):null),
      roughnessMap:(m.roughnessMap?((m.roughnessMap.image&&m.roughnessMap.image.width)+'x'+(m.roughnessMap.image&&m.roughnessMap.image.height)):null),
      normalMap:(m.normalMap?((m.normalMap.image&&m.normalMap.image.width)+'x'+(m.normalMap.image&&m.normalMap.image.height)):null),
      failClosedPlaceholder:!!u.failClosedPlaceholder,
      uniform_uCustomIbl:(U.uCustomIbl&&U.uCustomIbl.value?('CUBE n='+(U.uCustomIbl.value.image&&U.uCustomIbl.value.image.length)):null),
      uniform_uIblStrength:(U.uIblStrength?U.uIblStrength.value:null),
      uniform_envMapIntensity:(U.envMapIntensity?U.envMapIntensity.value:null)}); });
  return JSON.stringify(out); })()"""


def stats(path, mask=None):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.int32)
    px = a[mask] if mask is not None else a.reshape(-1, 3)
    lum = (0.299 * px[:, 0] + 0.587 * px[:, 1] + 0.114 * px[:, 2])
    return {'n': int(len(px)), 'mean': [round(float(px[:, 0].mean()), 1), round(float(px[:, 1].mean()), 1), round(float(px[:, 2].mean()), 1)],
            'lum_mean': round(float(lum.mean()), 2), 'lum_p50': round(float(np.percentile(lum, 50)), 1),
            'lum_p95': round(float(np.percentile(lum, 95)), 1), 'lum_max': round(float(lum.max()), 1),
            'pct_lum_lt16': round(float(100 * (lum < 16).mean()), 2),
            'pct_lum_gt245': round(float(100 * (lum > 245).mean()), 2),
            'sha16': hashlib.sha256(px.astype(np.uint8).tobytes()).hexdigest()[:16]}


async def main():
    viewer_sha = hashlib.sha256(urllib.request.urlopen(VIEWER_URL, timeout=20).read()).hexdigest()
    prof = os.path.join(OUT, '_profENV5')
    shutil.rmtree(prof, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                           '--window-size=1240,900', '--remote-debugging-port=%d' % PORT,
                           '--user-data-dir=%s' % prof, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    res = {'viewer_js_sha256_http': viewer_sha, 'states': {}}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0
            pending = {}

            def on_event(m):
                TOTAL[0] += 1
                me = m.get('method'); p = m.get('params') or {}
                if me == 'Runtime.consoleAPICalled':
                    txt = ' '.join(str((a or {}).get('value', (a or {}).get('description', '')))[:2500] for a in (p.get('args') or []))
                    EVENTS.append({'t': p.get('type'), 'text': txt[:2500]})
                elif me == 'Runtime.exceptionThrown':
                    d = (p.get('exceptionDetails') or {})
                    EVENTS.append({'t': 'exception', 'text': str(d.get('text'))[:300] + ' ' + str((d.get('exception') or {}).get('description'))[:800]})
                elif me == 'Log.entryAdded':
                    e = p.get('entry') or {}
                    EVENTS.append({'t': 'log/' + str(e.get('source')) + '/' + str(e.get('level')), 'text': str(e.get('text'))[:1000]})

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

            async def snap(tag):
                d = await ev("JSON.stringify(window.WikiWeaponViewer.snapshot())")
                if not isinstance(d, str) or not d.startswith('{'):
                    return {'error': str(d)[:300]}
                s = json.loads(d); raw = base64.b64decode(s['png'].split(',', 1)[-1])
                open(os.path.join(OUT, 'env5_%s.png' % tag), 'wb').write(raw)
                s.pop('png', None)
                s.update({'file': 'env5_%s.png' % tag, 'sha256_16': hashlib.sha256(raw).hexdigest()[:16]})
                return s

            async def cdpshot(tag):
                s = await send('Page.captureScreenshot', format='png')
                raw = base64.b64decode(s.get('data', ''))
                open(os.path.join(OUT, 'env5_%s.png' % tag), 'wb').write(raw)
                return {'file': 'env5_%s.png' % tag, 'sha256_16': hashlib.sha256(raw).hexdigest()[:16], 'bytes': len(raw)}

            await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable')
            await send('Page.navigate', url=PAGE)
            await asyncio.sleep(10)
            rel = 'assets/3d/weapon_skin/1110171'
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110171',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'});return 1;})()" % (rel, rel))
            for _ in range(40):
                st = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                if st and '"applied"' in st:
                    try:
                        if (json.loads(st).get('report') or {}).get('applied'):
                            res['report_applied'] = json.loads(st)['report']['applied']; break
                    except Exception:
                        pass
                await asyncio.sleep(2)
            await asyncio.sleep(6)
            res['hook'] = await ev(JS_HOOK)
            await ev("window.__primOnly(null)")
            await ev("window.WikiWeaponViewer.canvasShot(2)")
            await asyncio.sleep(1)
            res['post_fix_updates'] = await ev("JSON.stringify(window.WikiWeaponViewer.__post(false))")
            res['envuni'] = json.loads(await ev(JS_ENVUNI) or '[]')
            res['fraginfo'] = json.loads(await ev(JS_FRAGINFO) or '[]')
            res['direct_all_visible'] = await ev(JS_DIRECT)
            res['states']['DEF_chain'] = await snap('DEF_chain')
            res['shot_page'] = await cdpshot('page_default')
            res['masks'] = {}
            for i in range(7):
                await ev("window.__primOnly(%d)" % i)
                await asyncio.sleep(0.35)
                res['masks'][str(i)] = await snap('mask_%d' % i)
            await ev("window.__primOnly(null)")
            res['bg'] = await ev("(function(){var s=window.__envScene;window.__envHadOrigBg=1;window.__envOrigBg=s.background;s.background=new window.__envTHREE.Color(0xff00ff);return '#'+s.background.getHexString();})()")
            await ev(JS_DIRECT)
            res['states']['MAG_chain'] = await snap('MAG_chain')
            await ev("window.__primOnly(-1)")
            await ev(JS_DIRECT)
            res['direct_all_hidden'] = await ev(JS_DIRECT)
            res['states']['MAG_hidden'] = await snap('MAG_hidden')
            await ev("window.__primOnly(null)")
            await ev("(function(){window.__envScene.background=window.__envOrigBg;return 1;})()")
            await ev(JS_DIRECT)
            res['states']['DEF_chain_restored'] = await snap('DEF_chain_restored')
            res['console_events'] = EVENTS[:300]
            res['events_total'] = TOTAL[0]
    finally:
        try:
            pr.terminate()
        except Exception:
            pass

    def load(n):
        return np.asarray(Image.open(os.path.join(OUT, n)).convert('RGB')).astype(np.int32)

    analysis = {}
    try:
        masks = {}
        for i in range(7):
            m = res['masks'].get(str(i)) or {}
            if m.get('file'):
                a = load(m['file'])
                masks[i] = (a[:, :, 0] > 200) & (a[:, :, 1] > 200) & (a[:, :, 2] > 200)
        union = np.zeros(next(iter(masks.values())).shape, bool)
        for mk in masks.values():
            union |= mk
        analysis['mask_pixels'] = {str(i): int(mk.sum()) for i, mk in masks.items()}
        analysis['union_pixels'] = int(union.sum())
        ch = res['states'].get('MAG_chain') or {}
        hd = res['states'].get('MAG_hidden') or {}
        if ch.get('file') and hd.get('file'):
            a1, a2 = load(ch['file']), load(hd['file'])
            d = np.abs(a1 - a2).max(axis=2)
            analysis['MAG_chain_vs_hidden'] = {
                'diff_pct_union': round(100.0 * float((d[union] > 8).sum()) / max(1, int(union.sum())), 3),
                'per_prim_diff_pct': {str(i): round(100.0 * float((d[mk] > 8).sum()) / max(1, int(mk.sum())), 2) for i, mk in masks.items()},
                'whole_image_maxdiff': int(np.abs(a1 - a2).max())}
            analysis['MAG_chain_inside_union'] = stats(os.path.join(OUT, ch['file']), union)
            analysis['MAG_hidden_inside_union'] = stats(os.path.join(OUT, hd['file']), union)
        for tag in ('DEF_chain', 'DEF_chain_restored', 'MAG_chain'):
            st = res['states'].get(tag) or {}
            if st.get('file'):
                analysis[tag + '_whole'] = stats(os.path.join(OUT, st['file']))
    except Exception as e:
        analysis['error'] = str(e)
    res['analysis'] = analysis
    json.dump(res, open(os.path.join(OUT, 'env_probe_5.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('=== viewer.js sha256 (HTTP):', viewer_sha)
    print('=== hook', res['hook'], 'applied', res.get('report_applied'))
    print('=== direct all_visible', res.get('direct_all_visible'), ' all_hidden', res.get('direct_all_hidden'))
    print('=== envMap/纹理绑定（逐 prim）')
    for e in res.get('envuni') or []:
        print('  ', json.dumps(e, ensure_ascii=False))
    print('=== fraginfo')
    for e in res.get('fraginfo') or []:
        print('  prim', e.get('prim'), 'line', e.get('blockLine_1based'), 'dunder', e.get('dunder'), 'qvars', e.get('qvars'), 'declUblStrength', e.get('declares_uIblStrength'))
    print('=== 控制台（去重，跳过 ReadPixels）')
    seen = set()
    for e in res['console_events']:
        t = str(e.get('text', ''))
        if 'ReadPixels' in t:
            continue
        k = t[:70]
        if k in seen:
            continue
        seen.add(k)
        print('  [%s] %s' % (e.get('t'), t[:600].replace('\n', ' | ')))
    print('=== shot', res.get('shot_page'))
    print('=== analysis')
    print(json.dumps(res.get('analysis'), ensure_ascii=False, indent=1)[:4000])


asyncio.run(main())
