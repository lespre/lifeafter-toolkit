# -*- coding: utf-8 -*-
"""用 CDP 真点一次「同 model」卡片，验证：不开大图、能跳转/钉住。"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request

import websocket  # type: ignore

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9333
URL = "http://127.0.0.1:8765/board.html?b=fashion_wardrobe&q=%E7%A0%82%E6%B5%B7%E9%81%97%E7%8F%A0&d2=fw_1de76ebfd4&art=1"


def main() -> int:
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
        "--user-data-dir=" + r"C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_probe",
        URL,
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
        if not ws_url:
            print("CDP 连不上")
            return 1

        ws = websocket.create_connection(ws_url, timeout=15)
        mid = [0]

        def call(method, **params):
            mid[0] += 1
            ws.send(json.dumps({"id": mid[0], "method": method, "params": params}))
            while True:
                msg = json.loads(ws.recv())
                if msg.get("id") == mid[0]:
                    return msg

        time.sleep(3)
        r = call("Runtime.evaluate", expression="""
          (() => {
            const cards=[...document.querySelectorAll('.fr-sib-card')];
            return {count:cards.length, names:cards.map(c=>c.querySelector('.n')?.textContent||'')};
          })()
        """, returnByValue=True)
        print("同 model 卡片:", r.get("result", {}).get("result", {}).get("value"))

        r = call("Runtime.evaluate", expression="""
          (() => {
            try{
              const ok = window.__frJumpSibling ? window.__frJumpSibling('fw_1de76ebfd4','fw_077b6af8b2') : 'no impl';
              const mask=document.getElementById('c2mask');
              const title=(mask&&mask.querySelector('.c2-stage'))?mask.querySelector('.c2-stage').innerText.slice(0,60):'';
              return 'ok=' + ok + ', mask=' + (mask?mask.style.display:'none') + ', title=' + title;
            }catch(e){ return 'ERR ' + e.message; }
          })()
        """, returnByValue=True)
        print("直接调用:", r.get("result", {}).get("result", {}).get("value"))
        time.sleep(2)

        r = call("Runtime.evaluate", expression="""
          (() => ({
            url: location.href,
            bigBox: (document.getElementById('frBox')||{}).style ? document.getElementById('frBox').style.display : 'n/a',
            pinned: !!(window.C2 && C2.pinned),
            pinnedName: (window.C2 && C2.pinned) ? (C2.pinned.name||'') : '',
            detailOpen: !!(window.C2 && C2.open)
          }))()
        """, returnByValue=True)
        print("结果:", r.get("result", {}).get("result", {}).get("value"))
        ws.close()
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
