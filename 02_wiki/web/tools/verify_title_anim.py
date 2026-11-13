# -*- coding: utf-8 -*-
"""验证动态称号真的在动：同一页面相隔 900ms 截两次，比对卡片区域像素差异。"""
from __future__ import annotations

import base64
import io
import json
import subprocess
import sys
import time
import urllib.request

import websocket
from PIL import Image, ImageChops

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9403
TARGET_ID = sys.argv[1] if len(sys.argv) > 1 else "1074"


def main() -> int:
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
                             r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_anim",
                             "--window-size=1400,950", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ws_url = None
        for _ in range(40):
            try:
                d = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json").read())
                pg = [x for x in d if x.get("type") == "page"]
                if pg:
                    ws_url = pg[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                pass
            time.sleep(0.5)
        ws = websocket.create_connection(ws_url, timeout=30)
        mid = [0]

        def cmd(m, p=None):
            mid[0] += 1
            ws.send(json.dumps({"id": mid[0], "method": m, "params": p or {}}))
            while True:
                r = json.loads(ws.recv())
                if r.get("id") == mid[0]:
                    return r

        cmd("Page.navigate", {"url": "http://127.0.0.1:8765/board.html?b=title_catalog"})
        time.sleep(6)
        box = cmd("Runtime.evaluate", {"expression": f"""(() => {{
            const t=[...document.querySelectorAll('img[src$=".webp"]')];
            if(!t.length) return null;
            const el=t[0].closest('.i-logo')||t[0];
            el.scrollIntoView({block:'center'});
            const r=el.getBoundingClientRect();
            return {{x:r.x,y:r.y,w:r.width,h:r.height,src:t[0].getAttribute('src'),n:t.length}};
        }})()""", "returnByValue": True})
        time.sleep(1.5)
        box = cmd("Runtime.evaluate", {"expression": """(() => {
            const t=[...document.querySelectorAll('img[src$=\".webp\"]')];
            if(!t.length) return null;
            const el=t[0].closest('.i-logo')||t[0];
            const r=el.getBoundingClientRect();
            return {x:r.x,y:r.y,w:r.width,h:r.height,src:t[0].getAttribute('src'),n:t.length};
        })()""", "returnByValue": True})
        b = (box.get("result", {}).get("result", {}) or {}).get("value")
        print("定位底图:", b)
        if not b:
            print("页面没有 i-logo-anim（可能全是纯文字卡）")
            return 1

        def shot():
            r = cmd("Page.captureScreenshot", {"format": "png"})
            data = base64.b64decode(r["result"]["data"])
            return Image.open(io.BytesIO(data)).convert("RGB")

        a = shot()
        time.sleep(0.9)
        c = shot()
        clip = (int(b["x"]), int(b["y"]), int(b["x"] + b["w"]), int(b["y"] + b["h"]))
        ca, cc = a.crop(clip), c.crop(clip)
        diff = ImageChops.difference(ca, cc)
        bbox = diff.getbbox()
        px = sum(1 for p in diff.getdata() if sum(p) > 12)
        print(f"区域 {clip} | 差异像素 {px} / {ca.size[0]*ca.size[1]} | bbox {bbox}")
        print("结论：", "在动 ✓" if px > 200 else "静止 ✗")
        a.save(r"E:\la拆包项目\_截图\anim_t0.png")
        c.save(r"E:\la拆包项目\_截图\anim_t1.png")
        ws.close()
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
