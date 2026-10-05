# -*- coding: utf-8 -*-
"""SFX_e2e_check.py — 页面端实测：板块卡上 SFX 区块数量、<audio> 元素数、逐条网络状态码（只读）。

用 CDP 打开 board.html?b=weapon_skin_sfx_text_sources（默认视图），
统计 DOM 里 details.audio / audio[src]，并抓取所有 assets/audio/weapon_skin/* 的响应状态。
端口 9981（按 Lead 要求 9981+，不动 98xx/99xx 通配进程）。
"""
import asyncio, json, os, shutil, subprocess, urllib.request, collections
import websockets

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources&view=wiki&sort=id&dir=desc'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
PROF = os.path.join(os.environ.get('TEMP', OUT), 'SFX_prof9981')
PORT = 9981


async def main():
    shutil.rmtree(PROF, ignore_errors=True)
    pr = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--enable-unsafe-swiftshader',
                           '--no-first-run', '--hide-scrollbars', '--force-device-scale-factor=1',
                           '--window-size=1600,1200', '--remote-debugging-port=%d' % PORT,
                           '--user-data-dir=%s' % PROF, 'about:blank'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    res = {'url': URL, 'audio_responses': [], 'nonaudio_responses': collections.Counter(), 'events': []}
    try:
        pg = next(t for t in json.load(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT)) if t.get('type') == 'page')
        async with websockets.connect(pg['webSocketDebuggerUrl'], max_size=256 << 20) as ws:
            _i = 0
            pending = {}
            resps = []

            def on_event(m):
                me = m.get('method'); p = m.get('params') or {}
                if me == 'Network.responseReceived':
                    r = p.get('response') or {}
                    u = str(r.get('url'))
                    if '/assets/audio/weapon_skin/' in u:
                        resps.append({'url': u.split('/assets/audio/weapon_skin/')[-1], 'status': r.get('status'),
                                      'type': r.get('mimeType'), 'len': r.get('encodedDataLength')})
                    else:
                        res['nonaudio_responses'][str(r.get('status'))] += 1
                elif me == 'Network.loadingFailed':
                    res['events'].append({'failed': str(p.get('errorText')), 'type': p.get('type')})

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
                if 'error' in r:
                    raise RuntimeError('CDP %s -> %s' % (method, r['error']))
                return r.get('result', {})

            async def ev(expr):
                r = await send('Runtime.evaluate', expression=expr, returnByValue=True, awaitPromise=True, timeout=180000)
                if r.get('exceptionDetails'):
                    return 'EXC ' + str(r['exceptionDetails']['text'])[:200]
                return (r.get('result', {}) or {}).get('value')

            await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable')
            await send('Page.navigate', url=URL)
            await asyncio.sleep(12)
            # 等待音频元数据请求（preload=metadata）
            await asyncio.sleep(8)
            res['dom'] = json.loads(await ev("""JSON.stringify({
              board: (document.getElementById('title')||{}).textContent,
              metaline: (document.getElementById('metaline')||{}).textContent,
              cards: document.querySelectorAll('.skin-card').length,
              audio_details: document.querySelectorAll('details.audio').length,
              audio_elements: document.querySelectorAll('audio').length,
              audio_with_src: Array.from(document.querySelectorAll('audio')).filter(a=>a.getAttribute('src')).length,
              audio_unique_src: new Set(Array.from(document.querySelectorAll('audio')).map(a=>a.getAttribute('src'))).size,
              summaries: Array.from(document.querySelectorAll('details.audio>summary')).slice(0,5).map(s=>s.textContent),
              first_srcs: Array.from(document.querySelectorAll('audio')).slice(0,5).map(a=>new URL(a.src).pathname),
              audio_count_sum: Array.from(document.querySelectorAll('details.audio>summary')).map(s=>{const m=/\\d+/.exec(s.textContent);return m?+m[0]:0;}).reduce((a,b)=>a+b,0)
            })""") or '{}')
            res['audio_responses'] = sorted(resps, key=lambda x: x['url'])
            res['audio_status_counts'] = dict(collections.Counter(str(r['status']) for r in resps))
            res['audio_unique_requested'] = len(set(r['url'] for r in resps))
            res['audio_404'] = [r for r in resps if r['status'] != 200]
    finally:
        try:
            pr.terminate()
        except Exception:
            pass
    json.dump(res, open(os.path.join(OUT, 'SFX_e2e_check.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('== DOM ==')
    print(json.dumps(res.get('dom'), ensure_ascii=False, indent=1))
    print('== 音频网络请求 ==', res.get('audio_status_counts'), '唯一 URL', res.get('audio_unique_requested'))
    print('== 非音频响应码分布 ==', dict(res.get('nonaudio_responses')))
    print('== 音频 404/非200 ==', json.dumps(res.get('audio_404'), ensure_ascii=False)[:800])
    print('== loadingFailed ==', json.dumps(res.get('events'), ensure_ascii=False)[:400])
    print('json ->', os.path.join(OUT, 'SFX_e2e_check.json'))


asyncio.run(main())
