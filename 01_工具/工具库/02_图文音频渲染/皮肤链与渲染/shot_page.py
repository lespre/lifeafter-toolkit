"""★ 项目级截图工具（放项目里 ✗ 不放 scratch ⇒ 不会被 24h 清理 ✗）
用法: python shot_page.py <url> <out.png> [w] [h]
自动：起 CDP Chrome（9341）→ 导航 → 读 __dbg/__realTex → 截图。"""
import asyncio
import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PORT = 9341
PROF = r'C:\Users\<user>\AppData\Local\hermes\cache\cdp_profile_9341'


def ensure_chrome():
    try:
        urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT, timeout=2).read()
        return True
    except Exception:
        pass
    exe = None
    for c in (r'C:\Program Files\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
              r'C:\Users\<user>\AppData\Local\Google\Chrome\Application\chrome.exe'):
        if Path(c).is_file():
            exe = c
            break
    if not exe:
        print('  ✗ 找不到 chrome.exe')
        return False
    subprocess.Popen([exe, '--headless=new', '--disable-gpu', '--no-first-run',
                      '--remote-debugging-port=%d' % PORT,
                      '--user-data-dir=' + PROF,
                      '--window-size=1600,1000', 'about:blank'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        time.sleep(1)
        try:
            urllib.request.urlopen('http://127.0.0.1:%d/json' % PORT, timeout=2).read()
            return True
        except Exception:
            pass
    print('  ✗ Chrome 起了但 CDP 没通')
    return False


async def shoot(url, out, w, h):
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
        await send('Emulation.setDeviceMetricsOverride', width=w, height=h,
                   deviceScaleFactor=1, mobile=False)
        await send('Page.navigate', url=url)
        await asyncio.sleep(15)
        r = await send('Runtime.evaluate',
                       expression='JSON.stringify({dbg:window.__dbg,realTex:window.__realTex,'
                                  'title:document.title})', returnByValue=True)
        print('  状态 %s' % str(r.get('result', {}).get('value'))[:600])
        s = await send('Page.captureScreenshot', format='png')
        data = base64.b64decode(s['data'])
        Path(out).write_bytes(data)
        print('  SHOT → %s  %d B' % (out, len(data)))


if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8770/skin_preview_v2.html?sid=1110171'
    out = sys.argv[2] if len(sys.argv) > 2 else r'E:\la拆包项目\03_执行\90_临时\shot.png'
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1600
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
    if ensure_chrome():
        asyncio.run(shoot(url, out, w, h))
