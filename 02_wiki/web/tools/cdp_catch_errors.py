# -*- coding: utf-8 -*-
"""抓板页加载时的 JS 异常与 console.error。"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request

import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/board.html?b=fashion_wardrobe"
PORT = 9351


def main() -> int:
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
        r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_err",
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
        if not ws_url:
            print("CDP 连不上")
            return 1
        ws = websocket.create_connection(ws_url, timeout=20)
        for i, m in enumerate(("Runtime.enable", "Log.enable"), 1):
            ws.send(json.dumps({"id": i, "method": m}))
        ws.send(json.dumps({"id": 99, "method": "Page.reload", "params": {"ignoreCache": True}}))
        deadline = time.time() + 12
        ws.settimeout(2)
        seen = 0
        while time.time() < deadline:
            try:
                msg = json.loads(ws.recv())
            except Exception:
                continue
            method = msg.get("method")
            if method == "Runtime.exceptionThrown":
                d = msg["params"]["exceptionDetails"]
                txt = d.get("exception", {}).get("description") or d.get("text")
                print("EXC:", str(txt)[:400])
                seen += 1
            elif method == "Log.entryAdded":
                e = msg["params"]["entry"]
                if e.get("level") in ("error", "warning"):
                    print("LOG:", e.get("level"), str(e.get("text"))[:300])
                    seen += 1
            elif method == "Runtime.consoleAPICalled" and msg["params"].get("type") == "error":
                args = [a.get("value") or a.get("description") for a in msg["params"]["args"]]
                print("CONSOLE:", str(args)[:300])
                seen += 1
        print("异常/错误条数:", seen)

        ws.send(json.dumps({"id": 100, "method": "Runtime.evaluate", "params": {
            "expression": "document.getElementById('grid')?document.getElementById('grid').innerText.slice(0,80):'(no grid)'",
            "returnByValue": True}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == 100:
                print("grid 文本:", msg["result"]["result"].get("value"))
                break
        ws.close()
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
