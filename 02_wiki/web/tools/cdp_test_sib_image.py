# -*- coding: utf-8 -*-
"""实测：同 model 卡片里点【图片】，应当是跳转子卡，而不是打开大图。"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request

import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
URL = "http://127.0.0.1:8765/board.html?b=fashion_wardrobe&d2=fw_1de76ebfd4&art=1"
PORT = 9355


def main() -> int:
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
        r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_img",
        "--window-size=1300,900", URL,
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

        print("sib 数量:", ev("document.querySelectorAll('.fr-sib-card').length"))
        print("点击前 bigBox:", ev("(document.getElementById('frBox')||{}).style?document.getElementById('frBox').style.display:'n/a'"))
        ev("document.querySelector('.fr-sib-card img').click()")
        time.sleep(1.5)
        print("点击后 bigBox:", ev("(document.getElementById('frBox')||{}).style?document.getElementById('frBox').style.display:'n/a'"))
        print("点击后 panel:", ev("(document.getElementById('c2mask')||{}).style?document.getElementById('c2mask').style.display:'n/a'"))
        print("点击后标题:", ev("(()=>{const s=document.querySelector('.c2-stage');return s?s.innerText.slice(0,30):''})()"))
        ws.close()
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
