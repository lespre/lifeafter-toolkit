# -*- coding: utf-8 -*-
"""决定性验收：不看投影(NDC)，直接量【截图像素】里模型的位置
dpr 1 / 1.5 / 2 三种缩放；同时对比 canvas 布局尺寸 vs 舞台尺寸（应相等）
"""
import asyncio, json, os, shutil, subprocess, time
import urllib.request
import numpy as np
from PIL import Image
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\render_1003_010\_wiki_verify'

async def run(scale, port):
    prof = os.path.join(OUT, '_p_px%s' % scale); shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
                             '--hide-scrollbars', '--window-size=1920,1000', '--force-device-scale-factor=%s' % scale,
                             f'--remote-debugging-port={port}', f'--user-data-dir={prof}', 'about:blank'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(4)
    try:
        page = next(t for t in json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json')) if t.get('type') == 'page')
        async with websockets.connect(page['webSocketDebuggerUrl'], max_size=64 << 20) as ws:
            _id = 0
            async def send(m, **p):
                nonlocal _id
                _id += 1; mid = _id
                await ws.send(json.dumps(dict(id=mid, method=m, params=p)))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get('id') == mid:
                        return msg.get('result', {})
            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=URL); await asyncio.sleep(7)
            await send('Runtime.evaluate', expression="""(() => { window.WikiWeaponViewer.open({skin_id:'1110171',
              poster:'assets/3d/weapon_skin/1110171/poster.webp',
              preview_3d:{status:'ready',manifest:'assets/3d/weapon_skin/1110171/viewer.json'}},{title:'x'}); return 1;})()""",
                       returnByValue=True)
            await asyncio.sleep(14)
            info = (await send('Runtime.evaluate', expression="""(() => {
              const c=document.querySelector('.wv-canvas canvas'), st=document.querySelector('.wv-stage');
              const cr=c.getBoundingClientRect(), sr=st.getBoundingClientRect();
              return {dpr:devicePixelRatio, buf:[c.width,c.height], canvasLayout:[Math.round(cr.width),Math.round(cr.height)],
                      stage:[Math.round(sr.width),Math.round(sr.height)], rect:{x:Math.round(cr.x),y:Math.round(cr.y)},
                      stageRect:{x:Math.round(sr.x),y:Math.round(sr.y)}};})()""", returnByValue=True))['result']['value']
            import base64
            shot = await send('Page.captureScreenshot', format='png')
            png = os.path.join(OUT, 'px_dpr%s.png' % scale); open(png, 'wb').write(base64.b64decode(shot['data']))
            img = Image.open(png).convert('RGB')
            W, H = img.size
            sc = W / info['stage'][0] / 1.0
            # 舞台在截图里的像素范围（截图可能带 dpr 缩放）
            sx = info['stageRect']['x']; sy = info['stageRect']['y']
            k = W / (await send('Runtime.evaluate', expression='innerWidth', returnByValue=True))['result']['value']
            box = (int(sx * k), int(sy * k), int((sx + info['stage'][0]) * k), int((sy + info['stage'][1]) * k))
            a = np.asarray(img.crop(box), np.float32).mean(2)
            m = a > max(26.0, np.percentile(a, 99.3) * 0.22)
            ys, xs = np.nonzero(m)
            h, w = a.shape
            print('dpr=%s 实际%.2f | canvas布局=%s 舞台=%s (应相等) | 截图内模型中心=(%.3f, %.3f) 偏移=(%+.3f,%+.3f) | 左%.0f%% 右%.0f%% 上%.0f%% 下%.0f%%'
                  % (scale, info['dpr'], info['canvasLayout'], info['stage'],
                     (xs.min() + xs.max()) / 2 / w, (ys.min() + ys.max()) / 2 / h,
                     (xs.min() + xs.max()) / 2 / w - .5, (ys.min() + ys.max()) / 2 / h - .5,
                     100 * xs.min() / w, 100 * (w - xs.max()) / w, 100 * ys.min() / h, 100 * (h - ys.max()) / h))
            print('        截图 ->', png)
    finally:
        proc.kill(); time.sleep(0.5)

for i, s in enumerate(['1', '1.5', '2']):
    asyncio.run(run(s, 9400 + i))
