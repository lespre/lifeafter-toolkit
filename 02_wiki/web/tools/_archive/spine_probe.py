# -*- coding: utf-8 -*-
"""CDP 探针：打开页面 → 抓 console/异常 → 执行 JS → 截图。

用法：python spine_probe.py <url> <out.png> [js] [宽] [高] [等待秒]
"""
from __future__ import annotations

import asyncio
import base64
import json
import sys
import urllib.request

import websockets

PORT = 9333


async def run(url, out, js, width, height, sleep):
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json/list" % PORT).read())
    page = next(t for t in tabs if t["type"] == "page")
    logs, errs = [], []
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=60_000_000) as ws:
        i = 0

        async def call(method, **params):
            nonlocal i
            i += 1
            await ws.send(json.dumps({"id": i, "method": method, "params": params}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("method") == "Runtime.consoleAPICalled":
                    a = msg["params"]
                    logs.append("%s: %s" % (a["type"], " ".join(
                        str(x.get("value", x.get("description", ""))) for x in a.get("args", []))))
                elif msg.get("method") == "Runtime.exceptionThrown":
                    d = msg["params"]["exceptionDetails"]
                    errs.append("%s: %s" % (d.get("text"), (d.get("exception") or {}).get("description", "")))
                elif msg.get("method") == "Log.entryAdded":
                    e = msg["params"]["entry"]
                    logs.append("LOG[%s] %s %s" % (e.get("level"), e.get("text"), e.get("url", "")))
                if msg.get("id") == i:
                    return msg

        await call("Runtime.enable")
        await call("Log.enable")
        await call("Page.enable")
        await call("Emulation.setDeviceMetricsOverride", width=width, height=height,
                   deviceScaleFactor=1, mobile=False)
        await call("Page.navigate", url=url)
        await asyncio.sleep(sleep)
        if js:
            r = await call("Runtime.evaluate", returnByValue=True, expression=js, awaitPromise=True)
            v = r.get("result", {})
            print("JS_RESULT:", json.dumps(v.get("value", v), ensure_ascii=False)[:2000])
            await asyncio.sleep(1.0)
        r = await call("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        open(out, "wb").write(base64.b64decode(r["result"]["data"]))
    if errs:
        print("=== EXCEPTIONS ===")
        for e in errs[:20]:
            print(" ", e)
    if logs:
        print("=== CONSOLE (%d) ===" % len(logs))
        for l in logs[:40]:
            print(" ", l)
    print("saved", out)


def main():
    url = sys.argv[1]
    out = sys.argv[2]
    js = sys.argv[3] if len(sys.argv) > 3 else ""
    w = int(sys.argv[4]) if len(sys.argv) > 4 else 900
    h = int(sys.argv[5]) if len(sys.argv) > 5 else 700
    s = float(sys.argv[6]) if len(sys.argv) > 6 else 4.0
    asyncio.run(run(url, out, js, w, h, s))


if __name__ == "__main__":
    main()
