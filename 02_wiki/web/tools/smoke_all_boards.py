# -*- coding: utf-8 -*-
"""全站板块冒烟：逐个板块页检查 JS 异常 + 是否渲染出内容。

输出：01_索引与产物/30_分析/板块冒烟_<ts>.md
"""
from __future__ import annotations

import json
import subprocess
import time
import urllib.request
from pathlib import Path

import websocket

WEB = Path(r"E:\la拆包项目\02_wiki\web")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9395
OUT = Path(r"E:\la拆包项目\01_索引与产物\30_分析")


def main() -> int:
    pol = json.loads((WEB / "data/publication_policy.json").read_text(encoding="utf-8"))["boards"]
    pub = [b for b, m in pol.items() if (m or {}).get("publication_status") == "published"]

    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
                             r"--user-data-dir=C:\Users\Administrator\AppData\Local\hermes\cache\scratch\cdp_smoke",
                             "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    rows = []
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

        cmd("Runtime.enable")
        cmd("Log.enable")
        for bid in pub:
            cmd("Page.navigate", {"url": f"http://127.0.0.1:8765/board.html?b={bid}"})
            time.sleep(4.5)
            ev = cmd("Runtime.evaluate", {"expression":
                      "({txt:(document.body.innerText||'').trim().length, grid:(document.getElementById('grid')||{}).innerText||''})",
                      "returnByValue": True})
            val = (ev.get("result", {}).get("result", {}) or {}).get("value") or {}
            body_len = val.get("txt", 0)
            grid_len = len(val.get("grid", "") or "")
            err = cmd("Runtime.evaluate", {"expression": "window.__errcount||0", "returnByValue": True})
            rows.append({"board": bid, "body": body_len, "grid": grid_len,
                         "ok": body_len > 200 and grid_len > 0})
            print(f"{bid:34s} body={body_len:<6} grid={grid_len:<6} {'OK' if rows[-1]['ok'] else '✗'}", flush=True)
        ws.close()
    finally:
        proc.terminate()

    ts = time.strftime("%Y%m%d_%H%M")
    bad = [r for r in rows if not r["ok"]]
    md = OUT / f"板块冒烟_{ts}.md"
    lines = [f"# 板块冒烟 {ts}", "", f"- 板块 {len(rows)}，正常 {len(rows)-len(bad)}，异常 {len(bad)}", "",
             "| 板块 | body 字符 | grid 字符 | 结果 |", "|---|---:|---:|---|"]
    for r in rows:
        lines.append(f"| `{r['board']}` | {r['body']} | {r['grid']} | {'OK' if r['ok'] else '**异常**'} |")
    md.write_text("\n".join(lines), encoding="utf-8")
    print("\n异常:", [b["board"] for b in bad])
    print("报告", md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
