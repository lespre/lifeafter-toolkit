# -*- coding: utf-8 -*-
"""REPACK_matdump.py — 逐皮肤 __matDump 复核 + 运行时 metal/rough 贴图实际均值 + canvas 截图 + 回归。
端口 9919；只写 _target_1110171/REPACK_*。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BOARD = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9919
PROF = os.path.join(os.environ.get('TEMP', OUT), 'REPACK_prof9919')
SKINS = ['1110145', '1110165', '1110171', '1110152', '1110024']

JS_MAT = r"""(function(){
  var scene=null, r=null;
  try{ r=window.__envRenderer||null; }catch(e){}
  var out={meshes:[], console_errors:window.__errCount||0};
  // 通过 __matDump 拿绑定；再对绑定的贴图在页面内取样（canvas 2D 读像素）
  var d=(window.WikiWeaponViewer.__matDump?window.WikiWeaponViewer.__matDump():null);
  function sample(tex){
    if(!tex||!tex.image) return null;
    try{
      var c=document.createElement('canvas'); c.width=64; c.height=64;
      var x=c.getContext('2d'); x.drawImage(tex.image,0,0,64,64);
      var p=x.getImageData(0,0,64,64).data, n=0, G=0, B=0, mn=255, mx=0;
      for(var i=0;i<p.length;i+=4){ G+=p[i+1]; B+=p[i+2]; if(p[i+1]<mn)mn=p[i+1]; if(p[i+1]>mx)mx=p[i+1]; n++; }
      return {G_mean:+(G/n/255).toFixed(4), B_mean:+(B/n/255).toFixed(4), G_min:mn, G_max:mx};
    }catch(e){ return 'sample_err:'+e.message; }
  }
  // 遍历 3D 根的材质拿真实 Texture 对象
  var T=window.__envTHREE, root=null;
  if(T&&window.__envScene){ window.__envScene.traverse(function(o){ if(o.isMesh&&o.material&&(o.material.metalnessMap||o.material.map)){ if(!root) root=o; } }); }
  var mm=[];
  if(T&&window.__envScene) window.__envScene.traverse(function(o){
    if(!o.isMesh||!o.material) return; var m=o.material;
    mm.push({name:o.name||'', visible:!!o.visible, matType:m.type,
      metalness:m.metalness, roughness:m.roughness,
      hasMap:!!m.map, hasNormalMap:!!m.normalMap,
      metalnessMap:m.metalnessMap?('ok '+(m.metalnessMap.image?m.metalnessMap.image.width+'x'+m.metalnessMap.image.height:'noimg')):null,
      roughnessMap:m.roughnessMap?('ok '+(m.roughnessMap.image?m.roughnessMap.image.width+'x'+m.roughnessMap.image.height:'noimg')):null,
      metal_rt:sample(m.metalnessMap), rough_rt:sample(m.roughnessMap),
      map_rt:sample(m.map), normal_rt:sample(m.normalMap)});
  });
  return JSON.stringify({matDump:d, meshes:mm});
})()"""


async def main():
    shutil.rmtree(PROF, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
                           '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1400,1000',
                           '--remote-debugging-port=%d' % PORT, '--user-data-dir=%s' % PROF, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    res = {'skins': {}}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0
            pending = {}
            evs = []

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
                        p = m.get('params') or {}
                        if m.get('method') in ('Runtime.exceptionThrown',):
                            evs.append({'t': 'exception', 'text': str((p.get('exceptionDetails') or {}).get('text'))[:200]})
                        elif m.get('method') == 'Runtime.consoleAPICalled' and p.get('type') == 'error':
                            evs.append({'t': 'console_error', 'text': ' '.join(str((a or {}).get('value', ''))[:200] for a in (p.get('args') or []))})
            task = asyncio.create_task(pump())

            async def send(method, **params):
                nonlocal _i
                _i += 1
                fut = asyncio.get_event_loop().create_future(); pending[_i] = fut
                await ws.send(json.dumps({'id': _i, 'method': method, 'params': params}))
                r = await asyncio.wait_for(fut, timeout=120)
                if 'error' in r:
                    raise RuntimeError('%s -> %s' % (method, r['error']))
                return r.get('result', {})

            async def ev(expr, wait=0.0):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True, timeout=120000)
                if r.get('exceptionDetails'):
                    return 'EXC ' + str(r['exceptionDetails']['text'])[:200]
                if wait:
                    await asyncio.sleep(wait)
                return (r.get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=BOARD); await asyncio.sleep(10)
            # 装环境钩子（拿 THREE/scene/renderer）
            hook = r"""(async()=>{ if(window.__envHooked) return 'ok';
              const THREE=await import('http://127.0.0.1:8765/assets/vendor/three/three.module.min.js');
              const O=THREE.Object3D.prototype, ob=O.onBeforeRender;
              O.onBeforeRender=function(r,s,c){ if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envScene=s; window.__envCamera=c; } return ob.apply(this,arguments); };
              const tv=O.traverse; O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
              window.__envTHREE=THREE; window.__envHooked=true; window.__errCount=0; return 'ok'; })()"""
            await ev(hook)
            for skin in SKINS:
                rec = await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'%s',poster:'assets/3d/weapon_skin/%s/poster.webp',"
                               "preview_3d:{status:'ready',manifest:'assets/3d/weapon_skin/%s/viewer.json'}},{title:'%s'});return 1;})()" % (skin, skin, skin, skin))
                await asyncio.sleep(9)
                await ev("window.WikiWeaponViewer.canvasShot&&window.WikiWeaponViewer.canvasShot(2)")
                dump = await ev(JS_MAT)
                try:
                    dj = json.loads(dump)
                except Exception:
                    dj = {'error': str(dump)[:200]}
                s = await send('Page.captureScreenshot', format='png')
                raw = base64.b64decode(s['data'])
                fn = os.path.join(OUT, 'REPACK_%s.png' % skin)
                open(fn, 'wb').write(raw)
                dj['shot'] = {'file': fn, 'sha16': hashlib.sha256(raw).hexdigest()[:16]}
                res['skins'][skin] = dj
                print('== %s ==' % skin)
                for m in dj.get('meshes', [])[:3]:
                    print('   %s %s metal=%s rough=%s | metalMap=%s B_rt=%s | roughMap=%s G_rt=%s | map=%s normal=%s' % (
                        m['matType'], m['name'][:14], m['metalness'], m['roughness'], m['metalnessMap'],
                        (m['metal_rt'] or {}).get('B_mean') if isinstance(m['metal_rt'], dict) else m['metal_rt'],
                        m['roughnessMap'], (m['rough_rt'] or {}).get('G_mean') if isinstance(m['rough_rt'], dict) else m['rough_rt'],
                        m['hasMap'], m['hasNormalMap']))
                print('   截图 %s（sha16 %s）' % (fn, dj['shot']['sha16']))
            res['events'] = evs[:20]
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'REPACK_matdump.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n错误事件:', json.dumps(res.get('events'), ensure_ascii=False)[:400])
    print('json ->', os.path.join(OUT, 'REPACK_matdump.json'))


asyncio.run(main())
