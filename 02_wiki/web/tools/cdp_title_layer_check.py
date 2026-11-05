# -*- coding: utf-8 -*-
"""称号板渲染体检：每张卡里图片数量、文字是否与图共存（重影的结构判据）。"""
from __future__ import annotations

import json
import subprocess
import time
import urllib.request

import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9401


def main() -> int:
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
                             r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_tfix",
                             "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        ws = websocket.create_connection(ws_url, timeout=30)
        mid = [0]

        def cmd(method, params=None):
            mid[0] += 1
            ws.send(json.dumps({"id": mid[0], "method": method, "params": params or {}}))
            while True:
                m = json.loads(ws.recv())
                if m.get("id") == mid[0]:
                    return m

        cmd("Page.navigate", {"url": "http://127.0.0.1:8765/board.html?b=title_catalog"})
        time.sleep(6)
        expr = """(() => {
          const cards=[...document.querySelectorAll('[data-card], .card, .item, .rc')];
          let multi=0, txtOver=0, cardsWithTitle=0;
          const samples=[];
          for (const c of cards) {
            const t=c.querySelector('.i-title,.i-logo');
            if(!t) continue;
            cardsWithTitle++;
            const imgs=t.querySelectorAll('img');
            if(imgs.length>1){multi++; if(samples.length<5) samples.push(['multi',c.innerText.slice(0,20),imgs.length]);}
            const tn=t.querySelector('.i-name-txt');
            if(imgs.length>=1 && tn && getComputedStyle(tn).display!=='none'){txtOver++; if(samples.length<8) samples.push(['txt',c.innerText.slice(0,20)]);}
          }
          return {cards:cards.length, cardsWithTitle, multi, txtOver, samples};
        })()"""
        ev = cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        print(json.dumps((ev.get("result", {}).get("result", {}) or {}).get("value"), ensure_ascii=False, indent=1))
        ws.close()
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
