# -*- coding: utf-8 -*-
"""T5：lab 模式复核——打印 __neox() 原文、canvas 数量，并兜底整页截图。"""
import asyncio, json, os, shutil, subprocess, urllib.request, base64, hashlib
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc&lab=1'
OUT = os.path.dirname(os.path.abspath(__file__))
REL = 'assets/3d/weapon_skin/1110177'
PORT = 9983


async def main():
    prof = os.path.join(OUT, '_prof_lab2'); shutil.rmtree(prof, ignore_errors=True)
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                          '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                          '--window-size=1400,950', '--remote-debugging-port=%d' % PORT,
                          '--user-data-dir=%s' % prof, 'about:blank'],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            i = {'n': 0}; pend = {}

            async def rd():
                try:
                    async for raw in ws:
                        m = json.loads(raw)
                        if 'id' in m: pend[m['id']] = m
                except Exception: pass
            t = asyncio.create_task(rd())

            async def send(method, **pp):
                i['n'] += 1; k = i['n']
                await ws.send(json.dumps(dict(id=k, method=method, params=pp)))
                for _ in range(900):
                    if k in pend: return pend.pop(k).get('result', {})
                    await asyncio.sleep(0.02)
                return {}

            async def ev(e):
                r = await send('Runtime.evaluate', expression=e, returnByValue=True, awaitPromise=True)
                if r.get('exceptionDetails'): return 'EXC ' + str(r['exceptionDetails'].get('text'))[:300]
                return (r.get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable')
            await send('Page.navigate', url=URL); await asyncio.sleep(10)
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110177',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'极光剑'});return 1;})()" % (REL, REL))
            for _ in range(40):
                nx = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                if nx and 'applied' in str(nx): break
                await asyncio.sleep(2)
            await asyncio.sleep(14)
            print('neox raw head:', str(nx)[:260])
            open(os.path.join(OUT, '_t5_lab_neox.json'), 'w', encoding='utf-8').write(str(nx or ''))
            try:
                sh = await ev("JSON.stringify(window.WikiWeaponViewer.snapshot&&window.WikiWeaponViewer.snapshot())")
                sd = json.loads(sh or '{}')
                if sd.get('png'):
                    raw = base64.b64decode(sd['png'].split(',', 1)[-1])
                    open(os.path.join(OUT, 'T5_1110177_lab.png'), 'wb').write(raw)
                    print('lab snapshot sha16=', hashlib.sha256(raw).hexdigest()[:16], len(raw),
                          {k: sd.get(k) for k in ('w', 'h', 'mean', 'magenta_pct')})
            except Exception as e:
                print('snapshot fail', e)
            print('canvases:', await ev("document.querySelectorAll('canvas').length"))
            print('canvas box:', await ev("JSON.stringify((()=>{const c=document.querySelector('canvas');if(!c)return null;const b=c.getBoundingClientRect();return {x:Math.round(b.x),y:Math.round(b.y),w:Math.round(b.width),h:Math.round(b.height)};})())"))
            print('status text:', await ev("String((document.querySelector('.wv-status')||{}).textContent||'')[:200]"))
            await ev("(()=>{document.querySelectorAll('.wv-poster,.wv-loading,.wv-status,.wv-tools,.wv-params,.wv-tabs').forEach(e=>e.style.display='none');return 1;})()")
            await asyncio.sleep(1)
            s = await send('Page.captureScreenshot', format='png',
                           clip=dict(x=0, y=0, width=1400, height=950, scale=1))
            if 'data' not in s:
                print('captureScreenshot resp:', str(s)[:400])
                return
            raw = base64.b64decode(s['data'])
            open(os.path.join(OUT, 'T5_1110177_lab_full.png'), 'wb').write(raw)
            print('lab full page shot sha16=', hashlib.sha256(raw).hexdigest()[:16], len(raw))
            t.cancel()
    finally:
        try: p.terminate()
        except Exception: pass


asyncio.run(main())
