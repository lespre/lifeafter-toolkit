# -*- coding: utf-8 -*-
"""展开一期奖池卡，截图确认成员图标。"""
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
URL = "http://127.0.0.1:8765/board.html?b=lottery_periods"
PORT = 9371
OUT = pathlib.Path("E:/la拆包项目/_截图/lottery_members_icons.png")


def main() -> int:
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
                             r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_ico",
                             "--window-size=1400,1200", URL],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        ws = websocket.create_connection(ws_url, timeout=25)
        time.sleep(4.5)
        mid = [0]

        def ev(expr):
            mid[0] += 1
            ws.send(json.dumps({"id": mid[0], "method": "Runtime.evaluate",
                                "params": {"expression": expr, "returnByValue": True}}))
            while True:
                m = json.loads(ws.recv())
                if m.get("id") == mid[0]:
                    return m.get("result", {}).get("result", {}).get("value")

        # 点开「万圣绮夜」那张
        clicked = ev("""(function(){
          var rows=[...document.querySelectorAll('[data-period], .prow, .pcard, li')];
          var t=rows.find(e=>/万圣绮夜/.test(e.textContent||''));
          if(!t) return 'nf';
          t.click(); return 'ok';
        })()""")
        print("click:", clicked)
        time.sleep(1.5)
        print("imgs:", ev("document.querySelectorAll('img').length"))
        print("broken:", ev("[...document.images].filter(i=>!i.complete||i.naturalWidth===0).length"))
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
