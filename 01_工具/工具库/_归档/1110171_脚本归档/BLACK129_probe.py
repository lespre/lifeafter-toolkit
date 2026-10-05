# -*- coding: utf-8 -*-
"""BLACK129_probe.py — 1110129 纯黑剪影根因探查：envMapIntensity / 替代 cube 是否加载 / cube 亮度 / 与 1110145 同快照对照。
只读（写 _target_1110171/BLACK129_*）。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, urllib.error, base64, hashlib
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BOARD = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9921
PROF = os.path.join(os.environ.get('TEMP', OUT), 'BLACK129_prof')
SKINS = ['1110129', '1110145']


def http(u):
    for m in ('HEAD', 'GET'):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, method=m), timeout=12).status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception:
            return 'ERR' if m == 'GET' else None
    return 'ERR'


JS = r"""(function(){
  var out={dump:null, meshes:[]};
  try{ out.dump=window.WikiWeaponViewer.__matDump?window.WikiWeaponViewer.__matDump():null; }catch(e){ out.dumpErr=String(e); }
  var T=window.__envTHREE, scene=window.__envScene, r=window.__envRenderer;
  if(!T||!scene) return JSON.stringify({error:'no hook'});
  out.scene_environment = scene.environment? (scene.environment.isTexture? ('tex cs='+scene.environment.colorSpace+' mapping='+scene.environment.mapping) : String(scene.environment.type)) : null;
  out.environmentIntensity = (scene.environmentIntensity===undefined?null:scene.environmentIntensity);
  out.toneMapping = r.toneMapping; out.exposure = r.toneMappingExposure;
  function faceStats(list){
    var res=[];
    for(var i=0;i<list.length;i++){
      try{ var c=document.createElement('canvas'); c.width=32;c.height=32; var x=c.getContext('2d');
        x.drawImage(list[i],0,0,32,32); var d=x.getImageData(0,0,32,32).data; var n=0,R=0,G=0,B=0,A=0,mx=0;
        for(var p=0;p<d.length;p+=4){R+=d[p];G+=d[p+1];B+=d[p+2];A+=d[p+3];var l=(d[p]+d[p+1]+d[p+2])/3;if(l>mx)mx=l;n++;}
        res.push({i:i, mean:[+(R/n).toFixed(1),+(G/n).toFixed(1),+(B/n).toFixed(1)], meanA:+(A/n).toFixed(1), maxLum:mx,
                  src:String(list[i].currentSrc||list[i].src||'').split('/').slice(-2).join('/')});
      }catch(e){ res.push({i:i, error:String(e&&e.message||e)}); }
    }
    return res;
  }
  scene.traverse(function(o){ if(!o.isMesh||!o.material) return; var m=o.material; var ud=m.userData||{};
    var e=m.envMap; var rec={name:o.name||'', mat:m.type, visible:!!o.visible,
      metalness:m.metalness, roughness:m.roughness, envMapIntensity:(m.envMapIntensity===undefined?null:m.envMapIntensity),
      color:m.color?('#'+m.color.getHexString()):null, toneMapped:(m.toneMapped===undefined?null:!!m.toneMapped),
      envMap: e? {isCube:!!e.isCubeTexture, faces:(e.image&&e.image.length)||0, cs:e.colorSpace, mapping:e.mapping,
                  face_stats: (e.isCubeTexture&&e.image)?faceStats(e.image):faceStats([e.image])} : null,
      map:m.map?(m.map.image?m.map.image.width+'x'+m.map.image.height:'noimg'):null,
      normalMap:!!m.normalMap,
      ibl:(ud.ibl===undefined?null:ud.ibl), chain_prim:((ud.chain||{}).prim===undefined?null:ud.chain.prim),
      neox:(ud.neox?{environment:ud.neox.environment, fidelity:ud.neox.material_fidelity, fail_closed:ud.neox.ibl_fail_closed}:null),
      has_onBeforeCompile: (typeof m.onBeforeCompile==='function'),
      shader_uniform_ibl: (ud.__sh&&ud.__sh.uniforms&&ud.__sh.uniforms.uCustomIbl)?('cube faces='+((ud.__sh.uniforms.uCustomIbl.value&&ud.__sh.uniforms.uCustomIbl.value.image&&ud.__sh.uniforms.uCustomIbl.value.image.length)||0)):null,
      shader_uniform_iblScale: (ud.__sh&&ud.__sh.uniforms&&ud.__sh.uniforms.uIblScale)?ud.__sh.uniforms.uIblScale.value:null,
      shader_uniform_iblStrength: (ud.__sh&&ud.__sh.uniforms&&ud.__sh.uniforms.uIblStrength)?ud.__sh.uniforms.uIblStrength.value:null};
    out.meshes.push(rec); });
  return JSON.stringify(out);
})()"""


async def main():
    res = {'viewer_json': {}, 'http': {}}
    for skin in SKINS:
        vp = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', skin, 'viewer.json')
        if os.path.isfile(vp):
            v = json.load(open(vp, encoding='utf-8'))
            res['viewer_json'][skin] = {k: v.get(k) for k in ('background_image', 'env_from_background', 'environment_approximate',
                                                              'env_intensity', 'background', 'material_mapping', 'source_chain') if k in v}
        # cube 资源存在性 + HTTP
        base = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', skin, 'src_cube')
        res['http'][skin] = {'src_cube_dir': os.path.isdir(base),
                             'files': (sorted(os.listdir(base))[:8] if os.path.isdir(base) else []),
                             'faces_dir': (sorted(os.listdir(os.path.join(base, 'faces'))[:6]) if os.path.isdir(os.path.join(base, 'faces')) else [])}
        for rel in ('src_cube/qiangpi.dds', 'src_cube/faces/qiangpi_f0_m0.png', 'src_cube/faces/qiangpi_f5_m0.png'):
            p = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', skin, rel)
            res['http'][skin][rel] = {'disk': os.path.isfile(p),
                                      'http': http('http://127.0.0.1:8765/assets/3d/weapon_skin/%s/%s' % (skin, rel))}
    shutil.rmtree(PROF, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
                           '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1400,1000',
                           '--remote-debugging-port=%d' % PORT, '--user-data-dir=%s' % PROF, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0; pending = {}

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
                fut = asyncio.get_event_loop().create_future(); pending[_i] = fut
                await ws.send(json.dumps({'id': _i, 'method': method, 'params': params}))
                return await asyncio.wait_for(fut, timeout=120)

            async def ev(expr, wait=0.0):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True, timeout=120000)
                if r.get('result', {}).get('exceptionDetails'):
                    return 'EXC'
                if wait:
                    await asyncio.sleep(wait)
                return (r.get('result', {}).get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=BOARD); await asyncio.sleep(10)
            hook = r"""(async()=>{ if(window.__envHooked) return 'ok';
              const THREE=await import('http://127.0.0.1:8765/assets/vendor/three/three.module.min.js');
              const O=THREE.Object3D.prototype, ob=O.onBeforeRender;
              O.onBeforeRender=function(r,s,c){ if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envScene=s; } return ob.apply(this,arguments); };
              const tv=O.traverse; O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
              window.__envTHREE=THREE; window.__envHooked=true; return 'ok'; })()"""
            await ev(hook)
            for skin in SKINS:
                await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'%s',poster:'assets/3d/weapon_skin/%s/poster.webp',preview_3d:{status:'ready',manifest:'assets/3d/weapon_skin/%s/viewer.json'}},{title:'%s'});return 1;})()" % (skin, skin, skin, skin))
                await asyncio.sleep(9)
                await ev("window.WikiWeaponViewer.canvasShot&&window.WikiWeaponViewer.canvasShot(2)")
                d = await ev(JS)
                s = await send('Page.captureScreenshot', format='png')
                raw = base64.b64decode(s['result']['data'])
                fn = os.path.join(OUT, 'BLACK129_%s.png' % skin)
                open(fn, 'wb').write(raw)
                rec = json.loads(d) if isinstance(d, str) and d.startswith('{') else {'raw': str(d)[:200]}
                rec['shot'] = {'file': fn, 'sha16': hashlib.sha256(raw).hexdigest()[:16]}
                res[skin] = rec
                print('== %s == env=%s envInt=%s toneMap=%s exp=%s' % (skin, rec.get('scene_environment'), rec.get('environmentIntensity'), rec.get('toneMapping'), rec.get('exposure')))
                for m in (rec.get('meshes') or [])[:3]:
                    em = m.get('envMap') or {}
                    print('   %s metal=%s rough=%s envI=%s envMap=%s faces=%s ibl=%s neox=%s' % (
                        m['mat'], m['metalness'], m['roughness'], m['envMapIntensity'],
                        'yes' if m.get('envMap') else 'null', em.get('faces'), m.get('ibl'), json.dumps(m.get('neox'), ensure_ascii=False)))
                    for f in (em.get('face_stats') or [])[:2]:
                        print('        face%s mean=%s src=%s' % (f.get('i'), f.get('mean'), f.get('src')))
                print('   截图', fn, rec['shot']['sha16'])
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'BLACK129_probe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\nhttp:', json.dumps(res['http'], ensure_ascii=False)[:800])
    print('viewer.json 关键字段:', json.dumps(res['viewer_json'], ensure_ascii=False)[:600])
    print('json ->', os.path.join(OUT, 'BLACK129_probe.json'))


asyncio.run(main())
