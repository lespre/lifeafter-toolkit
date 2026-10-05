# -*- coding: utf-8 -*-
"""定位 lab 模式下 render 抛出的异常（只读 viewer，不改动）。"""
import asyncio, json, os, shutil, subprocess, urllib.request, sys
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
HERE = os.path.dirname(os.path.abspath(__file__))
REL = 'assets/3d/weapon_skin/1110177'
PORT = 9879
BASE = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'


async def run(url, tag):
    prof = os.path.join(HERE, '_proferr_' + tag)
    shutil.rmtree(prof, ignore_errors=True)
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
            await send('Page.navigate', url=url); await asyncio.sleep(10)
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110177',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'极光剑'});return 1;})()" % (REL, REL))
            for _ in range(40):
                nx = await ev("JSON.stringify(window.WikiWeaponViewer.__neox&&window.WikiWeaponViewer.__neox())")
                if nx and 'applied' in str(nx): break
                await asyncio.sleep(2)
            await asyncio.sleep(14)
            print('#### %s ####' % tag)
            print('render stack:', await ev("(()=>{try{window.WikiWeaponViewer.canvasShot(1);return 'RENDER OK';}catch(e){return String(e&&e.stack||e).slice(0,1400);}})()"))
            print('snapshot err:', await ev("(()=>{try{var s=window.WikiWeaponViewer.snapshot();return JSON.stringify({err:s&&s.error||null,w:s&&s.w,h:s&&s.h,mean:s&&s.mean});}catch(e){return 'THROW '+String(e&&e.stack||e).slice(0,900);}})()"))
            print('canvasPixels:', await ev("(()=>{try{return JSON.stringify(window.WikiWeaponViewer.canvasPixels());}catch(e){return 'THROW '+String(e).slice(0,300);}})()"))
            print('__lastShot len:', await ev("String((window.WikiWeaponViewer.canvasShot(2)||'').length)"))
            t.cancel()
    finally:
        try: p.terminate()
        except Exception: pass


async def main():
    await run(BASE + '&lab=1', 'lab')
    await run(BASE, 'prod')


asyncio.run(main())
