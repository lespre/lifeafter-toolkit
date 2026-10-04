# -*- coding: utf-8 -*-
"""env_probe_4.py — 只读诊断（task-4 / env-auditor）第四轮：直渲取证 + envMap uniform 归属 + 重命名对照。

承接 env_probe_3 的结论（链材质状态与「全部 mesh 隐藏」逐像素完全相同 → 完全未绘制），本轮补：
  1. 用 window.__envRenderer.render(scene,camera) 直接渲染主场景（跳过 composer/bloom），
     读取 renderer.info.render 的 triangles/calls —— 作为“几何是否被提交”的独立读数。
  2. 三类运行时对照（均在内存中改材质，不写文件、不新增配色）：
       T0 原始链材质（注入块含 __ 标识符）
       T1 去注入  m.onBeforeCompile=()=>{}          → 证明“不可见由注入块导致”
       T2 重命名  __x→_x 的同一注入块（公式逐字不变）→ 证明“仅标识符名违规”
     背景在 T1/T2 阶段临时设为洋红 0xff00ff 以便分辨“黑”与“没画”。
  3. 查 envMap uniform 的实际来源：material.envMap（源 cube）还是 scene.environment（棚光 PMREM）。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1'
THREE_URL = 'http://127.0.0.1:8765/assets/vendor/three/three.module.min.js'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9914
EVENTS, NET_BAD, TOTAL = [], [], [0]

# 与 viewer.js L938-948 注入块逐字一致，仅把保留的 '__x' 改成 '_x'
FIXED_BLOCK = (
    '  float _rough = max(roughnessFactor, 0.0019);\n'
    '  float _lod = 5.0 + 1.2 * log2(_rough);\n'
    '  vec3  _R  = reflect(normalize(vViewPosition), normal);\n'
    '  float _c = cos(uIblRot), _s2 = sin(uIblRot);\n'
    '  vec3  _Rr = vec3(_R.x*_s2 + _R.z*_c, _R.y, -_R.x*_c + _R.z*_s2);\n'
    '  vec4  _sm = textureLod(uCustomIbl, _Rr, _lod);\n'
    '  vec3  _L  = pow(_sm.rgb * _sm.a * 16.0, vec3(2.0)).xyz;\n'
    '  vec3  _Lc = min(_L, vec3(1.5));\n'
    '  vec3  _env= _L + uIblMix * (_Lc * 0.299805 - _L);\n'
    '  _env *= uIblScale;\n'
    '  gl_FragColor.rgb += _env * uIblStrength;\n')

JS_HOOK = r"""(async()=>{
  if(window.__envHooked) return 'already';
  const THREE=await import('%s');
  const O=THREE.Object3D.prototype;
  const ob=O.onBeforeRender;
  O.onBeforeRender=function(r,s,c){ if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envCamera=c; window.__envScene=s; } return ob.apply(this,arguments); };
  const tv=O.traverse;
  O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
  window.__envTHREE=THREE; window.__envHooked=true;
  return JSON.stringify({threeRev:(THREE.REVISION||null),rendererProtoRender:typeof THREE.WebGLRenderer.prototype.render});
})()""" % THREE_URL

JS_DIRECT = r"""(function(){ var r=window.__envRenderer,s=window.__envScene,c=window.__envCamera;
  if(!r||!s||!c) return 'ERR no handles';
  try{ r.render(s,c); }catch(e){ return 'EXC '+String(e&&e.message||e); }
  return JSON.stringify({info:JSON.parse(JSON.stringify(r.info.render)),programs:(r.info.programs?r.info.programs.length:null)}); })()"""

JS_ENVUNI = r"""(function(){ var s=window.__envScene; if(!s) return JSON.stringify({error:'no scene'}); var out=[];
  s.traverse(function(o){ if(!o.isMesh) return; var m=o.material, u=(m.userData||{});
    if(!u.__sh||!u.__sh.uniforms) return; var U=u.__sh.uniforms; var v=U.envMap?U.envMap.value:null;
    out.push({prim:(u.chain?u.chain.prim:null),
      mat_envMap:(m.envMap?(m.envMap.isCubeTexture?('CUBE '+String(m.envMap.uuid).slice(0,8)+' n='+(m.envMap.image&&m.envMap.image.length)):String(m.envMap.type)):null),
      mat_envMapIntensity:(m.envMapIntensity===undefined?null:m.envMapIntensity),
      uniform_envMap:(v?(v.isCubeTexture?('CUBE '+String(v.uuid).slice(0,8)):('2D '+String(v.uuid).slice(0,8)+' '+((v.image&&v.image.width)||0)+'x'+((v.image&&v.image.height)||0)+' mapping='+v.mapping)):null),
      uniform_envMapIntensity:(U.envMapIntensity?U.envMapIntensity.value:null),
      uniform_uCustomIbl:((U.uCustomIbl&&U.uCustomIbl.value)?('CUBE '+(U.uCustomIbl.value.image&&U.uCustomIbl.value.image.length)):null)});
  });
  return JSON.stringify(out); })()"""

JS_NOINJECT = r"""(function(){ var s=window.__envScene; if(!s) return 'no scene'; var n=0,list=[];
  s.traverse(function(o){ if(!o.isMesh) return; var m=o.material; if(!m) return; var u=m.userData||{}; if(!(u.chain||u.neox)) return;
    if(typeof m.onBeforeCompile==='function'){ m.onBeforeCompile=function(){}; n++; list.push(u.chain?u.chain.prim:null); }
    m.customProgramCacheKey=function(){ return 'noinject_'+String(m.uuid).slice(0,8); }; m.needsUpdate=true; });
  return JSON.stringify({patched:n,prims:list}); })()"""

JS_FIXINJECT = r"""(function(){ var s=window.__envScene; if(!s) return 'no scene';
  var cube=null; s.traverse(function(o){ if(!cube&&o.isMesh&&o.material&&o.material.envMap&&o.material.envMap.isCubeTexture) cube=o.material.envMap; });
  var BLOCK=%s;
  var n=0;
  s.traverse(function(o){ if(!o.isMesh) return; var m=o.material; if(!m) return; var u=m.userData||{}; if(!(u.chain||u.neox)) return;
    var ct=(m.envMap&&m.envMap.isCubeTexture)?m.envMap:cube;
    (function(mat,ctv){ mat.onBeforeCompile=function(sh){
        if(ctv) sh.uniforms.uCustomIbl={value:ctv};
        sh.uniforms.uIblStrength={value:1.0}; sh.uniforms.uIblRot={value:0.0};
        sh.uniforms.uIblMix={value:0.0};     sh.uniforms.uIblScale={value:1.0};
        sh.fragmentShader='uniform samplerCube uCustomIbl;\nuniform float uIblRot;\nuniform float uIblMix;\nuniform float uIblScale;\n'+sh.fragmentShader;
        sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>', BLOCK+'#include <dithering_fragment>');
        if(mat.userData){ mat.userData.__frag2=sh.fragmentShader; } }; })(m,ct);
    m.customProgramCacheKey=function(){ return 'fixedibl_'+String(m.uuid).slice(0,8); };
    m.needsUpdate=true; n++; });
  return JSON.stringify({patched:n,cube_found:!!cube,cube_uuid:cube?String(cube.uuid).slice(0,8):null,block_lines:BLOCK.split('\n').length}); })()""" % json.dumps(FIXED_BLOCK)


def stats(path, mask=None):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.int32)
    px = a[mask] if mask is not None else a.reshape(-1, 3)
    if len(px) == 0:
        return {'n': 0}
    lum = (0.299 * px[:, 0] + 0.587 * px[:, 1] + 0.114 * px[:, 2])
    return {'n': int(len(px)), 'mean': [round(float(px[:, 0].mean()), 1), round(float(px[:, 1].mean()), 1), round(float(px[:, 2].mean()), 1)],
            'lum_mean': round(float(lum.mean()), 2), 'lum_p50': round(float(np.percentile(lum, 50)), 1),
            'lum_p95': round(float(np.percentile(lum, 95)), 1), 'lum_max': round(float(lum.max()), 1),
            'pct_lum_lt16': round(float(100 * (lum < 16).mean()), 2),
            'sha16': hashlib.sha256(px.astype(np.uint8).tobytes()).hexdigest()[:16]}


async def main():
    prof = os.path.join(OUT, '_profENV4')
    shutil.rmtree(prof, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                           '--window-size=1240,900', '--remote-debugging-port=%d' % PORT,
                           '--user-data-dir=%s' % prof, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    res = {'states': {}}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0
            pending = {}

            def on_event(m):
                TOTAL[0] += 1
                me = m.get('method'); p = m.get('params') or {}
                if me == 'Runtime.consoleAPICalled':
                    txt = ' '.join(str((a or {}).get('value', (a or {}).get('description', '')))[:3000] for a in (p.get('args') or []))
                    EVENTS.append({'t': p.get('type'), 'text': txt[:3000]})
                elif me == 'Runtime.exceptionThrown':
                    d = (p.get('exceptionDetails') or {})
                    EVENTS.append({'t': 'exception', 'text': str(d.get('text'))[:300] + ' ' + str((d.get('exception') or {}).get('description'))[:800]})
                elif me == 'Log.entryAdded':
                    e = p.get('entry') or {}
                    EVENTS.append({'t': 'log/' + str(e.get('source')) + '/' + str(e.get('level')), 'text': str(e.get('text'))[:1000]})
                elif me == 'Network.responseReceived':
                    r_ = p.get('response') or {}
                    if int(r_.get('status', 200)) >= 400:
                        NET_BAD.append({'status': r_.get('status'), 'url': r_.get('url')})
                elif me == 'Network.loadingFailed':
                    NET_BAD.append({'failed': str(p.get('errorText')), 'requestId': p.get('requestId')})

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
                s = json.loads(d)
                raw = base64.b64decode(s['png'].split(',', 1)[-1])
                open(os.path.join(OUT, 'env4_%s.png' % tag), 'wb').write(raw)
                s.pop('png', None)
                s.update({'file': 'env4_%s.png' % tag, 'sha256_16': hashlib.sha256(raw).hexdigest()[:16], 'bytes': len(raw)})
                return s

            async def cdpshot(tag):
                s = await send('Page.captureScreenshot', format='png')
                raw = base64.b64decode(s.get('data', ''))
                open(os.path.join(OUT, 'env4_%s.png' % tag), 'wb').write(raw)
                return {'file': 'env4_%s.png' % tag, 'sha256_16': hashlib.sha256(raw).hexdigest()[:16], 'bytes': len(raw)}

            await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable'); await send('Network.enable')
            await send('Page.navigate', url=URL)
            await asyncio.sleep(10)
            rel = 'assets/3d/weapon_skin/1110171'
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110171',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'});return 1;})()" % (rel, rel))
            for _ in range(40):
                st = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                if st and '"applied"' in st:
                    try:
                        if (json.loads(st).get('report') or {}).get('applied'):
                            res['chain_report_applied'] = json.loads(st)['report']['applied']; break
                    except Exception:
                        pass
                await asyncio.sleep(2)
            await asyncio.sleep(6)
            res['hook'] = await ev(JS_HOOK)
            await ev("window.__primOnly(null)")
            await ev("window.WikiWeaponViewer.canvasShot(2)")
            await asyncio.sleep(1)
            res['scene_ok'] = bool(await ev("!!window.__envScene"))

            # ---- 掩码
            res['masks'] = {}
            for i in range(7):
                await ev("window.__primOnly(%d)" % i)
                await asyncio.sleep(0.35)
                res['masks'][str(i)] = await snap('mask_%d' % i)
            await ev("window.__primOnly(null)")
            await asyncio.sleep(0.4)

            # ---- T0 原始链材质：直渲 + 读数
            res['T0_direct_info'] = await ev(JS_DIRECT)
            res['T0_shot'] = await cdpshot('T0_page_chain')
            res['T0_snap'] = await snap('T0_snapshot_chain')
            res['envuni_before'] = json.loads(await ev(JS_ENVUNI) or '[]')
            # envMap uniform 归属：临时把 scene.environment 置 null
            res['sceneEnv_orig'] = await ev("(function(){var s=window.__envScene; if(!window.__envOrigEnvSet){window.__envOrigEnvSet=1;window.__envOrigEnv=s.environment;} s.environment=null; return s.environment===null;})()")
            await ev(JS_DIRECT)
            res['envuni_sceneEnvNull'] = json.loads(await ev(JS_ENVUNI) or '[]')
            await ev("(function(){window.__envScene.environment=window.__envOrigEnv; return !!window.__envScene.environment;})()")

            # ---- 全隐藏基线（默认背景 + 洋红背景）
            await ev("window.__primOnly(-1)"); await asyncio.sleep(0.4)
            res['T0h_direct_info'] = await ev(JS_DIRECT)
            res['states']['T0_default_hidden'] = await snap('T0_default_hidden')
            res['bg'] = await ev("(function(){var s=window.__envScene;window.__envHadOrigBg=1;window.__envOrigBg=s.background;s.background=new window.__envTHREE.Color(0xff00ff);return '#'+s.background.getHexString();})()")
            await ev(JS_DIRECT)
            res['states']['T0_magenta_hidden'] = await snap('T0_magenta_hidden')
            await ev("window.__primOnly(null)"); await asyncio.sleep(0.3)
            res['T0m_direct_info'] = await ev(JS_DIRECT)
            res['states']['T0_magenta_chain'] = await snap('T0_magenta_chain')
            res['T0m_shot'] = await cdpshot('T0_page_magenta_chain')

            # ---- T1 去注入
            ev_idx = len(EVENTS)
            res['T1_patch'] = await ev(JS_NOINJECT)
            await asyncio.sleep(0.6)
            res['T1_direct_info'] = await ev(JS_DIRECT)
            await asyncio.sleep(0.4)
            res['states']['T1_magenta_noinject'] = await snap('T1_magenta_noinject')
            res['T1_events'] = [e for e in EVENTS[ev_idx:] if 'ReadPixels' not in str(e.get('text'))][:20]
            res['T1_shot'] = await cdpshot('T1_page_magenta_noinject')

            # ---- T2 重命名注入（公式逐字不变）
            ev_idx2 = len(EVENTS)
            res['T2_patch'] = await ev(JS_FIXINJECT)
            await asyncio.sleep(0.8)
            res['T2_direct_info'] = await ev(JS_DIRECT)
            await asyncio.sleep(0.5)
            res['states']['T2_magenta_renamed'] = await snap('T2_magenta_renamed')
            res['T2_events'] = [e for e in EVENTS[ev_idx2:] if 'ReadPixels' not in str(e.get('text'))][:20]
            res['T2_shot'] = await cdpshot('T2_page_magenta_renamed')
            res['envuni_T2'] = json.loads(await ev(JS_ENVUNI) or '[]')
            await ev("(function(){var s=window.__envScene;s.background=window.__envOrigBg;return 1;})()")
            await ev(JS_DIRECT)
            res['states']['T2_default_renamed'] = await snap('T2_default_renamed')
            res['T2_shot_default'] = await cdpshot('T2_page_default_renamed')

            res['console_events'] = EVENTS[:400]
            res['events_total'] = TOTAL[0]
            res['net_bad'] = NET_BAD[:30]
    finally:
        try:
            pr.terminate()
        except Exception:
            pass

    def load(name):
        return np.asarray(Image.open(os.path.join(OUT, name)).convert('RGB')).astype(np.int32)

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
        base = res['states'].get('T0_magenta_hidden') or {}
        for tag in ('T0_magenta_chain', 'T1_magenta_noinject', 'T2_magenta_renamed'):
            st = res['states'].get(tag) or {}
            if st.get('file'):
                analysis[tag + '_inside'] = stats(os.path.join(OUT, st['file']), union)
        if base.get('file'):
            ab = load(base['file'])
            for tag in ('T0_magenta_chain', 'T1_magenta_noinject', 'T2_magenta_renamed'):
                st = res['states'].get(tag) or {}
                if not st.get('file'):
                    continue
                aa = load(st['file'])
                d = np.abs(aa - ab).max(axis=2)
                analysis['DIFF_' + tag] = {
                    'diff_pct_union': round(100.0 * float((d[union] > 8).sum()) / max(1, int(union.sum())), 3),
                    'per_prim_diff_pct': {str(i): round(100.0 * float((d[mk] > 8).sum()) / max(1, int(mk.sum())), 2) for i, mk in masks.items()},
                    'per_prim_chain_mean': {str(i): [round(float(x), 1) for x in aa[mk].mean(0)] for i, mk in masks.items()}}
        # 逐 prim：链材质状态 == 背景？（100% 表示完全未绘制）
        ch = res['states'].get('T0_magenta_chain') or {}
        if base.get('file') and ch.get('file'):
            aa, ab = load(ch['file']), load(base['file'])
            d = np.abs(aa - ab).max(axis=2)
            analysis['T0_chain_equals_background_pct_per_prim'] = {
                str(i): round(100.0 * float((d[mk] <= 8).mean()), 2) for i, mk in masks.items()}
        d0 = res['states'].get('T0_snapshot_chain') or {}
        dh = res['states'].get('T0_default_hidden') or {}
        if d0.get('file') and dh.get('file'):
            analysis['T0_default_chain_vs_hidden'] = {'maxdiff': int(np.abs(load(d0['file']) - load(dh['file'])).max()),
                                                      'diff_pixels': int((np.abs(load(d0['file']) - load(dh['file'])).max(axis=2) > 8).sum())}
    except Exception as e:
        analysis['error'] = str(e)
    res['analysis'] = analysis
    json.dump(res, open(os.path.join(OUT, 'env_probe_4.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('=== hook', res.get('hook'), 'scene_ok', res.get('scene_ok'), 'applied', res.get('chain_report_applied'))
    print('=== T0 direct     ', res.get('T0_direct_info'))
    print('=== T0h(全隐藏)   ', res.get('T0h_direct_info'))
    print('=== T0m(洋红+链)  ', res.get('T0m_direct_info'))
    print('=== T1(去注入)    ', res.get('T1_direct_info'), res.get('T1_patch'))
    print('=== T2(重命名)    ', res.get('T2_direct_info'), res.get('T2_patch'))
    print('=== bg', res.get('bg'), 'sceneEnvNull test:', res.get('sceneEnv_orig'))
    print('=== envMap uniform 归属 (before)')
    print(json.dumps(res.get('envuni_before'), ensure_ascii=False, indent=1)[:1800])
    print('=== envMap uniform 归属 (scene.environment=null)')
    print(json.dumps(res.get('envuni_sceneEnvNull'), ensure_ascii=False, indent=1)[:1800])
    print('=== T1 events', json.dumps(res.get('T1_events'), ensure_ascii=False)[:400])
    print('=== T2 events', json.dumps(res.get('T2_events'), ensure_ascii=False)[:400])
    print('=== 全量控制台（去重）')
    seen = set()
    for e in res['console_events']:
        t = str(e.get('text', ''))
        if 'ReadPixels' in t:
            continue
        k = t[:70]
        if k in seen:
            continue
        seen.add(k)
        print('  [%s] %s' % (e.get('t'), t[:900].replace('\n', ' | ')))
    print('=== net_bad', json.dumps(res.get('net_bad')[:6], ensure_ascii=False)[:300])
    print('=== snapshots')
    for k in ('T0_page_chain', 'T0_page_magenta_chain', 'T1_page_magenta_noinject', 'T2_page_magenta_renamed', 'T2_page_default_renamed'):
        print('  ', k, res.get(k))
    print('=== analysis')
    print(json.dumps(res.get('analysis'), ensure_ascii=False, indent=1)[:5000])


asyncio.run(main())
