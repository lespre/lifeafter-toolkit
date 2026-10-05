# -*- coding: utf-8 -*-
"""env_probe_3.py — 只读诊断（task-4 / env-auditor）第三轮：修正 scene 句柄 + 亮背景分叉定论 + 因果对照。

env_probe_2 的教训：
  * three r180 的 WebGLRenderer.render 是「实例属性」→ 钩 prototype 无效（probe_1 失败原因）；
    钩 Object3D.prototype.onBeforeRender 会被后处理的 fullscreen-quad scene 覆盖（probe_2 拿到错 scene）。
    本轮改为：traverse 钩子（只认 isScene 且 children>1）+ onBeforeRender 过滤，双保险。
  * JS_SETBG 传了字符串 '0xffffff' → THREE.Color 报 Unknown color（等于没改）。
    本轮改为传数字字面量，并回读校验。

本轮产出：
  A. 真实 scene/renderer/THREE 下的逐 mesh 材质绑定读数（含 envMap 六面与 envMapIntensity）。
  B. 链材质注入的 fragment 源（userData.__frag）中定位 __ 标识符块，与 GLSL 报错 token 对账。
  C. 【关键分叉】运行时把 scene.background 临时设为洋红 0xff00ff（内存，不写文件），
     比较 chain / 全隐藏 / 去注入 三种状态在武器掩码内的像素 → 判定「渲染为黑」还是「完全未绘制」。
  D. 因果对照 T_noinject：运行时把 7 个链材质的 onBeforeCompile 置空并 needsUpdate 重编译
     （只改内存材质，不加任何人工配色）→ 若武器出现，则确证不可见由该注入块导致。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib
import websockets
import numpy as np
from PIL import Image

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1'
THREE_URL = 'http://127.0.0.1:8765/assets/vendor/three/three.module.min.js'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9913
EVENTS, NET_BAD, TOTAL = [], [], [0]


def h16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def save_png(name, raw):
    open(os.path.join(OUT, name), 'wb').write(raw)
    return {'file': name, 'sha256_16': h16(raw), 'bytes': len(raw)}


JS_HOOK = r"""(async()=>{
  if(window.__envHooked) return 'already';
  const THREE=await import('%s');
  const O=THREE.Object3D.prototype;
  const ob=O.onBeforeRender;
  O.onBeforeRender=function(r,s,c){
    if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envCamera=c; window.__envScene=s; }
    return ob.apply(this,arguments); };
  const tv=O.traverse;
  O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
  window.__envTHREE=THREE; window.__envHooked=true; window.__envSceneTag=null;
  return JSON.stringify({rendererProtoRender:typeof THREE.WebGLRenderer.prototype.render, threeRev:(THREE.REVISION||null)});
})()""" % THREE_URL

JS_SETBG = r"""(function(){ var s=window.__envScene; if(!s) return 'no-scene';
  if(!window.__envHadOrigBg){ window.__envHadOrigBg=true;
    window.__envOrigBg=s.background?(s.background.clone?s.background.clone():s.background):null;
    window.__envOrigBgType=(s.background?(s.background.isColor?'color':(s.background.isTexture?'texture':s.background.type)):'null'); }
  s.background=new window.__envTHREE.Color(0xff00ff);
  return {'bg':('#'+s.background.getHexString()),'orig':window.__envOrigBgType,
          'meshes':(function(){var n=0;s.traverse(function(o){if(o.isMesh)n++;});return n;})()}; })()"""

JS_SELFTEST = r"""(function(){ var s=window.__envScene,r=window.__envRenderer,T=window.__envTHREE;
  if(!s||!r) return JSON.stringify({ok:false});
  var meshes=0,chain=0; s.traverse(function(o){ if(!o.isMesh) return; meshes++;
    var u=(o.material&&o.material.userData)||{}; if(u.chain) chain++; });
  return JSON.stringify({ok:true,threeRev:T.REVISION,meshes:meshes,chainMeshes:chain,
    bg:((s.background&&s.background.isColor)?('#'+s.background.getHexString()):((s.background&&s.background.isTexture)?'texture':String(s.background))),
    lights:(function(){var a=[];s.traverse(function(o){if(o.isLight)a.push(o.type);});return a;})(),
    info:JSON.parse(JSON.stringify(r.info.render))}); })()"""

JS_DUMP = r"""(function(){
  var T=window.__envTHREE, scene=window.__envScene, r=window.__envRenderer;
  if(!T||!scene||!r) return JSON.stringify({error:'hook 未生效'});
  function img(i){ if(!i) return null;
    return {w:i.width||0,h:i.height||0,nw:i.naturalWidth||0,nh:i.naturalHeight||0,
            complete:(i.complete===undefined?null:!!i.complete),src:String(i.currentSrc||i.src||'').split('/').slice(-1)[0]}; }
  function ti(t){ if(!t) return null; var im=t.image;
    return {isTexture:!!t.isTexture,isCubeTexture:!!t.isCubeTexture,uuid:String(t.uuid).slice(0,8),
            colorSpace:(t.colorSpace===undefined?null:t.colorSpace),version:t.version,needsUpdate:!!t.needsUpdate,
            minFilter:t.minFilter,magFilter:t.magFilter,generateMipmaps:!!t.generateMipmaps,
            mipmaps:(t.mipmaps?t.mipmaps.length:-1),image:Array.isArray(im)?im.map(img):img(im)}; }
  function ud(m){ var u=m.userData||{}, o={keys:Object.keys(u)};
    if(u.chain) o.chain=u.chain; if(u.neox) o.neox=u.neox; if(u.ibl!==undefined) o.ibl=u.ibl;
    o.failClosedPlaceholder=!!u.failClosedPlaceholder;
    var f=u.__frag||''; o.hasInjectShader=!!u.__sh; o.fragLen=f.length;
    o.frag_has_textureLod_uCustomIbl=/textureLod\(uCustomIbl/.test(f);
    o.frag_double_underscore_tokens=(f.match(/__[A-Za-z_][A-Za-z0-9_]*/g)||[]).filter(function(v,i,a){return a.indexOf(v)===i;});
    o.hasOnBeforeCompile=typeof m.onBeforeCompile==='function'; o.obc_src_len=m.onBeforeCompile?String(m.onBeforeCompile).length:0;
    if(u.__sh&&u.__sh.uniforms){ var U={};
      Object.keys(u.__sh.uniforms).forEach(function(k){ var v=u.__sh.uniforms[k].value;
        U[k]=(v&&v.isCubeTexture)?('<CubeTex faces='+((v.image&&v.image.length)||0)+' cs='+v.colorSpace+'>')
           :(v&&v.isTexture)?('<Tex '+((v.image&&v.image.width)||0)+'x'+((v.image&&v.image.height)||0)+'>'):v; });
      o.shaderUniforms=U; }
    return o; }
  var meshes=[],i=-1;
  scene.traverse(function(o){ if(!o.isMesh) return; i++; var m=o.material||{};
    meshes.push({idx:i,name:(o.name||''),visible:!!o.visible,
      vcount:(o.geometry&&o.geometry.attributes&&o.geometry.attributes.position)?o.geometry.attributes.position.count:null,
      mat:{type:m.type||null,uuid:String(m.uuid||'').slice(0,8),matVisible:(m.visible===undefined?null:!!m.visible),
           transparent:!!m.transparent,opacity:(m.opacity===undefined?null:m.opacity),side:(m.side===undefined?null:m.side),
           toneMapped:(m.toneMapped===undefined?null:!!m.toneMapped),metalness:m.metalness,roughness:m.roughness,
           envMapIntensity:(m.envMapIntensity===undefined?null:m.envMapIntensity),
           color:(m.color?('#'+m.color.getHexString()):null),
           map:ti(m.map),metalnessMap:ti(m.metalnessMap),roughnessMap:ti(m.roughnessMap),
           normalMap:ti(m.normalMap),envMap:ti(m.envMap),userData:ud(m)}});
  });
  var gl=r.getContext();
  return JSON.stringify({threeRev:T.REVISION,canvas:{w:r.domElement.width,h:r.domElement.height},
    dpr:(r.getPixelRatio?r.getPixelRatio():null),toneMapping:r.toneMapping,exposure:r.toneMappingExposure,
    outputColorSpace:r.outputColorSpace,autoClear:r.autoClear,
    gl:{version:gl.getParameter(gl.VERSION),renderer:gl.getParameter(gl.RENDERER),lost:gl.isContextLost()},
    scene_background:((scene.background&&scene.background.isColor)?('#'+scene.background.getHexString()):((scene.background&&scene.background.isTexture)?'texture':String(scene.background))),
    scene_environment:(scene.environment?(scene.environment.isTexture?('Texture cs='+scene.environment.colorSpace):String(scene.environment.type)):null),
    scene_environmentIntensity:(scene.environmentIntensity===undefined?null:scene.environmentIntensity),
    meshCount:meshes.length,lights:(function(){var a=[];scene.traverse(function(o){if(o.isLight)a.push({type:o.type,visible:o.visible,intensity:o.intensity});});return a;})(),
    info_render:JSON.parse(JSON.stringify(r.info.render)),info_memory:JSON.parse(JSON.stringify(r.info.memory)),
    programs:(r.info.programs||[]).map(function(p){return {name:p.name,usedTimes:p.usedTimes};}),
    meshes:meshes});
})()"""

JS_FRAG = r"""(function(){
  var scene=window.__envScene; if(!scene) return JSON.stringify({error:'no scene'});
  var out=[];
  scene.traverse(function(o){ if(!o.isMesh) return; var u=(o.material&&o.material.userData)||{};
    if(!u.__frag) return; var prim=(u.chain?u.chain.prim:null);
    if(out.some(function(x){return x.prim===prim;})) return;
    var f=u.__frag.split('\n'); var idx=-1;
    for(var i=0;i<f.length;i++){ if(f[i].indexOf('__rough')>=0){ idx=i; break; } }
    out.push({prim:prim,totalLines:f.length,firstDunderLine_1based:(idx>=0?idx+1:null),
              injectedBlock:(idx>=0?f.slice(Math.max(0,idx-2),idx+12).join('\n'):null)}); });
  return JSON.stringify(out);
})()"""

JS_CUBE_STATS = r"""(function(){
  var scene=window.__envScene; if(!scene) return JSON.stringify({error:'no scene'});
  var out=[],seen={};
  scene.traverse(function(o){ if(!o.isMesh) return; var m=o.material||{};
    [['envMap',m.envMap],['map',m.map],['metalnessMap',m.metalnessMap],['roughnessMap',m.roughnessMap],['normalMap',m.normalMap]].forEach(function(pr){
      var k=pr[0],t=pr[1]; if(!t||!t.image) return; var u=String(t.uuid); if(seen[u]) return; seen[u]=1;
      var faces=Array.isArray(t.image)?t.image:[t.image];
      var rec={slot:k,uuid:u.slice(0,8),isCube:!!t.isCubeTexture,colorSpace:(t.colorSpace===undefined?null:t.colorSpace),n:faces.length,faces:[]};
      faces.forEach(function(f,i){
        try{ var c=document.createElement('canvas'); c.width=32;c.height=32; var cx=c.getContext('2d');
          cx.drawImage(f,0,0,32,32); var d=cx.getImageData(0,0,32,32).data; var n=0,R=0,G=0,B=0,A=0,mx=0;
          for(var p=0;p<d.length;p+=4){ R+=d[p];G+=d[p+1];B+=d[p+2];A+=d[p+3]; var l=(d[p]+d[p+1]+d[p+2])/3; if(l>mx)mx=l; n++; }
          rec.faces.push({i:i,file:String(f.currentSrc||f.src||'').split('/').slice(-1)[0],srcW:f.naturalWidth,srcH:f.naturalHeight,
            mean:[+(R/n).toFixed(1),+(G/n).toFixed(1),+(B/n).toFixed(1)],meanA:+(A/n).toFixed(1),maxLum:mx});
        }catch(e){ rec.faces.push({i:i,error:String(e&&e.message||e)}); } });
      out.push(rec); });
  });
  return JSON.stringify(out);
})()"""

JS_NOINJECT = r"""(function(){
  var scene=window.__envScene; if(!scene) return JSON.stringify({error:'no scene'});
  var n=0,list=[];
  scene.traverse(function(o){ if(!o.isMesh) return; var m=o.material; if(!m) return;
    var u=m.userData||{}; if(!(u.chain||u.neox)) return;
    if(typeof m.onBeforeCompile==='function'){ m.onBeforeCompile=function(){}; n++; list.push(u.chain?u.chain.prim:null); }
    m.customProgramCacheKey=function(){ return 'noinject_'+String(m.uuid).slice(0,8); };
    m.needsUpdate=true; });
  return JSON.stringify({patched:n,prims:list});
})()"""


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
    prof = os.path.join(OUT, '_profENV3')
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
                    txt = ' '.join(str((a or {}).get('value', (a or {}).get('description', '')))[:4000] for a in (p.get('args') or []))
                    EVENTS.append({'t': p.get('type'), 'text': txt[:4000]})
                elif me == 'Runtime.exceptionThrown':
                    d = (p.get('exceptionDetails') or {})
                    EVENTS.append({'t': 'exception', 'text': str(d.get('text'))[:300] + ' ' + str((d.get('exception') or {}).get('description'))[:1200]})
                elif me == 'Log.entryAdded':
                    e = p.get('entry') or {}
                    EVENTS.append({'t': 'log/' + str(e.get('source')) + '/' + str(e.get('level')), 'text': str(e.get('text'))[:1500]})
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
                meta = save_png('env3_%s.png' % tag, raw)
                s.pop('png', None); s.update(meta)
                return s

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
                            res['chain_report'] = json.loads(st); break
                    except Exception:
                        pass
                await asyncio.sleep(2)
            await asyncio.sleep(6)

            # ---- hook + 触发一次真实渲染，拿到正确的 scene
            res['hook'] = await ev(JS_HOOK)
            await ev("window.__primOnly(null)")            # 触发 state.scene.traverse → 捕获 scene
            await ev("window.WikiWeaponViewer.canvasShot(2)")   # 触发主场景 render → 捕获 renderer
            await asyncio.sleep(1)
            res['selftest'] = json.loads(await ev(JS_SELFTEST) or '{}')
            if not res['selftest'].get('ok'):
                res['FATAL'] = 'scene 句柄未取得'
            else:
                res['dump'] = json.loads(await ev(JS_DUMP))
                res['frag_evidence'] = json.loads(await ev(JS_FRAG) or '[]')
                res['tex_cube_stats'] = json.loads(await ev(JS_CUBE_STATS) or '[]')
                res['neoxState'] = await ev("JSON.stringify(window.WikiWeaponViewer.neoxState&&window.WikiWeaponViewer.neoxState())")
                res['matDump'] = await ev("JSON.stringify(window.WikiWeaponViewer.__matDump&&window.WikiWeaponViewer.__matDump())")
                # 关后处理，让 renderer.info.render 反映主场景（不影响材质）
                res['post_off'] = await ev("JSON.stringify(window.WikiWeaponViewer.__post(false))")
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                res['info_render_all_visible'] = json.loads(await ev("JSON.stringify(window.__envRenderer.info.render)"))

                # ---- 掩码（默认背景）
                res['masks'] = {}
                for i in range(7):
                    await ev("window.__primOnly(%d)" % i)
                    await asyncio.sleep(0.4)
                    res['masks'][str(i)] = await snap('mask_%d' % i)
                await ev("window.__primOnly(null)")
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                res['info_render_all_visible2'] = json.loads(await ev("JSON.stringify(window.__envRenderer.info.render)"))
                res['states']['A_default_chain'] = await snap('A_default_chain')

                # 全隐藏 → 三角计数对照
                await ev("window.__primOnly(-1)")
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                res['info_render_all_hidden'] = json.loads(await ev("JSON.stringify(window.__envRenderer.info.render)"))
                res['states']['A_default_hidden'] = await snap('A_default_hidden')
                await ev("window.__primOnly(null)")
                await ev("window.WikiWeaponViewer.canvasShot(2)")

                # ---- 关键分叉：亮背景（洋红）
                res['bg_selftest'] = await ev("JSON.stringify(" + JS_SETBG + ")")
                await asyncio.sleep(0.3)
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                res['states']['B_magenta_chain'] = await snap('B_magenta_chain')
                res['bg_after_chain'] = await ev("(function(){var b=window.__envScene.background;return b&&b.isColor?('#'+b.getHexString()):String(b&&b.type);})()")
                await ev("window.__primOnly(-1)")
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                res['states']['B_magenta_hidden'] = await snap('B_magenta_hidden')
                await ev("window.__primOnly(null)")
                await ev("window.WikiWeaponViewer.canvasShot(2)")

                # ---- 因果对照：去掉注入块
                ev_idx = len(EVENTS)
                res['noinject'] = await ev(JS_NOINJECT)
                await asyncio.sleep(1.5)
                await ev("window.WikiWeaponViewer.canvasShot(3)")
                await asyncio.sleep(1.0)
                res['states']['C_magenta_noinject'] = await snap('C_magenta_noinject')
                res['events_after_noinject'] = [e for e in EVENTS[ev_idx:] if 'ReadPixels' not in str(e.get('text'))][:40]
                # 全隐藏对照（同一背景）
                await ev("window.__primOnly(-1)")
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                res['states']['C_magenta_noinject_hidden'] = await snap('C_magenta_noinject_hidden')
                await ev("window.__primOnly(null)")
                await ev("window.WikiWeaponViewer.canvasShot(2)")
                res['info_render_noinject'] = json.loads(await ev("JSON.stringify(window.__envRenderer.info.render)"))

            res['console_events'] = EVENTS[:400]
            res['events_total'] = TOTAL[0]
            res['net_bad'] = NET_BAD[:40]
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
        if masks:
            union = np.zeros(next(iter(masks.values())).shape, bool)
            for mk in masks.values():
                union |= mk
            analysis['mask_pixels'] = {str(i): int(mk.sum()) for i, mk in masks.items()}
            analysis['union_pixels'] = int(union.sum())
            for tag in ('A_default_chain', 'A_default_hidden', 'B_magenta_chain', 'B_magenta_hidden',
                        'C_magenta_noinject', 'C_magenta_noinject_hidden'):
                st = res['states'].get(tag) or {}
                if st.get('file'):
                    analysis[tag + '_inside'] = stats(os.path.join(OUT, st['file']), union)
            def diff_pair(a_tag, b_tag, label):
                a = res['states'].get(a_tag) or {}; b = res['states'].get(b_tag) or {}
                if not (a.get('file') and b.get('file') and union.any()):
                    return
                aa, bb = load(a['file']), load(b['file'])
                d = np.abs(aa - bb).max(axis=2)
                ok = d[union] > 8
                analysis[label] = {'diff_pixels_inside_mask': int(ok.sum()),
                                   'diff_pct_inside_mask': round(100.0 * float(ok.sum()) / max(1, int(union.sum())), 3),
                                   'mean_a_inside': [round(float(x), 1) for x in aa[union].mean(0)],
                                   'mean_b_inside': [round(float(x), 1) for x in bb[union].mean(0)],
                                   'per_prim_diff_pct': {str(i): round(100.0 * float((d[mk] > 8).sum()) / max(1, int(mk.sum())), 2) for i, mk in masks.items()},
                                   'whole_image_maxdiff': int(np.abs(aa - bb).max()),
                                   'whole_image_diff_pixels': int((np.abs(aa - bb).max(axis=2) > 8).sum())}
            diff_pair('B_magenta_chain', 'B_magenta_hidden', 'FORK_chain_vs_hidden')
            diff_pair('C_magenta_noinject', 'C_magenta_noinject_hidden', 'CTRL_noinject_vs_hidden')
            diff_pair('A_default_chain', 'A_default_hidden', 'A_chain_vs_hidden')
            diff_pair('B_magenta_chain', 'C_magenta_noinject', 'CHAIN_vs_NOINJECT')
            kind = {'weapon': [0, 4], 'crystal': [1, 2, 3, 5, 6]}
            for gname, idxs in kind.items():
                a = res['states'].get('B_magenta_chain') or {}; b = res['states'].get('B_magenta_hidden') or {}
                c = res['states'].get('C_magenta_noinject') or {}
                if a.get('file') and b.get('file') and c.get('file'):
                    aa, bb, cc = load(a['file']), load(b['file']), load(c['file'])
                    mk = np.zeros(union.shape, bool)
                    for i in idxs:
                        mk |= masks[i]
                    if mk.any():
                        analysis['group_%s' % gname] = {
                            'pixels': int(mk.sum()),
                            'chain_vs_hidden_maxdiff': int(np.abs(aa - bb).max(axis=2)[mk].max()),
                            'chain_equals_background_pct': round(100.0 * float((np.abs(aa - bb).max(axis=2)[mk] <= 8).mean()), 2),
                            'noinject_visible_pct': round(100.0 * float((np.abs(cc - bb).max(axis=2)[mk] > 8).mean()), 2),
                            'noinject_mean': [round(float(x), 1) for x in cc[mk].mean(0)]}
    except Exception as e:
        analysis['error'] = str(e)
    res['analysis'] = analysis
    json.dump(res, open(os.path.join(OUT, 'env_probe_3.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print('=== hook:', res.get('hook'))
    print('=== selftest:', json.dumps(res.get('selftest'), ensure_ascii=False))
    print('=== events_total', res['events_total'])
    seen = set()
    for e in res['console_events']:
        t = str(e.get('text', ''))
        if 'ReadPixels' in t and 'ReadPixels' in seen:
            continue
        key = t[:70]
        if key in seen:
            continue
        seen.add(key)
        if 'ReadPixels' in t:
            continue
        print('  [%s] %s' % (e.get('t'), t[:1500].replace('\n', ' | ')))
    print('=== net_bad', json.dumps(res['net_bad'][:8], ensure_ascii=False)[:400])
    d = res.get('dump')
    if d:
        print('=== threeRev', d.get('threeRev'), 'gl', d.get('gl'), 'bg', d.get('scene_background'), 'env', d.get('scene_environment'), 'envInt', d.get('scene_environmentIntensity'))
        print('=== lights', json.dumps(d.get('lights'), ensure_ascii=False))
        print('=== info_render', d.get('info_render'), 'memory', d.get('info_memory'))
        print('=== programs', json.dumps(d.get('programs'), ensure_ascii=False)[:600])
        for m in d.get('meshes', []):
            mt = m['mat']
            def s(t):
                if not t:
                    return 'null'
                if t.get('isCubeTexture'):
                    return 'CUBE faces=%s cs=%s ver=%s minF=%s mipmaps=%s' % (len(t.get('image') or []), t.get('colorSpace'), t.get('version'), t.get('minFilter'), t.get('mipmaps'))
                im = t.get('image')
                if isinstance(im, list):
                    im = im[0] if im else None
                return 'TEX %sx%s cs=%s ver=%s %s' % (im.get('w'), im.get('h'), t.get('colorSpace'), t.get('version'), im.get('src')) if im else 'TEX(no-img)'
            print('mesh%d vis=%s %s color=%s metal=%s rough=%s envI=%s vcount=%s' % (m['idx'], m['visible'], mt['type'], mt['color'], mt['metalness'], mt['roughness'], mt['envMapIntensity'], m.get('vcount')))
            print('    map=%s' % s(mt['map']))
            print('    metalMap=%s roughMap=%s' % (s(mt['metalnessMap']), s(mt['roughnessMap'])))
            print('    normalMap=%s envMap=%s' % (s(mt['normalMap']), s(mt['envMap'])))
            u = mt['userData']
            print('    chain=%s failClosed=%s obc=%s fragLen=%s dunder=%s' % (json.dumps(u.get('chain'), ensure_ascii=False)[:160], u.get('failClosedPlaceholder'), u.get('hasOnBeforeCompile'), u.get('fragLen'), json.dumps(u.get('frag_double_underscore_tokens'), ensure_ascii=False)[:220]))
            print('    uniforms=%s' % json.dumps(u.get('shaderUniforms'), ensure_ascii=False)[:300])
    print('=== bg_selftest', json.dumps(res.get('bg_selftest'), ensure_ascii=False), 'bg_after_chain', res.get('bg_after_chain'))
    print('=== frag_evidence')
    print(json.dumps(res.get('frag_evidence'), ensure_ascii=False, indent=1)[:2500])
    print('=== tex_cube_stats')
    print(json.dumps(res.get('tex_cube_stats'), ensure_ascii=False, indent=1)[:2500])
    print('=== noinject', res.get('noinject'), 'events_after_noinject', json.dumps(res.get('events_after_noinject'), ensure_ascii=False)[:800])
    print('=== info_render: all_visible', res.get('info_render_all_visible'), 'all_hidden', res.get('info_render_all_hidden'), 'noinject', res.get('info_render_noinject'))
    print('=== analysis')
    print(json.dumps(res.get('analysis'), ensure_ascii=False, indent=1)[:6000])


asyncio.run(main())
