# -*- coding: utf-8 -*-
"""wiki_acceptance.py — 真实 Wiki 页面生产验收"""
import asyncio, json, os, shutil, subprocess, urllib.request, hashlib, base64
import websockets
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'

async def main():
    prof = os.path.join(OUT, '_profAcc'); shutil.rmtree(prof, ignore_errors=True)
    p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
        '--no-first-run', '--hide-scrollbars', '--window-size=1240,900',
        '--remote-debugging-port=9890', '--user-data-dir=%s' % prof, 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    errs = []
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:9890/json')) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=128 << 20) as ws:
            _i = 0
            async def send(m, **pp):
                nonlocal _i; _i += 1
                await ws.send(json.dumps(dict(id=_i, method=m, params=pp)))
                while True:
                    r = json.loads(await ws.recv())
                    if r.get('id') == _i: return r.get('result', {})
            async def ev(e):
                r = await send('Runtime.evaluate', expression=e, returnByValue=True, awaitPromise=True)
                return (r.get('result', {}) or {}).get('value')
            await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable')
            await send('Page.navigate', url=URL); await asyncio.sleep(10)
            # 控制台错误
            try:
                while True:
                    r = json.loads(await asyncio.wait_for(ws.recv(), timeout=0.01))
                    if r.get('method') == 'Log.entryAdded':
                        e = r['params']['entry']
                        if e.get('level') in ('error',): errs.append((e.get('text') or '')[:200])
                    elif r.get('method') == 'Runtime.consoleAPICalled' and r['params'].get('type') == 'error':
                        errs.append(' '.join(str(a.get('value', '')) for a in r['params'].get('args', []))[:200])
            except Exception:
                pass
            # 卡片 poster 实际 URL
            pi = await ev("JSON.stringify([...document.querySelectorAll('img')].map(i=>i.currentSrc||i.src).filter(s=>s.includes('poster')).slice(0,3))")
            print('卡片 poster:', pi)
            await ev("window.dispatchEvent(new Event('resize'))")
            await send('Page.reload'); await asyncio.sleep(9)
            rel = 'assets/3d/weapon_skin/1110171'
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110171',poster:'%s/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'%s/viewer.json'}},{title:'x'});return 1;})()" % (rel, rel))
            await asyncio.sleep(22)
            st = await ev("JSON.stringify(window.WikiWeaponViewer.neoxState())")
            j = json.loads(st or '{}')
            print('fidelity:', j.get('fidelity'), '| mode:', j.get('mode'), '| canvas:', j.get('canvas'))
            for m in j.get('materials', [])[:7]:
                print('   %-12s %-22s map=%-34s loaded=%s' % (m.get('uuid'), m.get('type'),
                      (m.get('map_src') or '').split('/')[-1], m.get('map_loaded')))
            shot = await send('Page.captureScreenshot', format='png')
            open(os.path.join(OUT, 'wiki_page_final.png'), 'wb').write(base64.b64decode(shot['data']))
            print('shot -> wiki_page_final.png')
            # 刷新一致性
            await send('Page.reload'); await asyncio.sleep(10)
            ok2 = await ev("!!window.WikiWeaponViewer")
            print('刷新后 viewer 可用:', ok2)
    finally:
        p.terminate()
    print('\n控制台错误数:', len(errs))
    for e in errs[:6]: print('   ERR:', e)
asyncio.run(main())
