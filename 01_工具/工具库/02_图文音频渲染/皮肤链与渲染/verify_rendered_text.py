"""★ 权威校验：用 CDP 读【渲染后】的 body.innerText ⇒ 查 缺/半吊子
   （静态查源码不够 ✗ —— JS 运行时会写界面 ✓）"""
import asyncio
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, r'E:\la拆包项目\01_工具\工具库\02_图文音频渲染\皮肤链与渲染')

PORT = 9341
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8770/index.html'


async def main():
    import websockets
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT).read())
    ws_url = next((t['webSocketDebuggerUrl'] for t in tabs if t.get('type') == 'page'), None)
    if not ws_url:
        print('  ✗ 无 page tab')
        return
    async with websockets.connect(ws_url, max_size=64 * 1024 * 1024) as ws:
        n = [0]

        async def send(m, **kw):
            n[0] += 1
            mid = n[0]
            await ws.send(json.dumps({'id': mid, 'method': m, 'params': kw}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get('id') == mid:
                    return msg.get('result', {})

        await send('Page.enable')
        await send('Runtime.enable')
        await send('Page.navigate', url=URL)
        await asyncio.sleep(16)     # 等 JS 拉数据渲染完 ✓
        r = await send('Runtime.evaluate',
                       expression='document.body.innerText', returnByValue=True)
        txt = r.get('result', {}).get('value') or ''
        print('  渲染后文本 %d 字' % len(txt))
        for kw in ('缺', '半吊子', '未完成', '待修', 'TODO'):
            c = txt.count(kw)
            print('   %-8s %s' % (kw, ('✓ 无' if c == 0 else '✗ %d 处' % c)))
        if '缺' in txt or '半吊子' in txt:
            print()
            print('  ════ 命中上下文 ════')
            import re
            for m in re.finditer(r'.{0,24}(缺|半吊子).{0,24}', txt):
                print('   %r' % m.group(0))
        else:
            print()
            print('  ✅ 渲染后【无】缺 / 半吊子 —— 可以出图 ✓')
            print()
            print('  ════ 前 400 字预览 ════')
            print('  ' + txt[:400].replace('\n', ' | '))


asyncio.run(main())
