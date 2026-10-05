# -*- coding: utf-8 -*-
"""BLACK129_net2.py — 证明 1110129 的 cube 面实际请求 URL（faces_glob 字面 * 派生）与状态；对照 1110145。
   另测字面 * URL 的 HTTP 状态。只写 BLACK129_*。
"""
import asyncio, hashlib, json, os, shutil, subprocess, urllib.request, urllib.error
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BOARD = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9923
PROF = os.path.join(os.environ.get('TEMP', OUT), 'BLACK129net2_prof')
SKINS = ['1110129', '1110145']
HOST = 'http://127.0.0.1:8765/'


def http(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u), timeout=25) as r:
            return r.status, len(r.read())
    except urllib.error.HTTPError as e:
        return e.code, 0
    except Exception as e:
        return 'ERR:' + e.__class__.__name__, 0


async def main():
    res = {'literal_url_status': {}}
    # 1) 字面 * URL 的 HTTP 行为
    for skin, name in (('1110129', 'qiangpi'), ('1110145', 'bg61f_light_spherereflectioncapture_1')):
        for suffix in ('_f*_m0.png', '_f0_m0.png'):
            u = HOST + 'assets/3d/weapon_skin/%s/src_cube/faces/%s%s' % (skin, name, suffix)
            st, n = http(u)
            res['literal_url_status'][skin + '/' + suffix] = {'url': u.split('8765')[-1], 'status': st, 'bytes': n}
            print('HTTP %-6s %s' % (st, u.split('8765')[-1]))

    shutil.rmtree(PROF, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
                           '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1400,1000',
                           '--remote-debugging-port=%d' % PORT, '--user-data-dir=%s' % PROF, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0; pending = {}
            cur = {'skin': None, 'req': [], 'fail': [], 'console': []}

            def on_event(m):
                me = m.get('method'); p = m.get('params') or {}
                if me == 'Network.requestWillBeSent':
                    u = str((p.get('request') or {}).get('url'))
                    if 'src_cube' in u or '_f0_m0' in u:
                        cur['req'].append({'url': u.split('8765')[-1], 'status': 'SENT'})
                elif me == 'Network.responseReceived':
                    r = p.get('response') or {}
                    u = str(r.get('url'))
                    if 'src_cube' in u or '_f0_m0' in u:
                        cur['req'].append({'url': u.split('8765')[-1], 'status': r.get('status'), 'mime': r.get('mimeType')})
                    if int(r.get('status') or 0) >= 400:
                        cur['fail'].append({'url': u.split('8765')[-1], 'status': r.get('status')})
                elif me == 'Network.loadingFailed':
                    cur['fail'].append({'url': str(p.get('requestId')), 'err': p.get('errorText'), 'type': p.get('type')})
                elif me == 'Runtime.consoleAPICalled':
                    txt = ' '.join(str((a or {}).get('value')) for a in (p.get('args') or []))
                    if any(k in txt for k in ('Cube', 'cube', 'Failed', 'THREE', 'IBL', 'ibl', 'src_cube')):
                        cur['console'].append({'type': p.get('type'), 'text': txt[:260]})
                elif me == 'Runtime.exceptionThrown':
                    d = (p.get('exceptionDetails') or {})
                    cur['console'].append({'type': 'exception', 'text': str(d.get('text'))[:200] + ' | ' +
                                           str(((d.get('exception') or {}).get('description')))[:240]})

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
                fut = asyncio.get_event_loop().create_future(); pending[_i] = fut
                await ws.send(json.dumps({'id': _i, 'method': method, 'params': params}))
                return await asyncio.wait_for(fut, timeout=120)

            async def ev(expr):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True, timeout=120000)
                return (r.get('result', {}).get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable')
            await send('Page.navigate', url=BOARD); await asyncio.sleep(9)
            res['net'] = {}
            for skin in SKINS:
                cur['skin'] = skin; cur['req'] = []; cur['fail'] = []; cur['console'] = []
                row = {'skin': skin, 'req': cur['req'], 'fail': cur['fail'], 'console': cur['console']}
                res['net'][skin] = row
                await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'%s',poster:'assets/3d/weapon_skin/%s/poster.webp',preview_3d:{status:'ready',manifest:'assets/3d/weapon_skin/%s/viewer.json'}},{title:'%s'});return 1;})()" % (skin, skin, skin, skin))
                await asyncio.sleep(12)
                row['cubeDirProbe'] = await ev("JSON.stringify(window.__cubeDirProbe||null)")
                row['cubeDirErr'] = await ev("JSON.stringify(window.__cubeDirErr||null)")
                row['envImageLen'] = await ev("(function(){var V=window.WikiWeaponViewer;try{var s=V&&V.__state&&V.__state.scene;if(!s)return 'no-scene';var o=[],n=0;s.traverse(function(m){if(m.isMesh&&m.material){var e=m.material.envMap;if(e&&n<3){n++;o.push({has:true,len:(e.image&&e.image.length)||0,src:(e.image&&e.image[0]&&String(e.image[0].src||'').split('8765').pop())||null,ec:m.material.envMapIntensity,enabled:m.material.envMap!==null});}}});return JSON.stringify(o);}catch(e){return 'err:'+e.message}})()")
                row['neoxState'] = await ev("(function(){try{return JSON.stringify(window.WikiWeaponViewer.neoxState()).slice(0,1200);}catch(e){return 'err:'+e.message}})()")
                print('==== %s' % skin)
                print('  cubeDirProbe:', row['cubeDirProbe'])
                print('  envMap:', row['envImageLen'])
                for r in cur['req']:
                    print('   %-8s %s' % (r.get('status'), r['url']))
                for f in cur['fail']:
                    print('   FAIL', json.dumps(f, ensure_ascii=False)[:200])
                for c in cur['console'][:12]:
                    print('   CONSOLE[%s] %s' % (c['type'], c['text'][:220]))
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'BLACK129_net2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('json ->', os.path.join(OUT, 'BLACK129_net2.json'))


asyncio.run(main())
