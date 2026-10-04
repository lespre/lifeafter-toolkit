# -*- coding: utf-8 -*-
"""REPACK_1110129.py — 1110129 的 __matDump/实采样 + 分辨率核对 + 黑像素 前(旧repack)/后(新repack) A/B + 截图。
A/B 做法：换文件 → 重新导航（避免贴图缓存）→ 渲染 → 截 canvas → 同口径统计；结束时恢复新文件。
只写 _target_1110171/REPACK_*；对皮肤的写仅限 param_repack_008.png（先备份已有）。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib
import numpy as np
from PIL import Image
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BOARD = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
W = r'E:\la拆包项目\08Lifeafter wiki\assets\3d\weapon_skin\1110129'
CUR = os.path.join(W, 'src_tex', 'param_repack_008.png')
SRC = os.path.join(W, 'src_tex', '008_m.png')
BK = os.path.join(OUT, 'REPACK_backup')
NEW_TMP = os.path.join(OUT, 'REPACK_1110129_new.bin')
PORT = 9920
PROF = os.path.join(os.environ.get('TEMP', OUT), 'REPACK_prof9920')

res = {}
res['resolution'] = {'param_repack_008': Image.open(CUR).size, 'source_008_m': Image.open(SRC).size,
                     'match': Image.open(CUR).size == Image.open(SRC).size}
print('分辨率:', res['resolution'])
shutil.copyfile(CUR, NEW_TMP)                      # 暂存新图
bks = sorted(os.path.join(BK, f) for f in os.listdir(BK) if f.startswith('1110129_008_'))
OLD = bks[0] if bks else None
print('旧图备份:', OLD, '| 现图 sha16', hashlib.sha256(open(CUR, 'rb').read()).hexdigest()[:16],
      '| 备份 sha16', hashlib.sha256(open(OLD, 'rb').read()).hexdigest()[:16] if OLD else None)


def stats(path):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
    lum = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]
    return {'black_pct_lt16': round(float(100 * (lum < 16).mean()), 2),
            'black_pct_lt8': round(float(100 * (lum < 8).mean()), 2),
            'p50': round(float(np.percentile(lum, 50)), 1), 'p95': round(float(np.percentile(lum, 95)), 1),
            'mean': round(float(lum.mean()), 1)}


async def run_phase(pr_page, tag):
    async with websockets.connect(pr_page['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
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
            rr = r.get('result', {})
            if rr.get('exceptionDetails'):
                return 'EXC'
            if wait:
                await asyncio.sleep(wait)
            return (rr.get('result', {}) or {}).get('value')
        await send('Page.enable'); await send('Runtime.enable')
        await send('Page.setCacheDisabled', cacheDisabled=True)
        await send('Page.navigate', url=BOARD + '&_cb=' + tag)
        await asyncio.sleep(9)
        await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110129',poster:'assets/3d/weapon_skin/1110129/poster.webp',preview_3d:{status:'ready',manifest:'assets/3d/weapon_skin/1110129/viewer.json'}},{title:'1110129'});return 1;})()")
        await asyncio.sleep(9)
        hook = r"""(async()=>{ if(window.__envHooked) return 'ok';
          const THREE=await import('http://127.0.0.1:8765/assets/vendor/three/three.module.min.js');
          const O=THREE.Object3D.prototype, ob=O.onBeforeRender;
          O.onBeforeRender=function(r,s,c){ if(s&&s.isScene&&s.children&&s.children.length>1){ window.__envRenderer=r; window.__envScene=s; } return ob.apply(this,arguments); };
          const tv=O.traverse; O.traverse=function(cb){ if(this.isScene&&this.children&&this.children.length>1) window.__envScene=this; return tv.call(this,cb); };
          window.__envTHREE=THREE; window.__envHooked=true; return 'ok'; })()"""
        await ev(hook)
        await ev("window.WikiWeaponViewer.canvasShot&&window.WikiWeaponViewer.canvasShot(2)")
        dump = await ev(r"""(function(){
          var mm=[]; if(window.__envScene) window.__envScene.traverse(function(o){ if(!o.isMesh||!o.material) return; var m=o.material;
            function s(t){ if(!t||!t.image) return null; try{ var c=document.createElement('canvas'); c.width=64;c.height=64;
              var x=c.getContext('2d'); x.drawImage(t.image,0,0,64,64); var p=x.getImageData(0,0,64,64).data,n=0,G=0,B=0;
              for(var i=0;i<p.length;i+=4){G+=p[i+1];B+=p[i+2];n++;} return {G:+(G/n/255).toFixed(4),B:+(B/n/255).toFixed(4)}; }catch(e){return null;} }
            mm.push({name:o.name||'',mat:m.type,metalness:m.metalness,roughness:m.roughness,
              metalMap:m.metalnessMap?((m.metalnessMap.image?m.metalnessMap.image.width+'x'+m.metalnessMap.image.height:'noimg')):null,
              roughMap:m.roughnessMap?((m.roughnessMap.image?m.roughnessMap.image.width+'x'+m.roughnessMap.image.height:'noimg')):null,
              hasMap:!!m.map, hasNormal:!!m.normalMap, metal_rt:s(m.metalnessMap), rough_rt:s(m.roughnessMap)}); });
          return JSON.stringify(mm); })()""")
        s = await send('Page.captureScreenshot', format='png')
        raw = base64.b64decode(s['result']['data'])
        fn = os.path.join(OUT, 'REPACK_1110129_%s.png' % tag)
        open(fn, 'wb').write(raw)
        return {'dump': json.loads(dump), 'shot': fn, 'stats': stats(fn), 'sha16': hashlib.sha256(raw).hexdigest()[:16]}


async def main():
    shutil.rmtree(PROF, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
                           '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1400,1000',
                           '--remote-debugging-port=%d' % PORT, '--user-data-dir=%s' % PROF, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        shutil.copyfile(NEW_TMP, CUR)                                   # 相位1：新图
        res['new'] = await run_phase(pg, 'new')
        if OLD:
            shutil.copyfile(OLD, CUR)                                   # 相位2：旧图
            res['old'] = await run_phase(pg, 'old')
        shutil.copyfile(NEW_TMP, CUR)                                   # 恢复新图
        print('已恢复新图 sha16', hashlib.sha256(open(CUR, 'rb').read()).hexdigest()[:16])
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'REPACK_1110129.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for ph in ('new', 'old'):
        r = res.get(ph)
        if not r:
            continue
        print('== %s == %s' % (ph, json.dumps(r['stats'], ensure_ascii=False)), 'sha16', r['sha16'])
        for m in r['dump'][:3]:
            print('   %s metal=%s rough=%s metalMap=%s(%s) roughMap=%s(%s) map=%s normal=%s' % (
                m['mat'], m['metalness'], m['roughness'], m['metalMap'], m['metal_rt'], m['roughMap'], m['rough_rt'],
                m['hasMap'], m['hasNormal']))
    print('json ->', os.path.join(OUT, 'REPACK_1110129.json'))


asyncio.run(main())
