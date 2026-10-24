# -*- coding: utf-8 -*-
"""名片框 Spine 批量出图：解包三件套 → spine_view.html 渲染 → 裁切 PNG。

用法（需先起 wiki 服务 8765 与 headless chrome --remote-debugging-port=9333）：
  python render_namecard_frames.py [--limit 100] [--ids bc_1,bc_2] [--apply]

产出：assets/avatar_frames/<id>.png，并回写 avatar_catalog.json 的 _media.images
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import pathlib
import sys
import urllib.request

import websockets

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import spine_fetch as SF  # noqa: E402

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
LIVE = WEB / "assets/spine_live"
FRAMES = WEB / "assets/avatar_frames"
CAT = WEB / "data/boards/avatar_catalog.json"
CDP = 9333
SRV = "http://127.0.0.1:8765"

JS_EXPORT = r"""
(() => {
  const c = document.getElementById('cv');
  const ctx = c.getContext('2d');
  const d = ctx.getImageData(0, 0, c.width, c.height).data;
  let x0 = c.width, y0 = c.height, x1 = -1, y1 = -1;
  for (let y = 0; y < c.height; y++) {
    for (let x = 0; x < c.width; x++) {
      if (d[(y * c.width + x) * 4 + 3] > 8) {
        if (x < x0) x0 = x; if (x > x1) x1 = x;
        if (y < y0) y0 = y; if (y > y1) y1 = y;
      }
    }
  }
  if (x1 < 0) return JSON.stringify({ ok: false, why: 'empty' });
  const pad = 6, w = x1 - x0 + 1 + pad * 2, h = y1 - y0 + 1 + pad * 2;
  const out = document.createElement('canvas');
  out.width = w; out.height = h;
  out.getContext('2d').drawImage(c, x0 - pad, y0 - pad, w, h, 0, 0, w, h);
  return JSON.stringify({ ok: true, w: w, h: h, url: out.toDataURL('image/png') });
})()
"""


def ensure_assets(spine_path: str) -> tuple[bool, str]:
    """把 atlas/json/贴图页落到 spine_live/<spine_path 目录>/ 。返回 (ok, reason)。"""
    sp = spine_path.replace('\\', '/').lstrip('/')
    outdir = LIVE / sp.rsplit('/', 1)[0]
    name = sp.rsplit('/', 1)[-1]
    got = []
    for ext in ('.atlas', '.json'):
        p = outdir / (name + ext)
        if p.is_file() and p.stat().st_size > 0:
            got.append(ext)
            continue
        if SF.save(sp + ext, p):
            got.append(ext)
    if len(got) < 2:
        return False, 'text miss ' + ','.join(got)

    at = (outdir / (name + '.atlas')).read_text(encoding='utf-8', errors='ignore')
    pages = [l.strip() for l in at.splitlines()
             if l.strip().lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not pages:
        return False, 'no page in atlas'
    for pg in pages:
        dst = outdir / pg
        if dst.is_file() and dst.stat().st_size > 1024:
            continue
        if not SF.export_page(sp, dst):
            return False, 'page miss ' + pg
    return True, ''


async def render_all(items, ws_url, limit):
    done, fail = [], []
    async with websockets.connect(ws_url, max_size=80_000_000) as ws:
        i = 0

        async def call(method, **params):
            nonlocal i
            i += 1
            await ws.send(json.dumps({"id": i, "method": method, "params": params}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == i:
                    return msg

        await call("Page.enable")
        await call("Runtime.enable")
        await call("Emulation.setDeviceMetricsOverride", width=1100, height=860,
                   deviceScaleFactor=1, mobile=False)

        for n, it in enumerate(items, 1):
            sid, sp = it["id"], it["spine_path"]
            dst0 = FRAMES / (sid + '.png')
            if dst0.is_file() and dst0.stat().st_size > 2048:
                done.append((sid, 0, 0, dst0.stat().st_size))
                print('[%d/%d] %s 已有，跳过' % (n, len(items), sid))
                continue
            ok, why = ensure_assets(sp)
            if not ok:
                fail.append((sid, sp, why))
                print('[%d/%d] %s 取件失败: %s' % (n, len(items), sid, why))
                continue
            url = "%s/spine_view.html?f=%s.atlas" % (SRV, sp)
            await call("Page.navigate", url=url)
            data = None
            for _ in range(60):
                await asyncio.sleep(0.12)
                r = await call("Runtime.evaluate", returnByValue=True,
                               expression="JSON.stringify({ready:!!window.__ready,err:(document.getElementById('err')||{}).textContent||''})")
                v = json.loads(r["result"]["result"]["value"] if "result" in r["result"] else "{}")
                if v.get("ready") or v.get("err"):
                    break
            else:
                v = {}
            if not v.get("ready"):
                fail.append((sid, sp, 'render ' + str(v.get('err'))[:80]))
                print('[%d/%d] %s 渲染失败 %s' % (n, len(items), sid, v.get('err')))
                continue
            r = await call("Runtime.evaluate", returnByValue=True, expression=JS_EXPORT)
            try:
                res = json.loads(r["result"]["result"]["value"])
            except Exception:
                res = {"ok": False, "why": "eval"}
            if not res.get("ok"):
                fail.append((sid, sp, 'empty canvas'))
                print('[%d/%d] %s 画布空' % (n, len(items), sid))
                continue
            png = base64.b64decode(res["url"].split(',', 1)[1])
            dst = FRAMES / (sid + '.png')
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(png)
            done.append((sid, res["w"], res["h"], len(png)))
            print('[%d/%d] %s %dx%d %.0fKB' % (n, len(items), sid, res["w"], res["h"], len(png) / 1024))
    return done, fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=100)
    ap.add_argument('--ids', default='')
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    cat = json.loads(CAT.read_text(encoding='utf-8'))
    pool = [i for i in cat['items'] if i.get('kind') == '名片框' and i.get('spine_path')]
    if a.ids:
        keep = set(x.strip() for x in a.ids.split(',') if x.strip())
        pool = [i for i in pool if i['id'] in keep]
    pool = pool[: a.limit]
    print('待渲染 %d 条' % len(pool))

    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json/list" % CDP).read())
    page = next(t for t in tabs if t["type"] == "page")
    done, fail = asyncio.run(render_all(pool, page["webSocketDebuggerUrl"], a.limit))

    print('\n成功 %d ｜ 失败 %d' % (len(done), len(fail)))
    for f in fail[:10]:
        print('  fail', f)

    if a.apply:
        by = {d[0]: d for d in done}
        n = 0
        for it in cat['items']:
            if it['id'] in by:
                _, w, h, _sz = by[it['id']]
                imgs = [im for im in ((it.get('_media') or {}).get('images') or [])
                        if im.get('label') != '名片框']
                imgs.append({"png": "assets/avatar_frames/%s.png" % it['id'],
                             "label": "名片框", "w": w, "h": h,
                             "source": "spine/setup-pose",
                             "spine": it.get('spine_path')})
                it.setdefault('_media', {})['images'] = imgs
                n += 1
        CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding='utf-8')
        print('回写 %d 条 _media.images' % n)

    (FRAMES.parent / 'avatar_frames_report.json').write_text(
        json.dumps({"ok": done, "fail": fail}, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
