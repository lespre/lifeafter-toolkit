# -*- coding: utf-8 -*-
"""BLACK129_diag.py — 1110129 vs 1110145：全量请求 + __acceptanceReport 逐网格证据 + snapshot 图（default / lab=1 两版页面）。
   只读页面、只写 BLACK129_*。
"""
import asyncio, base64, json, os, shutil, subprocess, urllib.request
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
BASE_Q = ('http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc')
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PORT = 9924
SKINS = ['1110129', '1110145']


async def session(tag, board, skins, port):
    prof = os.path.join(os.environ.get('TEMP', OUT), 'BLACK129diag_%s' % tag)
    shutil.rmtree(prof, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader', '--no-first-run',
                           '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1400,1000',
                           '--remote-debugging-port=%d' % port, '--user-data-dir=%s' % prof, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    res = {'tag': tag, 'board': board, 'skins': {}}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % port)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=512 << 20) as ws:
            _i = 0; pending = {}
            cur = {'req': {}, 'fail': []}

            def on_event(m):
                me = m.get('method'); p = m.get('params') or {}
                if me == 'Network.responseReceived':
                    r = p.get('response') or {}
                    u = str(r.get('url'))
                    if '/assets/3d/weapon_skin/' in u:
                        cur['req'][u.split('8765')[-1]] = r.get('status')
                    if int(r.get('status') or 0) >= 400:
                        cur['fail'].append({'url': u.split('8765')[-1], 'status': r.get('status')})
                elif me == 'Network.loadingFailed':
                    ot = str(p.get('type'))
                    if ot == 'Image' or ot == 'Fetch':
                        cur['fail'].append({'url': 'loadingFailed/' + ot, 'status': p.get('errorText')})

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
                return await asyncio.wait_for(fut, timeout=180)

            async def ev(expr):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True, timeout=180000)
                return (r.get('result', {}).get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable')
            await send('Page.navigate', url=board); await asyncio.sleep(10)
            for skin in skins:
                cur['req'] = {}; cur['fail'] = []
                row = {'req': cur['req'], 'fail': cur['fail']}
                res['skins'][skin] = row
                await ev("(()=>{window.WikiWeaponViewer.open({skin_id:'%s',poster:'assets/3d/weapon_skin/%s/poster.webp',preview_3d:{status:'ready',manifest:'assets/3d/weapon_skin/%s/viewer.json'}},{title:'%s'});return 1;})()" % (skin, skin, skin, skin))
                await asyncio.sleep(13)
                row['acceptance'] = await ev("(function(){try{return window.__acceptanceReport();}catch(e){return 'err:'+e.message}})()")
                row['neoxState'] = await ev("(function(){try{var s=window.WikiWeaponViewer.neoxState();return JSON.stringify({mode:s.mode,fidelity:s.fidelity,canvas:s.canvas,mats:s.materials.map(function(m){return {type:m.type,fid:m.fidelity,view:m.view,map:m.map_src,map_loaded:m.map_loaded};})});}catch(e){return 'err:'+e.message}})()")
                snap = await ev("(function(){try{var s=window.WikiWeaponViewer.snapshot();return JSON.stringify({w:s.w,h:s.h,mean:s.mean,mag:s.magenta_pct,gray:s.gray_pct,png:s.png});}catch(e){return 'err:'+e.message}})()")
                if isinstance(snap, str) and snap.startswith('{'):
                    s = json.loads(snap)
                    png = s.pop('png', None)
                    row['snapshot'] = s
                    if png and png.startswith('data:image/png;base64,'):
                        p = os.path.join(OUT, 'BLACK129_diag_%s_%s.png' % (tag, skin))
                        open(p, 'wb').write(base64.b64decode(png.split(',', 1)[1]))
                        row['snapshot_png'] = p
                else:
                    row['snapshot'] = snap
                print('==== [%s] %s  snapshot=%s' % (tag, skin, json.dumps(row.get('snapshot'), ensure_ascii=False)))
                acc = row.get('acceptance')
                if isinstance(acc, str) and acc.strip().startswith('{'):
                    try:
                        a = json.loads(acc)
                        for mm in a.get('meshes', []):
                            print('   prim%-2s %-22s kind=%-10s map=%-28s metalM=%-26s env=%s' % (
                                mm.get('chain_prim'), mm.get('mat_type'), mm.get('kind'), mm.get('map'),
                                mm.get('metalness_map'), mm.get('envMap')))
                            print('        ibl_faces=%s src_env=%s radiance_override=%s' % (
                                json.dumps(mm.get('ibl_faces'), ensure_ascii=False), mm.get('source_env_bright'),
                                mm.get('frag_has_our_radiance_override')))
                    except Exception as e:
                        print('   acceptance parse err', e, str(acc)[:300])
                for u, st in sorted(cur['req'].items()):
                    print('   %-5s %s' % (st, u))
                if cur['fail']:
                    print('   FAILS:', json.dumps(cur['fail'], ensure_ascii=False)[:400])
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    return res


async def main():
    allres = []
    allres.append(await session('default', BASE_Q, SKINS, PORT))
    allres.append(await session('lab1', BASE_Q + '&lab=1', SKINS, PORT + 1))
    json.dump(allres, open(os.path.join(OUT, 'BLACK129_diag.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('json ->', os.path.join(OUT, 'BLACK129_diag.json'))


asyncio.run(main())
