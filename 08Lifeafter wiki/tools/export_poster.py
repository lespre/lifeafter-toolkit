# -*- coding: utf-8 -*-
"""从当前查看器同一次运行导出海报（P2）。
要求：① 与实时图同代码路径（同一 viewer.js / 同一 viewer.json / 同一 GLB）
     ② 产出登记来源与版本（写回 provenance.json）
     ③ 验收：__state() 的 projCenter≈[0.5,0.5] 且 clipped=false
"""
import asyncio, base64, hashlib, io, json, os, shutil, subprocess, sys, time
import urllib.request
import websockets
from PIL import Image
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
W = r'E:\la拆包项目\08Lifeafter wiki'
SID = sys.argv[1] if len(sys.argv) > 1 else '1110171'
STATE = sys.argv[2] if len(sys.argv) > 2 else 'dual'
WIDTH, HEIGHT = 2260, 1150
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\render_1003_010\_poster_export'
os.makedirs(OUT, exist_ok=True)

async def main():
    prof = os.path.join(OUT, '_prof'); shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
        '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
        '--window-size=%d,%d' % (WIDTH + 60, HEIGHT + 150), '--remote-debugging-port=9831',
        '--user-data-dir=%s' % prof, 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:9831/json')) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=128 << 20) as ws:
            _id = 0
            async def send(m, **p):
                nonlocal _id
                _id += 1; mid = _id
                await ws.send(json.dumps(dict(id=mid, method=m, params=p)))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get('id') == mid: return msg.get('result', {})
            async def ev(expr, await_=False):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=await_)
                return (r.get('result', {}) or {}).get('value')
            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=URL); await asyncio.sleep(7)
            rel = 'assets/3d/weapon_skin/%s' % SID
            await ev("(() => { window.WikiWeaponViewer.open({skin_id:'%s',poster:'%s/poster.webp',preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'}); return 1;})()" % (SID, rel, rel))
            await asyncio.sleep(16)
            # 形态
            await ev("(() => {const s=document.querySelector('.wv-state-select');if(s){s.value='%s';s.dispatchEvent(new Event('change',{bubbles:true}));}return s?s.value:'none';})()" % STATE)
            await asyncio.sleep(14)
            # 容器按海报尺寸固定（覆盖 CSS 上限），隐藏海报/加载层
            await ev("""(() => {
              let st=document.getElementById('__poster_export_css');
              if(!st){st=document.createElement('style');st.id='__poster_export_css';document.head.appendChild(st);}
              st.textContent='#weaponSkinViewer .wv-dialog{max-width:none!important;max-height:none!important;width:auto!important;height:auto!important;}'
                +'#weaponSkinViewer .wv-stage{width:%dpx!important;height:%dpx!important;max-width:none!important;max-height:none!important;}'
                +'#weaponSkinViewer .wv-poster,#weaponSkinViewer .wv-loading,#weaponSkinViewer .wv-status{display:none!important;}';
              document.querySelectorAll('.wv-poster,.wv-loading,.wv-status').forEach(e=>e.style.display='none');
              return 1;})()""" % (WIDTH, HEIGHT))
            await asyncio.sleep(2)
            # 复位视角 → 查看器自己按新画布重算取景
            for _ in range(2):
                await ev("(() => {const b=document.querySelector('.wv-reset');if(b)b.click();return 1;})()")
                await asyncio.sleep(4)
            st = await ev("JSON.parse(JSON.stringify(window.WikiWeaponViewer.__state()))")
            print('取景检查:', json.dumps({k: st.get(k) for k in ['version','projCenter','clipped','buffer','cssBox','dpr','up','crystalLayers']}, ensure_ascii=False))
            box = await ev("(() => {const c=document.querySelector('.wv-canvas canvas').getBoundingClientRect();return {x:c.x,y:c.y,w:Math.round(c.width),h:Math.round(c.height)};})()")
            print('画布盒子:', box)
            s = await send('Page.captureScreenshot', format='png', clip=dict(x=box['x'], y=box['y'], width=box['w'], height=box['h'], scale=1))
            im = Image.open(io.BytesIO(base64.b64decode(s['data']))).convert('RGB')
            if (im.width, im.height) != (WIDTH, HEIGHT):
                im = im.resize((WIDTH, HEIGHT), Image.LANCZOS)
            png = os.path.join(OUT, 'poster_%s_%s.png' % (SID, STATE)); im.save(png)
            dst = os.path.join(W, 'assets', '3d', 'weapon_skin', SID, 'poster.webp')
            im.save(dst, 'WEBP', quality=92, method=6)
            h16 = hashlib.sha256(open(dst, 'rb').read()).hexdigest()[:16]
            print('海报写出:', dst, '%dx%d' % (im.width, im.height), 'sha16', h16)
            # 登记来源与版本
            src = dict(
                generated_by='tools/export_poster.py (从查看器同一次运行导出)',
                generated_at=time.strftime('%Y-%m-%d %H:%M:%S'),
                viewer_version=st.get('version'),
                board_url=URL, manifest='%s/viewer.json' % rel, state=STATE,
                canvas_px=[WIDTH, HEIGHT], proj_center=st.get('projCenter'), clipped=st.get('clipped'),
                camera=[st.get('azimuth'), st.get('polar'), st.get('distance')],
                up=st.get('up'), roll_deg=(st.get('__roll') if st.get('__roll') is not None else None),
                pose_preset=dict([(k, v) for k, v in (json.load(open(os.path.join(W, 'assets/3d/weapon_skin', SID, 'viewer.json'), encoding='utf-8')).get('camera_presets') or [{}])[0].items() if k in ('label', 'position', 'target', 'up', 'distance', 'fov', 'fit_span')]),
                glb_sha16=dict(dual=hashlib.sha256(open(os.path.join(W, 'assets', '3d', 'weapon_skin', SID, 'dual.glb'), 'rb').read()).hexdigest()[:16],
                               single=hashlib.sha256(open(os.path.join(W, 'assets', '3d', 'weapon_skin', SID, 'single.glb'), 'rb').read()).hexdigest()[:16]),
                viewer_json_sha16=hashlib.sha256(open(os.path.join(W, 'assets', '3d', 'weapon_skin', SID, 'viewer.json'), 'rb').read()).hexdigest()[:16],
                poster_sha16=h16)
            pj = os.path.join(W, 'assets', '3d', 'weapon_skin', SID, 'provenance.json')
            d = json.load(open(pj, encoding='utf-8'))
            d['poster'] = src
            json.dump(d, open(pj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('provenance.json 已登记 poster 条目')
    finally:
        proc.kill(); await asyncio.sleep(0.3)

asyncio.run(main())
