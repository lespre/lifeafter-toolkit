# -*- coding: utf-8 -*-
"""诊断板页侧栏「显示内测板块」控件为什么看不见，并截侧栏图。"""
from __future__ import annotations

import base64
import json
import pathlib
import subprocess
import time
import urllib.request

import websocket

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
URL = "http://127.0.0.1:8765/board.html?b=fashion_wardrobe"
PORT = 9341
OUT = pathlib.Path("E:/la拆包项目/_截图/diag_nav.png")

EXPR = r"""
(function(){
  var o={};
  try{
    var nav=document.getElementById('siteNav');
    var a=document.getElementById('navOptPreviewRow');
    o.navRect=[nav.getBoundingClientRect().x, nav.getBoundingClientRect().y,
               nav.getBoundingClientRect().width, nav.getBoundingClientRect().height];
    o.navScroll=[nav.scrollTop, nav.scrollHeight, nav.clientHeight];
    if(!a){ o.row='缺失'; return JSON.stringify(o); }
    var ar=a.getBoundingClientRect();
    o.aRect=[ar.x, ar.y, ar.width, ar.height];
    var cs=getComputedStyle(a);
    o.style=[cs.display, cs.fontSize, cs.color, cs.visibility, cs.opacity];
    var tn=null;
    for(var i=0;i<a.childNodes.length;i++){ if(a.childNodes[i].nodeType===3 && a.childNodes[i].textContent.trim()){ tn=a.childNodes[i]; break; } }
    o.text=tn?tn.textContent.trim():'(无文本节点)';
    if(tn){
      var r=document.createRange(); r.selectNodeContents(tn);
      o.textRects=[...r.getClientRects()].map(function(x){return [Math.round(x.x),Math.round(x.y),Math.round(x.width),Math.round(x.height)];});
    }
    var cb=document.getElementById('navOptPreview');
    if(cb){ var cr=cb.getBoundingClientRect(); o.cbRect=[cr.x,cr.y,cr.width,cr.height]; }
  }catch(e){ o.err=String(e); }
  return JSON.stringify(o);
})()
"""


def main() -> int:
    proc = subprocess.Popen([
        CHROME, "--headless=new", "--disable-gpu", "--force-device-scale-factor=1",
        f"--remote-debugging-port={PORT}",
        r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_nav",
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

        ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
                            "params": {"expression": EXPR, "returnByValue": True}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == 1:
                val = msg.get("result", {}).get("result", {})
                print(val.get("value") or msg)
                break

        ws.send(json.dumps({"id": 2, "method": "Page.captureScreenshot",
                            "params": {"format": "png", "clip": {"x": 0, "y": 0, "width": 260, "height": 300, "scale": 3}}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == 2:
                OUT.write_bytes(base64.b64decode(msg["result"]["data"]))
                print("截图 →", OUT)
                break
        ws.close()
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    raise SystemExit(main())
