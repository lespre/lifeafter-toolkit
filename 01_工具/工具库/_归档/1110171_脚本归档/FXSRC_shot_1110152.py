# -*- coding: utf-8 -*-
"""FXSRC_shot_1110152.py — wiki 页面验收截图：运行时注入 viewer.json.effects（不改 Lead 的文件）+ 打开 SFX 开关。
用 CDP Fetch 拦截 1110152/viewer.json 的响应体并注入 effects；截图开关 ON/OFF 各一张。
端口 9917，全新 profile（不杀任何 98xx/99xx 进程）。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, urllib.error, base64, hashlib
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BOARD = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
SKIN = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110152')
PORT = 9917
PROF = os.path.join(os.environ.get('TEMP', OUT), 'FXSRC_prof9917')


def http(url):
    for m in ('HEAD', 'GET'):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, method=m), timeout=15)
            return r.status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception as e:
            if m == 'GET':
                return 'ERR:' + type(e).__name__


async def main():
    # 贴图 HTTP 验证
    texs = sorted(os.listdir(os.path.join(SKIN, 'sfx', 'tex')))
    texcheck = {}
    for t in texs:
        u = 'http://127.0.0.1:8765/assets/3d/weapon_skin/1110152/sfx/tex/' + t
        texcheck[t] = {'url': u, 'http': http(u), 'bytes': os.path.getsize(os.path.join(SKIN, 'sfx', 'tex', t))}
        print('贴图 %-26s HTTP %s (%dB)' % (t, texcheck[t]['http'], texcheck[t]['bytes']))

    inj = json.load(open(os.path.join(OUT, 'FXSRC_1110152_viewer_effects.json'), encoding='utf-8'))
    vj = json.load(open(os.path.join(SKIN, 'viewer.json'), encoding='utf-8'))
    vj['effects'] = inj
    body = json.dumps(vj, ensure_ascii=False).encode('utf-8')

    shutil.rmtree(PROF, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
                           '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1400,1000',
                           '--remote-debugging-port=%d' % PORT, '--user-data-dir=%s' % PROF, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    res = {'texture_http': texcheck}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0
            pending = {}
            intercepted = []

            async def pump():
                nonlocal _i
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
                    elif m.get('method') == 'Fetch.requestPaused':
                        p = m['params']
                        url = p['request']['url']
                        if '1110152/viewer.json' in url:
                            intercepted.append(url)
                            _i += 1
                            await ws.send(json.dumps({'id': _i, 'method': 'Fetch.fulfillRequest', 'params': {
                                'requestId': p['requestId'], 'responseCode': 200,
                                'responseHeaders': [{'name': 'Content-Type', 'value': 'application/json'}],
                                'body': base64.b64encode(body).decode()}}))
                        else:
                            _i += 1
                            await ws.send(json.dumps({'id': _i, 'method': 'Fetch.continueRequest',
                                                      'params': {'requestId': p['requestId']}}))

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

            async def shot(tag, full=True):
                if full:
                    s = await send('Page.captureScreenshot', format='png')
                else:
                    rect = json.loads(await ev("(function(){var c=document.querySelector('.wv-canvas canvas');if(!c)return 'null';var r=c.getBoundingClientRect();return JSON.stringify({x:r.left,y:r.top,w:r.width,h:r.height});})()") or 'null')
                    s = await send('Page.captureScreenshot', format='png', clip={'x': rect['x'], 'y': rect['y'], 'width': rect['w'], 'height': rect['h'], 'scale': 1})
                raw = base64.b64decode(s['data'])
                fn = os.path.join(OUT, 'FXSRC_%s.png' % tag)
                open(fn, 'wb').write(raw)
                return {'file': fn, 'sha16': hashlib.sha256(raw).hexdigest()[:16], 'bytes': len(raw)}

            await send('Page.enable'); await send('Runtime.enable')
            await send('Fetch.enable', patterns=[{'urlPattern': '*1110152/viewer.json*', 'requestStage': 'Request'}])
            await send('Page.navigate', url=BOARD)
            await asyncio.sleep(10)
            # 打开 1110152 的 3D 预览（走 viewer 的公开 API，避免依赖 DOM 细节）
            await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'1110152',poster:'assets/3d/weapon_skin/1110152/poster.webp',"
                     "preview_3d:{status:'ready',manifest:'assets/3d/weapon_skin/1110152/viewer.json'}},{title:'灵态诱导'});return 1;})()")
            await asyncio.sleep(10)
            res['intercepted'] = intercepted
            res['sfx_button_before'] = await ev("(function(){var b=document.querySelector('.wv-sfx');return b?JSON.stringify({text:b.textContent,disabled:b.disabled,pressed:b.getAttribute('aria-pressed'),title:b.title}):'NO BUTTON';})()")
            res['state_before'] = await ev("JSON.stringify((window.WikiWeaponViewer.__state&&window.WikiWeaponViewer.__state()||{}).sfxDiag)")
            res['shot_off'] = await shot('1110152_sfxoff_full')
            # 打开 SFX 开关
            res['click'] = await ev("(function(){var b=document.querySelector('.wv-sfx');if(!b)return 'no button';if(b.disabled)return 'disabled';b.click();return 'clicked';})()")
            await asyncio.sleep(3)
            res['sfx_button_after'] = await ev("(function(){var b=document.querySelector('.wv-sfx');return b?JSON.stringify({text:b.textContent,disabled:b.disabled,pressed:b.getAttribute('aria-pressed')}):'NO BUTTON';})()")
            res['state_after'] = await ev("JSON.stringify((window.WikiWeaponViewer.__state&&window.WikiWeaponViewer.__state()||{}).sfxDiag)")
            res['effects_handle'] = await ev("JSON.stringify(window.WikiWeaponViewer.__state?null:null)")
            res['shot_on'] = await shot('1110152_sfxon_full')
            res['shot_on_canvas'] = await shot('1110152_sfxon_canvas', full=False)
            res['console'] = []
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'FXSRC_shot_1110152.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n拦截 viewer.json 次数:', len(res.get('intercepted') or []))
    print('SFX 按钮 关:', res.get('sfx_button_before'))
    print('点击:', res.get('click'))
    print('SFX 按钮 开:', res.get('sfx_button_after'))
    print('sfxDiag off:', res.get('state_before'))
    print('sfxDiag on :', res.get('state_after'))
    print('截图:', res.get('shot_off'), res.get('shot_on'), res.get('shot_on_canvas'))
    print('json ->', os.path.join(OUT, 'FXSRC_shot_1110152.json'))


asyncio.run(main())
