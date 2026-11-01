# -*- coding: utf-8 -*-
"""验证左栏类目折叠：大目录（置顶）与子分组（装备属性）都能收放。"""
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
URL = "http://127.0.0.1:8765/board.html?b=fashion_wardrobe"
PORT = 9362
OUT = pathlib.Path("E:/la拆包项目/_截图/nav_tree_fold.png")


def main() -> int:
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
        r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_tree",
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
        time.sleep(3.5)
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

        print("大目录数:", ev("document.querySelectorAll('#siteNav .grp[data-grp]').length"))
        print("子分组数:", ev("document.querySelectorAll('#siteNav .leafhd[data-leaf]').length"))
        print("置顶分组:", ev("document.querySelector('#siteNav .grp[data-grp]').textContent.trim()"))
        print("第一个子分组:", ev("(document.querySelector('#siteNav .leafhd[data-leaf]')||{}).textContent"))

        # 点「置顶」大目录
        ev("document.querySelector('#siteNav .grp[data-grp]').click()")
        time.sleep(0.4)
        print("点后 置顶 body display:", ev("getComputedStyle(document.querySelector('#siteNav .grp[data-grp]').nextElementSibling).display"))
        print("localStorage:", ev("localStorage.getItem('board_nav_closed')"))

        # 展开回去，再点子分组
        ev("document.querySelector('#siteNav .grp[data-grp]').click()")
        time.sleep(0.3)
        hits = ev("""(function(){
          var hs=document.querySelectorAll('#siteNav .leafhd[data-leaf]');
          for(var i=0;i<hs.length;i++){ if(/装备/.test(hs[i].textContent)) return hs[i].getAttribute('data-leaf'); }
          return hs.length? hs[0].getAttribute('data-leaf') : null;
        })()""")
        print("目标子分组:", hits)
        ev(f"""document.querySelector('#siteNav .leafhd[data-leaf="{hits}"]').click()""")
        time.sleep(0.4)
        print("子分组折叠后 display:", ev(f"""getComputedStyle(document.querySelector('#siteNav .leafbody[data-lbody="{hits}"]')).display"""))
        print("展开后再折回去（保持折叠态用于截图）")

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
