# -*- coding: utf-8 -*-
"""抓指定板块页的 JS 异常 / console.error，并报渲染出的卡片数。"""
from __future__ import annotations

import json
import sys
import time
import urllib.request

import subprocess
import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9391


def main() -> int:
    bid = sys.argv[1] if len(sys.argv) > 1 else "kill_broadcast"
    url = f"http://127.0.0.1:8765/board.html?b={bid}"
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
                             r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_err2",
                             "--window-size=1200,700", url],
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
        mid = [0]

        def send(method, params=None):
            mid[0] += 1
            ws.send(json.dumps({"id": mid[0], "method": method, "params": params or {}}))
            return mid[0]

        send("Runtime.enable")
        send("Log.enable")
        errors = []
        deadline = time.time() + 9
        while time.time() < deadline:
            try:
                ws.settimeout(1.0)
                msg = json.loads(ws.recv())
            except Exception:
                continue
            m = msg.get("method")
            if m == "Runtime.exceptionThrown":
                d = msg["params"]["exceptionDetails"]
                errors.append(("exception", d.get("text"), (d.get("exception") or {}).get("description", "")[:300]))
            elif m == "Runtime.consoleAPICalled" and msg["params"].get("type") == "error":
                args = [a.get("value") or a.get("description") for a in msg["params"].get("args", [])]
                errors.append(("console.error", " ".join(str(a) for a in args)[:300]))
        # 读渲染结果
        mid[0] += 1
        ws.send(json.dumps({"id": mid[0], "method": "Runtime.evaluate",
                            "params": {"expression": "({cards:document.querySelectorAll('[data-card],.card,.rc').length, txt:(document.getElementById('grid')||{}).textContent ? (document.getElementById('grid').textContent.trim().slice(0,40)) : 'no-grid'})",
                                       "returnByValue": True}}))
        val = None
        t0 = time.time()
        while time.time() - t0 < 5:
            try:
                m2 = json.loads(ws.recv())
            except Exception:
                break
            if m2.get("id") == mid[0]:
                val = m2.get("result", {}).get("result", {}).get("value")
                break
        print("渲染:", val)
        print("错误", len(errors))
        for e in errors[:8]:
            print("  ", e)
        ws.close()
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
