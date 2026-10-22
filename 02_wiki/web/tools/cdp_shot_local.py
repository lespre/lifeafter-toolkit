# -*- coding: utf-8 -*-
r"""CDP 截图：打开页面 → 执行 JS（可选）→ 截图。用于本地主题验收。"""
from __future__ import annotations

import asyncio
import base64
import json
import sys
import urllib.request

import websockets

PORT = 9333


async def shot(url: str, out: str, width: int, height: int, sleep: float, js: str) -> None:
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json/list" % PORT).read())
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=40_000_000) as ws:
        i = 0

        async def call(method: str, **params):
            nonlocal i
            i += 1
            await ws.send(json.dumps({"id": i, "method": method, "params": params}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == i:
                    return msg

        await call("Page.enable")
        await call("Emulation.setDeviceMetricsOverride", width=width, height=height,
                   deviceScaleFactor=1, mobile=False)
        await call("Page.navigate", url=url)
        await asyncio.sleep(sleep)
        if js:
            r = await call("Runtime.evaluate", returnByValue=True, expression=js)
            print("JS:", json.dumps(r.get("result", {}).get("value"), ensure_ascii=False)[:300])
            await asyncio.sleep(1.2)
        r = await call("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        open(out, "wb").write(base64.b64decode(r["result"]["data"]))
        print("saved", out)


def main() -> int:
    url = sys.argv[1]
    out = sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1440
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
    js = sys.argv[5] if len(sys.argv) > 5 else ""
    asyncio.run(shot(url, out, w, h, 4.0, js))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
