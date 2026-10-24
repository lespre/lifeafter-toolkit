# -*- coding: utf-8 -*-
"""时装板自检：无头 Chrome(CDP 9333) 打开 board.html?b=fashion_wardrobe → 抓数 → 截图。"""
import asyncio, base64, json, sys, urllib.request, websockets

PORT = 9333
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8811/board.html?b=fashion_wardrobe"
OUT = sys.argv[2] if len(sys.argv) > 2 else r"C:/Users/Administrator/AppData/Local/hermes/cache/scratch/fw_page.png"

Q = r"""(async () => {
  const out = {};
  out.title = document.title;
  out.count = (document.querySelector('#count')||{}).textContent || null;
  out.pills = (document.querySelector('#pills')||{}).innerText || null;
  out.items = (window.DATA&&DATA.items)?DATA.items.length:null;
  out.cards = document.querySelectorAll('.fcard').length;
  const rails=[...document.querySelectorAll('.fr-rail')];
  out.rails = rails.length;
  out.railImgs = rails.reduce((s,r)=>s+r.querySelectorAll('img').length,0);
  out.placeholderImgs = rails.reduce((s,r)=>s+r.querySelectorAll('img[alt="占位"]').length,0);
  out.brokenImgs = [...document.querySelectorAll('.fr-rail img')].filter(i=>i.complete&&i.naturalWidth===0).length;
  const w=document.getElementById('fFashionWrap');
  out.filters = w? (w.innerText||'').replace(/\s+/g,' ').slice(0,600) : null;
  const sel=document.getElementById('frSort');
  out.sortOptions = sel? [...sel.options].map(o=>o.textContent) : null;
  out.sortValue = sel? sel.value : null;
  // 部位筛选：点「衣服」
  const chips=[...document.querySelectorAll('#fFashionWrap .fr-chip')];
  const cloth=chips.find(c=>c.textContent.startsWith('衣服'));
  if(cloth){ cloth.click(); await new Promise(r=>setTimeout(r,600));
    out.afterCloth = {cards:document.querySelectorAll('.fcard').length, pills:(document.querySelector('#pills')||{}).innerText,
                      url:location.search};
    cloth.click(); await new Promise(r=>setTimeout(r,600));
  }
  // 期限筛选：限时
  const timed=[...document.querySelectorAll('#fFashionWrap .fr-chip')].find(c=>c.textContent.startsWith('限时'));
  if(timed){ timed.click(); await new Promise(r=>setTimeout(r,600));
    out.afterTimed={cards:document.querySelectorAll('.fcard').length};
    timed.click(); await new Promise(r=>setTimeout(r,600));
  }
  // 图示筛选：有图
  const img=[...document.querySelectorAll('#fFashionWrap .fr-chip')].find(c=>c.textContent.startsWith('有图'));
  if(img){ img.click(); await new Promise(r=>setTimeout(r,600));
    out.afterHasImg={cards:document.querySelectorAll('.fcard').length};
    img.click(); await new Promise(r=>setTimeout(r,400));
  }
  // 性别筛选：女
  const fem=[...document.querySelectorAll('#fFashionWrap .fr-chip')].find(c=>c.textContent.startsWith('女'));
  if(fem){ fem.click(); await new Promise(r=>setTimeout(r,600));
    out.afterFemale={cards:document.querySelectorAll('.fcard').length};
    fem.click(); await new Promise(r=>setTimeout(r,400));
  }
  // 排序：魅力值 ↓
  const s=document.getElementById('frSort');
  if(s){ s.value='charm_desc'; s.dispatchEvent(new Event('change')); await new Promise(r=>setTimeout(r,700));
    const names=[...document.querySelectorAll('.fcard')].slice(0,5).map(c=>(c.querySelector('.fr-name')||{}).textContent);
    out.sortTop5 = names;
    s.value='model_desc'; s.dispatchEvent(new Event('change')); await new Promise(r=>setTimeout(r,300));
  }
  // 第一张卡的折叠区字段
  const det=document.querySelector('.fcard details.tech');
  out.firstCardTech = det? det.innerText.replace(/\s+/g,' ').slice(0,700):null;
  out.firstCardText = (document.querySelector('.fcard')||{}).innerText;
  return JSON.stringify(out);
})()"""


async def main():
    tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list").read())
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=60_000_000) as ws:
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
        await call("Emulation.setDeviceMetricsOverride", width=1440, height=1200, deviceScaleFactor=1, mobile=False)
        await call("Page.navigate", url=URL)
        await asyncio.sleep(7)
        r = await call("Runtime.evaluate", expression=Q, awaitPromise=True, returnByValue=True)
        val = r.get("result", {}).get("result", {}).get("value") or r.get("result", {}).get("value")
        if val is None:
            print("RAW:", json.dumps(r, ensure_ascii=False)[:1500])
        print(val)
        await asyncio.sleep(0.5)
        shot = await call("Page.captureScreenshot", format="png")
        open(OUT, "wb").write(base64.b64decode(shot["result"]["data"]))
        print("saved", OUT)

asyncio.run(main())
