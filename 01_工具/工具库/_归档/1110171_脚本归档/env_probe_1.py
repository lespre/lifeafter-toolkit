# -*- coding: utf-8 -*-
"""env_probe_1.py — 只读诊断（task-4 / env-auditor）

目标：判定 lab=1 下 1110171 的链材质武器是「渲染为黑（被暗背景吞没）」还是「完全未绘制」。

方法（全部只在运行时，绝不写项目文件）：
 1) 用 import() 取页面同一个 three 模块实例（ES module 缓存 → 同一 prototype），
    钩 WebGLRenderer.prototype.render，取得真实 scene / renderer / camera / THREE。
 2) 逐 mesh 转储材质真实绑定读数：map / metalnessMap / roughnessMap / normalMap / envMap
    （含 image 尺寸、complete、colorSpace、version）、envMapIntensity、metalness、roughness、
    userData.chain / failClosedPlaceholder、onBeforeCompile 是否注入、注入 uniform 值。
 3) 环境 cube 六面逐面入 canvas 取像素统计（均值/最大/alpha）→ 判定 envMap 是否“为黑”。
 4) 逐 prim 独占白模（__primOnly(i)）取得屏幕掩码；再用 __primOnly(-1) 取得「全隐藏」背景图。
 5) 【关键分叉】运行时把 scene.background 临时改为纯白 #ffffff / 洋红 #ff00ff（脚本内保存原值），
    对比「链材质可见」与「全隐藏」两图在武器掩码内的像素：
      - 掩码内 != 背景色 且 亮度≈0  → 渲染为黑
      - 掩码内 == 背景色（无差异）  → 完全未绘制
    （背景色只在运行时内存里替换，不写回任何文件）
 6) renderer.info.render.triangles 有/无武器对照，作为“几何是否被提交绘制”的独立读数。

输出：env_probe_1.json + env_*.png，全部写到 03拆包产物\\_target_1110171。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib, time
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1'
THREE_URL = 'http://127.0.0.1:8765/assets/vendor/three/three.module.min.js'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9911

EVENTS = []          # 控制台 / 异常 / 网络失败
NET_BAD = []
EVENTS_TOTAL = [0]


def h16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def save_png(name, raw):
    p = os.path.join(OUT, name)
    open(p, 'wb').write(raw)
    return {'file': name, 'sha256_16': h16(raw), 'bytes': len(raw)}


# ---------------------------------------------------------------- JS payloads
JS_HOOK = """(async()=>{
  if(window.__envHooked) return 'already';
  const THREE=await import('%s');
  const P=THREE.WebGLRenderer.prototype, orig=P.render;
  P.render=function(scene,camera){ window.__envScene=scene; window.__envRenderer=this; window.__envCamera=camera; return orig.apply(this,arguments); };
  window.__envTHREE=THREE; window.__envHooked=true; return 'hooked';
})()""" % THREE_URL

JS_DUMP = r"""(function(){
  var T=window.__envTHREE, scene=window.__envScene, r=window.__envRenderer, cam=window.__envCamera;
  if(!T||!scene||!r) return JSON.stringify({error:'hook 未生效', hooked:!!window.__envHooked});
  function img(i){ if(!i) return null;
    return {w:i.width||0,h:i.height||0,nw:i.naturalWidth||0,nh:i.naturalHeight||0,
            complete:(i.complete===undefined?null:!!i.complete),
            src:String(i.currentSrc||i.src||'').split('/').slice(-1)[0]}; }
  function ti(t){ if(!t) return null;
    var im=t.image;
    return {isTexture:!!t.isTexture,isCubeTexture:!!t.isCubeTexture,uuid:String(t.uuid).slice(0,8),
            colorSpace:(t.colorSpace===undefined?null:t.colorSpace),version:t.version,
            needsUpdate:!!t.needsUpdate,minFilter:t.minFilter,magFilter:t.magFilter,
            generateMipmaps:!!t.generateMipmaps,mipmaps:(t.mipmaps?t.mipmaps.length:-1),
            flipY:(t.flipY===undefined?null:t.flipY),
            image:Array.isArray(im)?im.map(img):img(im)}; }
  function ud(m){ var u=m.userData||{}, o={keys:Object.keys(u)};
    if(u.chain) o.chain=u.chain;
    if(u.neox) o.neox=u.neox;
    if(u.ibl!==undefined) o.ibl=u.ibl;
    o.failClosedPlaceholder=!!u.failClosedPlaceholder;
    if(u.__srcEnvBright!==undefined) o.__srcEnvBright=u.__srcEnvBright;
    var f=u.__frag||''; o.hasInjectShader=!!u.__sh; o.fragLen=f.length;
    o.frag_has_textureLod_uCustomIbl=/textureLod\(uCustomIbl/.test(f);
    o.frag_has_dithering_anchor=/dithering_fragment/.test(f);
    if(u.__sh&&u.__sh.uniforms){ var U={};
      Object.keys(u.__sh.uniforms).forEach(function(k){ var v=u.__sh.uniforms[k].value;
        U[k]=(v&&v.isCubeTexture)?('<CubeTexture '+((v.image&&v.image.length)||0)+' faces>')
           :(v&&v.isTexture)?('<Texture '+((v.image&&v.image.width)||0)+'x'+((v.image&&v.image.height)||0)+'>')
           :v; });
      o.shaderUniforms=U; }
    return o; }
  var meshes=[], i=-1;
  scene.traverse(function(o){ if(!o.isMesh) return; i++;
    var m=o.material||{};
    meshes.push({idx:i,name:(o.name||''),visible:!!o.visible,
      geometry:(o.geometry?(o.geometry.attributes&&o.geometry.attributes.position?o.geometry.attributes.position.count:null):null),
      mat:{type:m.type||null,uuid:String(m.uuid||'').slice(0,8),visible:(m.visible===undefined?null:!!m.visible),
           transparent:!!m.transparent,opacity:(m.opacity===undefined?null:m.opacity),side:(m.side===undefined?null:m.side),
           toneMapped:(m.toneMapped===undefined?null:!!m.toneMapped),
           metalness:(m.metalness===undefined?null:m.metalness),roughness:(m.roughness===undefined?null:m.roughness),
           envMapIntensity:(m.envMapIntensity===undefined?null:m.envMapIntensity),
           color:(m.color?('#'+m.color.getHexString()):null),
           map:ti(m.map),metalnessMap:ti(m.metalnessMap),roughnessMap:ti(m.roughnessMap),
           normalMap:ti(m.normalMap),envMap:ti(m.envMap),
           userData:ud(m)}});
  });
  var lights=[]; scene.traverse(function(o){ if(o.isLight) lights.push({type:o.type,visible:o.visible,intensity:o.intensity,
      color:'#'+(o.color?o.color.getHexString():'')}); });
  var bg=(scene.background&&scene.background.isColor)?('#'+scene.background.getHexString()):String(scene.background&&scene.background.type);
  var gl=r.getContext();
  return JSON.stringify({
    hook:true, canvas:{w:r.domElement.width,h:r.domElement.height,cw:r.domElement.clientWidth,ch:r.domElement.clientHeight},
    dpr:(r.getPixelRatio?r.getPixelRatio():null), renderer_toneMapping:r.toneMapping, renderer_exposure:r.toneMappingExposure,
    outputColorSpace:r.outputColorSpace, shadowMap:!!r.shadowMap, autoClear:r.autoClear,
    gl:{version:gl.getParameter(gl.VERSION),vendor:gl.getParameter(gl.VENDOR),renderer:gl.getParameter(gl.RENDERER),
        maxCubeSize:gl.getParameter(gl.MAX_CUBE_MAP_TEXTURE_SIZE),maxTexSize:gl.getParameter(gl.MAX_TEXTURE_SIZE),
        lost:gl.isContextLost()},
    scene_background:bg, scene_environment:(scene.environment?(scene.environment.isTexture?('Texture cs='+scene.environment.colorSpace):scene.environment.type):null),
    scene_environmentIntensity:(scene.environmentIntensity===undefined?null:scene.environmentIntensity),
    scene_fog:!!scene.fog, meshCount:meshes.length, lights:lights,
    info_render:JSON.parse(JSON.stringify(r.info.render)), info_memory:JSON.parse(JSON.stringify(r.info.memory)),
    programs:(r.info.programs?r.info.programs.length:null),
    meshes:meshes});
})()"""

JS_SETBG = (r"""(function(hex){ var s=window.__envScene; if(!s) return 'no-scene';
  if(!window.__envHadOrigBg){ window.__envHadOrigBg=true;
    window.__envOrigBg=s.background?(s.background.clone?s.background.clone():s.background):null; }
  s.background=new window.__envTHREE.Color(hex); return '#'+s.background.getHexString(); })('%s')""")

JS_RESTBG = r"""(function(){ var s=window.__envScene; if(!s||!window.__envHadOrigBg) return 'noop';
  s.background=window.__envOrigBg; return 'restored'; })()"""

JS_CUBE_STATS = r"""(function(){
  var scene=window.__envScene, T=window.__envTHREE; if(!scene||!T) return JSON.stringify({error:'no scene'});
  var out=[]; var seen={};
  scene.traverse(function(o){ if(!o.isMesh) return; var m=o.material||{};
    [['envMap',m.envMap],['map',m.map],['metalnessMap',m.metalnessMap],['roughnessMap',m.roughnessMap],['normalMap',m.normalMap]].forEach(function(pr){
      var k=pr[0], t=pr[1]; if(!t||!t.image) return;
      var u=String(t.uuid); if(seen[u]) return; seen[u]=1;
      var faces=Array.isArray(t.image)?t.image:[t.image];
      var rec={slot:k,uuid:u.slice(0,8),isCube:!!t.isCubeTexture,n:faces.length,faces:[]};
      faces.forEach(function(f,i){
        try{ var c=document.createElement('canvas'); c.width=32; c.height=32;
          var cx=c.getContext('2d'); cx.drawImage(f,0,0,32,32);
          var d=cx.getImageData(0,0,32,32).data; var n=0,R=0,G=0,B=0,A=0,mx=0;
          for(var p=0;p<d.length;p+=4){ R+=d[p];G+=d[p+1];B+=d[p+2];A+=d[p+3];
            var l=(d[p]+d[p+1]+d[p+2])/3; if(l>mx)mx=l; n++; }
          rec.faces.push({i:i,file:String(f.currentSrc||f.src||'').split('/').slice(-1)[0],
            srcW:f.naturalWidth,srcH:f.naturalHeight,
            mean:[+(R/n).toFixed(1),+(G/n).toFixed(1),+(B/n).toFixed(1)],meanA:+(A/n).toFixed(1),maxLum:mx});
        }catch(e){ rec.faces.push({i:i,error:String(e&&e.message||e)}); }
      });
      out.push(rec); });
  });
  return JSON.stringify(out);
})()"""


def img_stats(png_bytes, mask=None):
    """在整图或掩码内做像素统计。"""
    import io
    a = np.asarray(Image.open(io.BytesIO(png_bytes)).convert('RGB')).astype(np.int32)
    if mask is not None:
        px = a[mask]
    else:
        px = a.reshape(-1, 3)
    if len(px) == 0:
        return {'n': 0}
    lum = (0.299 * px[:, 0] + 0.587 * px[:, 1] + 0.114 * px[:, 2])
    return {'n': int(len(px)),
            'mean': [round(float(px[:, 0].mean()), 1), round(float(px[:, 1].mean()), 1), round(float(px[:, 2].mean()), 1)],
            'lum_mean': round(float(lum.mean()), 2), 'lum_p50': round(float(np.percentile(lum, 50)), 1),
            'lum_p95': round(float(np.percentile(lum, 95)), 1), 'lum_max': round(float(lum.max()), 1),
            'pct_lum_lt16': round(float(100 * (lum < 16).mean()), 2),
            'sha16': hashlib.sha256(px.astype(np.uint8).tobytes()).hexdigest()[:16]}


async def main():
    prof = os.path.join(OUT, '_profENV1')
    shutil.rmtree(prof, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                           '--window-size=1240,900', '--remote-debugging-port=%d' % PORT,
                           '--user-data-dir=%s' % prof, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    res = {'commands': [], 'states': {}}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT))
                  if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0
            pending = {}

            def on_event(m):
                EVENTS_TOTAL[0] += 1
                me = m.get('method')
                p = m.get('params') or {}
                if me == 'Runtime.consoleAPICalled':
                    txt = ' '.join(str((a or {}).get('value', (a or {}).get('description', '')))[:300]
                                   for a in (p.get('args') or []))
                    EVENTS.append({'t': p.get('type'), 'text': txt[:600]})
                elif me == 'Runtime.exceptionThrown':
                    d = (p.get('exceptionDetails') or {})
                    EVENTS.append({'t': 'exception', 'text': str(d.get('text'))[:300] + ' ' +
                                   str((d.get('exception') or {}).get('description'))[:400]})
                elif me == 'Log.entryAdded':
                    e = p.get('entry') or {}
                    EVENTS.append({'t': 'log/' + str(e.get('source')) + '/' + str(e.get('level')), 'text': str(e.get('text'))[:600]})
                elif me == 'Network.responseReceived':
                    r_ = p.get('response') or {}
                    if int(r_.get('status', 200)) >= 400:
                        NET_BAD.append({'status': r_.get('status'), 'url': r_.get('url')})
                elif me == 'Network.loadingFailed':
                    NET_BAD.append({'failed': str(p.get('errorText')), 'url': p.get('requestId')})

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
                r = await asyncio.wait_for(fut, timeout=180)
                if 'error' in r:
                    raise RuntimeError('CDP %s -> %s' % (method, r['error']))
                return r.get('result', {})

            async def ev(expr, wait=0.0):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True, timeout=120000)
                if r.get('exceptionDetails'):
                    return 'EXC ' + str(r['exceptionDetails'].get('text'))[:300]
                if wait:
                    await asyncio.sleep(wait)
                return (r.get('result', {}) or {}).get('value')

            async def snap(tag):
                """snapshot() → 渲染目标 readback（不受 preserveDrawingBuffer 影响）"""
                d = await ev("JSON.stringify(window.WikiWeaponViewer.snapshot())")
                if not isinstance(d, str) or not d.startswith('{'):
                    return {'error': str(d)[:200]}
                s = json.loads(d)
                raw = base64.b64decode(s['png'].split(',', 1)[-1])
                meta = save_png('env_%s.png' % tag, raw)
                s.pop('png', None)
                s.update(meta)
                res['commands'].append('snapshot ' + tag)
                return s

            async def cdpshot(tag):
                s = await send('Page.captureScreenshot', format='png')
                raw = base64.b64decode(s.get('data', ''))
                return save_png('env_%s.png' % tag, raw)

            await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable'); await send('Network.enable')
            await send('Page.navigate', url=URL)
            await asyncio.sleep(10)

            rel = 'assets/3d/weapon_skin/1110171'
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110171',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'});return 1;})()" % (rel, rel))
            chain = None
            for _ in range(40):
                st = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                if st and '"applied"' in st:
                    try:
                        j = json.loads(st)
                        if (j.get('report') or {}).get('applied'):
                            chain = j
                            break
                    except Exception:
                        pass
                await asyncio.sleep(2)
            await asyncio.sleep(6)
            await ev("window.WikiWeaponViewer.applyDebugUi(false)")
            res['chain_report'] = chain
            res['neoxState'] = await ev("JSON.stringify(window.WikiWeaponViewer.neoxState&&window.WikiWeaponViewer.neoxState())")
            res['matDump'] = await ev("JSON.stringify(window.WikiWeaponViewer.__matDump&&window.WikiWeaponViewer.__matDump())")
            res['debugState'] = await ev("JSON.stringify(window.WikiWeaponViewer.__state&&window.WikiWeaponViewer.__state())")

            # ---- 1) hook three + capture real scene objects
            res['hook'] = await ev(JS_HOOK)
            await ev("window.WikiWeaponViewer.canvasShot(2)")   # 触发 _forceRender → 命中 hook
            await asyncio.sleep(1)
            res['hooked'] = bool(await ev("!!window.__envScene"))
            if not res['hooked']:
                res['FATAL'] = 'hook 失败，后续读数不可用'
            else:
                res['dump_chain'] = json.loads(await ev(JS_DUMP))
                res['tex_cube_stats'] = json.loads(await ev(JS_CUBE_STATS) or '[]')
                res['info_render_chain'] = json.loads(await ev("JSON.stringify(window.__envRenderer.info.render)"))

                # ---- 2) 默认背景：截图 + 总览
                res['states']['DEF_chain'] = await snap('DEF_chain')

                # ---- 3) 逐 prim 独占白模掩码（默认背景）
                res['masks'] = {}
                for i in range(7):
                    await ev("window.__primOnly(%d)" % i)
                    await asyncio.sleep(0.4)
                    s = await snap('mask_%d' % i)
                    res['masks'][str(i)] = s
                    res['commands'].append('__primOnly(%d)' % i)
                await ev("window.__primOnly(null)")
                await asyncio.sleep(0.5)
                res['states']['DEF_restored'] = await snap('DEF_restored')

                # ---- 4) 全隐藏：三角形计数对照（默认背景）
                await ev("window.__primOnly(-1)")
                await asyncio.sleep(0.5)
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                res['info_render_hidden'] = json.loads(await ev("JSON.stringify(window.__envRenderer.info.render)"))
                res['states']['DEF_hidden'] = await snap('DEF_hidden')
                await ev("window.__primOnly(null)")
                await asyncio.sleep(0.5)

                # ---- 5) 【关键分叉】运行时临时亮背景
                for tag, hexv in (('WHITE', '0xffffff'), ('MAGENTA', '0xff00ff')):
                    res['bg_set_%s' % tag] = await ev(JS_SETBG % hexv)
                    await asyncio.sleep(0.4)
                    await ev("window.WikiWeaponViewer.canvasShot(2)")
                    res['states']['%s_chain' % tag] = await snap('%s_chain' % tag)
                    res['states']['%s_page' % tag] = await cdpshot('%s_page' % tag)
                    # 隐藏全部 mesh → 纯背景对照（同一背景色）
                    await ev("window.__primOnly(-1)")
                    await asyncio.sleep(0.4)
                    await ev("window.WikiWeaponViewer.canvasShot(2)")
                    res['states']['%s_hidden' % tag] = await snap('%s_hidden' % tag)
                    await ev("window.__primOnly(null)")
                    await asyncio.sleep(0.4)
                    res['commands'].append('bg=%s (runtime only)' % hexv)
                res['bg_restore'] = await ev(JS_RESTBG)
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                res['states']['FINAL_restored'] = await snap('FINAL_restored')

                # ---- 6) 对照（非源环境，仅用于确认管线是否可出图）：__useCubeEnv
                res['usecubeenv'] = await ev("window.__useCubeEnv(true)", wait=3.0)
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                res['states']['CANDENV_chain'] = await snap('CANDENV_chain')
                res['usecubeenv_off'] = await ev("window.__useCubeEnv(false)", wait=1.0)

            res['events_total'] = EVENTS_TOTAL[0]
            res['console_events'] = EVENTS[:250]
            res['net_bad'] = NET_BAD[:120]
            res['err_count'] = sum(1 for e in EVENTS if e.get('t') in ('exception', 'error') or str(e.get('t')).endswith('/error'))
    finally:
        try:
            pr.terminate()
        except Exception:
            pass

    # -------------------------------------------------- 像素分析
    import io
    def load(name):
        return np.asarray(Image.open(os.path.join(OUT, name)).convert('RGB')).astype(np.int32)

    analysis = {}
    try:
        def loadb(name):
            return open(os.path.join(OUT, name), 'rb').read()
        masks = {}
        for i in range(7):
            m = res['masks'][str(i)]
            if not m.get('file'):
                continue
            a = load(m['file'])
            masks[i] = (a[:, :, 0] > 200) & (a[:, :, 1] > 200) & (a[:, :, 2] > 200)
        if masks:
            shape = next(iter(masks.values())).shape
            union = np.zeros(shape, bool)
            for i, mk in masks.items():
                union |= mk
            analysis['mask_pixels'] = {str(i): int(mk.sum()) for i, mk in masks.items()}
            analysis['union_pixels'] = int(union.sum())
            for tag in ('DEF_chain', 'DEF_hidden', 'WHITE_chain', 'WHITE_hidden', 'MAGENTA_chain', 'MAGENTA_hidden',
                        'CANDENV_chain'):
                st = res['states'].get(tag) or {}
                if st.get('file'):
                    a = load(st['file'])
                    analysis[tag] = dict(img_stats(loadb(st['file']), union), whole=img_stats(loadb(st['file'])))
            # 关键：亮背景下 链材质 vs 全隐藏 的差异
            for tag in ('WHITE', 'MAGENTA'):
                c = res['states'].get('%s_chain' % tag) or {}
                h = res['states'].get('%s_hidden' % tag) or {}
                if c.get('file') and h.get('file'):
                    ac, ah = load(c['file']), load(h['file'])
                    d = np.abs(ac - ah).max(axis=2)
                    inside = int((d[union] > 8).sum()) if union.any() else 0
                    bgc = ac[~union]
                    analysis['fork_%s' % tag] = {
                        'mask_pixels': int(union.sum()),
                        'diff_pixels_inside_mask': inside,
                        'diff_pct_inside_mask': round(100.0 * inside / max(1, int(union.sum())), 3),
                        'mean_chain_inside': [round(float(x), 1) for x in ac[union].mean(0)] if union.any() else None,
                        'mean_hidden_inside': [round(float(x), 1) for x in ah[union].mean(0)] if union.any() else None,
                        'mean_bg_outside_mask': [round(float(x), 1) for x in bgc.mean(0)] if len(bgc) else None,
                        'inside_pixels_equal_to_bgcolor': int((np.abs(ac[union] - bgc.mean(0)).max(axis=1) <= 6).sum()) if union.any() and len(bgc) else None}
        if 'CANDENV_chain' in analysis and masks:
            cu = analysis['CANDENV_chain']
            analysis['CANDENV_lum'] = cu.get('lum_mean')
    except Exception as e:
        analysis['error'] = str(e)
    res['analysis'] = analysis

    json.dump(res, open(os.path.join(OUT, 'env_probe_1.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    # -------- 控制台摘要
    print('=== console/网络异常 (%d 事件) ===' % res['events_total'])
    for e in res['console_events'][:60]:
        print('  [%s] %s' % (e.get('t'), str(e.get('text'))[:200]))
    print('  net_bad:', json.dumps(res['net_bad'][:20], ensure_ascii=False)[:600])
    print('=== hook:', res.get('hook'), 'hooked=', res.get('hooked'))
    if res.get('dump_chain'):
        d = res['dump_chain']
        print('canvas', d.get('canvas'), 'bg', d.get('scene_background'), 'env', d.get('scene_environment'),
              'envInt', d.get('scene_environmentIntensity'), 'meshCount', d.get('meshCount'))
        print('gl', d.get('gl'))
        print('info_render', d.get('info_render'), 'programs', d.get('programs'))
        for m in d.get('meshes', []):
            mt = m['mat']
            def s(t):
                if not t:
                    return 'null'
                if t.get('isCubeTexture'):
                    n = t.get('image') or []
                    return 'CUBE img=%s cs=%s ver=%s' % (len(n) if isinstance(n, list) else n, t.get('colorSpace'), t.get('version'))
                im = t.get('image')
                return 'TEX %sx%s cs=%s ver=%s' % (im.get('w'), im.get('h'), t.get('colorSpace'), t.get('version')) if im else 'TEX(no-img)'
            print('mesh%d vis=%s %s metal=%s rough=%s envI=%s' % (m['idx'], m['visible'], mt['type'], mt['metalness'], mt['roughness'], mt['envMapIntensity']))
            print('      map=%s' % s(mt['map']))
            print('      metalMap=%s roughMap=%s normalMap=%s' % (s(mt['metalnessMap']), s(mt['roughnessMap']), s(mt['normalMap'])))
            print('      envMap=%s' % s(mt['envMap']))
            print('      ud=%s' % json.dumps(mt['userData'], ensure_ascii=False)[:700])
    print('=== info_render_chain', res.get('info_render_chain'), ' hidden', res.get('info_render_hidden'))
    print('=== tex/cube 逐面统计')
    print(json.dumps(res.get('tex_cube_stats'), ensure_ascii=False, indent=1)[:4000])
    print('=== analysis')
    print(json.dumps(res.get('analysis'), ensure_ascii=False, indent=1)[:4000])
    print('=== 输出: %s' % os.path.join(OUT, 'env_probe_1.json'))


asyncio.run(main())
