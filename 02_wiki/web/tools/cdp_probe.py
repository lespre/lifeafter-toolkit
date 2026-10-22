# -*- coding: utf-8 -*-
r"""CDP 探针：打印页面元素布局与计算样式，排查栅格宽度。"""
from __future__ import annotations

import asyncio
import json
import sys
import urllib.request

import websockets

PORT = 9333


async def main(url: str, expr: str) -> None:
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json/list" % PORT).read())
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=20_000_000) as ws:
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
        await call("Runtime.enable")
        await call("Page.navigate", url=url)
        await asyncio.sleep(3.5)
        r = await call("Runtime.evaluate", returnByValue=True, expression=expr, awaitPromise=True)
        print(json.dumps(r, ensure_ascii=False, indent=1)[:4000])


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))
