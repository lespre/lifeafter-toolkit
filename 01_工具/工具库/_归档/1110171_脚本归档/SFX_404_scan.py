# -*- coding: utf-8 -*-
"""SFX_404_scan.py — 列出 board 页面加载中的**全部**非 200 资源（含 404 的具体 URL）。端口 9982。"""
import asyncio, json, os, shutil, subprocess, urllib.request, collections
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PROF = os.path.join(os.environ.get('TEMP', OUT), 'SFX_prof9982')
PORT = 9982


async def main():
    shutil.rmtree(PROF, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                           '--window-size=1600,1200', '--remote-debugging-port=%d' % PORT,
                           '--user-data-dir=%s' % PROF, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    res = {'bad': [], 'counts': collections.Counter(), 'failed': collections.Counter()}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0
            pending = {}
            seen = set()

            def on_event(m):
                me = m.get('method'); p = m.get('params') or {}
                if me == 'Network.responseReceived':
                    r = p.get('response') or {}
                    u = str(r.get('url')).split('127.0.0.1:8765')[-1]
                    st = int(r.get('status', 0))
                    res['counts'][str(st)] += 1
                    if st >= 400 and u not in seen:
                        seen.add(u)
                        res['bad'].append({'status': st, 'url': u, 'type': r.get('mimeType'),
                                           'from': 'audio' if '/assets/audio/weapon_skin/' in u else 'other'})
                elif me == 'Network.loadingFailed':
                    res['failed'][str(p.get('errorText')) + '/' + str(p.get('type'))] += 1

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
                return r.get('result', {})

            await send('Page.enable'); await send('Network.enable')
            await send('Page.navigate', url=URL)
            await asyncio.sleep(20)
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'SFX_404_scan.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('状态码分布:', dict(res['counts']))
    print('非 200（含音频）:', len(res['bad']))
    for b in res['bad'][:40]:
        print('   %s %s  [%s]' % (b['status'], b['url'], b['from']))
    print('loadingFailed 分布:', dict(res['failed']))


asyncio.run(main())
