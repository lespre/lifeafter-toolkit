# -*- coding: utf-8 -*-
"""BLACK129_net.py — 抓 1110129 / 1110145 打开时的全部 cube 面请求（URL·状态·是否失败）。只写 BLACK129_*。
"""
import asyncio, json, os, shutil, subprocess, urllib.request
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BOARD = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9922
PROF = os.path.join(os.environ.get('TEMP', OUT), 'BLACK129net_prof')
SKINS = ['1110129', '1110145']


async def main():
    res = {'manifests': {}}
    for skin in SKINS:
        for fn in ('viewer.json', 'neox_material.json'):
            p = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', skin, fn)
            if not os.path.isfile(p):
                continue
            try:
                d = json.load(open(p, encoding='utf-8'))
            except Exception as e:
                res['manifests'][skin + '/' + fn] = {'error': str(e)}
                continue
            if fn == 'viewer.json':
                res['manifests'][skin + '/viewer.json'] = {k: d.get(k) for k in ('source_chain', 'material_mapping', 'environment_approximate', 'background_image') if k in d}
            else:
                cubes = {}
                for pr in d.get('primitives', []):
                    t = (pr.get('textures') or {}).get('t_custom_ibl')
                    if t:
                        cubes[pr.get('material')] = {'local_file': t.get('local_file'), 'logical': t.get('logical_path') or t.get('logical')}
                res['manifests'][skin + '/neox_material.json'] = {'t_custom_ibl': cubes}
    print('manifest t_custom_ibl:', json.dumps(res['manifests'], ensure_ascii=False)[:900])

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
            current = {'skin': None, 'req': [], 'fail': []}

            def on_event(m):
                me = m.get('method'); p = m.get('params') or {}
                if me == 'Network.responseReceived':
                    r = p.get('response') or {}
                    u = str(r.get('url'))
                    if any(k in u for k in ('_f0_m0', '_f1_m0', '_f2_m0', '_f3_m0', '_f4_m0', '_f5_m0')):
                        current['req'].append({'url': u.split('127.0.0.1:8765')[-1], 'status': r.get('status'), 'mime': r.get('mimeType')})
                elif me == 'Network.requestWillBeSent':
                    u = str((p.get('request') or {}).get('url'))
                    if any(k in u for k in ('_f0_m0', '_f1_m0', '_f2_m0', '_f3_m0', '_f4_m0', '_f5_m0')):
                        current['req'].append({'url': u.split('127.0.0.1:8765')[-1], 'status': 'SENT'})
                elif me == 'Network.loadingFailed':
                    current['fail'].append({'requestId': p.get('requestId'), 'err': p.get('errorText'), 'type': p.get('type')})

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

            async def ev(expr, wait=0.0):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True, timeout=120000)
                if wait:
                    await asyncio.sleep(wait)
                return (r.get('result', {}).get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable')
            await send('Page.navigate', url=BOARD); await asyncio.sleep(9)
            for skin in SKINS:
                current['skin'] = skin
                current['req'] = []; current['fail'] = []
                cur = {'skin': skin, 'req': current['req'], 'fail': current['fail']}
                res.setdefault('net', {})[skin] = cur
                await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'%s',poster:'assets/3d/weapon_skin/%s/poster.webp',preview_3d:{status:'ready',manifest:'assets/3d/weapon_skin/%s/viewer.json'}},{title:'%s'});return 1;})()" % (skin, skin, skin, skin))
                await asyncio.sleep(11)
                # 同时读 envMap 面数，确认状态
                n = await ev("(function(){var n=null; if(window.__envScene) window.__envScene.traverse(function(o){ if(n===null&&o.isMesh&&o.material&&o.material.envMap) n=(o.material.envMap.image&&o.material.envMap.image.length)||0; }); return n; })()")
                cur['envmap_faces_after'] = n
                print('== %s == envMap faces=%s' % (skin, n))
                for r in current['req']:
                    print('   %-8s %s' % (r.get('status'), r['url']))
                if current['fail']:
                    print('   loadingFailed:', json.dumps(current['fail'], ensure_ascii=False)[:300])
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'BLACK129_net.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('json ->', os.path.join(OUT, 'BLACK129_net.json'))


asyncio.run(main())
