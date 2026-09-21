# -*- coding: utf-8 -*-
"""双枪逐子网格/材质隔离图：定位"金色丢在哪个材质"（不作任何颜色交换，仅隔离显示）"""
import asyncio, base64, io, json, os, shutil, subprocess, time
import urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import websockets
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\render_1003_010\_dual_mats'
os.makedirs(OUT, exist_ok=True)
REL = 'assets/3d/weapon_skin/1110171'
META = [
    (0, 0, 'skin_1003_012_0', 'pbr_weapon', '012枪身'),
    (1, 1, 'skin_1003_012_1', 'pbr_crystal', '012晶体'),
    (2, 2, 'skin_1003_012_2', 'pbr_crystal', '012晶体'),
    (3, 3, 'skin_1003_012_3', 'pbr_crystal', '012晶体'),
    (4, 4, 'skin_1003_010_0', 'pbr_weapon', '010枪身'),
    (5, 5, 'skin_1003_010_1', 'pbr_crystal', '010晶体'),
    (6, 6, 'skin_1003_010_2', 'pbr_crystal', '010晶体'),
]
async def main():
    prof = os.path.join(OUT, '_prof'); shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
        '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1400,900',
        '--remote-debugging-port=9833', '--user-data-dir=%s' % prof, 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:9833/json')) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=128 << 20) as ws:
            _id = 0
            async def send(m, **p):
                nonlocal _id
                _id += 1; mid = _id
                await ws.send(json.dumps(dict(id=mid, method=m, params=p)))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get('id') == mid: return msg.get('result', {})
            async def ev(e, aw=False):
                r = await send('Runtime.evaluate', expression=e, returnByValue=True, awaitPromise=aw)
                return (r.get('result', {}) or {}).get('value')
            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=URL); await asyncio.sleep(7)
            await ev("(() => { window.WikiWeaponViewer.open({skin_id:'1110171',poster:'%s/poster.webp',preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'}); return 1;})()" % (REL, REL))
            await asyncio.sleep(16)
            await ev("(() => {const s=document.querySelector('.wv-state-select');if(s){s.value='dual';s.dispatchEvent(new Event('change',{bubbles:true}));}return 1;})()")
            await asyncio.sleep(15)
            await ev("(() => {document.querySelectorAll('.wv-poster,.wv-loading,.wv-status').forEach(e=>e.style.display='none');return 1;})()")
            st = await ev("JSON.parse(JSON.stringify(window.WikiWeaponViewer.__state()))")
            print('取景:', json.dumps({k: st.get(k) for k in ['projCenter', 'clipped', 'crystalLayers', 'buffer']}, ensure_ascii=False))
            box = await ev("(() => {const c=document.querySelector('.wv-canvas canvas').getBoundingClientRect();return {x:c.x,y:c.y,w:Math.round(c.width),h:Math.round(c.height)};})()")
            tiles = []
            for sub, mtl, name, shader, part in META:
                await ev("window.WikiWeaponViewer.__materialExperiment({onlySubmesh:%d})" % sub)
                await asyncio.sleep(1.0)
                s = await send('Page.captureScreenshot', format='png', clip=dict(x=box['x'], y=box['y'], width=box['w'], height=box['h'], scale=1))
                im = Image.open(io.BytesIO(base64.b64decode(s['data']))).convert('RGB')
                a = np.asarray(im, np.float32)
                ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]
                bgl = np.stack([a[3,3], a[3,-4], a[-4,3], a[-4,-4]]).mean(0)
                m = np.abs(a - bgl).max(2) > 12
                cov = 100 * float(m.mean())
                if m.sum() > 50:
                    px = a[m]
                    mean = px.mean(0); p90 = np.percentile(px, 90, axis=0)
                    warm = float(((px[:, 0] > px[:, 2] + 12) & (px[:, 0] > 60)).mean() * 100)
                else:
                    mean = p90 = np.zeros(3); warm = 0.0
                print('  Sub%d Mtl%d %-18s %-12s 覆盖%.1f%% 均值(%3.0f,%3.0f,%3.0f) p90(%3.0f,%3.0f,%3.0f) 暖色占%.1f%%' % (
                    sub, mtl, name, shader, cov, *mean, *p90, warm))
                fn = os.path.join(OUT, 'sub%d_%s.png' % (sub, name)); im.save(fn)
                tiles.append((im, 'Sub%d  MtlIdx=%d  %s  %s  「%s」' % (sub, mtl, name, shader, part), cov, mean, warm))
            await ev("window.WikiWeaponViewer.__materialExperiment({})")
            W2 = 640
            th = [t[0].resize((W2, int(t[0].height * W2 / t[0].width)), Image.LANCZOS) for t in tiles]
            cols, rows = 4, 2
            cw, chh = W2, max(t.height for t in th) + 44
            sheet = Image.new('RGB', (cw * cols, chh * rows + 30), (14, 18, 26))
            d = ImageDraw.Draw(sheet)
            try: F = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 15); F2 = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 13)
            except Exception: F = F2 = ImageFont.load_default()
            d.text((6, 6), '光影咏叹调·双枪 逐子网格/材质隔离（同一相机·同一环境·无颜色交换）', fill=(255, 235, 160), font=F)
            for i, (im, lb, cov, mean, warm) in enumerate(tiles):
                cx, cy = (i % cols) * cw, 30 + (i // cols) * chh
                sheet.paste(im, (cx, cy + 40))
                d.text((cx + 4, cy + 4), lb, fill=(210, 230, 255), font=F)
                d.text((cx + 4, cy + 22), '覆盖%.1f%% 均值(%3.0f,%3.0f,%3.0f) 暖色%4.1f%%' % (cov, *mean, warm), fill=(180, 200, 230), font=F2)
            out = os.path.join(OUT, 'dual_submesh_sheet.png'); sheet.save(out)
            print('->', out)
    finally:
        proc.kill(); await asyncio.sleep(0.3)
asyncio.run(main())
