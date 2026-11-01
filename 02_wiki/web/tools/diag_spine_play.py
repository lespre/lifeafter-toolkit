# -*- coding: utf-8 -*-
"""读 spine_play 页面的 __dbg 状态，诊断为什么画布是空的。"""
import asyncio, json, os, subprocess, sys, urllib.request, shutil

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9861


async def main(url):
    import websockets
    prof = os.path.join(os.environ.get("TMPDIR", "."), "_spinedbg")
    shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--enable-unsafe-swiftshader",
        "--no-first-run", "--window-size=1280,800", "--remote-debugging-port=%d" % PORT,
        "--user-data-dir=%s" % prof, "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await asyncio.sleep(4)
    try:
        pg = next(t for t in json.load(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT))
                  if t.get("type") == "page")
        async with websockets.connect(pg["webSocketDebuggerUrl"], max_size=64 << 20) as ws:
            _id = 0
            evs = []

            async def send(m, **p):
                nonlocal _id
                _id += 1
                mid = _id
                await ws.send(json.dumps(dict(id=mid, method=m, params=p)))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == mid:
                        return msg.get("result", {})
                    evs.append(msg)

            async def ev(e):
                r = await send("Runtime.evaluate", expression=e, returnByValue=True)
                return (r.get("result", {}) or {}).get("value")

            await send("Page.enable"); await send("Runtime.enable"); await send("Log.enable")
            await send("Page.navigate", url=url)
            await asyncio.sleep(16)
            for m in evs:
                if m.get("method") == "Runtime.exceptionThrown":
                    d = m["params"]["exceptionDetails"]
                    print("★ EXC:", d.get("text"), "|", (d.get("exception") or {}).get("description", "")[:300])
                elif m.get("method") == "Log.entryAdded":
                    e = m["params"]["entry"]
                    if e.get("level") == "error":
                        print("★ LOG:", e.get("text", "")[:200])
            print("__loaded :", await ev("window.__loaded"))
            print("__err    :", await ev("window.__err"))
            print("__dbg    :", await ev("JSON.stringify(window.__dbg ? window.__dbg() : null)"))
            print("__bounds :", await ev("JSON.stringify(window.__bounds)"))
            print("__raw    :", await ev("JSON.stringify(window.__raw ? window.__raw() : null)"))
            print("probeTex :", await ev("window.__probeTexture ? window.__probeTexture() : 'no probe'"))
            await asyncio.sleep(1.5)
            # 直接量画布中心像素：若全透明/全黑说明没画上
            print("像素采样 :", await ev("""(() => {
              const c = document.querySelector('canvas');
              const t = document.createElement('canvas'); t.width = 60; t.height = 40;
              const g = t.getContext('2d'); g.drawImage(c, 0, 0, 60, 40);
              const d = g.getImageData(0,0,60,40).data;
              let lit = 0, maxv = 0;
              for (let i=0;i<d.length;i+=4){ const v=(d[i]+d[i+1]+d[i+2])/3; if (v>40) lit++; if (v>maxv) maxv=v; }
              return JSON.stringify({lit, maxv, canvas: c.width+'x'+c.height});
            })()"""))
    finally:
        proc.kill()
        await asyncio.sleep(0.3)


asyncio.run(main(sys.argv[1]))
