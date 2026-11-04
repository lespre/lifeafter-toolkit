# -*- coding: utf-8 -*-
"""称号板视觉层体检：抓 404 资源 + 统计底图/美术字节点数。"""
from __future__ import annotations

import json
import subprocess
import time
import urllib.request

import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9397


def main() -> int:
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu",
                             f"--remote-debugging-port={PORT}",
                             r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_title",
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

        def cmd(method, params=None, wait=True):
            mid[0] += 1
            ws.send(json.dumps({"id": mid[0], "method": method, "params": params or {}}))
            if not wait:
                return None
            while True:
                m = json.loads(ws.recv())
                if m.get("id") == mid[0]:
                    return m

        cmd("Network.enable")
        cmd("Runtime.enable")
        cmd("Page.navigate", {"url": "http://127.0.0.1:8765/board.html?b=title_catalog"})
        bad = []
        deadline = time.time() + 12
        while time.time() < deadline:
            try:
                ws.settimeout(0.8)
                m = json.loads(ws.recv())
            except Exception:
                continue
            if m.get("method") == "Network.responseReceived":
                r = m["params"]["response"]
                if r.get("status", 0) >= 400:
                    bad.append((r["status"], r["url"][-70:]))
        ev = cmd("Runtime.evaluate", {"expression":
                  "({cards:document.querySelectorAll('.i-title,.title-name').length,"
                  " art:document.querySelectorAll('.title-art,.t-art').length,"
                  " dyn:document.querySelectorAll('.title-dyn,.t-dyn').length,"
                  " imgs:document.querySelectorAll('.grid img').length,"
                  " broken:Array.from(document.images).filter(i=>!i.complete||i.naturalWidth===0).length})",
                  "returnByValue": True})
        print("节点统计:", (ev.get("result", {}).get("result", {}) or {}).get("value"))
        print("404/失败", len(bad))
        for b in bad[:8]:
            print("  ", b)
        ws.close()
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
