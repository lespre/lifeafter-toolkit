# -*- coding: utf-8 -*-
"""点一次左栏折叠手柄，截图确认折叠效果。"""
from __future__ import annotations

import base64
import json
import pathlib
import subprocess
import sys
import time
import urllib.request

import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
URL = "http://127.0.0.1:8765/board.html?b=fashion_wardrobe&d2=fw_1de76ebfd4"
PORT = 9361
OUT = pathlib.Path("E:/la拆包项目/_截图/nav_collapsed.png")


def main() -> int:
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
        r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_nc2",
        "--window-size=1300,860", URL,
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(40):
            try:
                data = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json").read())
                pages = [d for d in data if d.get("type") == "page"]
                if pages:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            time.sleep(0.5)
        ws = websocket.create_connection(ws_url, timeout=20)
        time.sleep(3)
        mid = [0]

        def ev(expr):
            mid[0] += 1
            ws.send(json.dumps({"id": mid[0], "method": "Runtime.evaluate",
                                "params": {"expression": expr, "returnByValue": True}}))
            while True:
                m = json.loads(ws.recv())
                if m.get("id") == mid[0]:
                    return m.get("result", {}).get("result", {}).get("value")

        print("手柄存在:", ev("!!document.getElementById('navCollapse')"))
        ev("document.getElementById('navCollapse').click()")
        time.sleep(1)
        print("折叠后 body class:", ev("document.body.className"))
        print("折叠后 侧栏宽:", ev("document.getElementById('siteNav').getBoundingClientRect().width"))
        print("折叠后 正文左内边距:", ev("getComputedStyle(document.body).paddingLeft"))
        mid[0] += 1
        ws.send(json.dumps({"id": mid[0], "method": "Page.captureScreenshot", "params": {"format": "png"}}))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == mid[0]:
                OUT.write_bytes(base64.b64decode(m["result"]["data"]))
                print("截图 →", OUT)
                break
        ws.close()
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
