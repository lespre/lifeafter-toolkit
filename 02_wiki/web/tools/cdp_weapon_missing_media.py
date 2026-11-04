# -*- coding: utf-8 -*-
"""查武器皮肤板上「缺图」标记到底落在哪些卡上、原因是什么。"""
from __future__ import annotations

import json
import subprocess
import time
import urllib.request

import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
URL = "http://127.0.0.1:8765/board.html?b=weapon_skin_sfx_text_sources"
PORT = 9381


def main() -> int:
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
                             r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_ws",
                             "--window-size=1400,1000", URL],
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
        time.sleep(5)
        mid = [0]

        def ev(expr):
            mid[0] += 1
            ws.send(json.dumps({"id": mid[0], "method": "Runtime.evaluate",
                                "params": {"expression": expr, "returnByValue": True}}))
            while True:
                m = json.loads(ws.recv())
                if m.get("id") == mid[0]:
                    r = m.get("result", {}).get("result", {})
                    return r.get("value")

        print("卡片数:", ev("document.querySelectorAll('.i-card, [data-skin-id]').length"))
        print("带缺图文字元素:", ev("[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&/缺图/.test(e.textContent||'')).length"))
        print("样例:", ev("""(()=>{
          const els=[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&/缺图/.test(e.textContent||'')).slice(0,6);
          return els.map(e=>{const c=e.closest('[data-skin-id]');return {txt:e.textContent.trim().slice(0,20), skinId:c?c.dataset.skinId:null, cls:e.className};});
        })()"""))
        print("媒体库条数:", ev("Object.keys((window.WEAPON_SKIN_MEDIA||{}).skins||{}).length"))
        print("板上无媒体条目:", ev("""(()=>{
          const b=(window.WIKI_BOARD_weapon_skin_sfx_text_sources||{}).items||[];
          const bank=(window.WEAPON_SKIN_MEDIA||{}).skins||{};
          const miss=b.filter(i=>!bank[String(i.id)]);
          return {total:b.length, miss:miss.length, ids:miss.map(i=>String(i.id)).slice(0,10)};
        })()"""))
        ws.close()
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
